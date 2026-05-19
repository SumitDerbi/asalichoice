"""GRN service — the **only** place that writes inventory.

Stock policy (ADR-007): a PO never writes stock. When a GRN is approved
we (a) emit a `VendorLedger` credit for the cost value, (b) write the
inventory movement (M05 stub today, real :class:`InventoryLedger` rows
in M05), and (c) transition the source PO to PARTIAL / RECEIVED.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable
from decimal import Decimal
from typing import Any

from django.db import IntegrityError, transaction
from django.utils import timezone

from ..exceptions import (
    GRNDuplicate,
    GRNInvalidTransition,
    GRNNegativeQty,
    GRNOverReceive,
    OfflineGRNPOClosed,
    OfflineUUIDConflict,
)
from ..models import GRN, GRNItem, GRNStatus, POStatus, PurchaseOrder, VendorLedger
from .po_service import mark_received
from .vendor_service import ensure_active

logger = logging.getLogger(__name__)


def _grn_cost_value(grn: GRN) -> Decimal:
    total = Decimal("0")
    for item in grn.items.all():
        total += Decimal(str(item.cost_price or 0)) * Decimal(str(item.qty_accepted or 0))
    return total


def _vendor_balance(vendor_id: int, branch_id: int | None) -> Decimal:
    last = (
        VendorLedger.objects.filter(vendor_id=vendor_id, branch_id=branch_id)
        .order_by("-timestamp", "-id")
        .first()
    )
    return Decimal(last.balance_after) if last else Decimal("0")


def _write_vendor_ledger(
    *,
    vendor_id: int,
    branch_id: int | None,
    amount: Decimal,
    reference_type: str,
    reference_id: str,
    remarks: str = "",
) -> VendorLedger:
    before = _vendor_balance(vendor_id, branch_id)
    return VendorLedger.objects.create(
        vendor_id=vendor_id,
        branch_id=branch_id,
        amount=amount,
        balance_before=before,
        balance_after=before + amount,
        reference_type=reference_type,
        reference_id=str(reference_id),
        remarks=remarks[:255],
    )


def _write_inventory_movement(grn: GRN) -> None:
    """Post inventory rows for an approved GRN via the M05 ledger service.

    Each ``GRNItem`` becomes one positive ledger line. When the line
    carries a batch number we upsert a :class:`apps.inventory.models.Batch`
    via the service's ``batch_kwargs`` plumbing so subsequent outbound
    movements can drain it FIFO.
    """

    from apps.inventory.models import InventoryRefType
    from apps.inventory.services import ledger_service

    items: list[dict[str, Any]] = []
    for grn_item in grn.items.all():
        qty_accepted = Decimal(str(grn_item.qty_accepted or 0))
        if qty_accepted <= 0:
            continue
        payload: dict[str, Any] = {
            "product_id": grn_item.product_id,
            "variant_id": grn_item.variant_id,
            "qty_change": qty_accepted,
            "cost_price": grn_item.cost_price,
        }
        if grn_item.batch_no:
            payload["batch_kwargs"] = {
                "batch_no": grn_item.batch_no,
                "mfg_date": grn_item.mfg_date,
                "expiry_date": grn_item.expiry_date,
                "cost_price": grn_item.cost_price,
            }
        items.append(payload)

    if not items:
        return

    ledger_service.post(
        ref_type=InventoryRefType.GRN,
        ref_id=grn.pk,
        items=items,
        branch=grn.branch,
        remarks=f"GRN {grn.grn_no} approved",
    )


def _check_qty_nonneg(items: Iterable[dict[str, Any]]) -> None:
    for item in items:
        for key in ("qty_received", "qty_accepted", "qty_rejected"):
            val = item.get(key)
            if val is None:
                continue
            if Decimal(str(val)) < 0:
                raise GRNNegativeQty()


def _check_over_receive(po: PurchaseOrder | None, items: Iterable[dict[str, Any]]) -> None:
    if po is None:
        return
    by_po_item: dict[int, Decimal] = {}
    for item in items:
        po_item = item.get("po_item")
        if po_item is None:
            continue
        po_item_id = po_item.pk if hasattr(po_item, "pk") else int(po_item)
        by_po_item.setdefault(po_item_id, Decimal("0"))
        by_po_item[po_item_id] += Decimal(str(item.get("qty_received", "0")))
    for po_item_id, total in by_po_item.items():
        try:
            ordered = po.items.get(pk=po_item_id).qty
        except po.items.model.DoesNotExist:
            continue
        already = Decimal("0")
        for prev in GRNItem.objects.filter(
            po_item_id=po_item_id, grn__status=GRNStatus.APPROVED
        ).values_list("qty_received", flat=True):
            already += Decimal(str(prev))
        if already + total > Decimal(str(ordered)):
            raise GRNOverReceive()


@transaction.atomic
def create_grn(
    *,
    vendor,
    branch,
    grn_no: str,
    items: Iterable[dict[str, Any]],
    po: PurchaseOrder | None = None,
    offline_uuid=None,
    **fields,
) -> GRN:
    ensure_active(vendor)
    items_list = [dict(item) for item in items]
    _check_qty_nonneg(items_list)
    _check_over_receive(po, items_list)
    try:
        grn = GRN.objects.create(
            grn_no=grn_no,
            po=po,
            vendor=vendor,
            branch=branch,
            status=GRNStatus.DRAFT,
            offline_uuid=offline_uuid,
            **fields,
        )
    except IntegrityError as exc:
        msg = str(exc).lower()
        if "offline_uuid" in msg:
            raise OfflineUUIDConflict() from exc
        raise GRNDuplicate() from exc

    for item in items_list:
        payload = dict(item)
        qty_received = Decimal(str(payload.get("qty_received", "0")))
        payload.setdefault(
            "qty_accepted", qty_received - Decimal(str(payload.get("qty_rejected", "0")))
        )
        GRNItem.objects.create(grn=grn, **payload)
    return grn


@transaction.atomic
def submit_grn(grn: GRN) -> GRN:
    if grn.status != GRNStatus.DRAFT:
        raise GRNInvalidTransition()
    grn.status = GRNStatus.SUBMITTED
    grn.save(update_fields=["status", "updated_at"])
    return grn


@transaction.atomic
def approve_grn(grn: GRN, *, actor=None) -> GRN:
    if grn.status not in (GRNStatus.DRAFT, GRNStatus.SUBMITTED):
        raise GRNInvalidTransition()
    grn.status = GRNStatus.APPROVED
    grn.received_at = grn.received_at or timezone.now()
    grn.save(update_fields=["status", "received_at", "updated_at"])

    # 1) Inventory: M05 stub (single seam to replace later).
    _write_inventory_movement(grn)

    # 2) Vendor ledger credit for the goods received.
    cost_value = _grn_cost_value(grn)
    if cost_value > 0:
        _write_vendor_ledger(
            vendor_id=grn.vendor_id,
            branch_id=grn.branch_id,
            amount=cost_value,
            reference_type="purchase.GRN",
            reference_id=str(grn.pk),
            remarks=f"GRN {grn.grn_no} approved",
        )

    # 3) Roll up PO status.
    if grn.po_id:
        po = PurchaseOrder.objects.select_for_update().get(pk=grn.po_id)
        ordered_total = sum(
            (Decimal(str(it.qty)) for it in po.items.all()),
            Decimal("0"),
        )
        received_total = Decimal("0")
        for entry in GRNItem.objects.filter(
            grn__po_id=po.pk, grn__status=GRNStatus.APPROVED
        ).values_list("qty_received", flat=True):
            received_total += Decimal(str(entry))
        mark_received(po, partial=received_total < ordered_total)
    return grn


@transaction.atomic
def reject_grn(grn: GRN, *, reason: str = "") -> GRN:
    if grn.status not in (GRNStatus.DRAFT, GRNStatus.SUBMITTED):
        raise GRNInvalidTransition()
    grn.status = GRNStatus.REJECTED
    if reason:
        grn.totals_json = {**(grn.totals_json or {}), "rejection_reason": reason}
    grn.save(update_fields=["status", "totals_json", "updated_at"])
    return grn


@transaction.atomic
def sync_offline_grn(
    *,
    offline_uuid,
    vendor,
    branch,
    grn_no: str,
    items: Iterable[dict[str, Any]],
    po: PurchaseOrder | None = None,
    **fields,
) -> GRN:
    """Idempotent offline-GRN sync entry point.

    If a row already exists for ``offline_uuid`` we return it unchanged
    (the client may safely retry). If the source PO is already closed
    we reject with :class:`OfflineGRNPOClosed`.
    """

    existing = GRN.objects.filter(offline_uuid=offline_uuid).first()
    if existing is not None:
        return existing
    if po is not None and po.status in (POStatus.CLOSED, POStatus.CANCELLED):
        raise OfflineGRNPOClosed()
    return create_grn(
        vendor=vendor,
        branch=branch,
        grn_no=grn_no,
        items=items,
        po=po,
        offline_uuid=offline_uuid,
        **fields,
    )


__all__ = [
    "approve_grn",
    "create_grn",
    "reject_grn",
    "submit_grn",
    "sync_offline_grn",
]
