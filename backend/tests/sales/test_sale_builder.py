"""Tests for ``apps.sales.services.sale_builder``."""

from __future__ import annotations

from decimal import Decimal

import pytest

from apps.sales.models import Sale, SaleItem, SaleOrigin, TaxMode
from apps.sales.services import sale_builder

pytestmark = pytest.mark.django_db


def _make_sale(branch, tax_mode=TaxMode.EXCLUSIVE):
    return Sale(
        sale_no=f"T-{branch.pk}-{tax_mode}",
        origin=SaleOrigin.POS,
        branch=branch,
        tax_mode=tax_mode,
    )


def _make_item(sale, *, product, uom, qty, sale_price, tax=None, discount=0):
    return SaleItem(
        sale=sale,
        product=product,
        uom=uom,
        tax=tax,
        qty=Decimal(str(qty)),
        sale_price=Decimal(str(sale_price)),
        discount_amount=Decimal(str(discount)),
    )


def test_recompute_exclusive_single_line(branch, product, uom, gst18):
    sale = _make_sale(branch)
    item = _make_item(sale, product=product, uom=uom, qty=2, sale_price="100", tax=gst18)

    sale_builder.recompute(sale, [item])

    assert item.line_subtotal == Decimal("200.0000")
    assert item.line_total == Decimal("236.0000")
    assert sale.subtotal == Decimal("200.0000")
    assert sale.tax_total == Decimal("36.0000")
    assert sale.grand_total == Decimal("236.0000")
    assert sale.totals_json["grand_total"] == "236.0000"


def test_recompute_inclusive_single_line(branch, product, uom, gst18):
    sale = _make_sale(branch, tax_mode=TaxMode.INCLUSIVE)
    item = _make_item(sale, product=product, uom=uom, qty=1, sale_price="118", tax=gst18)

    sale_builder.recompute(sale, [item])

    # Inclusive: grand_total equals subtotal minus discount; the
    # tax_breakup_json carries the unwrapped base.
    assert sale.grand_total == Decimal("118.0000")
    assert Decimal(item.tax_breakup_json["base"]) == Decimal("100.0000")


def test_recompute_with_line_discount(branch, product, uom, gst18):
    sale = _make_sale(branch)
    item = _make_item(
        sale,
        product=product,
        uom=uom,
        qty=1,
        sale_price="100",
        tax=gst18,
        discount=10,
    )

    sale_builder.recompute(sale, [item])

    # Line subtotal drops to 90; tax is 18% of 90 = 16.20
    assert item.line_subtotal == Decimal("90.0000")
    assert sale.tax_total == Decimal("16.2000")
    assert sale.grand_total == Decimal("106.2000")


def test_recompute_multiple_lines_aggregates(branch, product, product_b, uom, gst18):
    sale = _make_sale(branch)
    items = [
        _make_item(sale, product=product, uom=uom, qty=1, sale_price="100", tax=gst18),
        _make_item(sale, product=product_b, uom=uom, qty=2, sale_price="50", tax=None),
    ]

    sale_builder.recompute(sale, items)

    assert sale.subtotal == Decimal("200.0000")  # 100 + 100
    assert sale.tax_total == Decimal("18.0000")  # only first line taxed
    assert sale.grand_total == Decimal("218.0000")
