"""AppConfig for the ``theme`` app."""

from __future__ import annotations

from django.apps import AppConfig


class ThemeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "theme"
    label = "theme"
    verbose_name = "Theme"
