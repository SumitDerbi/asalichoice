"""Service-layer tests for M01 master management."""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from apps.core.api.exceptions import DomainError
from apps.master.models import Branch, BranchType, Category, Pincode, Tax, Zone
from apps.master.services import (
    BRANCH_MAX_DEPTH,
    CATEGORY_MAX_DEPTH,
    check_branch_depth,
    check_category_depth,
    compute_tax_breakup,
    resolve_zone_for_pincode,
    validate_model,
)

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# Tax breakup
# ---------------------------------------------------------------------------


def _gst18() -> Tax:
    return Tax.objects.create(
        code="GST18",
        name="GST 18%",
        rate_total=Decimal("18"),
        components_json=[
            {"type": "CGST", "rate": "9"},
            {"type": "SGST", "rate": "9"},
        ],
    )


def test_compute_tax_breakup_exclusive():
    tax = _gst18()
    result = compute_tax_breakup(Decimal("100.00"), tax, inclusive=False)
    assert result["base"] == Decimal("100.00")
    assert result["tax_total"] == Decimal("18.00")
    assert result["grand_total"] == Decimal("118.00")
    assert len(result["components"]) == 2
    cgst = next(c for c in result["components"] if c["type"] == "CGST")
    sgst = next(c for c in result["components"] if c["type"] == "SGST")
    assert cgst["amount"] == Decimal("9.00")
    assert sgst["amount"] == Decimal("9.00")


def test_compute_tax_breakup_inclusive():
    tax = _gst18()
    result = compute_tax_breakup(Decimal("118.00"), tax, inclusive=True)
    assert result["grand_total"] == Decimal("118.00")
    assert result["base"] == Decimal("100.00")
    assert result["tax_total"] == Decimal("18.00")


def test_compute_tax_breakup_zero_rate():
    tax = Tax.objects.create(
        code="GST0",
        name="GST 0%",
        rate_total=Decimal("0"),
        components_json=[{"type": "CGST", "rate": "0"}, {"type": "SGST", "rate": "0"}],
    )
    result = compute_tax_breakup(Decimal("250.00"), tax)
    assert result["tax_total"] == Decimal("0.00")
    assert result["grand_total"] == Decimal("250.00")


def test_compute_tax_breakup_igst_fallback_when_components_empty():
    tax = Tax.objects.create(
        code="IGST18",
        name="IGST 18%",
        rate_total=Decimal("18"),
        components_json=[],
    )
    result = compute_tax_breakup(Decimal("100.00"), tax)
    assert len(result["components"]) == 1
    assert result["components"][0]["type"] == "IGST"
    assert result["components"][0]["amount"] == Decimal("18.00")


# ---------------------------------------------------------------------------
# Branch / Category depth
# ---------------------------------------------------------------------------


def _make_branch(code: str, parent: Branch | None = None) -> Branch:
    return Branch.objects.create(
        code=code,
        name=code,
        type=BranchType.STORE,
        parent=parent,
    )


def test_check_branch_depth_within_limit():
    root = _make_branch("R")
    # New child under root → depth 2 (root=1, new=2).
    assert check_branch_depth(root) == 2


def test_check_branch_depth_exceeded():
    parent = _make_branch("L0")
    for i in range(1, BRANCH_MAX_DEPTH):
        parent = _make_branch(f"L{i}", parent)
    # parent now sits at depth = BRANCH_MAX_DEPTH; one more child violates.
    with pytest.raises(DomainError) as exc:
        check_branch_depth(parent)
    assert exc.value.code == "MST-011"


def _make_category(code: str, parent: Category | None = None) -> Category:
    return Category.objects.create(code=code, name=code, parent=parent)


def test_check_category_depth_exceeded():
    parent = _make_category("C0")
    for i in range(1, CATEGORY_MAX_DEPTH):
        parent = _make_category(f"C{i}", parent)
    with pytest.raises(DomainError) as exc:
        check_category_depth(parent)
    assert exc.value.code == "MST-010"


# ---------------------------------------------------------------------------
# Zone resolution
# ---------------------------------------------------------------------------


def _seed_pincode(code: str) -> Pincode:
    from apps.master.models import City, Country, State

    country, _ = Country.objects.get_or_create(iso2="IN", defaults={"iso3": "IND", "name": "India"})
    state, _ = State.objects.get_or_create(
        country=country, code="MH", defaults={"name": "Maharashtra"}
    )
    city, _ = City.objects.get_or_create(state=state, name="Mumbai")
    return Pincode.objects.create(code=code, city=city)


def _make_branch_for_zone() -> Branch:
    return _make_branch("HQ-Z")


def test_resolve_zone_direct_m2m_match():
    pc = _seed_pincode("400001")
    zone = Zone.objects.create(code="Z1", name="Z1", branch=_make_branch_for_zone())
    zone.pincodes.add(pc)
    assert resolve_zone_for_pincode(pc) == zone


def test_resolve_zone_range_match():
    pc = _seed_pincode("400050")
    zone = Zone.objects.create(
        code="Z2",
        name="Z2",
        branch=_make_branch_for_zone(),
        pincode_ranges_json=[{"from": "400000", "to": "400100"}],
    )
    assert resolve_zone_for_pincode(pc) == zone


def test_resolve_zone_miss_returns_none():
    pc = _seed_pincode("999999")
    assert resolve_zone_for_pincode(pc) is None


# ---------------------------------------------------------------------------
# Model validation
# ---------------------------------------------------------------------------


def test_tax_clean_rejects_component_sum_mismatch():
    tax = Tax(
        code="BAD",
        name="bad",
        rate_total=Decimal("18"),
        components_json=[{"type": "CGST", "rate": "9"}, {"type": "SGST", "rate": "8"}],
    )
    with pytest.raises(ValidationError):
        validate_model(tax)
