"""Shared M05 inventory test fixtures."""

from __future__ import annotations

from decimal import Decimal

import pytest


@pytest.fixture
def branch(db):
    from apps.master.models import Branch

    return Branch.objects.create(code="BR-INV", name="Inventory Branch", type="STORE")


@pytest.fixture
def other_branch(db):
    from apps.master.models import Branch

    return Branch.objects.create(code="BR-INV2", name="Inventory Branch 2", type="STORE")


@pytest.fixture
def uom(db):
    from apps.master.models import UnitOfMeasure

    return UnitOfMeasure.objects.create(code="EA", name="Each", symbol="ea", decimals=0)


@pytest.fixture
def category(db):
    from apps.master.models import Category

    return Category.objects.create(code="CAT-INV", name="Inventory Cat")


@pytest.fixture
def product(db, category, uom):
    from apps.catalog.models import Product, ProductStatus

    return Product.objects.create(
        code="P-INV-1",
        sku="SKU-INV-1",
        slug="p-inv-1",
        name="Inventory Product",
        category=category,
        base_uom=uom,
        status=ProductStatus.ACTIVE,
    )


@pytest.fixture
def product_b(db, category, uom):
    from apps.catalog.models import Product, ProductStatus

    return Product.objects.create(
        code="P-INV-2",
        sku="SKU-INV-2",
        slug="p-inv-2",
        name="Inventory Product B",
        category=category,
        base_uom=uom,
        status=ProductStatus.ACTIVE,
    )


@pytest.fixture
def qty():
    """Decimal helper to keep test bodies terse."""

    return lambda value: Decimal(str(value))
