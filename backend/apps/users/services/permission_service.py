"""Permission resolution service.

Given a :class:`apps.users.models.User`, returns the union of permission
codes granted via :class:`UserRole` (filtered by branch when supplied).
Superusers get the universal wildcard ``"*"``.
"""

from __future__ import annotations

from collections.abc import Iterable

from django.db.models import Q

from ..models import User, UserBranchAccess


def get_user_permissions(user: User, *, branch_id: int | None = None) -> set[str]:
    """Return the set of permission codes the user holds.

    A role with ``branch IS NULL`` is global; a role attached to a
    specific branch only counts when ``branch_id`` matches (or
    ``branch_id`` is None — in which case only global roles count).
    """

    if not user or not user.is_authenticated:
        return set()
    if user.is_superuser:
        return {"*"}

    qs = user.user_roles.select_related("role").prefetch_related("role__permissions")
    if branch_id is None:
        qs = qs.filter(branch__isnull=True)
    else:
        qs = qs.filter(Q(branch__isnull=True) | Q(branch_id=branch_id))

    perms: set[str] = set()
    for ur in qs:
        for p in ur.role.permissions.all():
            perms.add(p.code)
    return perms


def user_has(user: User, perm_code: str, *, branch_id: int | None = None) -> bool:
    """Return True if ``user`` holds ``perm_code`` in the given branch."""

    perms = get_user_permissions(user, branch_id=branch_id)
    if "*" in perms:
        return True
    return perm_code in perms


def user_branches(user: User) -> list[int]:
    """Return the branch ids the user is explicitly allowed to access.

    Superusers see every active branch (returned as an empty list to
    signal "no restriction" — callers must check ``is_superuser``
    separately).
    """

    if user.is_superuser:
        return []
    return list(
        UserBranchAccess.objects.filter(user=user, is_active=True).values_list(
            "branch_id", flat=True
        ),
    )


def serialize_me(user: User, *, branch_id: int | None = None) -> dict:
    """Payload returned from ``GET /api/v1/auth/me/``.

    Embeds the permission set so the admin-UI can render permission-aware
    chrome without an extra round-trip.
    """

    branches = list(
        UserBranchAccess.objects.filter(user=user, is_active=True).values(
            "branch_id", "is_default"
        ),
    )
    return {
        "id": user.pk,
        "email": user.email,
        "mobile": user.mobile or "",
        "employee_code": user.employee_code or "",
        "name": user.name,
        "display_name": user.display_name,
        "primary_identifier": user.primary_identifier,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "is_active": user.is_active,
        "permissions": sorted(get_user_permissions(user, branch_id=branch_id)),
        "branches": branches,
    }


__all__: Iterable[str] = (
    "get_user_permissions",
    "serialize_me",
    "user_branches",
    "user_has",
)
