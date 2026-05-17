"""Public seam exposed by the users module.

Other apps must import from here — never from ``apps.users.models`` or
``apps.users.services`` directly. See ADR-002 for the cross-app
dependency rules.
"""

from __future__ import annotations

from collections.abc import Iterable

from .services.permission_service import get_user_permissions, user_branches, user_has


def user_has_permission(user, perm_code: str, *, branch_id: int | None = None) -> bool:
    """Return True if ``user`` holds ``perm_code`` (optionally in branch)."""

    return user_has(user, perm_code, branch_id=branch_id)


def user_can_access_branch(user, branch_id: int) -> bool:
    """Return True when ``user`` is allowed to operate in ``branch_id``.

    Superusers and staff bypass the ACL. Everyone else must have an
    :class:`apps.users.models.UserBranchAccess` row.
    """

    if user is None or not getattr(user, "is_authenticated", False):
        return False
    if user.is_superuser or user.is_staff:
        return True
    from .models import UserBranchAccess

    return UserBranchAccess.objects.filter(user=user, branch_id=branch_id).exists()


def list_user_branches(user) -> list[int]:
    return user_branches(user)


def user_permission_codes(user, *, branch_id: int | None = None) -> set[str]:
    return get_user_permissions(user, branch_id=branch_id)


__all__: Iterable[str] = (
    "list_user_branches",
    "user_can_access_branch",
    "user_has_permission",
    "user_permission_codes",
)
