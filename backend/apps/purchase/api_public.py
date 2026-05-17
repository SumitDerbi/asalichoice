"""Public seam for ``apps.purchase``.

Other modules must import vendor / PO / GRN primitives from here, never
from :mod:`apps.purchase.models` or :mod:`apps.purchase.services`
directly (ADR-002).
"""

from __future__ import annotations

from decimal import Decimal

from .models import GRN, GRNStatus, POStatus, PurchaseOrder, Vendor, VendorLedger

__all__ = [
    "GRNStatus",
    "POStatus",
    "get_approved_grns_for_invoice",
    "get_po_status",
    "get_vendor_outstanding",
]


def get_vendor_outstanding(vendor: Vendor | int, branch_id: int | None = None) -> Decimal:
    """Return the latest ``balance_after`` for *vendor*."""

    vendor_id = vendor.pk if isinstance(vendor, Vendor) else int(vendor)
    qs = VendorLedger.objects.filter(vendor_id=vendor_id)
    if branch_id is not None:
        qs = qs.filter(branch_id=branch_id)
    last = qs.order_by("-timestamp", "-id").first()
    return Decimal(last.balance_after) if last else Decimal("0")


def get_po_status(po_id: int) -> str | None:
    row = PurchaseOrder.objects.filter(pk=po_id).only("status").first()
    return row.status if row else None


def get_approved_grns_for_invoice(vendor: Vendor | int, branch_id: int | None = None):
    """Return approved GRNs for *vendor* not yet attached to any PI."""

    vendor_id = vendor.pk if isinstance(vendor, Vendor) else int(vendor)
    qs = GRN.objects.filter(vendor_id=vendor_id, status=GRNStatus.APPROVED, invoices__isnull=True)
    if branch_id is not None:
        qs = qs.filter(branch_id=branch_id)
    return qs.distinct()
