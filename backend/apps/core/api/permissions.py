"""
Shared DRF permission classes.

These compose the permission model described in ``plans/_meta.yaml``
§ security. Full RBAC (role + permission tables, per-branch grants)
lands in M02 — until then ``HasAnyPermission`` reads Django's built-in
``user.has_perm()`` and ``IsBranchScoped`` is a soft check that simply
verifies a branch context is present.
"""

from __future__ import annotations

from typing import Any, ClassVar

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from ..context import current_branch_id


class IsSuperAdmin(BasePermission):
    """Allow access only to authenticated superusers."""

    message = "Super-admin role required."

    def has_permission(self, request: Request, view: APIView) -> bool:
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and user.is_superuser)


class IsBranchScoped(BasePermission):
    """Require an active branch context for write operations.

    Reads (``GET`` / ``HEAD`` / ``OPTIONS``) are allowed without a
    branch; mutating verbs require :func:`apps.core.context.current_branch_id`
    to return a value. The real per-branch permission grant lands in
    M02 once the ``Branch`` model exists.
    """

    SAFE_METHODS: ClassVar[frozenset[str]] = frozenset({"GET", "HEAD", "OPTIONS"})
    message = "Branch context required."

    def has_permission(self, request: Request, view: APIView) -> bool:
        if request.method in self.SAFE_METHODS:
            return True
        return current_branch_id() is not None


class HasAnyPermission(BasePermission):
    """Allow access if the user holds any of the permissions in ``required_perms``.

    Views declare the list via a ``required_perms`` attribute::

        class ProductViewSet(BaseModelViewSet):
            required_perms = ("masters.view_product", "masters.change_product")

    For finer-grained read/write splits, views may additionally declare
    ``required_perms_write`` which is consulted for any non-safe HTTP
    method (anything other than ``GET``/``HEAD``/``OPTIONS``)::

        class ProductViewSet(BaseModelViewSet):
            required_perms = ("catalog.view_product",)
            required_perms_write = (
                "catalog.add_product",
                "catalog.change_product",
                "catalog.delete_product",
            )

    Falls back to allow-all when no perms are declared (handy for the
    pre-M02 phase 0 where modules don't yet have grant tables). A
    misconfigured view (empty tuple) is treated as "no auth needed
    beyond IsAuthenticated".
    """

    message = "Missing required permission."
    SAFE_METHODS: ClassVar[frozenset[str]] = frozenset({"GET", "HEAD", "OPTIONS"})

    def _resolve_perms(self, request: Request, view: APIView) -> tuple[str, ...]:
        if request.method not in self.SAFE_METHODS:
            write_perms = getattr(view, "required_perms_write", None)
            if write_perms:
                return tuple(write_perms)
        return tuple(getattr(view, "required_perms", ()) or ())

    def has_permission(self, request: Request, view: APIView) -> bool:
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        perms = self._resolve_perms(request, view)
        if not perms:
            return True
        return any(user.has_perm(p) for p in perms)

    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        # Object-level checks land per-module; the default falls back
        # to the view-level check so opt-in is explicit.
        return self.has_permission(request, view)
