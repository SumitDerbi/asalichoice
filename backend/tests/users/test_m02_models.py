"""M02 — User identity + RBAC model-level tests."""

from __future__ import annotations

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.users.models import (
    Permission,
    PrimaryIdentifier,
    Role,
    RolePermission,
    User,
    UserBranchAccess,
    UserRole,
)

pytestmark = pytest.mark.django_db


def test_user_clean_normalises_blank_uniques(user_factory):
    u = user_factory(email="a@example.test")
    u.mobile = ""
    u.employee_code = ""
    u.full_clean()
    assert u.mobile is None
    assert u.employee_code is None


def test_user_create_with_all_identifiers(user_factory):
    u = user_factory(
        email="multi@example.test",
        mobile="9999999999",
        employee_code="EMP-001",
        primary_identifier=PrimaryIdentifier.MOBILE,
    )
    assert u.mobile == "9999999999"
    assert u.employee_code == "EMP-001"
    assert u.primary_identifier == PrimaryIdentifier.MOBILE


def test_mobile_unique(user_factory):
    user_factory(email="x@example.test", mobile="8888888888")
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            user_factory(email="y@example.test", mobile="8888888888")


def test_role_permission_uniqueness():
    role = Role.objects.create(code="TEST", name="Test")
    perm = Permission.objects.create(code="x.view", name="View", module="x")
    RolePermission.objects.create(role=role, permission=perm)
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            RolePermission.objects.create(role=role, permission=perm)


def test_user_role_uniqueness_with_branch(user_factory):
    from apps.master.models import Branch

    user = user_factory()
    role = Role.objects.create(code="STAFF2", name="Staff")
    branch = Branch.objects.create(code="BR-UR1", name="Br UR1")
    UserRole.objects.create(user=user, role=role, branch=branch)
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            UserRole.objects.create(user=user, role=role, branch=branch)


def test_user_branch_access_uniqueness(user_factory):
    from apps.master.models import Branch

    user = user_factory()
    branch = Branch.objects.create(code="BR-T1", name="Test branch")
    UserBranchAccess.objects.create(user=user, branch=branch)
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            UserBranchAccess.objects.create(user=user, branch=branch)


def test_user_clean_requires_at_least_one_identifier():
    u = User(email="", mobile=None, employee_code=None)
    with pytest.raises(ValidationError):
        u.full_clean()
