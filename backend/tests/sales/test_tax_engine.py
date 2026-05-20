"""Tests for ``apps.sales.services.tax_engine``."""

from __future__ import annotations

from decimal import Decimal

import pytest

from apps.sales.services import tax_engine

pytestmark = pytest.mark.django_db


def test_no_tax_returns_passthrough():
    breakup = tax_engine.compute_line(line_subtotal=Decimal("100"), tax=None, tax_mode="EXCLUSIVE")
    assert breakup["tax_total"] == "0"
    assert breakup["components"] == []


def test_exclusive_tax_18_percent(gst18):
    breakup = tax_engine.compute_line(line_subtotal=Decimal("100"), tax=gst18, tax_mode="EXCLUSIVE")
    assert Decimal(breakup["tax_total"]) == Decimal("18.0000")
    assert Decimal(breakup["grand_total"]) == Decimal("118.0000")
    types = [comp["type"] for comp in breakup["components"]]
    assert types == ["CGST", "SGST"]


def test_inclusive_tax_18_percent(gst18):
    """If 118 already contains 18%, base should be 100."""

    breakup = tax_engine.compute_line(line_subtotal=Decimal("118"), tax=gst18, tax_mode="INCLUSIVE")
    assert Decimal(breakup["base"]) == Decimal("100.0000")
    assert Decimal(breakup["tax_total"]) == Decimal("18.0000")


def test_zero_subtotal_short_circuits(gst18):
    breakup = tax_engine.compute_line(line_subtotal=Decimal("0"), tax=gst18, tax_mode="EXCLUSIVE")
    assert breakup["tax_total"] == "0"
