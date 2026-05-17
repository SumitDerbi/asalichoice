"""Purchase Invoice service.

A PI aggregates one or more **approved** GRNs from a single vendor.
Posting the invoice writes a vendor-ledger row that brings the
``balance_after`` to the running outstanding for that vendor.
"""

from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.utils import timezone

from ..exceptions import PIDuplicate, PINoApprovedGRNs
from ..models import GRN, GRNStatus, PIStatus, PurchaseInvoice, VendorLedger
from .grn_service import _grn_cost_value, _vendor_balance


def _aggregate_totals(grns: Iterable[GRN]) -> dict:
    grand = Decimal("0")
    for grn in grns:
        grand += _grn_cost_value(grn)
    return {"grand_total": str(grand)}


@transaction.atomic
def create_invoice_from_grns(
    *,
    vendor,
    branch,
    pi_no: str,
    grn_ids: Iterable[int],
    invoice_no_vendor: str = "",
    invoice_date=None,
    due_date=None,
    payment_terms: str = "",
) -> PurchaseInvoice:
    grns = list(
        GRN.objects.filter(pk__in=list(grn_ids), vendor_id=vendor.pk, status=GRNStatus.APPROVED)
    )
    if not grns:
        raise PINoApprovedGRNs()
    try:
        pi = PurchaseInvoice.objects.create(
            pi_no=pi_no,
            vendor=vendor,
            branch=branch,
            invoice_no_vendor=invoice_no_vendor,
            invoice_date=invoice_date,
            due_date=due_date,
            payment_terms=payment_terms,
            status=PIStatus.DRAFT,
            totals_json=_aggregate_totals(grns),
        )
    except IntegrityError as exc:
        raise PIDuplicate() from exc
    pi.grns.add(*grns)
    return pi


@transaction.atomic
def post_invoice(pi: PurchaseInvoice) -> PurchaseInvoice:
    if pi.status != PIStatus.DRAFT:
        return pi
    pi.status = PIStatus.POSTED
    pi.invoice_date = pi.invoice_date or timezone.now().date()
    pi.save(update_fields=["status", "invoice_date", "updated_at"])
    # Vendor ledger: posting the invoice does not double-count because
    # GRN approve already credited the goods. The PI row here is an
    # informational ledger marker — net zero — so the ledger trail
    # carries the PI reference.
    VendorLedger.objects.create(
        vendor_id=pi.vendor_id,
        branch_id=pi.branch_id,
        amount=Decimal("0"),
        balance_before=_vendor_balance(pi.vendor_id, pi.branch_id),
        balance_after=_vendor_balance(pi.vendor_id, pi.branch_id),
        reference_type="purchase.PurchaseInvoice",
        reference_id=str(pi.pk),
        remarks=f"PI {pi.pi_no} posted",
    )
    return pi


@transaction.atomic
def record_payment(pi: PurchaseInvoice, *, amount: Decimal, remarks: str = "") -> PurchaseInvoice:
    if amount <= 0:
        return pi
    before = _vendor_balance(pi.vendor_id, pi.branch_id)
    VendorLedger.objects.create(
        vendor_id=pi.vendor_id,
        branch_id=pi.branch_id,
        amount=-amount,
        balance_before=before,
        balance_after=before - amount,
        reference_type="purchase.Payment",
        reference_id=str(pi.pk),
        remarks=remarks[:255] or f"Payment against PI {pi.pi_no}",
    )
    grand = Decimal(str((pi.totals_json or {}).get("grand_total", "0")))
    new_balance = _vendor_balance(pi.vendor_id, pi.branch_id)
    pi.status = PIStatus.PAID if new_balance <= 0 or amount >= grand else PIStatus.PART_PAID
    pi.save(update_fields=["status", "updated_at"])
    return pi


__all__ = [
    "create_invoice_from_grns",
    "post_invoice",
    "record_payment",
]
