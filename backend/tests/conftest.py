"""
Shared pytest fixtures for the backend test suite.

Fixtures here are intentionally minimal in phase 0 — real branch /
permission fixtures land with M01-M02. The placeholders below give
later tests a single import path to migrate to.
"""

from __future__ import annotations

from typing import Any

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.core.audit.models import AuditLog
from apps.core.context import RequestContext, reset_request_context, set_request_context

User = get_user_model()


@pytest.fixture(autouse=True)
def _clear_throttle_cache():
    """Reset DRF throttle counters between tests so login/OTP tests do not
    bleed into each other in the full-suite run.
    """

    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def user_factory(db):
    """Return a callable that creates throwaway users."""

    counter = {"n": 0}

    def _make(**overrides: Any):
        counter["n"] += 1
        defaults: dict[str, Any] = {
            "email": f"user-{counter['n']}@example.test",
        }
        defaults.update(overrides)
        password = defaults.pop("password", None)
        # The production hasher (Argon2) requires a native lib that
        # isn't part of the minimal dev install; tests opt into a real
        # password via the ``password=`` kwarg when needed.
        user = User(**defaults)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    return _make


@pytest.fixture
def api_client(user_factory):
    """Return a factory producing :class:`APIClient` instances.

    Call without args for an anonymous client, or with a user to get a
    force-authenticated client. Real JWT auth flows are exercised in
    M02's test suite.
    """

    def _make(user=None) -> APIClient:
        client = APIClient()
        if user is None:
            return client
        if user is True:
            user = user_factory()
        client.force_authenticate(user=user)
        return client

    return _make


@pytest.fixture
def branch_id() -> int:
    """Placeholder branch id used by branch-scoped tests until M02 lands."""

    return 1


@pytest.fixture
def push_request_context():
    """Context-managed fixture for binding a :class:`RequestContext`.

    Usage::

        def test_thing(push_request_context, user_factory):
            with push_request_context(actor=user_factory(), branch_id=1):
                ...
    """

    from contextlib import contextmanager

    @contextmanager
    def _push(**overrides: Any):
        ctx = RequestContext(**overrides)
        token = set_request_context(ctx)
        try:
            yield ctx
        finally:
            reset_request_context(token)

    return _push


@pytest.fixture
def capture_audit(db):
    """Yield a helper that returns audit rows created during the test."""

    baseline = AuditLog.objects.count()

    def _new_rows():
        return list(AuditLog.objects.order_by("id")[baseline:])

    return _new_rows
