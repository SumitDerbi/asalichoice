"""Purchase app config."""

from __future__ import annotations

from django.apps import AppConfig


class PurchaseConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.purchase"
    label = "purchase"
    verbose_name = "Vendor & Purchase"

    def ready(self) -> None:  # pragma: no cover - signal wiring
        from . import signals  # noqa: F401
