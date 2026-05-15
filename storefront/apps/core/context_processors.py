"""Template context processors for the storefront."""

from __future__ import annotations

from django.conf import settings
from django.http import HttpRequest


def site_meta(request: HttpRequest) -> dict[str, str]:
    """Expose site-wide metadata (name, description, version) to all templates.

    Keeps ``base.html`` free of ``{% load %}`` / settings lookups and gives
    a single point of override per environment via ``SITE_NAME`` etc.
    """
    return {
        "SITE_NAME": getattr(settings, "SITE_NAME", "AsliChoice"),
        "SITE_DESCRIPTION": getattr(settings, "SITE_DESCRIPTION", ""),
        "APP_VERSION": getattr(settings, "APP_VERSION", "0.0.0"),
    }
