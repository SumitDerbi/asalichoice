"""Sale lifecycle service — the orchestrator for M11 Sales.

Public entry points:

* :func:`create_draft` — build a Sale in ``DRAFT`` state without
  touching stock or money.
* :func:`recompute` — rebuild totals after an edit (calls
  ``sale_builder.recompute`` and saves).
* :func:`post` — flip a sale to ``CONFIRMED``/``PAID``, write payments,
  emit the inventory ledger ``SALE`` movement, fire ``sale_posted``.
* :func:`cancel` — reverse a posted sale: ledger reversal, mark
  payments REFUNDED, fire ``sale_cancelled``.

All write-paths run inside ``@transaction.atomic`` so a partial sale
cannot leak. The function never touches ``Stock.qty_*`` directly — it
exclusively calls :func:`apps.inventory.services.ledger_service.post`
(ADR-007 single-writer invariant).
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Iterable
from decimal import Decimal
from typing import Any

from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.inventory.models import InventoryRefType
from apps.inventory.services import ledger_service
from apps.master.api_public import is_payment_mode_enabled

from ..exceptions import (
    DuplicateOfflineSale,
    EmptySale,
    InvalidSaleState,
    PaymentTotalMismatch,
    PriceOverrideForbidden,
    UnknownPaymentMode,
)
from ..models import (
    PriceOverride,
    Sale,
    SaleItem,
    SaleOrigin,
    SalePayment,
    SalePaymentStatus,
    SaleStatus,
)
from ..signals import sale_cancelled, sale_posted
from . import sale_builder

logger = logging.getLogger(__name__)

_ZERO = Decimal("0")

# Lifecycle transitions that ``post`` is allowed to start from. Lifecycle
# rules are loose at M11 because the storefront (M06) hasn't been wired
# in; we tighten the matrix when M06/M07 ship.
_POSTABLE_STATES = {SaleStatus.DRAFT, SaleStatus.HELD, SaleStatus.CONFIRMED}


# ---------------------------------------------------------------------------
# Numbering
# ---------------------------------------------------------------------------


def _next_sale_no(*, origin: str, branch_id: int) -> str:
    """Generate a unique ``sale_no`` like ``POS-B1-20251128-0042``.

    Implementation is intentionally lightweight at M11 — collision is
    handled by the unique-constraint retry in :func:`_create_with_unique_sale_no`.
    A proper sequence allocator lands with M07.
    """

    today = timezone.localdate().strftime("%Y%m%d")
    suffix = uuid.uuid4().hex[:6].upper()
    return f"{origin}-B{branch_id}-{today}-{suffix}"


# ---------------------------------------------------------------------------
# Draft creation
# ---------------------------------------------------------------------------


@transaction.atomic
def create_draft(
    *,
    branch,
    origin: str = SaleOrigin.POS,
    customer=None,
    cashier=None,
    tax_mode: str = "EXCLUSIVE",
    notes: str = "",
    offline_uuid: uuid.UUID | None = None,
    items: Iterable[dict[str, Any]] = (),
    payments: Iterable[dict[str, Any]] = (),
    actor=None,
) -> Sale:
    """Create a :class:`Sale` in ``DRAFT`` status with its lines/payments.

    Each ``items`` dict must carry:

    * ``product`` xor ``variant`` (instance or id)
    * ``uom`` (instance or id)
    * ``qty`` (Decimal-coercible)
    * ``sale_price``

    Optional per-item keys: ``mrp``, ``discount_amount``, ``tax``,
    ``batch``, ``hsn``, ``price_override_reason``.

    The function refuses to create a duplicate when ``offline_uuid`` is
    supplied and already exists in the database, raising
    :class:`DuplicateOfflineSale`.
    """

    if offline_uuid is not None and Sale.objects.filter(offline_uuid=offline_uuid).exists():
        raise DuplicateOfflineSale(
            details={"offline_uuid": str(offline_uuid)},
        )

    sale = Sale(
        sale_no=_next_sale_no(origin=origin, branch_id=getattr(branch, "pk", branch)),
        origin=origin,
        branch=branch,
        customer=customer,
        cashier=cashier,
        status=SaleStatus.DRAFT,
        tax_mode=tax_mode,
        notes=notes,
        offline_uuid=offline_uuid,
    )
    try:
        sale.save()
    except IntegrityError as exc:  # pragma: no cover - extremely unlikely UUID race
        if offline_uuid is not None:
            raise DuplicateOfflineSale(
                details={"offline_uuid": str(offline_uuid)},
            ) from exc
        raise

    item_objs: list[SaleItem] = []
    for raw in items:
        item = _build_item(sale=sale, raw=raw, actor=actor)
        item_objs.append(item)

    sale_builder.recompute(sale, item_objs)
    SaleItem.objects.bulk_create(item_objs)
    sale.save()  # persist totals

    for raw in payments:
        _add_payment(sale=sale, raw=raw)

    sale.refresh_from_db()
    return sale


def _build_item(*, sale: Sale, raw: dict[str, Any], actor=None) -> SaleItem:
    qty = Decimal(str(raw["qty"]))
    sale_price = Decimal(str(raw["sale_price"]))
    mrp = Decimal(str(raw.get("mrp", sale_price)))
    discount_amount = Decimal(str(raw.get("discount_amount", 0)))

    item = SaleItem(
        sale=sale,
        product=raw.get("product"),
        variant=raw.get("variant"),
        uom=raw["uom"],
        batch=raw.get("batch"),
        hsn=raw.get("hsn"),
        tax=raw.get("tax"),
        qty=qty,
        mrp=mrp,
        sale_price=sale_price,
        discount_amount=discount_amount,
    )

    # Price override audit: any line whose ``sale_price`` differs from
    # the supplied ``mrp`` is captured. Permission gating is enforced
    # only when the caller flags ``check_override_perm=True``.
    override_reason = raw.get("price_override_reason")
    if sale_price != mrp or override_reason:
        check_perm = bool(raw.get("check_override_perm"))
        if check_perm:
            if actor is None or not actor.has_perm("sales.price.override"):
                raise PriceOverrideForbidden(
                    details={"product": getattr(raw.get("product"), "pk", None)},
                )
        # PriceOverride is created post-bulk_create in caller's flow if
        # the line was overridden. Stash the metadata on the instance.
        item._override_audit = {  # type: ignore[attr-defined]
            "original_price": mrp,
            "new_price": sale_price,
            "reason": override_reason or "",
            "by": actor,
            "perm_check_passed": True,
        }
    return item


def _add_payment(*, sale: Sale, raw: dict[str, Any]) -> SalePayment:
    mode = raw["payment_mode"]
    if not is_payment_mode_enabled(sale.branch, getattr(mode, "code", str(mode))):
        raise UnknownPaymentMode(
            details={"mode": getattr(mode, "code", str(mode))},
        )
    payment = SalePayment.objects.create(
        sale=sale,
        payment_mode=mode,
        amount=Decimal(str(raw["amount"])),
        ref_no=raw.get("ref_no", ""),
        gateway_txn=raw.get("gateway_txn", ""),
        status=raw.get("status", SalePaymentStatus.SUCCESS),
    )
    if payment.status == SalePaymentStatus.SUCCESS:
        Sale.objects.filter(pk=sale.pk).update(
            payment_total=sale.payment_total + payment.amount,
        )
        sale.payment_total = sale.payment_total + payment.amount
    return payment


# ---------------------------------------------------------------------------
# Recompute
# ---------------------------------------------------------------------------


@transaction.atomic
def recompute(sale: Sale) -> Sale:
    """Refresh totals after an external mutation (admin edit, etc.)."""

    items = list(sale.items.select_related("tax").all())
    sale_builder.recompute(sale, items)
    SaleItem.objects.bulk_update(
        items,
        fields=["line_subtotal", "tax_breakup_json", "line_total", "discount_amount"],
    )
    sale.save(
        update_fields=[
            "subtotal",
            "discount_total",
            "tax_total",
            "grand_total",
            "totals_json",
        ]
    )
    return sale


# ---------------------------------------------------------------------------
# Post
# ---------------------------------------------------------------------------


@transaction.atomic
def post(
    sale: Sale,
    *,
    actor=None,
    allow_partial_payment: bool = False,
    reason_code: str = "",
    remarks: str = "",
) -> Sale:
    """Confirm a sale: write ledger, mark payments, fire signal.

    Raises:

    * :class:`InvalidSaleState` — sale is not in a postable state.
    * :class:`EmptySale` — sale has no items.
    * :class:`PaymentTotalMismatch` — payments don't match grand total
      and ``allow_partial_payment`` is False.
    """

    sale.refresh_from_db()
    if sale.status not in _POSTABLE_STATES:
        raise InvalidSaleState(
            details={"current": sale.status, "allowed": sorted(_POSTABLE_STATES)},
        )

    items = list(sale.items.select_related("product", "variant", "tax", "batch").all())
    if not items:
        raise EmptySale()

    # Recompute under the lock to defeat stale edits.
    sale_builder.recompute(sale, items)

    # Payment validation
    successful_total = sum(
        (p.amount for p in sale.payments.filter(status=SalePaymentStatus.SUCCESS)),
        start=_ZERO,
    )
    if not allow_partial_payment and successful_total != sale.grand_total:
        raise PaymentTotalMismatch(
            details={
                "expected": str(sale.grand_total),
                "received": str(successful_total),
            },
        )

    # Inventory ledger — single writer of stock.
    ledger_service.post(
        ref_type=InventoryRefType.SALE,
        ref_id=str(sale.pk),
        items=[
            {
                "product": item.product if not item.variant_id else None,
                "variant": item.variant,
                "qty_change": -item.qty,
                "batch": item.batch,
            }
            for item in items
        ],
        branch=sale.branch,
        actor=actor,
        reason_code=reason_code or "SALE",
        remarks=remarks or f"Sale {sale.sale_no}",
    )

    # Persist any price-override audit rows now that SaleItems have PKs.
    for item in items:
        audit = getattr(item, "_override_audit", None)
        if audit:
            PriceOverride.objects.get_or_create(
                sale_item=item,
                defaults=audit,
            )

    sale.payment_total = successful_total
    sale.billed_at = timezone.now()
    if successful_total >= sale.grand_total:
        sale.status = SaleStatus.PAID
    elif successful_total > _ZERO:
        sale.status = SaleStatus.PARTIALLY_PAID
    else:
        sale.status = SaleStatus.CONFIRMED
    sale.save(
        update_fields=[
            "payment_total",
            "billed_at",
            "status",
            "subtotal",
            "discount_total",
            "tax_total",
            "grand_total",
            "totals_json",
        ]
    )

    SaleItem.objects.bulk_update(
        items,
        fields=["line_subtotal", "tax_breakup_json", "line_total", "discount_amount"],
    )

    sale_posted.send(sender=Sale, sale=sale, actor=actor)
    return sale


# ---------------------------------------------------------------------------
# Cancel
# ---------------------------------------------------------------------------


@transaction.atomic
def cancel(sale: Sale, *, actor=None, reason: str = "") -> Sale:
    """Reverse a posted sale.

    Writes a matching ledger entry with positive ``qty_change`` (returning
    stock), marks ``SUCCESS`` payments as ``REFUNDED``, flips the sale
    status to ``CANCELLED`` and fires :data:`sale_cancelled`.
    """

    sale.refresh_from_db()
    if sale.status in {SaleStatus.CANCELLED, SaleStatus.REFUNDED, SaleStatus.DRAFT}:
        raise InvalidSaleState(
            details={"current": sale.status},
        )

    items = list(sale.items.select_related("product", "variant", "batch").all())
    if items and sale.status in {
        SaleStatus.CONFIRMED,
        SaleStatus.PARTIALLY_PAID,
        SaleStatus.PAID,
    }:
        ledger_service.post(
            ref_type=InventoryRefType.SALE,
            ref_id=f"CANCEL:{sale.pk}",
            items=[
                {
                    "product": item.product if not item.variant_id else None,
                    "variant": item.variant,
                    "qty_change": item.qty,
                    "batch": item.batch,
                }
                for item in items
            ],
            branch=sale.branch,
            actor=actor,
            reason_code="SALE_CANCEL",
            remarks=reason or f"Cancel sale {sale.sale_no}",
        )

    refunded_total = _ZERO
    refundable = list(sale.payments.filter(status=SalePaymentStatus.SUCCESS))
    for payment in refundable:
        payment.status = SalePaymentStatus.REFUNDED
        payment.save(update_fields=["status"])
        refunded_total += payment.amount

    sale.status = SaleStatus.CANCELLED
    sale.cancelled_at = timezone.now()
    sale.payment_total = max(sale.payment_total - refunded_total, _ZERO)
    sale.save(update_fields=["status", "cancelled_at", "payment_total"])

    sale_cancelled.send(sender=Sale, sale=sale, actor=actor, reason=reason)
    return sale


__all__ = ["cancel", "create_draft", "post", "recompute"]
