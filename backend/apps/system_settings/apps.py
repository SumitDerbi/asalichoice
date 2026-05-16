"""App config for ``apps.system_settings``."""

from __future__ import annotations

from django.apps import AppConfig


class SystemSettingsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.system_settings"
    label = "system_settings"
    verbose_name = "System Settings"

    def ready(self) -> None:  # pragma: no cover - signal wiring
        from . import signals  # noqa: F401
