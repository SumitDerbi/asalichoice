"""Shared M11 Sales test fixtures."""

from __future__ import annotations

from decimal import Decimal

import pytest


@pytest.fixture
def branch(db):
    from apps.master.models import Branch

    return Branch.objects.create(code="BR-SAL", name="Sales Branch", type="STORE")


@pytest.fixture
def uom(db):
    from apps.master.models import UnitOfMeasure

    return UnitOfMeasure.objects.create(code="EA", name="Each", symbol="ea", decimals=0)


@pytest.fixture
def category(db):
    from apps.master.models import Category

    return Category.objects.create(code="CAT-SAL", name="Sales Cat")


@pytest.fixture
def product(db, category, uom):
    from apps.catalog.models import Product, ProductStatus

    return Product.objects.create(
        code="P-SAL-1",
        sku="SKU-SAL-1",
        slug="p-sal-1",
        name="Sales Product",
        category=category,
        base_uom=uom,
        status=ProductStatus.ACTIVE,
    )


@pytest.fixture
def product_b(db, category, uom):
    from apps.catalog.models import Product, ProductStatus

    return Product.objects.create(
        code="P-SAL-2",
        sku="SKU-SAL-2",
        slug="p-sal-2",
        name="Sales Product B",
        category=category,
        base_uom=uom,
        status=ProductStatus.ACTIVE,
    )


@pytest.fixture
def gst18(db):
    """An EXCLUSIVE 18% GST split CGST 9 + SGST 9."""

    from apps.master.models import Tax, TaxComponentType

    tax = Tax.objects.create(
        code="GST18",
        name="GST 18%",
        rate_total=Decimal("18.000"),
        components_json=[
            {"type": TaxComponentType.CGST.value, "rate": "9.000"},
            {"type": TaxComponentType.SGST.value, "rate": "9.000"},
        ],
    )
    return tax


@pytest.fixture
def cash_mode(db, branch):
    from apps.master.models import PaymentMode

    mode = PaymentMode.objects.create(code="CASH", name="Cash", type="CASH")
    mode.branches.add(branch)
    return mode


@pytest.fixture
def upi_mode(db, branch):
    from apps.master.models import PaymentMode

    mode = PaymentMode.objects.create(
        code="UPI",
        name="UPI",
        type="UPI",
        is_online=True,
    )
    mode.branches.add(branch)
    return mode


@pytest.fixture
def grn_in(db, branch):
    """Helper: post inbound stock for a product so sale tests have headroom."""

    from apps.inventory.models import InventoryRefType
    from apps.inventory.services import ledger_service

    def _post(product, qty):
        ledger_service.post(
            ref_type=InventoryRefType.GRN,
            ref_id="seed",
            items=[{"product": product, "qty_change": Decimal(str(qty))}],
            branch=branch,
        )

    return _post


@pytest.fixture
def qty():
    return lambda value: Decimal(str(value))
