"""Tests for ``apps.inventory.services.ledger_service`` (M05 step 3)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from apps.inventory.exceptions import InsufficientStock
from apps.inventory.models import Batch, BatchStatus, InventoryLedger, InventoryRefType, Stock
from apps.inventory.services import ledger_service

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_post_creates_stock_and_ledger_on_first_inbound(branch, product, qty):
    entries = ledger_service.post(
        ref_type=InventoryRefType.GRN,
        ref_id=1,
        items=[{"product_id": product.pk, "qty_change": qty(10)}],
        branch=branch,
    )

    assert len(entries) == 1
    entry = entries[0]
    assert entry.amount == qty(10)
    assert entry.balance_before == qty(0)
    assert entry.balance_after == qty(10)
    assert entry.reference_type == InventoryRefType.GRN
    assert entry.reference_id == "1"

    stock = Stock.objects.get(branch=branch, product=product)
    assert stock.qty_on_hand == qty(10)
    assert stock.last_movement_at is not None


def test_post_increments_existing_stock(branch, product, qty):
    ledger_service.post(
        ref_type=InventoryRefType.GRN,
        ref_id=1,
        items=[{"product_id": product.pk, "qty_change": qty(10)}],
        branch=branch,
    )
    entries = ledger_service.post(
        ref_type=InventoryRefType.GRN,
        ref_id=2,
        items=[{"product_id": product.pk, "qty_change": qty(5)}],
        branch=branch,
    )

    assert entries[0].balance_before == qty(10)
    assert entries[0].balance_after == qty(15)
    assert Stock.objects.get(branch=branch, product=product).qty_on_hand == qty(15)
    assert InventoryLedger.objects.filter(product=product, branch=branch).count() == 2


def test_post_supports_outbound_movement(branch, product, qty):
    ledger_service.post(
        ref_type=InventoryRefType.GRN,
        ref_id=1,
        items=[{"product_id": product.pk, "qty_change": qty(10)}],
        branch=branch,
    )
    ledger_service.post(
        ref_type=InventoryRefType.SALE,
        ref_id=42,
        items=[{"product_id": product.pk, "qty_change": qty(-3)}],
        branch=branch,
    )

    assert Stock.objects.get(branch=branch, product=product).qty_on_hand == qty(7)


# ---------------------------------------------------------------------------
# Negative-stock guard (INV-010)
# ---------------------------------------------------------------------------


def test_post_blocks_negative_stock(branch, product, qty):
    with pytest.raises(InsufficientStock) as excinfo:
        ledger_service.post(
            ref_type=InventoryRefType.SALE,
            ref_id=1,
            items=[{"product_id": product.pk, "qty_change": qty(-1)}],
            branch=branch,
        )

    assert excinfo.value.default_code == "INV-010"
    # Rollback: no Stock, no ledger row leaks.
    assert not Stock.objects.filter(branch=branch, product=product).exists()
    assert InventoryLedger.objects.count() == 0


def test_post_rolls_back_entire_batch_on_one_negative(branch, product, product_b, qty):
    # Seed product A with 5 on hand. product_b has zero.
    ledger_service.post(
        ref_type=InventoryRefType.GRN,
        ref_id=1,
        items=[{"product_id": product.pk, "qty_change": qty(5)}],
        branch=branch,
    )
    with pytest.raises(InsufficientStock):
        ledger_service.post(
            ref_type=InventoryRefType.SALE,
            ref_id=2,
            items=[
                {"product_id": product.pk, "qty_change": qty(-2)},  # would succeed alone
                {"product_id": product_b.pk, "qty_change": qty(-1)},  # blows up
            ],
            branch=branch,
        )

    # Atomicity: product A's first line must have rolled back too.
    assert Stock.objects.get(branch=branch, product=product).qty_on_hand == qty(5)
    assert InventoryLedger.objects.filter(reference_id="2").count() == 0


# ---------------------------------------------------------------------------
# Batch upsert + status roll
# ---------------------------------------------------------------------------


def test_inbound_with_batch_kwargs_creates_batch(branch, product, qty):
    ledger_service.post(
        ref_type=InventoryRefType.GRN,
        ref_id=1,
        items=[
            {
                "product_id": product.pk,
                "qty_change": qty(8),
                "cost_price": Decimal("12.50"),
                "batch_kwargs": {
                    "batch_no": "B-001",
                    "expiry_date": date(2027, 1, 1),
                },
            }
        ],
        branch=branch,
    )

    batch = Batch.objects.get(branch=branch, product=product, batch_no="B-001")
    assert batch.qty_received == qty(8)
    assert batch.qty_remaining == qty(8)
    assert batch.status == BatchStatus.ACTIVE
    assert batch.expiry_date == date(2027, 1, 1)


def test_outbound_drains_batch_and_marks_consumed(branch, product, qty):
    ledger_service.post(
        ref_type=InventoryRefType.GRN,
        ref_id=1,
        items=[
            {
                "product_id": product.pk,
                "qty_change": qty(2),
                "batch_kwargs": {"batch_no": "B-002"},
            }
        ],
        branch=branch,
    )
    ledger_service.post(
        ref_type=InventoryRefType.SALE,
        ref_id=2,
        items=[
            {
                "product_id": product.pk,
                "qty_change": qty(-2),
                "batch_kwargs": {"batch_no": "B-002"},
            }
        ],
        branch=branch,
    )

    batch = Batch.objects.get(branch=branch, product=product, batch_no="B-002")
    assert batch.qty_remaining == qty(0)
    assert batch.status == BatchStatus.CONSUMED


def test_outbound_unknown_batch_is_rejected(branch, product, qty):
    # Even with positive stock, missing batch reference is a programmer error.
    ledger_service.post(
        ref_type=InventoryRefType.GRN,
        ref_id=1,
        items=[{"product_id": product.pk, "qty_change": qty(5)}],
        branch=branch,
    )
    with pytest.raises(ValueError):
        ledger_service.post(
            ref_type=InventoryRefType.SALE,
            ref_id=2,
            items=[
                {
                    "product_id": product.pk,
                    "qty_change": qty(-1),
                    "batch_kwargs": {"batch_no": "DOES-NOT-EXIST"},
                }
            ],
            branch=branch,
        )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def test_xor_target_enforced(branch, qty):
    with pytest.raises(ValueError):
        ledger_service.post(
            ref_type=InventoryRefType.GRN,
            ref_id=1,
            items=[{"qty_change": qty(1)}],  # neither product nor variant
            branch=branch,
        )


def test_zero_qty_change_is_skipped(branch, product, qty):
    entries = ledger_service.post(
        ref_type=InventoryRefType.GRN,
        ref_id=1,
        items=[{"product_id": product.pk, "qty_change": qty(0)}],
        branch=branch,
    )
    assert entries == []
    assert InventoryLedger.objects.count() == 0
