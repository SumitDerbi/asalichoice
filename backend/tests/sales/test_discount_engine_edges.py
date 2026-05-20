"""Edge-case tests added to lift M11 coverage to the plan's ≥90% gate.

These exercise discount-engine branches not covered by the happy-path
suite plus a tiny import smoke test for the permission registry.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from apps.sales.exceptions import DiscountNotApplicable
from apps.sales.models import Discount, DiscountKind, DiscountScope, Sale, SaleItem, SaleOrigin
from apps.sales.permissions import SALES_PERMISSIONS
from apps.sales.services import discount_engine

pytestmark = pytest.mark.django_db


def _make_sale(branch, *, subtotal=Decimal("0")):
    sale = Sale(
        sale_no=f"DX-{branch.pk}",
        origin=SaleOrigin.POS,
        branch=branch,
    )
    sale.subtotal = subtotal
    return sale


def _make_item(sale, product, uom, qty, price, *, discount=Decimal("0")):
    return SaleItem(
        sale=sale,
        product=product,
        uom=uom,
        qty=Decimal(str(qty)),
        sale_price=Decimal(str(price)),
        discount_amount=discount,
    )


def test_permission_registry_well_formed():
    codes = {row[0] for row in SALES_PERMISSIONS}
    assert {"sales.view", "sales.manage", "sales.cancel"} <= codes
    for code, label, help_text in SALES_PERMISSIONS:
        assert code.startswith("sales.")
        assert label and help_text


def test_apply_line_rejects_header_scope_discount(branch, product, uom):
    discount = Discount.objects.create(
        code="HDRONLY",
        name="Header only",
        scope=DiscountScope.HEADER,
        kind=DiscountKind.PERCENT,
        value=Decimal("10"),
    )
    sale = _make_sale(branch, subtotal=Decimal("100"))
    item = _make_item(sale, product, uom, 1, 100)
    with pytest.raises(DiscountNotApplicable):
        discount_engine.apply_line(discount, sale=sale, items=[item])


def test_valid_to_in_the_past_blocks(branch, product, uom):
    discount = Discount.objects.create(
        code="EXPIRED",
        name="Expired",
        scope=DiscountScope.HEADER,
        kind=DiscountKind.FLAT,
        value=Decimal("10"),
        condition_json={"valid_to": "2000-01-01"},
    )
    sale = _make_sale(branch, subtotal=Decimal("100"))
    item = _make_item(sale, product, uom, 1, 100)
    with pytest.raises(DiscountNotApplicable):
        discount_engine.apply_header(discount, sale=sale, items=[item])


def test_malformed_date_string_is_ignored(branch, product, uom):
    """``_parse_iso_date`` swallows bad input → discount stays applicable."""

    discount = Discount.objects.create(
        code="BADDATE",
        name="Bad date",
        scope=DiscountScope.HEADER,
        kind=DiscountKind.FLAT,
        value=Decimal("5"),
        condition_json={"valid_from": "not-a-date", "valid_to": "also-bad"},
    )
    sale = _make_sale(branch, subtotal=Decimal("100"))
    item = _make_item(sale, product, uom, 1, 100)
    applied = discount_engine.apply_header(discount, sale=sale, items=[item])
    assert applied == Decimal("5")


def test_products_filter_with_no_match_rejects(branch, product, uom):
    """A LINE discount limited to product=99999 should be inapplicable."""

    discount = Discount.objects.create(
        code="WRONGSKU",
        name="Wrong sku",
        scope=DiscountScope.LINE,
        kind=DiscountKind.PERCENT,
        value=Decimal("10"),
        condition_json={"applies_to_products": [99_999]},
    )
    sale = _make_sale(branch, subtotal=Decimal("100"))
    item = _make_item(sale, product, uom, 1, 100)
    with pytest.raises(DiscountNotApplicable):
        discount_engine.apply_line(discount, sale=sale, items=[item])


def test_products_filter_skips_non_matching_lines(branch, product, product_b, uom):
    """When two lines exist and the filter only matches one, only that
    line's ``discount_amount`` is mutated."""

    discount = Discount.objects.create(
        code="ONLYA",
        name="Only A",
        scope=DiscountScope.LINE,
        kind=DiscountKind.PERCENT,
        value=Decimal("10"),
        condition_json={"applies_to_products": [product.pk]},
    )
    sale = _make_sale(branch, subtotal=Decimal("200"))
    item_a = _make_item(sale, product, uom, 1, 100)
    item_b = _make_item(sale, product_b, uom, 1, 100)
    applied = discount_engine.apply_line(discount, sale=sale, items=[item_a, item_b])
    assert applied == Decimal("10")
    assert item_a.discount_amount == Decimal("10")
    assert item_b.discount_amount == Decimal("0")


def test_apply_line_skips_already_zero_lines(branch, product, uom):
    """A line whose discount already equals the subtotal contributes 0."""

    discount = Discount.objects.create(
        code="NOOP",
        name="No-op",
        scope=DiscountScope.LINE,
        kind=DiscountKind.PERCENT,
        value=Decimal("50"),
    )
    sale = _make_sale(branch, subtotal=Decimal("100"))
    # qty 1 x price 100 = 100, with a pre-existing discount of 100 ->
    # line_base = 0, so the engine should skip without mutating.
    item = _make_item(sale, product, uom, 1, 100, discount=Decimal("100"))
    applied = discount_engine.apply_line(discount, sale=sale, items=[item])
    assert applied == Decimal("0")
    assert item.discount_amount == Decimal("100")


def test_apply_header_returns_zero_when_no_base_remains(branch, product, uom):
    """When subtotal == discount_total already, header returns 0."""

    discount = Discount.objects.create(
        code="HDR5",
        name="Header 5",
        scope=DiscountScope.HEADER,
        kind=DiscountKind.PERCENT,
        value=Decimal("5"),
    )
    sale = _make_sale(branch, subtotal=Decimal("100"))
    sale.discount_total = Decimal("100")
    item = _make_item(sale, product, uom, 1, 100)
    applied = discount_engine.apply_header(discount, sale=sale, items=[item])
    assert applied == Decimal("0")
    assert sale.discount_total == Decimal("100")
