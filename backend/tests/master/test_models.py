"""Model-level tests for M01 master entities.

These focus on field-level invariants that the existing service/API tests
don't exercise directly:

* ``Tax.clean()`` rejects malformed ``components_json`` and mismatched totals.
* Unique constraints fire for composite keys (state code per country,
  city name per state).
* Soft-delete via ``BaseModel`` keeps rows queryable through ``all_objects``.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.master.models import Branch, BranchType, City, Country, State, Tax

pytestmark = pytest.mark.django_db


def _make_country(iso2: str = "IN") -> Country:
    return Country.objects.create(iso2=iso2, name=f"Country {iso2}")


# ---------------------------------------------------------------------------
# Tax.clean()
# ---------------------------------------------------------------------------


def test_tax_clean_accepts_matching_components():
    tax = Tax(
        code="GST5",
        name="GST 5%",
        rate_total=Decimal("5.000"),
        components_json=[
            {"type": "CGST", "rate": "2.5"},
            {"type": "SGST", "rate": "2.5"},
        ],
    )
    tax.full_clean()  # should not raise


def test_tax_clean_rejects_non_list_components():
    tax = Tax(code="GST5", name="x", rate_total=Decimal("5"), components_json={"oops": 1})
    with pytest.raises(ValidationError) as exc:
        tax.full_clean()
    assert "components_json" in exc.value.message_dict


def test_tax_clean_rejects_invalid_component_type():
    tax = Tax(
        code="GST5",
        name="x",
        rate_total=Decimal("5"),
        components_json=[{"type": "FOO", "rate": "5"}],
    )
    with pytest.raises(ValidationError) as exc:
        tax.full_clean()
    assert "components_json" in exc.value.message_dict


def test_tax_clean_rejects_mismatched_total():
    tax = Tax(
        code="GST5",
        name="x",
        rate_total=Decimal("5"),
        components_json=[{"type": "CGST", "rate": "1.0"}, {"type": "SGST", "rate": "2.5"}],
    )
    with pytest.raises(ValidationError) as exc:
        tax.full_clean()
    assert "rate_total" in exc.value.message_dict


# ---------------------------------------------------------------------------
# Unique / composite constraints
# ---------------------------------------------------------------------------


def test_state_code_unique_per_country():
    c1 = _make_country("IN")
    c2 = _make_country("US")
    State.objects.create(country=c1, code="KA", name="Karnataka")
    # Same code under a different country is fine.
    State.objects.create(country=c2, code="KA", name="Kentucky-ish")
    # Same (country, code) duplicate must fail.
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            State.objects.create(country=c1, code="KA", name="Dup")


def test_city_name_unique_per_state():
    country = _make_country("IN")
    state = State.objects.create(country=country, code="KA", name="Karnataka")
    City.objects.create(state=state, name="Bengaluru")
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            City.objects.create(state=state, name="Bengaluru")


def test_branch_code_unique():
    Branch.objects.create(code="HQ1", name="HQ One", type=BranchType.HQ)
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Branch.objects.create(code="HQ1", name="HQ Two", type=BranchType.HQ)


# ---------------------------------------------------------------------------
# Soft-delete via BaseModel
# ---------------------------------------------------------------------------


def test_branch_soft_delete_hides_from_default_manager():
    branch = Branch.objects.create(code="S1", name="Store 1", type=BranchType.STORE)
    branch.delete()  # BaseModel soft-delete
    assert not Branch.objects.filter(pk=branch.pk).exists()
    assert Branch.all_objects.filter(pk=branch.pk).exists()
