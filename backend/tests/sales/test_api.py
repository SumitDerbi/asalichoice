"""API smoke + lifecycle tests for the M11 Sales endpoints.

Covers the viewset & serializers (which are otherwise only exercised
through the admin UI) so the sales module clears the 90% coverage
gate set by ``plans/phase-1-modules/M11-sales-billing.md`` Step 9.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from apps.sales.models import Sale, SaleStatus

pytestmark = pytest.mark.django_db


def _super(user_factory):
    return user_factory(is_staff=True, is_superuser=True)


# ---------------------------------------------------------------------------
# AuthN / AuthZ
# ---------------------------------------------------------------------------


def test_anonymous_cannot_list_sales(api_client):
    resp = api_client().get("/api/v1/sales/")
    assert resp.status_code == 401


def test_super_can_list_sales(api_client, user_factory):
    resp = api_client(_super(user_factory)).get("/api/v1/sales/")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Create draft via POST /sales/
# ---------------------------------------------------------------------------


def _draft_payload(branch, product, uom, gst18, cash_mode, *, auto_post=False):
    return {
        "origin": "POS",
        "branch": branch.id,
        "tax_mode": "EXCLUSIVE",
        "items": [
            {
                "product": product.id,
                "uom": uom.id,
                "tax": gst18.id,
                "qty": "2",
                "sale_price": "100",
            }
        ],
        "payments": [
            {"payment_mode": cash_mode.id, "amount": "236"},
        ],
        "auto_post": auto_post,
    }


def test_create_draft_via_api(api_client, user_factory, branch, product, uom, gst18, cash_mode):
    client = api_client(_super(user_factory))
    resp = client.post(
        "/api/v1/sales/",
        _draft_payload(branch, product, uom, gst18, cash_mode),
        format="json",
    )
    assert resp.status_code == 201, resp.content
    body = resp.json()
    assert body["status"] == SaleStatus.DRAFT
    assert body["grand_total"] == "236.0000"
    assert Sale.objects.filter(pk=body["id"]).exists()


def test_create_rejects_item_with_both_product_and_variant(
    api_client, user_factory, branch, product, uom, gst18
):
    client = api_client(_super(user_factory))
    payload = {
        "origin": "POS",
        "branch": branch.id,
        "items": [
            {
                "product": product.id,
                "variant": product.id,  # XOR violation
                "uom": uom.id,
                "tax": gst18.id,
                "qty": "1",
                "sale_price": "100",
            }
        ],
    }
    resp = client.post("/api/v1/sales/", payload, format="json")
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# auto_post + post action
# ---------------------------------------------------------------------------


def test_create_with_auto_post_marks_billed(
    api_client, user_factory, branch, product, uom, gst18, cash_mode, grn_in
):
    grn_in(product, 10)
    client = api_client(_super(user_factory))
    resp = client.post(
        "/api/v1/sales/",
        _draft_payload(branch, product, uom, gst18, cash_mode, auto_post=True),
        format="json",
    )
    assert resp.status_code == 201, resp.content
    assert resp.json()["status"] == SaleStatus.PAID


def test_post_action_endpoint(
    api_client, user_factory, branch, product, uom, gst18, cash_mode, grn_in
):
    grn_in(product, 10)
    client = api_client(_super(user_factory))
    create = client.post(
        "/api/v1/sales/",
        _draft_payload(branch, product, uom, gst18, cash_mode),
        format="json",
    )
    assert create.status_code == 201
    sale_id = create.json()["id"]
    resp = client.post(f"/api/v1/sales/{sale_id}/post/", {}, format="json")
    assert resp.status_code == 200, resp.content
    assert resp.json()["status"] == SaleStatus.PAID


def test_post_action_returns_envelope_on_unpaid_sale(
    api_client, user_factory, branch, product, uom, gst18, grn_in
):
    grn_in(product, 10)
    client = api_client(_super(user_factory))
    payload = {
        "origin": "POS",
        "branch": branch.id,
        "items": [
            {
                "product": product.id,
                "uom": uom.id,
                "tax": gst18.id,
                "qty": "1",
                "sale_price": "100",
            }
        ],
    }
    create = client.post("/api/v1/sales/", payload, format="json")
    sale_id = create.json()["id"]
    resp = client.post(f"/api/v1/sales/{sale_id}/post/", {}, format="json")
    assert resp.status_code >= 400
    assert "error" in resp.json()


# ---------------------------------------------------------------------------
# Cancel action — requires sales.cancel permission
# ---------------------------------------------------------------------------


def test_cancel_requires_permission(
    api_client, user_factory, branch, product, uom, gst18, cash_mode, grn_in
):
    grn_in(product, 10)
    admin = api_client(_super(user_factory))
    create = admin.post(
        "/api/v1/sales/",
        _draft_payload(branch, product, uom, gst18, cash_mode, auto_post=True),
        format="json",
    )
    sale_id = create.json()["id"]

    # Regular user without sales.cancel: gets 403 envelope.
    regular = user_factory(is_staff=True)
    client = api_client(regular)
    resp = client.post(f"/api/v1/sales/{sale_id}/cancel/", {}, format="json")
    # Could be 403 from HasAnyPermission (no sales.view) or from the
    # explicit sales.cancel check inside the view — both prove the guard.
    assert resp.status_code == 403


def test_cancel_succeeds_for_superuser(
    api_client, user_factory, branch, product, uom, gst18, cash_mode, grn_in
):
    grn_in(product, 10)
    client = api_client(_super(user_factory))
    create = client.post(
        "/api/v1/sales/",
        _draft_payload(branch, product, uom, gst18, cash_mode, auto_post=True),
        format="json",
    )
    sale_id = create.json()["id"]
    resp = client.post(
        f"/api/v1/sales/{sale_id}/cancel/",
        {"reason": "test cancel"},
        format="json",
    )
    assert resp.status_code == 200, resp.content
    assert resp.json()["status"] == SaleStatus.CANCELLED


# ---------------------------------------------------------------------------
# Add payment action
# ---------------------------------------------------------------------------


def test_add_payment_requires_payment_mode(
    api_client, user_factory, branch, product, uom, gst18, cash_mode
):
    client = api_client(_super(user_factory))
    create = client.post(
        "/api/v1/sales/",
        _draft_payload(branch, product, uom, gst18, cash_mode),
        format="json",
    )
    sale_id = create.json()["id"]
    resp = client.post(
        f"/api/v1/sales/{sale_id}/payments/",
        {"amount": "10"},
        format="json",
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "API-400"


def test_add_payment_unknown_mode_returns_400(
    api_client, user_factory, branch, product, uom, gst18, cash_mode
):
    client = api_client(_super(user_factory))
    create = client.post(
        "/api/v1/sales/",
        _draft_payload(branch, product, uom, gst18, cash_mode),
        format="json",
    )
    sale_id = create.json()["id"]
    resp = client.post(
        f"/api/v1/sales/{sale_id}/payments/",
        {"payment_mode": 9_999_999, "amount": "10"},
        format="json",
    )
    assert resp.status_code == 400


def test_add_payment_succeeds(api_client, user_factory, branch, product, uom, gst18, upi_mode):
    """Draft created without payments → add one via the action."""

    client = api_client(_super(user_factory))
    payload = {
        "origin": "POS",
        "branch": branch.id,
        "items": [
            {
                "product": product.id,
                "uom": uom.id,
                "tax": gst18.id,
                "qty": "1",
                "sale_price": "100",
            }
        ],
    }
    create = client.post("/api/v1/sales/", payload, format="json")
    sale_id = create.json()["id"]
    resp = client.post(
        f"/api/v1/sales/{sale_id}/payments/",
        {"payment_mode": upi_mode.id, "amount": "118", "ref_no": "TXN1"},
        format="json",
    )
    assert resp.status_code == 201, resp.content
    assert resp.json()["amount"] == "118.0000"


# ---------------------------------------------------------------------------
# Filters on list
# ---------------------------------------------------------------------------


def test_list_filters_by_branch_and_status(
    api_client, user_factory, branch, product, uom, gst18, cash_mode, grn_in
):
    grn_in(product, 10)
    client = api_client(_super(user_factory))
    # one BILLED sale
    client.post(
        "/api/v1/sales/",
        _draft_payload(branch, product, uom, gst18, cash_mode, auto_post=True),
        format="json",
    )
    # one DRAFT sale
    client.post(
        "/api/v1/sales/",
        _draft_payload(branch, product, uom, gst18, cash_mode),
        format="json",
    )
    paid = client.get(f"/api/v1/sales/?branch={branch.id}&status={SaleStatus.PAID}")
    drafted = client.get(f"/api/v1/sales/?branch={branch.id}&status={SaleStatus.DRAFT}")
    assert paid.status_code == 200
    assert drafted.status_code == 200
    paid_results = paid.json().get("results", paid.json())
    drafted_results = drafted.json().get("results", drafted.json())
    assert all(s["status"] == SaleStatus.PAID for s in paid_results)
    assert all(s["status"] == SaleStatus.DRAFT for s in drafted_results)
    assert all(s["branch"] == branch.id for s in paid_results)


# ---------------------------------------------------------------------------
# Discount viewset — CRUD smoke
# ---------------------------------------------------------------------------


def test_discount_create_and_list(api_client, user_factory):
    client = api_client(_super(user_factory))
    resp = client.post(
        "/api/v1/discounts/",
        {
            "code": "FLAT10",
            "name": "Flat 10",
            "scope": "LINE",
            "kind": "PERCENT",
            "value": "10.00",
            "is_active": True,
        },
        format="json",
    )
    assert resp.status_code == 201, resp.content
    listing = client.get("/api/v1/discounts/")
    assert listing.status_code == 200
    results = listing.json().get("results", listing.json())
    assert any(d["code"] == "FLAT10" for d in results)


# ---------------------------------------------------------------------------
# Detail retrieve
# ---------------------------------------------------------------------------


def test_retrieve_sale_serialises_items_and_payments(
    api_client, user_factory, branch, product, uom, gst18, cash_mode
):
    client = api_client(_super(user_factory))
    create = client.post(
        "/api/v1/sales/",
        _draft_payload(branch, product, uom, gst18, cash_mode),
        format="json",
    )
    sale_id = create.json()["id"]
    detail = client.get(f"/api/v1/sales/{sale_id}/")
    assert detail.status_code == 200
    body = detail.json()
    assert len(body["items"]) == 1
    assert len(body["payments"]) == 1
    assert Decimal(body["items"][0]["line_total"]) > Decimal("0")
