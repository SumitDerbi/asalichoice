"""Tests for ``apps.sales.services.discount_engine``."""

from __future__ import annotations

import datetime as _dt
from decimal import Decimal

import pytest

from apps.sales.exceptions import DiscountNotApplicable, DiscountRequiresApproval
from apps.sales.models import Discount, DiscountKind, DiscountScope, Sale, SaleItem, SaleOrigin
from apps.sales.services import discount_engine

pytestmark = pytest.mark.django_db


def _make_sale(branch, *, subtotal=Decimal("0")):
    sale = Sale(
        sale_no=f"D-{branch.pk}",
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


def test_line_percent_discount_applies(branch, product, uom):
    discount = Discount.objects.create(
        code="LINE10",
        name="10% line",
        scope=DiscountScope.LINE,
        kind=DiscountKind.PERCENT,
        value=Decimal("10"),
    )
    sale = _make_sale(branch, subtotal=Decimal("100"))
    item = _make_item(sale, product, uom, 1, 100)

    applied = discount_engine.apply_line(discount, sale=sale, items=[item])

    assert applied == Decimal("10")
    assert item.discount_amount == Decimal("10")


def test_line_flat_discount_capped_at_line(branch, product, uom):
    discount = Discount.objects.create(
        code="LINE999",
        name="Big flat",
        scope=DiscountScope.LINE,
        kind=DiscountKind.FLAT,
        value=Decimal("999"),
    )
    sale = _make_sale(branch, subtotal=Decimal("50"))
    item = _make_item(sale, product, uom, 1, 50)

    applied = discount_engine.apply_line(discount, sale=sale, items=[item])

    assert applied == Decimal("50")
    assert item.discount_amount == Decimal("50")


def test_header_percent_discount(branch, product, uom):
    discount = Discount.objects.create(
        code="HEAD20",
        name="20% header",
        scope=DiscountScope.HEADER,
        kind=DiscountKind.PERCENT,
        value=Decimal("20"),
    )
    sale = _make_sale(branch, subtotal=Decimal("500"))
    item = _make_item(sale, product, uom, 1, 500)

    applied = discount_engine.apply_header(discount, sale=sale, items=[item])

    assert applied == Decimal("100")
    assert sale.discount_total == Decimal("100")


def test_discount_requires_approval_blocks_without_flag(branch, product, uom):
    discount = Discount.objects.create(
        code="VIP",
        name="VIP",
        scope=DiscountScope.LINE,
        kind=DiscountKind.PERCENT,
        value=Decimal("50"),
        requires_approval=True,
    )
    sale = _make_sale(branch, subtotal=Decimal("100"))
    item = _make_item(sale, product, uom, 1, 100)

    with pytest.raises(DiscountRequiresApproval):
        discount_engine.apply_line(discount, sale=sale, items=[item])

    # With ``approved=True`` it goes through
    applied = discount_engine.apply_line(discount, sale=sale, items=[item], approved=True)
    assert applied == Decimal("50")


def test_inactive_discount_not_applicable(branch, product, uom):
    discount = Discount.objects.create(
        code="OLD",
        name="Old",
        scope=DiscountScope.LINE,
        kind=DiscountKind.PERCENT,
        value=Decimal("10"),
        is_active=False,
    )
    sale = _make_sale(branch, subtotal=Decimal("100"))
    item = _make_item(sale, product, uom, 1, 100)

    with pytest.raises(DiscountNotApplicable):
        discount_engine.apply_line(discount, sale=sale, items=[item])


def test_condition_min_subtotal_blocks(branch, product, uom):
    discount = Discount.objects.create(
        code="MIN500",
        name="Min 500",
        scope=DiscountScope.HEADER,
        kind=DiscountKind.FLAT,
        value=Decimal("50"),
        condition_json={"min_subtotal": "500"},
    )
    sale = _make_sale(branch, subtotal=Decimal("100"))
    item = _make_item(sale, product, uom, 1, 100)

    with pytest.raises(DiscountNotApplicable):
        discount_engine.apply_header(discount, sale=sale, items=[item])


def test_condition_valid_from_to_window(branch, product, uom):
    discount = Discount.objects.create(
        code="WINDOW",
        name="Window",
        scope=DiscountScope.HEADER,
        kind=DiscountKind.FLAT,
        value=Decimal("10"),
        condition_json={"valid_from": "2099-01-01"},
    )
    sale = _make_sale(branch, subtotal=Decimal("100"))
    item = _make_item(sale, product, uom, 1, 100)

    # Today is before valid_from → not applicable.
    with pytest.raises(DiscountNotApplicable):
        discount_engine.apply_header(discount, sale=sale, items=[item])

    # Travel forward, the discount is applicable.
    applied = discount_engine.apply_header(
        discount, sale=sale, items=[item], today=_dt.date(2099, 6, 1)
    )
    assert applied == Decimal("10")


def test_header_discount_rejected_for_line_scope(branch, product, uom):
    discount = Discount.objects.create(
        code="LINEONLY",
        name="Line",
        scope=DiscountScope.LINE,
        kind=DiscountKind.PERCENT,
        value=Decimal("10"),
    )
    sale = _make_sale(branch, subtotal=Decimal("100"))
    item = _make_item(sale, product, uom, 1, 100)
    with pytest.raises(DiscountNotApplicable):
        discount_engine.apply_header(discount, sale=sale, items=[item])
