"""Sales app config (M11)."""

from __future__ import annotations

from django.apps import AppConfig


class SalesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.sales"
    label = "sales"
    verbose_name = "Sales & Billing"

    def ready(self) -> None:  # pragma: no cover - signal wiring
        from . import signals  # noqa: F401
