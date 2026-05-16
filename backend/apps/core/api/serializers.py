"""
Shared serializer bases.

:class:`BaseModelSerializer` makes the audit + soft-delete columns
read-only by default and adds the ``display_name`` virtual field used
across the platform for nice list rendering. Module serializers
declare only the business fields they care about.
"""

from __future__ import annotations

from rest_framework import serializers

# Fields contributed by :class:`apps.core.models.BaseModel` that must
# never be writable through the API.
BASE_READ_ONLY_FIELDS: tuple[str, ...] = (
    "id",
    "created_at",
    "updated_at",
    "created_by",
    "updated_by",
    "is_active",
    "deleted_at",
)


class BaseModelSerializer(serializers.ModelSerializer):
    """ModelSerializer with the BaseModel audit + soft-delete columns
    declared read-only by default.

    Subclasses just declare ``Meta.model`` and ``Meta.fields`` (or
    ``Meta.exclude``); the base merges its read-only set with whatever
    ``Meta.read_only_fields`` the subclass already lists, so adding
    additional read-only fields is purely additive.
    """

    def get_extra_kwargs(self):  # type: ignore[override]
        extra_kwargs = dict(super().get_extra_kwargs() or {})
        for name in BASE_READ_ONLY_FIELDS:
            current = dict(extra_kwargs.get(name, {}))
            current.setdefault("read_only", True)
            extra_kwargs[name] = current
        return extra_kwargs
