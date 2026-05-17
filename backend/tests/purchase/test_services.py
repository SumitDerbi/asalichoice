"""M04 purchase service-layer tests."""

from __future__ import annotations

from decimal import Decimal

import pytest

from apps.purchase.exceptions import (
    GRNNegativeQty,
    GRNOverReceive,
    OfflineGRNPOClosed,
    PINoApprovedGRNs,
    POAlreadyApproved,
    POClosedForChanges,
    ReturnQtyExceedsReceipt,
    VendorCodeDuplicate,
    VendorGSTINInvalid,
    VendorInactive,
)
from apps.purchase.models import PIStatus, POStatus, PRStatus, VendorLedger
from apps.purchase.services import (
    approve_grn,
    approve_po,
    cancel_po,
    create_grn,
    create_invoice_from_grns,
    create_po,
    create_return,
    create_vendor,
    deactivate_vendor,
    post_invoice,
    post_return,
    record_payment,
    required_approvers,
    submit_po,
    sync_offline_grn,
)

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# Vendor
# ---------------------------------------------------------------------------


def test_create_vendor_valid_gstin():
    v = create_vendor(code="V-GST", name="GST OK", gstin="29ABCDE1234F1Z5")
    assert v.pk is not None


def test_create_vendor_invalid_gstin():
    with pytest.raises(VendorGSTINInvalid):
        create_vendor(code="V-BAD", name="Bad GST", gstin="not-a-gstin")


def test_create_vendor_duplicate_code(vendor):
    with pytest.raises(VendorCodeDuplicate):
        create_vendor(code=vendor.code, name="dup")


def test_deactivate_blocks_po_creation(vendor, branch, product, uom):
    deactivate_vendor(vendor)
    with pytest.raises(VendorInactive):
        create_po(
            vendor=vendor,
            branch=branch,
            po_no="PO-INACTIVE",
            items=[{"product": product, "uom": uom, "qty": Decimal("1"), "rate": Decimal("1")}],
        )


# ---------------------------------------------------------------------------
# PO state machine
# ---------------------------------------------------------------------------


def test_po_full_happy_path(po_factory):
    po = po_factory()
    assert po.status == POStatus.DRAFT
    assert Decimal(po.totals_json["grand_total"]) == Decimal("1000.0000")

    submit_po(po)
    po.refresh_from_db()
    assert po.status == POStatus.PENDING_APPROVAL

    approve_po(po)
    po.refresh_from_db()
    assert po.status == POStatus.APPROVED


def test_po_double_approve_raises(po_factory):
    po = po_factory()
    submit_po(po)
    approve_po(po)
    with pytest.raises(POAlreadyApproved):
        approve_po(po)


def test_cancel_draft_po(po_factory):
    po = po_factory()
    cancel_po(po)
    po.refresh_from_db()
    assert po.status == POStatus.CANCELLED


def test_cancel_blocked_after_approved_grn(po_factory, product, uom):
    po = po_factory(qty=Decimal("5"), rate=Decimal("100"))
    submit_po(po)
    approve_po(po)
    grn = create_grn(
        vendor=po.vendor,
        branch=po.branch,
        grn_no="GRN-CB-1",
        po=po,
        items=[
            {
                "product": product,
                "qty_received": Decimal("5"),
                "qty_accepted": Decimal("5"),
                "cost_price": Decimal("90"),
                "po_item": po.items.first(),
            }
        ],
    )
    approve_grn(grn)
    with pytest.raises(POClosedForChanges):
        cancel_po(po)


# ---------------------------------------------------------------------------
# Approval routing
# ---------------------------------------------------------------------------


def _set_thresholds(tiers):
    from apps.system_settings.models import SettingScope, SiteSetting
    from apps.system_settings.services import invalidate_setting_cache

    SiteSetting.objects.update_or_create(
        key="purchase.po.approval_thresholds",
        scope=SettingScope.GLOBAL,
        branch_id=None,
        defaults={"value_json": tiers},
    )
    invalidate_setting_cache("purchase.po.approval_thresholds")


def test_required_approvers_below_lowest_tier(po_factory):
    _set_thresholds(
        [
            {"min_amount": "50000", "approver_role": "MANAGER"},
            {"min_amount": "200000", "approver_role": "DIRECTOR"},
        ]
    )
    po = po_factory(qty=Decimal("1"), rate=Decimal("100"))
    assert required_approvers(po) == []


