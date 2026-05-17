"""Service-layer tests for catalog pricing + import + product CRUD."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.catalog.exceptions import (
    PriceNotFound,
    PriceTargetInvalid,
    PriceWindowInvalid,
    ProductArchived,
    ProductSKUDuplicate,
)
from apps.catalog.models import Product, ProductPrice, ProductStatus
from apps.catalog.services import (
    archive_product,
    bulk_lookup,
    create_product,
    get_effective_price,
    import_products_csv,
    set_price,
    update_product,
)

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# Product CRUD service
# ---------------------------------------------------------------------------


def test_create_product_happy(category, uom):
    product = create_product(
        code="P-A", sku="SKU-A", slug="p-a", name="A", category=category, base_uom=uom
    )
    assert product.pk
    assert product.status == ProductStatus.DRAFT


def test_create_product_duplicate_sku_raises(product, category, uom):
    with pytest.raises(ProductSKUDuplicate):
        create_product(
            code="P-DIFF",
            sku=product.sku,
            slug="p-diff",
            name="Dup",
            category=category,
            base_uom=uom,
        )


def test_update_archived_blocks_writes(product):
    archive_product(product)
    with pytest.raises(ProductArchived):
        update_product(product, name="New")


def test_archive_then_unarchive(product):
    archive_product(product)
    update_product(product, status=ProductStatus.ACTIVE)
    product.refresh_from_db()
    assert product.status == ProductStatus.ACTIVE


# ---------------------------------------------------------------------------
# Pricing service
# ---------------------------------------------------------------------------


def test_set_price_xor_target_required(product, branch):
    with pytest.raises(PriceTargetInvalid):
        set_price(branch_id=branch.id, mrp=Decimal("10"), sale_price=Decimal("9"))


def test_set_price_invalid_window(product, branch):
    now = timezone.now()
    with pytest.raises(PriceWindowInvalid):
        set_price(
            product=product,
            branch_id=branch.id,
            mrp=Decimal("10"),
            sale_price=Decimal("9"),
            valid_from=now,
            valid_to=now - timedelta(hours=1),
        )


def test_effective_price_picks_most_recent(product, branch):
    now = timezone.now()
    set_price(
        product=product,
        branch_id=branch.id,
        mrp=Decimal("100"),
        sale_price=Decimal("90"),
        valid_from=now - timedelta(days=10),
    )
    set_price(
        product=product,
        branch_id=branch.id,
        mrp=Decimal("110"),
        sale_price=Decimal("95"),
        valid_from=now - timedelta(days=1),
    )
    band = get_effective_price(product, branch.id, use_cache=False)
    assert band.mrp == Decimal("110.00")
    assert band.sale_price == Decimal("95.00")


def test_effective_price_respects_valid_to_window(product, branch):
    now = timezone.now()
    set_price(
        product=product,
        branch_id=branch.id,
        mrp=Decimal("100"),
        sale_price=Decimal("80"),
        valid_from=now - timedelta(days=10),
        valid_to=now - timedelta(days=1),  # expired
    )
    with pytest.raises(PriceNotFound):
        get_effective_price(product, branch.id, use_cache=False)


def test_effective_price_for_variant(variant, branch):
    set_price(
        variant=variant,
        branch_id=branch.id,
        mrp=Decimal("50"),
        sale_price=Decimal("45"),
        valid_from=timezone.now() - timedelta(days=1),
    )
    band = get_effective_price(variant, branch.id, use_cache=False)
    assert band.sale_price == Decimal("45.00")


def test_bulk_lookup_returns_keys(product, variant, branch):
    now = timezone.now()
    set_price(
        product=product,
        branch_id=branch.id,
        mrp=Decimal("100"),
        sale_price=Decimal("90"),
        valid_from=now - timedelta(days=1),
    )
    set_price(
        variant=variant,
        branch_id=branch.id,
        mrp=Decimal("50"),
        sale_price=Decimal("45"),
        valid_from=now - timedelta(days=1),
    )
    result = bulk_lookup([(product, branch.id), (variant, branch.id)])
    assert ("p", product.id, branch.id) in result
    assert ("v", variant.id, branch.id) in result


def test_xor_constraint_enforced_at_db(product, variant, branch):
    """A ProductPrice row must NOT set both product and variant."""

    from django.db import IntegrityError, transaction

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            ProductPrice.objects.create(
                product=product,
                variant=variant,
                branch_id=branch.id,
                mrp=Decimal("1"),
                sale_price=Decimal("1"),
                valid_from=timezone.now(),
            )


# ---------------------------------------------------------------------------
# CSV import service
# ---------------------------------------------------------------------------


def _csv(rows: list[str]) -> str:
    header = (
        "code,sku,name,slug,category_code,brand_code,hsn_code,tax_code,"
        "base_uom_code,status,description"
    )
    return "\n".join([header, *rows])


def test_import_dry_run_reports_errors(category, uom):
    text = _csv(
        [
            f"IMP-1,IMP-SKU-1,Imp One,imp-1,{category.code},,,,{uom.code},ACTIVE,",
            ",IMP-SKU-2,Imp Two,imp-2,UNKNOWN,,,,EA,ACTIVE,",
            f"IMP-3,IMP-SKU-3,Imp Three,imp-3,UNKNOWN,,,,{uom.code},ACTIVE,",
        ]
    )
    result = import_products_csv(text, dry_run=True)
    assert result["total"] == 3
    assert result["valid"] == 1
    assert result["committed"] is False
    assert len(result["errors"]) == 2
    assert Product.objects.count() == 0


def test_import_commit_persists_valid_rows(category, uom):
    text = _csv(
        [
            f"IMP-A,IMP-SKU-A,A,imp-a,{category.code},,,,{uom.code},ACTIVE,",
            f"IMP-B,IMP-SKU-B,B,imp-b,{category.code},,,,{uom.code},ACTIVE,",
        ]
    )
    result = import_products_csv(text, dry_run=False)
    assert result["created"] == 2
    assert result["committed"] is True
    assert Product.objects.filter(code__in=("IMP-A", "IMP-B")).count() == 2
