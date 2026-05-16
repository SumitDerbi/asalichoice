"""API smoke tests for M01 master management endpoints."""

from __future__ import annotations

from decimal import Decimal

import pytest

from apps.master.models import (
    Brand,
    Category,
    Country,
    Department,
    HSNCode,
    PaymentMode,
    PaymentModeType,
    State,
    Tax,
    UnitOfMeasure,
)

pytestmark = pytest.mark.django_db


def _super(user_factory):
    return user_factory(is_staff=True, is_superuser=True)


# ---------------------------------------------------------------------------
# AuthZ
# ---------------------------------------------------------------------------


def test_anonymous_cannot_list_branches(api_client):
    resp = api_client().get("/api/v1/master/branches/")
    assert resp.status_code == 401


def test_super_can_list_branches(api_client, user_factory):
    resp = api_client(_super(user_factory)).get("/api/v1/master/branches/")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# CRUD smoke
# ---------------------------------------------------------------------------


def test_create_department(api_client, user_factory):
    client = api_client(_super(user_factory))
    resp = client.post(
        "/api/v1/master/departments/",
        {"code": "SALES", "name": "Sales"},
        format="json",
    )
    assert resp.status_code == 201, resp.content
    assert Department.objects.filter(code="SALES").exists()


def test_create_brand(api_client, user_factory):
    client = api_client(_super(user_factory))
    resp = client.post(
        "/api/v1/master/brands/",
        {"code": "ACME", "name": "Acme"},
        format="json",
    )
    assert resp.status_code == 201, resp.content
    assert Brand.objects.filter(code="ACME").exists()


def test_create_uom(api_client, user_factory):
    client = api_client(_super(user_factory))
    resp = client.post(
        "/api/v1/master/uom/",
        {"code": "DOZEN", "name": "Dozen", "symbol": "dz", "decimals": 0},
        format="json",
    )
    assert resp.status_code == 201, resp.content
    assert UnitOfMeasure.objects.filter(code="DOZEN").exists()


# ---------------------------------------------------------------------------
# Tax breakup action
# ---------------------------------------------------------------------------


def test_tax_breakup_endpoint(api_client, user_factory):
    tax = Tax.objects.create(
        code="GST18T",
        name="GST 18%",
        rate_total=Decimal("18"),
        components_json=[
            {"type": "CGST", "rate": "9"},
            {"type": "SGST", "rate": "9"},
        ],
    )
    client = api_client(_super(user_factory))
    resp = client.get(f"/api/v1/master/taxes/{tax.id}/breakup/?amount=100")
    assert resp.status_code == 200, resp.content
    body = resp.json()
    assert body["base"] == "100.00"
    assert body["tax_total"] == "18.00"
    assert body["grand_total"] == "118.00"


def test_tax_breakup_missing_amount_returns_400(api_client, user_factory):
    tax = Tax.objects.create(
        code="GST5T",
        name="GST 5%",
        rate_total=Decimal("5"),
        components_json=[
            {"type": "CGST", "rate": "2.5"},
            {"type": "SGST", "rate": "2.5"},
        ],
    )
    client = api_client(_super(user_factory))
    resp = client.get(f"/api/v1/master/taxes/{tax.id}/breakup/")
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Zone resolve action
# ---------------------------------------------------------------------------


def test_zone_resolve_not_found(api_client, user_factory):
    client = api_client(_super(user_factory))
    resp = client.get("/api/v1/master/zones/resolve/?pincode=999999")
    assert resp.status_code == 404
    body = resp.json()
    assert body.get("error", {}).get("code") == "MST-030"


# ---------------------------------------------------------------------------
# Geo read endpoints (data exists from seed_master in test DB? — create fresh)
# ---------------------------------------------------------------------------


def test_states_list(api_client, user_factory):
    country = Country.objects.create(iso2="IN", iso3="IND", name="India")
    State.objects.create(country=country, code="MH", name="Maharashtra", gst_state_code="27")
    client = api_client(_super(user_factory))
    resp = client.get("/api/v1/master/states/")
    assert resp.status_code == 200
    body = resp.json()
    results = body.get("results", body)
    assert any(s["code"] == "MH" for s in results)


# ---------------------------------------------------------------------------
# Category depth guard via API
# ---------------------------------------------------------------------------


def test_category_depth_violation_via_api(api_client, user_factory):
    client = api_client(_super(user_factory))
    parent = None
    # Pre-create 4 levels directly to make the 5th create violate.
    from apps.master.services import CATEGORY_MAX_DEPTH

    for i in range(CATEGORY_MAX_DEPTH):
        parent = Category.objects.create(code=f"L{i}", name=f"L{i}", parent=parent)
    resp = client.post(
        "/api/v1/master/categories/",
        {"code": "TOODEEP", "name": "Too Deep", "parent": parent.id},
        format="json",
    )
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Payment mode + HSN simple create
# ---------------------------------------------------------------------------


def test_create_payment_mode(api_client, user_factory):
    client = api_client(_super(user_factory))
    resp = client.post(
        "/api/v1/master/payment-modes/",
        {
            "code": "WALLET",
            "name": "Wallet",
            "type": PaymentModeType.WALLET,
            "is_online": True,
        },
        format="json",
    )
    assert resp.status_code == 201, resp.content
    assert PaymentMode.objects.filter(code="WALLET").exists()


def test_create_hsn(api_client, user_factory):
    client = api_client(_super(user_factory))
    resp = client.post(
        "/api/v1/master/hsn/",
        {"code": "1006", "description": "Rice"},
        format="json",
    )
    assert resp.status_code == 201, resp.content
    assert HSNCode.objects.filter(code="1006").exists()