def test_required_approvers_mid_tier(po_factory):
    _set_thresholds(
        [
            {"min_amount": "50000", "approver_role": "MANAGER"},
            {"min_amount": "200000", "approver_role": "DIRECTOR"},
        ]
    )
    po = po_factory(qty=Decimal("100"), rate=Decimal("600"))  # 60k
    assert required_approvers(po) == ["MANAGER"]


def test_required_approvers_top_tier(po_factory):
    _set_thresholds(
        [
            {"min_amount": "50000", "approver_role": "MANAGER"},
            {"min_amount": "200000", "approver_role": "DIRECTOR"},
        ]
    )
    po = po_factory(qty=Decimal("100"), rate=Decimal("2500"))  # 250k
    assert required_approvers(po) == ["MANAGER", "DIRECTOR"]


# ---------------------------------------------------------------------------
# GRN
# ---------------------------------------------------------------------------


def test_grn_create_rejects_negative_qty(po_factory, product):
    po = po_factory()
    submit_po(po)
    approve_po(po)
    with pytest.raises(GRNNegativeQty):
        create_grn(
            vendor=po.vendor,
            branch=po.branch,
            grn_no="GRN-NEG",
            po=po,
            items=[
                {
                    "product": product,
                    "qty_received": Decimal("-1"),
                    "po_item": po.items.first(),
                }
            ],
        )


def test_grn_over_receive_blocked(po_factory, product):
    po = po_factory(qty=Decimal("5"), rate=Decimal("100"))
    submit_po(po)
    approve_po(po)
    with pytest.raises(GRNOverReceive):
        create_grn(
            vendor=po.vendor,
            branch=po.branch,
            grn_no="GRN-OVER",
            po=po,
            items=[
                {
                    "product": product,
                    "qty_received": Decimal("99"),
                    "qty_accepted": Decimal("99"),
                    "cost_price": Decimal("90"),
                    "po_item": po.items.first(),
                }
            ],
        )


def test_grn_approve_writes_vendor_ledger(po_factory, product):
    po = po_factory(qty=Decimal("4"), rate=Decimal("100"))
    submit_po(po)
    approve_po(po)
    grn = create_grn(
        vendor=po.vendor,
        branch=po.branch,
        grn_no="GRN-LED-1",
        po=po,
        items=[
            {
                "product": product,
                "qty_received": Decimal("4"),
                "qty_accepted": Decimal("4"),
                "cost_price": Decimal("90"),
                "po_item": po.items.first(),
            }
        ],
    )
    approve_grn(grn)
    ledger = VendorLedger.objects.get(reference_type="purchase.GRN", reference_id=str(grn.pk))
    assert ledger.amount == Decimal("360.0000")
    assert ledger.balance_after == Decimal("360.0000")


def test_grn_partial_rolls_po_to_partial(po_factory, product):
    po = po_factory(qty=Decimal("10"), rate=Decimal("100"))
    submit_po(po)
    approve_po(po)
    grn = create_grn(
        vendor=po.vendor,
        branch=po.branch,
        grn_no="GRN-PARTIAL",
        po=po,
        items=[
            {
                "product": product,
                "qty_received": Decimal("4"),
                "qty_accepted": Decimal("4"),
                "cost_price": Decimal("90"),
                "po_item": po.items.first(),
            }
        ],
    )
    approve_grn(grn)
    po.refresh_from_db()
    assert po.status == POStatus.PARTIAL


def test_grn_full_rolls_po_to_received(po_factory, product):
    po = po_factory(qty=Decimal("4"), rate=Decimal("100"))
    submit_po(po)
    approve_po(po)
    grn = create_grn(
        vendor=po.vendor,
        branch=po.branch,
        grn_no="GRN-FULL",
        po=po,
        items=[
            {
                "product": product,
                "qty_received": Decimal("4"),
                "qty_accepted": Decimal("4"),
                "cost_price": Decimal("90"),
                "po_item": po.items.first(),
            }
        ],
    )
    approve_grn(grn)
    po.refresh_from_db()
    assert po.status == POStatus.RECEIVED


