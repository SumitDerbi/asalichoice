"""API smoke tests for the M03 catalog endpoints."""

from __future__ import annotations

import io
from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.catalog.models import Bundle, ProductStatus

pytestmark = pytest.mark.django_db


def _super(user_factory):
    return user_factory(is_staff=True, is_superuser=True)


# ---------------------------------------------------------------------------
# AuthZ
# ---------------------------------------------------------------------------


def test_anonymous_cannot_list_products(api_client):
    resp = api_client().get("/api/v1/catalog/products/")
    assert resp.status_code == 401


def test_super_can_list_products(api_client, user_factory):
    resp = api_client(_super(user_factory)).get("/api/v1/catalog/products/")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Product CRUD
# ---------------------------------------------------------------------------


def test_create_product(api_client, user_factory, category, uom):
    client = api_client(_super(user_factory))
    resp = client.post(
        "/api/v1/catalog/products/",
        {
            "code": "API-1",
            "sku": "API-SKU-1",
            "slug": "api-1",
            "name": "API Product",
            "category": category.id,
            "base_uom": uom.id,
            "status": ProductStatus.ACTIVE,
        },
        format="json",
    )
    assert resp.status_code == 201, resp.content


def test_search_product_by_sku(api_client, user_factory, product):
    client = api_client(_super(user_factory))
    resp = client.get(f"/api/v1/catalog/products/?q={product.sku}")
    assert resp.status_code == 200
    body = resp.json()
    results = body.get("results", body)
    assert len(results) >= 1


def test_archive_action(api_client, user_factory, product):
    client = api_client(_super(user_factory))
    resp = client.post(f"/api/v1/catalog/products/{product.id}/archive/")
    assert resp.status_code == 200, resp.content
    product.refresh_from_db()
    assert product.status == ProductStatus.ARCHIVED


# ---------------------------------------------------------------------------
# Pricing endpoints
# ---------------------------------------------------------------------------


def test_create_price_band(api_client, user_factory, product, branch):
    client = api_client(_super(user_factory))
    resp = client.post(
        "/api/v1/catalog/prices/",
        {
            "product": product.id,
            "branch": branch.id,
            "mrp": "100.00",
            "sale_price": "90.00",
            "valid_from": (timezone.now() - timedelta(days=1)).isoformat(),
        },
        format="json",
    )
    assert resp.status_code == 201, resp.content


def test_product_price_endpoint(api_client, user_factory, product, branch):
    from apps.catalog.services import set_price

    set_price(
        product=product,
        branch_id=branch.id,
        mrp=Decimal("100"),
        sale_price=Decimal("85"),
        valid_from=timezone.now() - timedelta(days=1),
    )
    client = api_client(_super(user_factory))
    resp = client.get(f"/api/v1/catalog/products/{product.id}/price/?branch={branch.id}")
    assert resp.status_code == 200, resp.content
    body = resp.json()
    assert body["sale_price"] == "85.00"


def test_product_price_endpoint_missing_branch_returns_envelope(api_client, user_factory, product):
    client = api_client(_super(user_factory))
    resp = client.get(f"/api/v1/catalog/products/{product.id}/price/")
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "API-400"


def test_price_serializer_rejects_both_targets(api_client, user_factory, product, variant, branch):
    client = api_client(_super(user_factory))
    resp = client.post(
        "/api/v1/catalog/prices/",
        {
            "product": product.id,
            "variant": variant.id,
            "branch": branch.id,
            "mrp": "10",
            "sale_price": "9",
            "valid_from": timezone.now().isoformat(),
        },
        format="json",
    )
    assert resp.status_code == 400, resp.content


# ---------------------------------------------------------------------------
# Bundle endpoint
# ---------------------------------------------------------------------------


def test_bundle_fixed_requires_price(api_client, user_factory):
    client = api_client(_super(user_factory))
    resp = client.post(
        "/api/v1/catalog/bundles/",
        {"code": "B1", "name": "B1", "kind": "COMBO", "price_policy": "FIXED"},
        format="json",
    )
    assert resp.status_code == 400, resp.content


def test_bundle_sum_policy_no_price(api_client, user_factory):
    client = api_client(_super(user_factory))
    resp = client.post(
        "/api/v1/catalog/bundles/",
        {"code": "B-SUM", "name": "Sum Bundle", "kind": "COMBO", "price_policy": "SUM"},
        format="json",
    )
    assert resp.status_code == 201, resp.content
    assert Bundle.objects.filter(code="B-SUM").exists()


# ---------------------------------------------------------------------------
# Barcode resolve
# ---------------------------------------------------------------------------


def test_barcode_resolve(api_client, user_factory, product):
    from apps.catalog.models import Barcode

    Barcode.objects.create(value="123456789012", product=product, type="EAN13")
    client = api_client(_super(user_factory))
    resp = client.get("/api/v1/catalog/barcodes/resolve/?value=123456789012")
    assert resp.status_code == 200
    assert resp.json()["product"] == product.id


def test_barcode_resolve_unknown_returns_envelope(api_client, user_factory):
    client = api_client(_super(user_factory))
    resp = client.get("/api/v1/catalog/barcodes/resolve/?value=NOPE")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "CAT-040"


# ---------------------------------------------------------------------------
# CSV import endpoint
# ---------------------------------------------------------------------------


def test_import_endpoint_dry_run(api_client, user_factory, category, uom):
    client = api_client(_super(user_factory))
    csv_text = (
        "code,sku,name,slug,category_code,brand_code,hsn_code,tax_code,"
        "base_uom_code,status,description\n"
        f"E-1,E-S-1,E1,e-1,{category.code},,,,{uom.code},ACTIVE,\n"
    )
    upload = io.BytesIO(csv_text.encode("utf-8"))
    upload.name = "products.csv"
    resp = client.post(
        "/api/v1/catalog/import/",
        {"file": upload, "dry_run": "true"},
        format="multipart",
    )
    assert resp.status_code == 200, resp.content
    body = resp.json()
    assert body["committed"] is False
    assert body["valid"] == 1
