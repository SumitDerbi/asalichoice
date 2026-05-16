"""Tests for the shared DRF baseline (plan 008)."""

from __future__ import annotations

import pytest
from rest_framework.test import APIRequestFactory

from apps.core.api import (
    DefaultPageNumberPagination,
    DomainError,
    HasAnyPermission,
    IsBranchScoped,
    IsSuperAdmin,
    LedgerCursorPagination,
)
from apps.core.api.filters import BaseSearchFilterBackend
from apps.core.context import RequestContext, reset_request_context, set_request_context

# --- DomainError -----------------------------------------------------------


def test_domain_error_defaults():
    class MyErr(DomainError):  # noqa: N818
        default_code = "INV-001"
        default_message = "Insufficient stock"
        default_status = 409

    err = MyErr()
    env = err.to_envelope()
    assert env == {
        "error": {
            "code": "INV-001",
            "message": "Insufficient stock",
            "details": {},
        }
    }
    assert err.status == 409


def test_domain_error_per_instance_override():
    err = DomainError("Custom msg", code="MST-007", status=422, details={"x": 1})
    assert err.to_envelope() == {
        "error": {"code": "MST-007", "message": "Custom msg", "details": {"x": 1}}
    }
    assert err.status == 422


# --- Pagination ------------------------------------------------------------


def test_default_pagination_settings():
    p = DefaultPageNumberPagination()
    assert p.page_size == 25
    assert p.max_page_size == 200
    assert p.page_size_query_param == "page_size"


def test_ledger_pagination_is_cursor():
    p = LedgerCursorPagination()
    assert p.page_size == 50
    assert p.ordering == "-id"
    assert p.cursor_query_param == "cursor"


# --- Permissions -----------------------------------------------------------


def test_is_super_admin(user_factory):
    factory = APIRequestFactory()
    perm = IsSuperAdmin()

    regular = user_factory()
    req = factory.get("/")
    req.user = regular
    assert perm.has_permission(req, view=None) is False

    admin = user_factory(is_superuser=True, is_staff=True)
    req = factory.get("/")
    req.user = admin
    assert perm.has_permission(req, view=None) is True


def test_is_branch_scoped_safe_methods_pass():
    factory = APIRequestFactory()
    perm = IsBranchScoped()
    for method in ("get", "head", "options"):
        req = getattr(factory, method)("/")
        assert perm.has_permission(req, view=None) is True


def test_is_branch_scoped_writes_require_branch():
    factory = APIRequestFactory()
    perm = IsBranchScoped()
    req = factory.post("/")

    # No branch context bound → reject.
    assert perm.has_permission(req, view=None) is False

    ctx = RequestContext(branch_id=1)
    token = set_request_context(ctx)
    try:
        assert perm.has_permission(req, view=None) is True
    finally:
        reset_request_context(token)


def test_has_any_permission_no_perms_declared_allows(user_factory):
    factory = APIRequestFactory()
    perm = HasAnyPermission()

    class _V:
        required_perms = ()

    req = factory.get("/")
    req.user = user_factory()
    assert perm.has_permission(req, _V()) is True


def test_has_any_permission_rejects_unauth():
    from django.contrib.auth.models import AnonymousUser

    factory = APIRequestFactory()
    perm = HasAnyPermission()

    class _V:
        required_perms = ("masters.view_product",)

    req = factory.get("/")
    req.user = AnonymousUser()
    assert perm.has_permission(req, _V()) is False


def test_has_any_permission_accepts_when_any_match(user_factory, monkeypatch):
    factory = APIRequestFactory()
    perm = HasAnyPermission()

    user = user_factory()
    monkeypatch.setattr(
        type(user),
        "has_perm",
        lambda self, code, obj=None: code == "masters.view_product",
    )

    class _V:
        required_perms = ("masters.add_product", "masters.view_product")

    req = factory.get("/")
    req.user = user
    assert perm.has_permission(req, _V()) is True


# --- Filter backend --------------------------------------------------------


def test_base_filter_skips_models_without_is_active():
    from apps.core.audit.models import AuditLog  # no is_active column

    backend = BaseSearchFilterBackend()
    factory = APIRequestFactory()
    qs = AuditLog.objects.all()
    out = backend.filter_queryset(factory.get("/"), qs, view=None)
    # Same queryset back, no FieldError raised.
    assert out is qs


@pytest.mark.django_db
def test_base_filter_excludes_inactive_by_default(user_factory):
    active = user_factory()
    inactive = user_factory(is_active=False)

    from django.contrib.auth import get_user_model

    UserModel = get_user_model()  # noqa: N806 - Django convention for model classes

    backend = BaseSearchFilterBackend()
    factory = APIRequestFactory()

    # Default: only active rows.
    qs = UserModel.all_objects.all()
    out = backend.filter_queryset(factory.get("/"), qs, view=None)
    ids = set(out.values_list("id", flat=True))
    assert active.id in ids
    assert inactive.id not in ids

    # ?include_inactive=true: tombstones returned too.
    qs = UserModel.all_objects.all()
    out = backend.filter_queryset(factory.get("/", {"include_inactive": "true"}), qs, view=None)
    ids = set(out.values_list("id", flat=True))
    assert active.id in ids
    assert inactive.id in ids
