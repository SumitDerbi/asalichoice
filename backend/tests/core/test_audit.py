"""Tests for :mod:`apps.core.audit`."""

from __future__ import annotations

import pytest

from apps.core.audit import AuditLog, audit
from apps.core.audit.models import AuditAction

pytestmark = pytest.mark.django_db


def test_audit_records_basic_fields(capture_audit):
    entry = audit(
        model="catalog.Product",
        object_id=42,
        action=AuditAction.CREATE,
        before=None,
        after={"sku": "SKU-1"},
    )
    assert entry.pk is not None
    assert entry.model == "catalog.Product"
    assert entry.object_id == "42"
    assert entry.action == "create"
    assert entry.after == {"sku": "SKU-1"}
    assert capture_audit() == [entry]


def test_audit_pulls_actor_and_branch_from_request_context(
    push_request_context,
    user_factory,
    branch_id,
):
    user = user_factory()
    with push_request_context(actor=user, ip="10.0.0.1", user_agent="UA", branch_id=branch_id):
        entry = audit(
            model="catalog.Product",
            object_id=1,
            action=AuditAction.UPDATE,
            before={"v": 1},
            after={"v": 2},
        )
    assert entry.actor_id == user.pk
    assert entry.branch_id == branch_id
    assert entry.ip == "10.0.0.1"
    assert entry.user_agent == "UA"


def test_audit_drops_anonymous_actor(push_request_context):
    class _Anon:
        pk = None
        is_authenticated = False

    with push_request_context(actor=_Anon()):
        entry = audit(model="catalog.Product", object_id=1, action="update")
    assert entry.actor is None


def test_audit_requires_model_or_instance():
    with pytest.raises(ValueError):
        audit(action=AuditAction.OTHER)


def test_audit_log_is_immutable_on_update():
    entry = audit(model="catalog.Product", object_id=1, action="create")
    entry.action = "update"
    with pytest.raises(RuntimeError):
        entry.save()


def test_audit_log_delete_is_blocked():
    entry = audit(model="catalog.Product", object_id=1, action="create")
    with pytest.raises(RuntimeError):
        entry.delete()


def test_audit_user_agent_truncated_to_512_chars():
    huge = "x" * 1000
    entry = audit(
        model="catalog.Product",
        object_id=1,
        action="create",
        user_agent=huge,
    )
    assert len(entry.user_agent) == 512


def test_audit_log_count_increases(capture_audit):
    assert capture_audit() == []
    audit(model="catalog.Product", object_id=1, action="create")
    audit(model="catalog.Product", object_id=2, action="create")
    rows = capture_audit()
    assert len(rows) == 2
    assert all(isinstance(r, AuditLog) for r in rows)
