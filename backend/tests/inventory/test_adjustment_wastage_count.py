"""Tests for M05 adjustment, wastage, count services (step 6)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from apps.inventory.exceptions import InvalidDocumentState, UnknownReasonCode
from apps.inventory.models import (
    DocumentStatus,
    InventoryLedger,
    InventoryRefType,
    PhysicalCount,
    PhysicalCountItem,
    PhysicalCountStatus,
    Stock,
    StockAdjustment,
    StockAdjustmentItem,
    Wastage,
    WastageItem,
)
from apps.inventory.services import (
    adjustment_service,
    count_service,
    ledger_service,
    wastage_service,
)

pytestmark = pytest.mark.django_db


def _seed(product, branch, qty):
    ledger_service.post(
        ref_type=InventoryRefType.OPENING,
        ref_id="OPEN-1",
        items=[{"product": product, "qty_change": Decimal(str(qty))}],
        branch=branch,
        remarks="opening",
    )


# ---------------------------------------------------------------------------
# Adjustment
# ---------------------------------------------------------------------------


def test_adjustment_post_writes_signed_ledger(product, branch):
    _seed(product, branch, 10)
    adj = StockAdjustment.objects.create(adj_no="ADJ-1", branch=branch, reason_code="MANUAL")
    StockAdjustmentItem.objects.create(adjustment=adj, product=product, qty_change=Decimal("-3"))
    adjustment_service.post(adj)
    adj.refresh_from_db()
    assert adj.status == DocumentStatus.POSTED
    assert adj.posted_at is not None
    assert Stock.objects.get(product=product, branch=branch).qty_on_hand == Decimal("7")
    entry = InventoryLedger.objects.get(reference_type="ADJUSTMENT")
    assert entry.amount == Decimal("-3")
    assert entry.reason_code == "MANUAL"


def test_adjustment_rejects_non_draft(product, branch):
    _seed(product, branch, 5)
    adj = StockAdjustment.objects.create(adj_no="ADJ-2", branch=branch, reason_code="MANUAL")
    StockAdjustmentItem.objects.create(adjustment=adj, product=product, qty_change=Decimal("1"))
    adjustment_service.post(adj)
    with pytest.raises(InvalidDocumentState):
        adjustment_service.post(adj)


def test_adjustment_rejects_unknown_reason(product, branch):
    _seed(product, branch, 5)
    adj = StockAdjustment.objects.create(adj_no="ADJ-3", branch=branch, reason_code="NOPE")
    StockAdjustmentItem.objects.create(adjustment=adj, product=product, qty_change=Decimal("1"))
    with pytest.raises(UnknownReasonCode):
        adjustment_service.post(adj)
    adj.refresh_from_db()
    assert adj.status == DocumentStatus.DRAFT


# ---------------------------------------------------------------------------
# Wastage
# ---------------------------------------------------------------------------


def test_wastage_post_writes_negative_ledger(product, branch):
    _seed(product, branch, 10)
    w = Wastage.objects.create(wastage_no="W-1", branch=branch, reason_code="DAMAGE")
    WastageItem.objects.create(wastage=w, product=product, qty=Decimal("2"))
    wastage_service.post(w)
    w.refresh_from_db()
    assert w.status == DocumentStatus.POSTED
    assert Stock.objects.get(product=product, branch=branch).qty_on_hand == Decimal("8")
    entry = InventoryLedger.objects.get(reference_type="WASTAGE")
    assert entry.amount == Decimal("-2")
    assert entry.reason_code == "DAMAGE"


def test_wastage_rejects_unknown_reason(product, branch):
    _seed(product, branch, 5)
    w = Wastage.objects.create(wastage_no="W-2", branch=branch, reason_code="MANUAL")
    WastageItem.objects.create(wastage=w, product=product, qty=Decimal("1"))
    with pytest.raises(UnknownReasonCode):
        wastage_service.post(w)


# ---------------------------------------------------------------------------
# Physical Count
# ---------------------------------------------------------------------------


def test_count_mark_then_post_writes_diff(product, branch):
    _seed(product, branch, 10)
    c = PhysicalCount.objects.create(count_no="PC-1", branch=branch)
    PhysicalCountItem.objects.create(count=c, product=product, qty_counted=Decimal("8"))

    count_service.mark_counted(c)
    c.refresh_from_db()
    assert c.status == PhysicalCountStatus.COUNTED
    item = c.items.first()
    assert item.qty_expected == Decimal("10")

    count_service.post(c)
    c.refresh_from_db()
    assert c.status == PhysicalCountStatus.POSTED
    assert Stock.objects.get(product=product, branch=branch).qty_on_hand == Decimal("8")
    entry = InventoryLedger.objects.get(reference_type="COUNT")
    assert entry.amount == Decimal("-2")
    assert entry.reason_code == "COUNT_DIFF"


def test_count_post_skips_when_zero_diff(product, branch):
    _seed(product, branch, 5)
    c = PhysicalCount.objects.create(count_no="PC-2", branch=branch)
    PhysicalCountItem.objects.create(count=c, product=product, qty_counted=Decimal("5"))
    count_service.mark_counted(c)
    count_service.post(c)
    assert not InventoryLedger.objects.filter(reference_type="COUNT").exists()
    assert Stock.objects.get(product=product, branch=branch).qty_on_hand == Decimal("5")


def test_count_post_requires_counted_state(product, branch):
    _seed(product, branch, 5)
    c = PhysicalCount.objects.create(count_no="PC-3", branch=branch)
    PhysicalCountItem.objects.create(count=c, product=product, qty_counted=Decimal("5"))
    with pytest.raises(InvalidDocumentState):
        count_service.post(c)
