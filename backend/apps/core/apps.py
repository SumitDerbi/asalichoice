"""App config for ``apps.core``."""

from __future__ import annotations

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    label = "core"
    verbose_name = "Core"

    def ready(self) -> None:
        # Register project-wide system checks once the app registry is ready.
        from django.core.checks import Tags, register

        from .checks import check_models_inherit_base_model

        register(check_models_inherit_base_model, Tags.models)
