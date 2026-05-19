"""Inventory ledger service — the **single writer** for stock movements.

ADR-007 / M05 plan: every stock change goes through
:func:`post`. Callers (GRN approval, purchase return posting, sales
billing, transfers, adjustments, wastage, counts) translate their
domain items into the generic ``items=[{...}]`` payload accepted here
and the service handles:

* per-(item, branch[, warehouse]) lock & ``Stock`` upsert
* ``InventoryLedger`` write with ``balance_before`` / ``balance_after``
* per-``Batch`` lock & ``qty_remaining`` adjust (inbound creates,
  outbound decrements; auto-marks ``CONSUMED`` at zero)
* **negative-stock guard** — if any ``qty_after < 0`` the whole call
  rolls back with :class:`apps.inventory.exceptions.InsufficientStock`
  (code ``INV-010``).

The function is decorated ``@transaction.atomic`` so a partial batch
cannot leak: either every line posts or none do.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from ..exceptions import InsufficientStock
from ..models import Batch, BatchStatus, InventoryLedger, Stock

logger = logging.getLogger(__name__)


# Tiny helpers — kept local so the service has no external surface
# beyond ``post`` and the ``MovementItem`` dataclass.


def _to_decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def _resolve_target(item: dict[str, Any]) -> tuple[int | None, int | None]:
    """Return ``(product_id, variant_id)`` with XOR validation."""

    product = item.get("product") or item.get("product_id")
    variant = item.get("variant") or item.get("variant_id")
    product_id = getattr(product, "pk", product) if product is not None else None
    variant_id = getattr(variant, "pk", variant) if variant is not None else None
    if (product_id is None) == (variant_id is None):
        raise ValueError(
            "ledger_service.post: each item must set exactly one of product / variant.",
        )
    return product_id, variant_id


@dataclass(frozen=True)
class MovementItem:
    """Internal normalised representation of one ledger line."""

    product_id: int | None
    variant_id: int | None
    qty_change: Decimal
    batch: Batch | None
    cost_price: Decimal


def _normalise_items(
    items: Iterable[dict[str, Any]],
    *,
    branch_id: int,
) -> list[MovementItem]:
    """Validate inputs and resolve ``batch`` references.

    ``batch_kwargs`` (``{"batch_no", "mfg_date", "expiry_date",
    "cost_price"}``) is upserted into a :class:`Batch` row at this
    stage so the per-item loop below can lock it. Inbound movements
    (positive ``qty_change``) create the batch when missing; outbound
    movements require it to already exist.
    """

    normalised: list[MovementItem] = []
    for raw in items:
        product_id, variant_id = _resolve_target(raw)
        qty_change = _to_decimal(raw.get("qty_change"))
        if qty_change == 0:
            continue  # nothing to post
        cost_price = _to_decimal(raw.get("cost_price"))

        batch: Batch | None = raw.get("batch")
        batch_kwargs = raw.get("batch_kwargs")
        if batch is None and batch_kwargs:
            batch_no = (batch_kwargs.get("batch_no") or "").strip()
            if batch_no:
                lookup = {
                    "branch_id": branch_id,
                    "batch_no": batch_no,
                    "product_id": product_id,
                    "variant_id": variant_id,
                }
                batch = Batch.objects.filter(**lookup).first()
                if batch is None:
                    if qty_change <= 0:
                        raise ValueError(
                            "ledger_service.post: outbound movement references "
                            f"unknown batch {batch_no!r}.",
                        )
                    batch = Batch.objects.create(
                        **lookup,
                        mfg_date=batch_kwargs.get("mfg_date"),
                        expiry_date=batch_kwargs.get("expiry_date"),
                        cost_price=_to_decimal(batch_kwargs.get("cost_price") or cost_price),
                        qty_received=qty_change,
                        qty_remaining=qty_change,
                    )

        normalised.append(
            MovementItem(
                product_id=product_id,
                variant_id=variant_id,
                qty_change=qty_change,
                batch=batch,
                cost_price=cost_price,
            )
        )
    return normalised


def _lock_stock_row(
    *,
    product_id: int | None,
    variant_id: int | None,
    branch_id: int,
    warehouse_id: int | None,
) -> Stock:
    """Return a row-locked :class:`Stock` row, creating it if missing.

    ``select_for_update`` serialises concurrent ``post`` calls on the
    same (item, branch[, warehouse]) so balance computations stay
    consistent — this is the cornerstone of the concurrency guarantee
    tested in step 10.
    """

    qs = Stock.all_objects.select_for_update().filter(
        branch_id=branch_id,
        product_id=product_id,
        variant_id=variant_id,
        warehouse_id=warehouse_id,
    )
    row = qs.first()
    if row is not None:
        return row
    return Stock.objects.create(
        product_id=product_id,
        variant_id=variant_id,
        branch_id=branch_id,
        warehouse_id=warehouse_id,
    )


def _apply_batch_delta(batch: Batch, qty_change: Decimal) -> None:
    """Adjust :attr:`Batch.qty_remaining` and roll the status."""

    locked = Batch.all_objects.select_for_update().get(pk=batch.pk)
    new_remaining = _to_decimal(locked.qty_remaining) + qty_change
    if new_remaining < 0:
        # Same INV-010 boundary — a batch can never go negative either.
        raise InsufficientStock()
    locked.qty_remaining = new_remaining
    if new_remaining == 0 and qty_change < 0:
        locked.status = BatchStatus.CONSUMED
    locked.save(update_fields=["qty_remaining", "status", "updated_at"])


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


@transaction.atomic
def post(
    *,
    ref_type: str,
    ref_id: str | int,
    items: Iterable[dict[str, Any]],
    branch,
    actor=None,
    warehouse=None,
    reason_code: str = "",
    remarks: str = "",
) -> list[InventoryLedger]:
    """Write a batch of inventory movements atomically.

    Parameters
    ----------
    ref_type:
        One of :class:`apps.inventory.models.InventoryRefType` values
        (``GRN``, ``SALE``, ``TRANSFER`` …).
    ref_id:
        Identifier of the originating document; coerced to ``str``.
    items:
        Iterable of dicts. Required keys per item:

        * ``product`` or ``product_id`` *xor* ``variant`` or ``variant_id``
        * ``qty_change`` (signed Decimal/str/int; ``0`` is skipped)

        Optional:

        * ``batch`` (instance) **or** ``batch_kwargs={batch_no, mfg_date,
          expiry_date, cost_price}`` — inbound calls upsert the batch
          on demand.
        * ``cost_price`` — falls through to the batch row when one is
          created.
    branch, warehouse, actor:
        FK targets / acting user (instances **or** ids).
    reason_code:
        Free-form short code; required by adjustments / wastage /
        counts (validated by their respective services, not here).

    Returns
    -------
    list[InventoryLedger]
        The freshly created ledger rows in input order.

    Raises
    ------
    InsufficientStock
        When any line would push :attr:`Stock.qty_on_hand` or
        :attr:`Batch.qty_remaining` below zero. The transaction is
        rolled back so no partial movement leaks.
    """

    branch_id = getattr(branch, "pk", branch)
    warehouse_id = getattr(warehouse, "pk", warehouse) if warehouse is not None else None
    actor_id = getattr(actor, "pk", actor) if actor is not None else None

    normalised = _normalise_items(items, branch_id=branch_id)
    created: list[InventoryLedger] = []
    now = timezone.now()

    for item in normalised:
        stock = _lock_stock_row(
            product_id=item.product_id,
            variant_id=item.variant_id,
            branch_id=branch_id,
            warehouse_id=warehouse_id,
        )
        qty_before = _to_decimal(stock.qty_on_hand)
        qty_after = qty_before + item.qty_change
        if qty_after < 0:
            raise InsufficientStock()

        entry = InventoryLedger.objects.create(
            reference_type=str(ref_type),
            reference_id=str(ref_id),
            amount=item.qty_change,
            balance_before=qty_before,
            balance_after=qty_after,
            actor_id=actor_id,
            branch_id=branch_id,
            remarks=(remarks or "")[:255],
            product_id=item.product_id,
            variant_id=item.variant_id,
            batch=item.batch,
            branch=stock.branch,
            warehouse_id=warehouse_id,
            reason_code=reason_code or "",
        )
        created.append(entry)

        stock.qty_on_hand = qty_after
        stock.last_movement_at = now
        stock.save(update_fields=["qty_on_hand", "last_movement_at", "updated_at"])

        if item.batch is not None and item.qty_change < 0:
            # Inbound creates already wrote qty_received/qty_remaining.
            _apply_batch_delta(item.batch, item.qty_change)

    logger.info(
        "inventory.ledger.posted",
        extra={
            "ref_type": ref_type,
            "ref_id": str(ref_id),
            "branch_id": branch_id,
            "count": len(created),
        },
    )
    return created


__all__ = ["MovementItem", "post"]
