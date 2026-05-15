"""AppConfig for ``apps.website``."""

from __future__ import annotations

from django.apps import AppConfig


class WebsiteConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.website"
    label = "website"
    verbose_name = "Website"
