"""Shared catalog test fixtures."""

from __future__ import annotations

import pytest

from apps.master.models import Branch, Category, UnitOfMeasure


@pytest.fixture
def category(db):
    return Category.objects.create(code="CAT-GEN", name="General")


@pytest.fixture
def uom(db):
    return UnitOfMeasure.objects.create(code="EA", name="Each", symbol="ea", decimals=0)


@pytest.fixture
def branch(db):
    return Branch.objects.create(code="BR-MAIN", name="Main", type="STORE")


@pytest.fixture
def product(db, category, uom):
    from apps.catalog.models import Product, ProductStatus

    return Product.objects.create(
        code="P-001",
        sku="SKU-001",
        slug="p-001",
        name="Test Product",
        category=category,
        base_uom=uom,
        status=ProductStatus.ACTIVE,
    )


@pytest.fixture
def variant(db, product):
    from apps.catalog.models import ProductVariant

    return ProductVariant.objects.create(product=product, sku="SKU-001-V1", is_default=True)