# ---------------------------------------------------------------------------
# Offline sync
# ---------------------------------------------------------------------------


def test_offline_sync_is_idempotent(vendor, branch, product):
    import uuid

    u = uuid.uuid4()
    a = sync_offline_grn(
        offline_uuid=u,
        vendor=vendor,
        branch=branch,
        grn_no="GRN-OFF-1",
        items=[
            {
                "product": product,
                "qty_received": Decimal("1"),
                "qty_accepted": Decimal("1"),
                "cost_price": Decimal("50"),
            }
        ],
    )
    b = sync_offline_grn(
        offline_uuid=u,
        vendor=vendor,
        branch=branch,
        grn_no="GRN-OFF-2",
        items=[],
    )
    assert a.pk == b.pk


def test_offline_sync_rejects_closed_po(po_factory, product):
    import uuid

    po = po_factory()
    po.status = POStatus.CLOSED
    po.save(update_fields=["status"])
    with pytest.raises(OfflineGRNPOClosed):
        sync_offline_grn(
            offline_uuid=uuid.uuid4(),
            vendor=po.vendor,
            branch=po.branch,
            grn_no="GRN-OFF-CLOSED",
            po=po,
            items=[
                {
                    "product": product,
                    "qty_received": Decimal("1"),
                    "qty_accepted": Decimal("1"),
                    "cost_price": Decimal("10"),
                }
            ],
        )


# ---------------------------------------------------------------------------
# Purchase invoice
# ---------------------------------------------------------------------------


def _approved_grn(po, product):
    grn = create_grn(
        vendor=po.vendor,
        branch=po.branch,
        grn_no=f"GRN-INV-{po.pk}",
        po=po,
        items=[
            {
                "product": product,
                "qty_received": po.items.first().qty,
                "qty_accepted": po.items.first().qty,
                "cost_price": Decimal("90"),
                "po_item": po.items.first(),
            }
        ],
    )
    return approve_grn(grn)


def test_pi_from_grns_requires_approved(vendor, branch):
    with pytest.raises(PINoApprovedGRNs):
        create_invoice_from_grns(vendor=vendor, branch=branch, pi_no="PI-EMPTY", grn_ids=[])


def test_pi_post_and_pay(po_factory, product):
    po = po_factory(qty=Decimal("4"), rate=Decimal("100"))
    submit_po(po)
    approve_po(po)
    grn = _approved_grn(po, product)

    pi = create_invoice_from_grns(
        vendor=po.vendor,
        branch=po.branch,
        pi_no="PI-1",
        grn_ids=[grn.pk],
    )
    assert pi.status == PIStatus.DRAFT
    post_invoice(pi)
    pi.refresh_from_db()
    assert pi.status == PIStatus.POSTED

    record_payment(pi, amount=Decimal("100"))
    pi.refresh_from_db()
    assert pi.status == PIStatus.PART_PAID

    record_payment(pi, amount=Decimal("260"))
    pi.refresh_from_db()
    assert pi.status == PIStatus.PAID


# ---------------------------------------------------------------------------
# Returns
# ---------------------------------------------------------------------------


def test_return_qty_capped_by_receipt(po_factory, product):
    po = po_factory(qty=Decimal("4"), rate=Decimal("100"))
    submit_po(po)
    approve_po(po)
    grn = _approved_grn(po, product)
    with pytest.raises(ReturnQtyExceedsReceipt):
        create_return(
            grn=grn,
            pr_no="PR-OVER",
            items=[{"product_id": product.pk, "qty": "99", "cost_price": "90"}],
        )


def test_return_post_writes_debit(po_factory, product):
    po = po_factory(qty=Decimal("4"), rate=Decimal("100"))
    submit_po(po)
    approve_po(po)
    grn = _approved_grn(po, product)
    pr = create_return(
        grn=grn,
        pr_no="PR-OK",
        items=[{"product_id": product.pk, "qty": "1", "cost_price": "90"}],
        reason="damaged",
    )
    post_return(pr)
    pr.refresh_from_db()
    assert pr.status == PRStatus.POSTED
    debit = VendorLedger.objects.filter(reference_type="purchase.PurchaseReturn").first()
    assert debit is not None
    assert debit.amount == Decimal("-90.0000")
