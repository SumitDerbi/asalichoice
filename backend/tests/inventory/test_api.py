"""M05 inventory API smoke + permission tests (Item 8)."""

from __future__ import annotations

import pytest

from apps.inventory.models import (
    BranchTransfer,
    BranchTransferStatus,
    DocumentStatus,
    InventoryLedger,
    InventoryRefType,
    PhysicalCount,
    PhysicalCountStatus,
    ReservationStatus,
    Stock,
    StockAdjustment,
    Wastage,
)
from apps.inventory.services import ledger_service

pytestmark = pytest.mark.django_db


def _super(user_factory):
    return user_factory(is_staff=True, is_superuser=True)


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


def test_anonymous_blocked_on_stock(api_client):
    assert api_client().get("/api/v1/inventory/stock/").status_code == 401


def test_super_can_list_stock(api_client, user_factory):
    assert api_client(_super(user_factory)).get("/api/v1/inventory/stock/").status_code == 200


# ---------------------------------------------------------------------------
# Read endpoints
# ---------------------------------------------------------------------------


def test_stock_filter_by_branch(api_client, user_factory, product, branch, other_branch):
    Stock.objects.create(product=product, branch=branch, qty_on_hand="5")
    Stock.objects.create(product=product, branch=other_branch, qty_on_hand="3")
    client = api_client(_super(user_factory))
    resp = client.get(f"/api/v1/inventory/stock/?branch={branch.pk}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 1
    assert body["results"][0]["branch"] == branch.pk


def test_ledger_uses_cursor_pagination(api_client, user_factory, product, branch):
    ledger_service.post(
        ref_type=InventoryRefType.OPENING,
        ref_id="api-test",
        items=[{"product": product, "qty_change": "10"}],
        branch=branch,
    )
    client = api_client(_super(user_factory))
    resp = client.get("/api/v1/inventory/ledger/")
    assert resp.status_code == 200
    body = resp.json()
    # CursorPagination shape — no "count", has "next"/"previous"/"results".
    assert "count" not in body
    assert "results" in body
    assert "next" in body
    assert len(body["results"]) == 1
    assert InventoryLedger.objects.count() == 1


# ---------------------------------------------------------------------------
# Reservations
# ---------------------------------------------------------------------------


def test_reservation_create_and_release(api_client, user_factory, product, branch):
    # Seed stock so reservations can land.
    ledger_service.post(
        ref_type=InventoryRefType.OPENING,
        ref_id="seed",
        items=[{"product": product, "qty_change": "5"}],
        branch=branch,
    )
    client = api_client(_super(user_factory))
    payload = {
        "product": product.pk,
        "branch": branch.pk,
        "qty": "2",
        "ref_type": "ORDER",
        "ref_id": "SO-1",
    }
    r1 = client.post("/api/v1/inventory/reservations/", payload, format="json")
    assert r1.status_code == 201, r1.content
    res_id = r1.json()["id"]
    r2 = client.post(f"/api/v1/inventory/reservations/{res_id}/release/")
    assert r2.status_code == 200, r2.content
    assert r2.json()["status"] == ReservationStatus.RELEASED


def test_reservation_insufficient_stock_returns_envelope(api_client, user_factory, product, branch):
    # Seed an empty stock row so the lock succeeds but available == 0.
    Stock.objects.create(product=product, branch=branch, qty_on_hand="0")
    client = api_client(_super(user_factory))
    payload = {
        "product": product.pk,
        "branch": branch.pk,
        "qty": "1",
        "ref_type": "ORDER",
        "ref_id": "SO-NO-STOCK",
    }
    r = client.post("/api/v1/inventory/reservations/", payload, format="json")
    assert r.status_code == 409, r.content
    assert r.json()["error"]["code"] == "INV-010"


# ---------------------------------------------------------------------------
# Branch transfers — dispatch + receive
# ---------------------------------------------------------------------------


def test_transfer_dispatch_receive_via_api(api_client, user_factory, product, branch, other_branch):
    # Seed source stock so dispatch ledger doesn't trip INV-010.
    ledger_service.post(
        ref_type=InventoryRefType.OPENING,
        ref_id="seed-tr",
        items=[{"product": product, "qty_change": "10"}],
        branch=branch,
    )
    client = api_client(_super(user_factory))
    payload = {
        "tr_no": "TR-API-1",
        "from_branch": branch.pk,
        "to_branch": other_branch.pk,
        "items": [{"product": product.pk, "qty_sent": "4"}],
    }
    r1 = client.post("/api/v1/inventory/transfers/", payload, format="json")
    assert r1.status_code == 201, r1.content
    tr_id = r1.json()["id"]
    r2 = client.post(f"/api/v1/inventory/transfers/{tr_id}/dispatch/")
    assert r2.status_code == 200, r2.content
    assert r2.json()["status"] == BranchTransferStatus.IN_TRANSIT
    # Set qty_received on the item directly (mobile flow would PATCH first).
    transfer = BranchTransfer.objects.get(pk=tr_id)
    item = transfer.items.first()
    item.qty_received = 4
    item.save()
    r3 = client.post(f"/api/v1/inventory/transfers/{tr_id}/receive/")
    assert r3.status_code == 200, r3.content
    assert r3.json()["status"] == BranchTransferStatus.RECEIVED


def test_transfer_dispatch_wrong_state_returns_envelope(
    api_client, user_factory, branch, other_branch
):
    transfer = BranchTransfer.objects.create(
        tr_no="TR-API-WRONG",
        from_branch=branch,
        to_branch=other_branch,
        status=BranchTransferStatus.RECEIVED,
    )
    client = api_client(_super(user_factory))
    r = client.post(f"/api/v1/inventory/transfers/{transfer.pk}/dispatch/")
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "INV-020"


# ---------------------------------------------------------------------------
# Adjustment / Wastage / Count via API
# ---------------------------------------------------------------------------


def test_adjustment_create_and_post(api_client, user_factory, product, branch):
    client = api_client(_super(user_factory))
    payload = {
        "adj_no": "ADJ-API-1",
        "branch": branch.pk,
        "reason_code": "MANUAL",
        "items": [{"product": product.pk, "qty_change": "3"}],
    }
    r1 = client.post("/api/v1/inventory/adjustments/", payload, format="json")
    assert r1.status_code == 201, r1.content
    adj_id = r1.json()["id"]
    r2 = client.post(f"/api/v1/inventory/adjustments/{adj_id}/post/")
    assert r2.status_code == 200, r2.content
    assert r2.json()["status"] == DocumentStatus.POSTED
    assert StockAdjustment.objects.get(pk=adj_id).status == DocumentStatus.POSTED


def test_wastage_create_and_post(api_client, user_factory, product, branch):
    # Need stock to wastage against.
    ledger_service.post(
        ref_type=InventoryRefType.OPENING,
        ref_id="seed-w",
        items=[{"product": product, "qty_change": "5"}],
        branch=branch,
    )
    client = api_client(_super(user_factory))
    payload = {
        "wastage_no": "WAS-API-1",
        "branch": branch.pk,
        "reason_code": "DAMAGE",
        "items": [{"product": product.pk, "qty": "2"}],
    }
    r1 = client.post("/api/v1/inventory/wastage/", payload, format="json")
    assert r1.status_code == 201, r1.content
    w_id = r1.json()["id"]
    r2 = client.post(f"/api/v1/inventory/wastage/{w_id}/post/")
    assert r2.status_code == 200, r2.content
    assert Wastage.objects.get(pk=w_id).status == DocumentStatus.POSTED


def test_count_mark_then_post(api_client, user_factory, product, branch):
    ledger_service.post(
        ref_type=InventoryRefType.OPENING,
        ref_id="seed-c",
        items=[{"product": product, "qty_change": "10"}],
        branch=branch,
    )
    client = api_client(_super(user_factory))
    payload = {
        "count_no": "CNT-API-1",
        "branch": branch.pk,
        "items": [{"product": product.pk, "qty_counted": "8"}],
    }
    r1 = client.post("/api/v1/inventory/counts/", payload, format="json")
    assert r1.status_code == 201, r1.content
    cnt_id = r1.json()["id"]
    r2 = client.post(f"/api/v1/inventory/counts/{cnt_id}/mark-counted/")
    assert r2.status_code == 200, r2.content
    assert r2.json()["status"] == PhysicalCountStatus.COUNTED
    r3 = client.post(f"/api/v1/inventory/counts/{cnt_id}/post/")
    assert r3.status_code == 200, r3.content
    assert PhysicalCount.objects.get(pk=cnt_id).status == PhysicalCountStatus.POSTED


# ---------------------------------------------------------------------------
# Permission split — view-only user cannot write
# ---------------------------------------------------------------------------


def test_non_super_user_cannot_create_transfer(
    api_client, user_factory, branch, other_branch, product
):
    # Plain authenticated user without inventory.transfer → write denied.
    user = user_factory()
    client = api_client(user)
    payload = {
        "tr_no": "TR-DENY",
        "from_branch": branch.pk,
        "to_branch": other_branch.pk,
        "items": [{"product": product.pk, "qty_sent": "1"}],
    }
    resp = client.post("/api/v1/inventory/transfers/", payload, format="json")
    assert resp.status_code == 403


def test_non_super_user_cannot_read_stock(api_client, user_factory):
    user = user_factory()
    resp = api_client(user).get("/api/v1/inventory/stock/")
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Item 9 — Ledger cursor pagination + filters
# ---------------------------------------------------------------------------


def _seed_ledger(product, branch, n: int, ref_type=InventoryRefType.OPENING):
    for i in range(n):
        ledger_service.post(
            ref_type=ref_type,
            ref_id=f"seed-{i}",
            items=[{"product": product, "qty_change": "1"}],
            branch=branch,
        )


def test_ledger_cursor_round_trip(api_client, user_factory, product, branch):
    _seed_ledger(product, branch, 5)
    client = api_client(_super(user_factory))

    page1 = client.get("/api/v1/inventory/ledger/?page_size=2").json()
    assert len(page1["results"]) == 2
    assert page1["next"] is not None

    page2 = client.get(page1["next"]).json()
    assert len(page2["results"]) == 2
    # Stable, newest-first: no overlap with page1.
    ids1 = {r["id"] for r in page1["results"]}
    ids2 = {r["id"] for r in page2["results"]}
    assert ids1.isdisjoint(ids2)
    # Newest-first ordering preserved across the cursor jump.
    assert max(ids2) < min(ids1)

    # And we can walk backwards from page2.
    page1_back = client.get(page2["previous"]).json()
    assert {r["id"] for r in page1_back["results"]} == ids1


def test_ledger_filter_by_reason_code(api_client, user_factory, product, branch):
    ledger_service.post(
        ref_type=InventoryRefType.ADJUSTMENT,
        ref_id="adj-A",
        items=[{"product": product, "qty_change": "1"}],
        branch=branch,
        reason_code="DAMAGED",
    )
    ledger_service.post(
        ref_type=InventoryRefType.ADJUSTMENT,
        ref_id="adj-B",
        items=[{"product": product, "qty_change": "1"}],
        branch=branch,
        reason_code="LOST",
    )
    client = api_client(_super(user_factory))
    resp = client.get("/api/v1/inventory/ledger/?reason_code=DAMAGED").json()
    assert len(resp["results"]) == 1
    assert resp["results"][0]["reason_code"] == "DAMAGED"


def test_ledger_filter_by_ref_type(api_client, user_factory, product, branch):
    ledger_service.post(
        ref_type=InventoryRefType.OPENING,
        ref_id="op",
        items=[{"product": product, "qty_change": "5"}],
        branch=branch,
    )
    ledger_service.post(
        ref_type=InventoryRefType.ADJUSTMENT,
        ref_id="adj",
        items=[{"product": product, "qty_change": "1"}],
        branch=branch,
    )
    client = api_client(_super(user_factory))
    resp = client.get(f"/api/v1/inventory/ledger/?ref_type={InventoryRefType.OPENING}").json()
    assert len(resp["results"]) == 1
    assert resp["results"][0]["reference_type"] == InventoryRefType.OPENING


def test_ledger_filter_by_timestamp_range(api_client, user_factory, product, branch):
    from datetime import timedelta
    from urllib.parse import quote

    ledger_service.post(
        ref_type=InventoryRefType.OPENING,
        ref_id="t1",
        items=[{"product": product, "qty_change": "1"}],
        branch=branch,
    )
    t1 = InventoryLedger.objects.get(reference_id="t1")
    cutoff_dt = t1.timestamp + timedelta(microseconds=1)
    cutoff = quote(cutoff_dt.isoformat())
    ledger_service.post(
        ref_type=InventoryRefType.OPENING,
        ref_id="t2",
        items=[{"product": product, "qty_change": "1"}],
        branch=branch,
    )
    # Force t2's timestamp strictly after the cutoff.
    InventoryLedger.objects.filter(reference_id="t2").update(
        timestamp=t1.timestamp + timedelta(seconds=1)
    )
    client = api_client(_super(user_factory))

    after = client.get(f"/api/v1/inventory/ledger/?timestamp_from={cutoff}").json()
    assert len(after["results"]) == 1
    assert after["results"][0]["reference_id"] == "t2"

    before = client.get(f"/api/v1/inventory/ledger/?timestamp_to={cutoff}").json()
    assert len(before["results"]) == 1
    assert before["results"][0]["reference_id"] == "t1"


def test_ledger_filter_by_actor(api_client, user_factory, product, branch):
    actor_a = user_factory()
    actor_b = user_factory()
    ledger_service.post(
        ref_type=InventoryRefType.OPENING,
        ref_id="actor-a",
        items=[{"product": product, "qty_change": "1"}],
        branch=branch,
        actor=actor_a,
    )
    ledger_service.post(
        ref_type=InventoryRefType.OPENING,
        ref_id="actor-b",
        items=[{"product": product, "qty_change": "1"}],
        branch=branch,
        actor=actor_b,
    )
    client = api_client(_super(user_factory))
    resp = client.get(f"/api/v1/inventory/ledger/?actor={actor_a.pk}").json()
    assert len(resp["results"]) == 1
    assert resp["results"][0]["actor"] == actor_a.pk


def test_ledger_empty_filter_returns_empty_results(api_client, user_factory, product, branch):
    _seed_ledger(product, branch, 2)
    client = api_client(_super(user_factory))
    resp = client.get("/api/v1/inventory/ledger/?reason_code=NONEXISTENT").json()
    assert resp["results"] == []
    assert resp["next"] is None
