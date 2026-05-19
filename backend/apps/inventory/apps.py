"""Inventory app config (M05)."""

from __future__ import annotations

from django.apps import AppConfig


class InventoryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.inventory"
    label = "inventory"
    verbose_name = "Inventory & Branch Transfer"

    def ready(self) -> None:  # pragma: no cover - signal wiring
        from . import signals  # noqa: F401
