"""Purchase Order service — create / submit / approve / cancel.

State machine::

    DRAFT ──submit──► PENDING_APPROVAL ──approve──► APPROVED
                                                       │
                                                       ▼
                                       (GRN approvals) PARTIAL / RECEIVED
                                                       │
                                                       ▼
                                                     CLOSED

``CANCELLED`` is reachable from DRAFT, PENDING_APPROVAL, or APPROVED
(when no GRN has been received).
"""

from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal
from typing import Any

from django.db import IntegrityError, transaction
from django.utils import timezone

from ..exceptions import POAlreadyApproved, POClosedForChanges, PODuplicate, POInvalidTransition
from ..models import POItem, POStatus, PurchaseOrder
from .approval_service import required_approvers
from .vendor_service import ensure_active


def _compute_line_total(item: dict[str, Any]) -> Decimal:
    qty = Decimal(str(item.get("qty", "0")))
    rate = Decimal(str(item.get("rate", "0")))
    discount = Decimal(str(item.get("discount", "0")))
    return (qty * rate) - discount


@transaction.atomic
def create_po(
    *, vendor, branch, po_no: str, items: Iterable[dict[str, Any]], **fields
) -> PurchaseOrder:
    ensure_active(vendor)
    try:
        po = PurchaseOrder.objects.create(
            po_no=po_no,
            vendor=vendor,
            branch=branch,
            status=POStatus.DRAFT,
            **fields,
        )
    except IntegrityError as exc:
        raise PODuplicate() from exc

    grand_total = Decimal("0")
    for item in items:
        payload = dict(item)
        payload.setdefault("line_total", _compute_line_total(payload))
        po_item = POItem.objects.create(po=po, **payload)
        grand_total += po_item.line_total
    po.totals_json = {"grand_total": str(grand_total)}
    po.save(update_fields=["totals_json", "updated_at"])
    return po


@transaction.atomic
def submit_po(po: PurchaseOrder) -> PurchaseOrder:
    if po.status != POStatus.DRAFT:
        raise POInvalidTransition()
    po.approval_chain_json = required_approvers(po, branch_id=po.branch_id)
    po.status = POStatus.PENDING_APPROVAL
    po.save(update_fields=["status", "approval_chain_json", "updated_at"])
    return po


@transaction.atomic
def approve_po(po: PurchaseOrder, *, actor=None) -> PurchaseOrder:
    if po.status == POStatus.APPROVED:
        raise POAlreadyApproved()
    if po.status not in (POStatus.DRAFT, POStatus.PENDING_APPROVAL):
        raise POInvalidTransition()
    po.status = POStatus.APPROVED
    po.approved_by = actor
    po.approved_at = timezone.now()
    po.save(update_fields=["status", "approved_by", "approved_at", "updated_at"])
    return po


@transaction.atomic
def cancel_po(po: PurchaseOrder) -> PurchaseOrder:
    if po.status in (POStatus.RECEIVED, POStatus.CLOSED):
        raise POClosedForChanges()
    if po.grns.filter(status__in=("APPROVED",)).exists():
        raise POClosedForChanges()
    po.status = POStatus.CANCELLED
    po.save(update_fields=["status", "updated_at"])
    return po


@transaction.atomic
def mark_received(po: PurchaseOrder, *, partial: bool = False) -> PurchaseOrder:
    """Internal: called by the GRN service after a successful approval."""

    po.status = POStatus.PARTIAL if partial else POStatus.RECEIVED
    po.save(update_fields=["status", "updated_at"])
    return po


__all__ = [
    "approve_po",
    "cancel_po",
    "create_po",
    "mark_received",
    "submit_po",
]
