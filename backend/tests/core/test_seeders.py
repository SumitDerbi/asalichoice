"""Idempotency tests for the phase-0 seeders.

Each seeder is run twice; the second run must not raise and must not
add additional rows.
"""

from __future__ import annotations

import pytest
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import override_settings

from apps.system_settings.models import (
    ContactInfo,
    FeatureToggle,
    SettingScope,
    SiteSetting,
    SocialLink,
)
from apps.users.management.commands.seed_roles import DEFAULT_ROLES

pytestmark = pytest.mark.django_db


def _row_counts() -> dict[str, int]:
    return {
        "groups": Group.objects.count(),
        "settings": SiteSetting.objects.count(),
        "toggles": FeatureToggle.objects.count(),
        "social": SocialLink.objects.count(),
        "contact": ContactInfo.objects.count(),
    }


def test_seed_roles_idempotent():
    call_command("seed_roles")
    first = Group.objects.count()
    assert first >= len(DEFAULT_ROLES)
    assert set(DEFAULT_ROLES).issubset(set(Group.objects.values_list("name", flat=True)))

    call_command("seed_roles")
    assert Group.objects.count() == first


def test_seed_roles_reset_requires_debug(settings):
    settings.DEBUG = False
    from django.core.management.base import CommandError

    with pytest.raises(CommandError):
        call_command("seed_roles", "--reset")


def test_seed_roles_reset_in_debug(settings):
    settings.DEBUG = True
    call_command("seed_roles")
    before = Group.objects.filter(name__in=DEFAULT_ROLES).count()
    assert before == len(DEFAULT_ROLES)

    call_command("seed_roles", "--reset")
    assert Group.objects.filter(name__in=DEFAULT_ROLES).count() == len(DEFAULT_ROLES)


def test_seed_default_currency_idempotent():
    call_command("seed_default_currency")
    row = SiteSetting.objects.get(key="site.default_currency")
    assert row.value_json == "INR"

    call_command("seed_default_currency")
    assert SiteSetting.objects.filter(key="site.default_currency").count() == 1


def test_seed_default_timezone_idempotent():
    call_command("seed_default_timezone")
    row = SiteSetting.objects.get(key="site.default_timezone")
    assert row.value_json == "Asia/Kolkata"

    call_command("seed_default_timezone")
    assert SiteSetting.objects.filter(key="site.default_timezone").count() == 1


def test_seed_default_branch_idempotent():
    call_command("seed_default_branch")
    assert SiteSetting.objects.get(key="branch.default_code").value_json == "HQ"
    assert SiteSetting.objects.get(key="branch.default_name").value_json == "Head Office"

    call_command("seed_default_branch")
    assert (
        SiteSetting.objects.filter(
            key__in=("branch.default_code", "branch.default_name"),
            scope=SettingScope.GLOBAL,
            branch_id=None,
        ).count()
        == 2
    )


def test_seed_all_runs_every_seeder_twice():
    call_command("seed_all", "--skip-superuser")
    first = _row_counts()

    # All key tables populated.
    assert first["groups"] >= len(DEFAULT_ROLES)
    assert first["settings"] >= 6  # seed_settings DEFAULTS + branch placeholders
    assert first["toggles"] >= 4
    assert first["social"] >= 3
    assert first["contact"] >= 1

    call_command("seed_all", "--skip-superuser")
    second = _row_counts()
    assert first == second


def test_seed_all_invokes_superuser_when_env_set(monkeypatch):
    monkeypatch.setenv("SEED_SUPERUSER_EMAIL", "boot@example.test")
    monkeypatch.setenv("SEED_SUPERUSER_PASSWORD", "boot-pass-1234")

    with override_settings(
        PASSWORD_HASHERS=["django.contrib.auth.hashers.PBKDF2PasswordHasher"],
    ):
        call_command("seed_all")

    from django.contrib.auth import get_user_model

    user_model = get_user_model()
    assert user_model.objects.filter(email="boot@example.test", is_superuser=True).exists()


def test_seed_all_skips_superuser_when_env_missing(monkeypatch):
    monkeypatch.delenv("SEED_SUPERUSER_EMAIL", raising=False)
    monkeypatch.delenv("SEED_SUPERUSER_PASSWORD", raising=False)
    # Must not raise.
    call_command("seed_all")
    # No bootstrap superuser was created.
    from django.contrib.auth import get_user_model

    user_model = get_user_model()
    assert not user_model.objects.filter(email="boot@example.test").exists()
