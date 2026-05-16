"""Tests for the seed_master management command."""

from __future__ import annotations

import pytest
from django.core.management import call_command

from apps.master.models import Branch, City, Country, PaymentMode, State, Tax, UnitOfMeasure

pytestmark = pytest.mark.django_db


def test_seed_master_creates_expected_rows():
    call_command("seed_master")
    assert Country.objects.filter(iso2="IN").count() == 1
    # 37 Indian states/UTs in the curated list.
    assert State.objects.filter(country__iso2="IN").count() == 37
    # Cities: 95 curated entries.
    assert City.objects.count() == 95
    assert UnitOfMeasure.objects.count() == 8
    assert Tax.objects.count() == 5
    assert PaymentMode.objects.count() == 4
    assert Branch.objects.filter(code="HQ").exists()


def test_seed_master_is_idempotent():
    call_command("seed_master")
    counts_before = {
        "countries": Country.objects.count(),
        "states": State.objects.count(),
        "cities": City.objects.count(),
        "uoms": UnitOfMeasure.objects.count(),
        "taxes": Tax.objects.count(),
        "modes": PaymentMode.objects.count(),
        "branches": Branch.objects.count(),
    }
    call_command("seed_master")
    counts_after = {
        "countries": Country.objects.count(),
        "states": State.objects.count(),
        "cities": City.objects.count(),
        "uoms": UnitOfMeasure.objects.count(),
        "taxes": Tax.objects.count(),
        "modes": PaymentMode.objects.count(),
        "branches": Branch.objects.count(),
    }
    assert counts_before == counts_after
