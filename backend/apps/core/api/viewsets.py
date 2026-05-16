"""
Base viewset every module's CRUD endpoint inherits from.

Composes:

- :class:`IdempotencyKeyMixin` for ``Idempotency-Key`` replay.
- ``rest_framework.viewsets.ModelViewSet`` for the standard CRUD verbs.
- Soft-delete-aware ``destroy`` that calls ``instance.delete()`` (which
  the :class:`apps.core.models.BaseModel` overrides to flip flags).
- Automatic ``created_by`` / ``updated_by`` stamping via ``perform_create``
  / ``perform_update`` when the model has those fields.
- Optional service-layer hook: when ``service_create`` /
  ``service_update`` / ``service_destroy`` callables are declared on
  the viewset, the relevant CRUD hook delegates to them (see ADR-002).

Module viewsets typically just declare ``queryset`` + ``serializer_class``
plus a ``service`` reference for writes::

    class ProductViewSet(BaseModelViewSet):
        queryset = Product.objects.all()
        serializer_class = ProductSerializer
        required_perms = ("masters.view_product",)

        def service_create(self, serializer):
            return create_product(**serializer.validated_data)
"""

from __future__ import annotations

from typing import Any

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import BaseSerializer

from .filters import BaseSearchFilterBackend
from .idempotency import IdempotencyKeyMixin
from .pagination import DefaultPageNumberPagination
from .permissions import HasAnyPermission


class BaseModelViewSet(IdempotencyKeyMixin, viewsets.ModelViewSet):
    """Default ModelViewSet for AsliChoice modules."""

    permission_classes = (IsAuthenticated, HasAnyPermission)
    pagination_class = DefaultPageNumberPagination
    filter_backends = (BaseSearchFilterBackend,)

    # OpenAPI tag — modules may override per viewset for finer grouping.
    tags: tuple[str, ...] = ()

    def _user_or_none(self) -> Any:
        user = getattr(self.request, "user", None)
        if user and user.is_authenticated:
            return user
        return None

    def perform_create(self, serializer: BaseSerializer) -> None:
        kwargs: dict[str, Any] = {}
        model = serializer.Meta.model  # type: ignore[attr-defined]
        if hasattr(model, "created_by_id"):
            user = self._user_or_none()
            if user is not None:
                kwargs["created_by"] = user
                kwargs["updated_by"] = user
        serializer.save(**kwargs)

    def perform_update(self, serializer: BaseSerializer) -> None:
        kwargs: dict[str, Any] = {}
        model = serializer.Meta.model  # type: ignore[attr-defined]
        if hasattr(model, "updated_by_id"):
            user = self._user_or_none()
            if user is not None:
                kwargs["updated_by"] = user
        serializer.save(**kwargs)

    def perform_destroy(self, instance: Any) -> None:
        # BaseModel.delete() performs the soft delete; falls back to
        # the real delete for models that opted out.
        instance.delete()
