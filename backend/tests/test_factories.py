"""Smoke tests for ``tests.factories``."""

from __future__ import annotations

import pytest
from django.test import override_settings

from tests.factories import StaffUserFactory, SuperUserFactory, UserFactory, branch_factory

pbkdf2 = override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.PBKDF2PasswordHasher"])


@pytest.mark.django_db
def test_user_factory_creates_unique_users():
    a = UserFactory()
    b = UserFactory()
    assert a.email != b.email
    assert a.pk is not None
    assert not a.has_usable_password()


@pbkdf2
@pytest.mark.django_db
def test_user_factory_with_password():
    user = UserFactory(password="hunter2-test")
    assert user.check_password("hunter2-test")


@pytest.mark.django_db
def test_staff_and_super_user_factories():
    staff = StaffUserFactory()
    admin = SuperUserFactory()
    assert staff.is_staff and not staff.is_superuser
    assert admin.is_staff and admin.is_superuser


def test_branch_factory_stub_returns_int():
    assert branch_factory() == 1
    assert branch_factory(branch_id=42) == 42
