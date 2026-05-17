"""M04 purchase API smoke + permission tests."""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest

from apps.purchase.models import POStatus, Vendor

pytestmark = pytest.mark.django_db


def _super(user_factory):
    return user_factory(is_staff=True, is_superuser=True)


# ---------------------------------------------------------------------------
# AuthZ
# ---------------------------------------------------------------------------


def test_anonymous_cannot_list_vendors(api_client):
    resp = api_client().get("/api/v1/purchase/vendors/")
    assert resp.status_code == 401


def test_super_can_list_vendors(api_client, user_factory):
    resp = api_client(_super(user_factory)).get("/api/v1/purchase/vendors/")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Vendor CRUD
# ---------------------------------------------------------------------------


def test_create_vendor_api(api_client, user_factory):
    client = api_client(_super(user_factory))
    resp = client.post(
        "/api/v1/purchase/vendors/",
        {"code": "V-API-1", "name": "API Vendor"},
        format="json",
    )
    assert resp.status_code == 201, resp.content
    assert Vendor.objects.filter(code="V-API-1").exists()


def test_deactivate_vendor_action(api_client, user_factory, vendor):
    client = api_client(_super(user_factory))
    resp = client.post(f"/api/v1/purchase/vendors/{vendor.pk}/deactivate/")
    assert resp.status_code == 200, resp.content
    vendor.refresh_from_db()
    assert vendor.is_active is False


# ---------------------------------------------------------------------------
# PO lifecycle via API
# ---------------------------------------------------------------------------


def test_po_submit_approve_actions(api_client, user_factory, po_factory):
    po = po_factory()
    client = api_client(_super(user_factory))
    r1 = client.post(f"/api/v1/purchase/pos/{po.pk}/submit/")
    assert r1.status_code == 200, r1.content
    r2 = client.post(f"/api/v1/purchase/pos/{po.pk}/approve/")
    assert r2.status_code == 200, r2.content
    po.refresh_from_db()
    assert po.status == POStatus.APPROVED


def test_po_cancel_action(api_client, user_factory, po_factory):
    po = po_factory()
    client = api_client(_super(user_factory))
    r = client.post(f"/api/v1/purchase/pos/{po.pk}/cancel/")
    assert r.status_code == 200, r.content
    po.refresh_from_db()
    assert po.status == POStatus.CANCELLED


# ---------------------------------------------------------------------------
# GRN offline sync endpoint
# ---------------------------------------------------------------------------


def test_grn_sync_offline_idempotent(api_client, user_factory, vendor, branch, product):
    client = api_client(_super(user_factory))
    body = {
        "offline_uuid": str(uuid.uuid4()),
        "vendor": vendor.pk,
        "branch": branch.pk,
        "grn_no": "GRN-OFF-API",
        "items": [
            {
                "product": product.pk,
                "qty_received": "2",
                "qty_accepted": "2",
                "cost_price": "50",
            }
        ],
    }
    r1 = client.post("/api/v1/purchase/grns/sync-offline/", body, format="json")
    assert r1.status_code == 201, r1.content
    r2 = client.post("/api/v1/purchase/grns/sync-offline/", body, format="json")
    assert r2.status_code == 201, r2.content
    assert r1.json()["id"] == r2.json()["id"]


def test_grn_sync_offline_missing_fields_returns_envelope(api_client, user_factory):
    client = api_client(_super(user_factory))
    r = client.post("/api/v1/purchase/grns/sync-offline/", {}, format="json")
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "API-400"


# ---------------------------------------------------------------------------
# Vendor ledger read
# ---------------------------------------------------------------------------


def test_vendor_ledger_list_filters_by_vendor(api_client, user_factory, vendor):
    client = api_client(_super(user_factory))
    resp = client.get(f"/api/v1/purchase/ledger/?vendor={vendor.pk}")
    assert resp.status_code == 200, resp.content


# ---------------------------------------------------------------------------
# Full end-to-end via API
# ---------------------------------------------------------------------------


def test_full_po_to_payment_flow(api_client, user_factory, po_factory, product, branch):
    client = api_client(_super(user_factory))
    po = po_factory(qty=Decimal("3"), rate=Decimal("100"))

    assert client.post(f"/api/v1/purchase/pos/{po.pk}/submit/").status_code == 200
    assert client.post(f"/api/v1/purchase/pos/{po.pk}/approve/").status_code == 200

    # Create GRN via service-shaped POST (no items in serializer; minimum row).
    from apps.purchase.services import create_grn

    grn = create_grn(
        vendor=po.vendor,
        branch=branch,
        grn_no="GRN-FLOW-1",
        po=po,
        items=[
            {
                "product": product,
                "qty_received": Decimal("3"),
                "qty_accepted": Decimal("3"),
                "cost_price": Decimal("90"),
                "po_item": po.items.first(),
            }
        ],
    )
    assert client.post(f"/api/v1/purchase/grns/{grn.pk}/approve/").status_code == 200
    grn.refresh_from_db()
    assert grn.status == "APPROVED"

    r = client.post(
        "/api/v1/purchase/invoices/from-grns/",
        {
            "vendor": po.vendor.pk,
            "branch": branch.pk,
            "pi_no": "PI-FLOW-1",
            "grn_ids": [grn.pk],
        },
        format="json",
    )
    assert r.status_code == 201, r.content
    pi_id = r.json()["id"]

    assert client.post(f"/api/v1/purchase/invoices/{pi_id}/post/").status_code == 200
    rp = client.post(
        f"/api/v1/purchase/invoices/{pi_id}/pay/",
        {"amount": "270"},
        format="json",
    )
    assert rp.status_code == 200, rp.content
    assert rp.json()["status"] == "PAID"
