"""
``audit()`` service — the single entry point services use to record a
write to :class:`apps.core.audit.models.AuditLog`.

Service-layer code looks like::

    from apps.core.audit import audit

    def deactivate_customer(customer):
        before = serialize(customer)
        customer.is_active = False
        customer.save()
        audit(
            instance=customer,
            action="update",
            before=before,
            after=serialize(customer),
        )

Actor, branch, IP, and user-agent are pulled from the active request
context by default; callers can override any of them.
"""

from __future__ import annotations

from typing import Any

from django.db import models

from ..context import current_branch_id, request_context
from .models import AuditAction, AuditLog


def audit(
    *,
    instance: models.Model | None = None,
    model: str | None = None,
    object_id: str | int | None = None,
    action: str = AuditAction.OTHER,
    before: Any = None,
    after: Any = None,
    actor: Any | None = None,
    branch_id: int | None = None,
    ip: str | None = None,
    user_agent: str | None = None,
) -> AuditLog:
    """Record an audit entry.

    Either pass ``instance`` (preferred — model label and pk are derived
    from it) or supply ``model`` and ``object_id`` explicitly (useful
    when the row has already been hard-deleted).
    """

    if instance is not None:
        model = model or instance._meta.label
        if object_id is None:
            object_id = instance.pk

    if not model:
        raise ValueError("audit(): either 'instance' or 'model' must be provided.")

    ctx = request_context()
    if ctx is not None:
        if actor is None:
            actor = ctx.actor
        if ip is None:
            ip = ctx.ip
        if user_agent is None:
            user_agent = ctx.user_agent
    if branch_id is None:
        branch_id = current_branch_id()

    return AuditLog.objects.create(
        model=model,
        action=action,
        object_id="" if object_id is None else str(object_id),
        before=before,
        after=after,
        actor=actor if _is_saved_user(actor) else None,
        branch_id=branch_id,
        ip=ip,
        user_agent=(user_agent or "")[:512],
    )


def _is_saved_user(actor: Any | None) -> bool:
    """Return True only for an authenticated, persisted user instance.

    ``AnonymousUser`` and unsaved user objects must be stored as ``None``
    on the FK column.
    """

    if actor is None:
        return False
    if getattr(actor, "is_authenticated", False) is False:
        return False
    return getattr(actor, "pk", None) is not None
