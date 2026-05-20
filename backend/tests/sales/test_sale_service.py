"""Tests for ``apps.sales.services.sale_service`` — the full sale lifecycle."""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest

from apps.inventory.models import InventoryLedger, InventoryRefType, Stock
from apps.sales.exceptions import (
    DuplicateOfflineSale,
    EmptySale,
    InvalidSaleState,
    PaymentTotalMismatch,
)
from apps.sales.models import SalePaymentStatus, SaleStatus
from apps.sales.services import sale_service

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# create_draft
# ---------------------------------------------------------------------------


def test_create_draft_with_items_and_payment(branch, product, uom, gst18, cash_mode):
    sale = sale_service.create_draft(
        branch=branch,
        items=[{"product": product, "uom": uom, "qty": 2, "sale_price": "100", "tax": gst18}],
        payments=[
            {"payment_mode": cash_mode, "amount": "236"},
        ],
    )

    assert sale.status == SaleStatus.DRAFT
    assert sale.items.count() == 1
    assert sale.payments.count() == 1
    assert sale.grand_total == Decimal("236.0000")
    assert sale.payment_total == Decimal("236.0000")


def test_create_draft_dedupes_offline_uuid(branch, product, uom, gst18):
    oid = uuid.uuid4()
    sale_service.create_draft(
        branch=branch,
        offline_uuid=oid,
        items=[{"product": product, "uom": uom, "qty": 1, "sale_price": "100", "tax": gst18}],
    )
    with pytest.raises(DuplicateOfflineSale):
        sale_service.create_draft(
            branch=branch,
            offline_uuid=oid,
            items=[{"product": product, "uom": uom, "qty": 1, "sale_price": "100", "tax": gst18}],
        )


# ---------------------------------------------------------------------------
# post
# ---------------------------------------------------------------------------


def test_post_writes_inventory_ledger_and_marks_paid(
    branch, product, uom, gst18, cash_mode, grn_in
):
    grn_in(product, 10)

    sale = sale_service.create_draft(
        branch=branch,
        items=[{"product": product, "uom": uom, "qty": 2, "sale_price": "100", "tax": gst18}],
        payments=[
            {"payment_mode": cash_mode, "amount": "236"},
        ],
    )

    sale = sale_service.post(sale)

    assert sale.status == SaleStatus.PAID
    assert sale.billed_at is not None

    # Inventory ledger received a SALE row reducing stock by 2.
    sale_entries = InventoryLedger.objects.filter(reference_type=InventoryRefType.SALE)
    assert sale_entries.count() == 1
    entry = sale_entries.first()
    assert entry.amount == Decimal("-2")

    stock = Stock.objects.get(branch=branch, product=product)
    assert stock.qty_on_hand == Decimal("8")


def test_post_blocks_empty_sale(branch, cash_mode):
    sale = sale_service.create_draft(
        branch=branch,
        items=[],
    )
    with pytest.raises(EmptySale):
        sale_service.post(sale)


def test_post_blocks_payment_mismatch(branch, product, uom, gst18, cash_mode, grn_in):
    grn_in(product, 5)
    sale = sale_service.create_draft(
        branch=branch,
        items=[{"product": product, "uom": uom, "qty": 1, "sale_price": "100", "tax": gst18}],
        payments=[
            {"payment_mode": cash_mode, "amount": "10"},  # not enough
        ],
    )
    with pytest.raises(PaymentTotalMismatch):
        sale_service.post(sale)


def test_post_allows_partial_payment_when_flag(branch, product, uom, gst18, cash_mode, grn_in):
    grn_in(product, 5)
    sale = sale_service.create_draft(
        branch=branch,
        items=[{"product": product, "uom": uom, "qty": 1, "sale_price": "100", "tax": gst18}],
        payments=[
            {"payment_mode": cash_mode, "amount": "10"},
        ],
    )
    sale = sale_service.post(sale, allow_partial_payment=True)
    assert sale.status == SaleStatus.PARTIALLY_PAID
    assert sale.payment_total == Decimal("10.0000")


def test_post_blocks_already_paid(branch, product, uom, gst18, cash_mode, grn_in):
    grn_in(product, 5)
    sale = sale_service.create_draft(
        branch=branch,
        items=[{"product": product, "uom": uom, "qty": 1, "sale_price": "100", "tax": gst18}],
        payments=[
            {"payment_mode": cash_mode, "amount": "118"},
        ],
    )
    sale_service.post(sale)
    with pytest.raises(InvalidSaleState):
        sale_service.post(sale)


# ---------------------------------------------------------------------------
# cancel
# ---------------------------------------------------------------------------


def test_cancel_reverses_ledger_and_refunds_payments(
    branch, product, uom, gst18, cash_mode, grn_in
):
    grn_in(product, 5)
    sale = sale_service.create_draft(
        branch=branch,
        items=[{"product": product, "uom": uom, "qty": 1, "sale_price": "100", "tax": gst18}],
        payments=[
            {"payment_mode": cash_mode, "amount": "118"},
        ],
    )
    sale_service.post(sale)
    assert Stock.objects.get(branch=branch, product=product).qty_on_hand == Decimal("4")

    sale = sale_service.cancel(sale, reason="customer changed mind")

    assert sale.status == SaleStatus.CANCELLED
    assert sale.payment_total == Decimal("0")

    # Stock should have been restored.
    assert Stock.objects.get(branch=branch, product=product).qty_on_hand == Decimal("5")

    # All SUCCESS payments flipped to REFUNDED.
    assert sale.payments.filter(status=SalePaymentStatus.REFUNDED).count() == sale.payments.count()

    # A reversing ledger row exists.
    cancel_entries = InventoryLedger.objects.filter(
        reference_type=InventoryRefType.SALE,
        reference_id__startswith="CANCEL:",
    )
    assert cancel_entries.count() == 1
    assert cancel_entries.first().amount == Decimal("1")


def test_cancel_blocks_draft(branch):
    sale = sale_service.create_draft(branch=branch, items=[])
    with pytest.raises(InvalidSaleState):
        sale_service.cancel(sale)


# ---------------------------------------------------------------------------
# signals
# ---------------------------------------------------------------------------


def test_post_emits_sale_posted_signal(branch, product, uom, gst18, cash_mode, grn_in):
    from apps.sales.signals import sale_posted

    received = []

    def _handler(sender, sale, **kwargs):
        received.append(sale.pk)

    sale_posted.connect(_handler, dispatch_uid="test-post-handler")
    try:
        grn_in(product, 5)
        sale = sale_service.create_draft(
            branch=branch,
            items=[{"product": product, "uom": uom, "qty": 1, "sale_price": "100", "tax": gst18}],
            payments=[
                {"payment_mode": cash_mode, "amount": "118"},
            ],
        )
        sale_service.post(sale)
        assert received == [sale.pk]
    finally:
        sale_posted.disconnect(dispatch_uid="test-post-handler")
