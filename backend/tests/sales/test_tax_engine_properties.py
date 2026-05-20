"""Property-style coverage of the sales tax engine.

Hypothesis is not in the project's minimal dev dependency set, so we
use pytest parametrisation across a wide grid of (rate, amount) pairs
to assert the algebraic properties the tax engine must hold:

* ``base + tax_total == grand_total`` (no rounding leaks bigger than 1 paisa)
* inclusive of ``X`` at rate ``r`` returns base ``X / (1 + r)`` within 1 paisa
* exclusive of ``X`` at rate ``r`` returns tax ``X * r`` within 1 paisa
* component amounts sum to ``tax_total``
"""

from __future__ import annotations

from decimal import Decimal
from itertools import product

import pytest

from apps.master.models import Tax, TaxComponentType
from apps.sales.services import tax_engine

pytestmark = pytest.mark.django_db


# Indian GST slabs that appear in the seed data plus a few edge rates.
_SLABS: tuple[tuple[str, Decimal], ...] = (
    ("GST0", Decimal("0.000")),
    ("GST5", Decimal("5.000")),
    ("GST12", Decimal("12.000")),
    ("GST18", Decimal("18.000")),
    ("GST28", Decimal("28.000")),
    ("CESS40", Decimal("40.000")),
)

# A spread of amounts covering small (₹1), typical (₹100, ₹999.50), and large
# (₹12 345.67) lines plus values picked to surface paise rounding.
_AMOUNTS: tuple[Decimal, ...] = (
    Decimal("1.0000"),
    Decimal("9.9900"),
    Decimal("100.0000"),
    Decimal("123.4500"),
    Decimal("999.5000"),
    Decimal("1234.5600"),
    Decimal("12345.6700"),
)


@pytest.fixture
def slab_taxes(db) -> dict[str, Tax]:
    """Build one ``Tax`` row per slab with an equal CGST / SGST split."""

    out: dict[str, Tax] = {}
    for code, rate in _SLABS:
        half = (rate / 2).quantize(Decimal("0.001"))
        out[code] = Tax.objects.create(
            code=code,
            name=code,
            rate_total=rate,
            components_json=[
                {"type": TaxComponentType.CGST.value, "rate": str(half)},
                {"type": TaxComponentType.SGST.value, "rate": str(half)},
            ],
        )
    return out


# Build a single parametrize grid so each (slab, amount, mode) becomes its
# own test row in the pytest report.
_GRID = list(product(_SLABS, _AMOUNTS, ("EXCLUSIVE", "INCLUSIVE")))


@pytest.mark.parametrize(("slab", "amount", "mode"), _GRID)
def test_tax_engine_algebraic_invariants(slab_taxes, slab, amount, mode):
    code, rate = slab
    tax = slab_taxes[code]

    breakup = tax_engine.compute_line(line_subtotal=amount, tax=tax, tax_mode=mode)

    base = Decimal(breakup["base"])
    tax_total = Decimal(breakup["tax_total"])
    grand_total = Decimal(breakup["grand_total"])

    # 1 paisa tolerance covers banker's rounding at the component split.
    tolerance = Decimal("0.01")

    # Invariant 1: components sum to tax_total.
    summed = sum(
        (Decimal(comp["amount"]) for comp in breakup["components"]),
        start=Decimal("0"),
    )
    assert abs(summed - tax_total) <= tolerance, f"components sum {summed} != tax_total {tax_total}"

    # Invariant 2: base + tax == grand_total.
    assert (
        abs((base + tax_total) - grand_total) <= tolerance
    ), f"{base} + {tax_total} != {grand_total}"

    if rate == Decimal("0.000"):
        assert tax_total == Decimal("0")
        assert base == grand_total
        return

    if mode == "EXCLUSIVE":
        # base equals the input subtotal; tax = base * rate / 100.
        assert abs(base - amount) <= tolerance
        expected_tax = (amount * rate / Decimal("100")).quantize(Decimal("0.0001"))
        assert abs(tax_total - expected_tax) <= tolerance
    else:
        # INCLUSIVE: the input is the grand_total; base = input / (1 + rate/100).
        assert abs(grand_total - amount) <= tolerance
        expected_base = (amount / (Decimal("1") + rate / Decimal("100"))).quantize(
            Decimal("0.0001")
        )
        assert abs(base - expected_base) <= tolerance


def test_zero_rate_returns_passthrough(slab_taxes):
    breakup = tax_engine.compute_line(
        line_subtotal=Decimal("100"),
        tax=slab_taxes["GST0"],
        tax_mode="EXCLUSIVE",
    )
    assert Decimal(breakup["tax_total"]) == Decimal("0")
    assert Decimal(breakup["base"]) == Decimal(breakup["grand_total"])
