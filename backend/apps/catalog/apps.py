"""Catalog app config."""

from __future__ import annotations

from django.apps import AppConfig


class CatalogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.catalog"
    label = "catalog"
    verbose_name = "Catalog"

    def ready(self) -> None:  # pragma: no cover - signal wiring
        from . import signals  # noqa: F401
