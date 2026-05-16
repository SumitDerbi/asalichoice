"""
Shared filter backends.

Built on top of ``django-filter`` (already declared in
``REST_FRAMEWORK['DEFAULT_FILTER_BACKENDS']``). This module adds a thin
wrapper that documents the standard query parameters every list
endpoint should support:

- ``search``       — text search (handled by DRF's ``SearchFilter``)
- ``ordering``     — ``?ordering=field`` / ``?ordering=-field``
- ``page`` / ``page_size`` — pagination (set on the pagination class)
- ``is_active``    — soft-delete tombstone toggle on ``BaseModel`` rows
"""

from __future__ import annotations

from django.db.models import QuerySet
from rest_framework.filters import BaseFilterBackend
from rest_framework.request import Request
from rest_framework.views import APIView


class BaseSearchFilterBackend(BaseFilterBackend):
    """Filter ``BaseModel`` querysets by ``is_active``.

    When ``?include_inactive=true`` is passed, soft-deleted rows are
    included (admin / restore flows). Without it the default
    :class:`apps.core.models.base.ActiveOnlyManager` already excludes
    them, but this backend also handles viewsets that explicitly use
    ``all_objects`` and want runtime control.
    """

    INCLUDE_PARAM = "include_inactive"

    def filter_queryset(
        self,
        request: Request,
        queryset: QuerySet,
        view: APIView,
    ) -> QuerySet:
        params = getattr(request, "query_params", None) or request.GET
        include = params.get(self.INCLUDE_PARAM, "").lower()
        if include in ("1", "true", "yes"):
            return queryset
        # Only filter if the model actually has the ``is_active`` field —
        # otherwise this would raise FieldError on non-soft-delete models.
        if hasattr(queryset.model, "is_active"):
            return queryset.filter(is_active=True)
        return queryset
