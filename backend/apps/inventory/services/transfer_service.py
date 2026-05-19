"""M05 Inventory — branch transfer service (step 5).

Two-step transfer flow:

* :func:`dispatch` — DRAFT → IN_TRANSIT. Posts a negative ledger line at
  the source branch and bumps ``Stock.qty_in_transit`` at the destination
  so reporting can see goods on the road.
* :func:`receive`  — IN_TRANSIT → RECEIVED. Posts a positive ledger line
  at the destination using ``qty_received`` per item (any shortfall lands
  on ``qty_lost``) and clears ``qty_in_transit``.
* :func:`cancel`   — DRAFT → CANCELLED. Only valid before dispatch.

All three are ``@transaction.atomic``; the negative-stock guard at the
ledger boundary blocks dispatches that would overdraw the source.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from ..exceptions import InvalidTransferState
from ..models import (
    BranchTransfer,
    BranchTransferItem,
    BranchTransferStatus,
    InventoryRefType,
    Stock,
)
from . import ledger_service


def _to_decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def _build_ledger_items(
    items: list[BranchTransferItem],
    *,
    qty_attr: str,
    sign: int,
) -> list[dict[str, Any]]:
    payload: list[dict[str, Any]] = []
    for it in items:
        qty = _to_decimal(getattr(it, qty_attr))
        if qty == 0:
            continue
        line: dict[str, Any] = {"qty_change": sign * qty}
        if it.product_id is not None:
            line["product_id"] = it.product_id
        else:
            line["variant_id"] = it.variant_id
        if it.batch_id is not None:
            line["batch"] = it.batch
        payload.append(line)
    return payload


def _adjust_in_transit(
    items: list[BranchTransferItem],
    *,
    to_branch_id: int,
    sign: int,
) -> None:
    """Bump (sign=+1) or clear (sign=-1) ``Stock.qty_in_transit`` rows on
    the destination side, one per (item, branch). Uses
    ``select_for_update`` for parity with ledger_service.
    """

    for it in items:
        qty = _to_decimal(it.qty_sent)
        if qty == 0:
            continue
        qs = Stock.all_objects.select_for_update().filter(
            branch_id=to_branch_id,
            product_id=it.product_id,
            variant_id=it.variant_id,
            warehouse_id=None,
        )
        row = qs.first()
        if row is None:
            row = Stock.objects.create(
                product_id=it.product_id,
                variant_id=it.variant_id,
                branch_id=to_branch_id,
            )
        new_val = _to_decimal(row.qty_in_transit) + (sign * qty)
        if new_val < 0:
            new_val = Decimal("0")
        row.qty_in_transit = new_val
        row.save(update_fields=["qty_in_transit", "updated_at"])


@transaction.atomic
def dispatch(transfer: BranchTransfer, *, actor=None) -> BranchTransfer:
    """Lock the transfer, post outbound ledger at source, mark IN_TRANSIT."""

    locked = BranchTransfer.all_objects.select_for_update().get(pk=transfer.pk)
    if locked.status != BranchTransferStatus.DRAFT:
        raise InvalidTransferState()

    items = list(locked.items.all())
    ledger_items = _build_ledger_items(items, qty_attr="qty_sent", sign=-1)
    if ledger_items:
        ledger_service.post(
            ref_type=InventoryRefType.TRANSFER,
            ref_id=locked.pk,
            items=ledger_items,
            branch=locked.from_branch_id,
            actor=actor,
            remarks=f"Transfer {locked.tr_no} dispatched",
        )
    _adjust_in_transit(items, to_branch_id=locked.to_branch_id, sign=+1)

    locked.status = BranchTransferStatus.IN_TRANSIT
    locked.dispatched_at = timezone.now()
    locked.save(update_fields=["status", "dispatched_at", "updated_at"])
    return locked


@transaction.atomic
def receive(transfer: BranchTransfer, *, actor=None) -> BranchTransfer:
    """Lock the transfer, post inbound ledger at destination, mark RECEIVED.

    ``qty_received`` per item drives the positive ledger line; any
    ``qty_sent - qty_received`` is recorded as ``qty_lost`` on the item.
    ``Stock.qty_in_transit`` at the destination is cleared by ``qty_sent``.
    """

    locked = BranchTransfer.all_objects.select_for_update().get(pk=transfer.pk)
    if locked.status != BranchTransferStatus.IN_TRANSIT:
        raise InvalidTransferState()

    items = list(locked.items.all())

    # Reconcile qty_lost = qty_sent - qty_received.
    for it in items:
        sent = _to_decimal(it.qty_sent)
        received = _to_decimal(it.qty_received)
        lost = sent - received
        if lost < 0:
            lost = Decimal("0")
        it.qty_lost = lost
        it.save(update_fields=["qty_lost", "updated_at"])

    ledger_items = _build_ledger_items(items, qty_attr="qty_received", sign=+1)
    if ledger_items:
        ledger_service.post(
            ref_type=InventoryRefType.TRANSFER,
            ref_id=locked.pk,
            items=ledger_items,
            branch=locked.to_branch_id,
            actor=actor,
            remarks=f"Transfer {locked.tr_no} received",
        )
    _adjust_in_transit(items, to_branch_id=locked.to_branch_id, sign=-1)

    locked.status = BranchTransferStatus.RECEIVED
    locked.received_at = timezone.now()
    locked.save(update_fields=["status", "received_at", "updated_at"])
    return locked


@transaction.atomic
def cancel(transfer: BranchTransfer, *, actor=None) -> BranchTransfer:
    """Cancel a DRAFT transfer. Any other state is invalid."""

    locked = BranchTransfer.all_objects.select_for_update().get(pk=transfer.pk)
    if locked.status != BranchTransferStatus.DRAFT:
        raise InvalidTransferState()
    locked.status = BranchTransferStatus.CANCELLED
    locked.save(update_fields=["status", "updated_at"])
    return locked


__all__ = ["dispatch", "receive", "cancel"]
