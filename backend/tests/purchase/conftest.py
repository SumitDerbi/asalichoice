"""Shared purchase test fixtures."""

from __future__ import annotations

from decimal import Decimal

import pytest

from apps.master.models import Branch, Category, UnitOfMeasure


@pytest.fixture
def branch(db):
    return Branch.objects.create(code="BR-PUR", name="Purchase Branch", type="STORE")


@pytest.fixture
def uom(db):
    return UnitOfMeasure.objects.create(code="EA", name="Each", symbol="ea", decimals=0)


@pytest.fixture
def category(db):
    return Category.objects.create(code="CAT-PUR", name="Purchase Cat")


@pytest.fixture
def product(db, category, uom):
    from apps.catalog.models import Product, ProductStatus

    return Product.objects.create(
        code="P-PUR-1",
        sku="SKU-PUR-1",
        slug="p-pur-1",
        name="Purchase Product",
        category=category,
        base_uom=uom,
        status=ProductStatus.ACTIVE,
    )


@pytest.fixture
def vendor(db):
    from apps.purchase.models import Vendor

    return Vendor.objects.create(code="V-001", name="Acme Suppliers")


@pytest.fixture
def po_factory(db, vendor, branch, product, uom):
    from apps.purchase.services import create_po

    counter = {"n": 0}

    def _make(*, qty=Decimal("10"), rate=Decimal("100"), po_no=None):
        counter["n"] += 1
        return create_po(
            vendor=vendor,
            branch=branch,
            po_no=po_no or f"PO-T-{counter['n']:04d}",
            items=[{"product": product, "uom": uom, "qty": qty, "rate": rate}],
        )

    return _make
