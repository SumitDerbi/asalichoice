"""Tests for M05 transfer_service (step 5)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from apps.inventory.exceptions import InsufficientStock, InvalidTransferState
from apps.inventory.models import (
    BranchTransfer,
    BranchTransferItem,
    BranchTransferStatus,
    InventoryLedger,
    InventoryRefType,
    Stock,
)
from apps.inventory.services import ledger_service, transfer_service

pytestmark = pytest.mark.django_db


def _seed_source_stock(product, branch, qty):
    """Use the ledger service so Stock and Batch land via the canonical path."""

    ledger_service.post(
        ref_type=InventoryRefType.OPENING,
        ref_id="OPEN-1",
        items=[{"product": product, "qty_change": Decimal(str(qty))}],
        branch=branch,
        remarks="opening",
    )


def _make_transfer(product, from_branch, to_branch, qty_sent, tr_no="TR-1"):
    tr = BranchTransfer.objects.create(tr_no=tr_no, from_branch=from_branch, to_branch=to_branch)
    BranchTransferItem.objects.create(transfer=tr, product=product, qty_sent=Decimal(str(qty_sent)))
    return tr


def test_dispatch_posts_negative_ledger_and_marks_in_transit(product, branch, other_branch):
    _seed_source_stock(product, branch, 10)
    tr = _make_transfer(product, branch, other_branch, 4)

    transfer_service.dispatch(tr)

    tr.refresh_from_db()
    assert tr.status == BranchTransferStatus.IN_TRANSIT
    assert tr.dispatched_at is not None

    # Source stock decremented
    src = Stock.objects.get(product=product, branch=branch)
    assert src.qty_on_hand == Decimal("6")

    # Destination has qty_in_transit row
    dst = Stock.objects.get(product=product, branch=other_branch)
    assert dst.qty_on_hand == Decimal("0")
    assert dst.qty_in_transit == Decimal("4")

    # Ledger line at source with TRANSFER ref
    entry = InventoryLedger.objects.get(reference_type="TRANSFER", branch=branch)
    assert entry.amount == Decimal("-4")


def test_dispatch_blocks_when_source_insufficient(product, branch, other_branch):
    _seed_source_stock(product, branch, 2)
    tr = _make_transfer(product, branch, other_branch, 5)

    with pytest.raises(InsufficientStock):
        transfer_service.dispatch(tr)

    tr.refresh_from_db()
    assert tr.status == BranchTransferStatus.DRAFT


def test_dispatch_rejects_non_draft(product, branch, other_branch):
    _seed_source_stock(product, branch, 10)
    tr = _make_transfer(product, branch, other_branch, 4)
    transfer_service.dispatch(tr)
    with pytest.raises(InvalidTransferState):
        transfer_service.dispatch(tr)


def test_receive_posts_positive_ledger_and_clears_in_transit(product, branch, other_branch):
    _seed_source_stock(product, branch, 10)
    tr = _make_transfer(product, branch, other_branch, 4)
    transfer_service.dispatch(tr)

    # Mark full receipt
    item = tr.items.first()
    item.qty_received = Decimal("4")
    item.save(update_fields=["qty_received"])

    transfer_service.receive(tr)

    tr.refresh_from_db()
    assert tr.status == BranchTransferStatus.RECEIVED
    assert tr.received_at is not None

    dst = Stock.objects.get(product=product, branch=other_branch)
    assert dst.qty_on_hand == Decimal("4")
    assert dst.qty_in_transit == Decimal("0")

    item.refresh_from_db()
    assert item.qty_lost == Decimal("0")

    inbound = InventoryLedger.objects.get(reference_type="TRANSFER", branch=other_branch)
    assert inbound.amount == Decimal("4")


def test_receive_records_qty_lost_for_shortfall(product, branch, other_branch):
    _seed_source_stock(product, branch, 10)
    tr = _make_transfer(product, branch, other_branch, 5)
    transfer_service.dispatch(tr)

    item = tr.items.first()
    item.qty_received = Decimal("3")
    item.save(update_fields=["qty_received"])

    transfer_service.receive(tr)

    item.refresh_from_db()
    assert item.qty_lost == Decimal("2")

    dst = Stock.objects.get(product=product, branch=other_branch)
    assert dst.qty_on_hand == Decimal("3")
    assert dst.qty_in_transit == Decimal("0")


def test_receive_rejects_non_in_transit(product, branch, other_branch):
    _seed_source_stock(product, branch, 10)
    tr = _make_transfer(product, branch, other_branch, 4)
    with pytest.raises(InvalidTransferState):
        transfer_service.receive(tr)


def test_cancel_only_allowed_on_draft(product, branch, other_branch):
    _seed_source_stock(product, branch, 10)
    tr = _make_transfer(product, branch, other_branch, 4)

    transfer_service.cancel(tr)
    tr.refresh_from_db()
    assert tr.status == BranchTransferStatus.CANCELLED

    with pytest.raises(InvalidTransferState):
        transfer_service.cancel(tr)
