"""Tests for the ``seed_superuser`` management command."""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.core.management import CommandError, call_command
from django.test import override_settings

pbkdf2 = override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.PBKDF2PasswordHasher"])

pytestmark = pytest.mark.django_db

User = get_user_model()


@pbkdf2
def test_seed_creates_superuser(monkeypatch):
    monkeypatch.setenv("SEED_SUPERUSER_EMAIL", "boss@example.test")
    monkeypatch.setenv("SEED_SUPERUSER_PASSWORD", "boss-pw-1")
    call_command("seed_superuser")
    user = User.objects.get(email="boss@example.test")
    assert user.is_superuser
    assert user.is_staff
    assert user.check_password("boss-pw-1")


@pbkdf2
def test_seed_is_idempotent(monkeypatch):
    monkeypatch.setenv("SEED_SUPERUSER_EMAIL", "boss@example.test")
    monkeypatch.setenv("SEED_SUPERUSER_PASSWORD", "boss-pw-1")
    call_command("seed_superuser")
    # Second invocation must not create a duplicate or change anything.
    call_command("seed_superuser")
    assert User.objects.filter(email="boss@example.test").count() == 1


@pbkdf2
def test_seed_update_password_flag(monkeypatch):
    monkeypatch.setenv("SEED_SUPERUSER_EMAIL", "boss@example.test")
    monkeypatch.setenv("SEED_SUPERUSER_PASSWORD", "boss-pw-1")
    call_command("seed_superuser")

    monkeypatch.setenv("SEED_SUPERUSER_PASSWORD", "boss-pw-2")
    call_command("seed_superuser", "--update-password")
    user = User.objects.get(email="boss@example.test")
    assert user.check_password("boss-pw-2")


def test_seed_requires_env_vars(monkeypatch):
    monkeypatch.delenv("SEED_SUPERUSER_EMAIL", raising=False)
    monkeypatch.delenv("SEED_SUPERUSER_PASSWORD", raising=False)
    with pytest.raises(CommandError):
        call_command("seed_superuser")
