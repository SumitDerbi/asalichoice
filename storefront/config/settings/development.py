"""
Development settings for the AsliChoice storefront.

Used by ``manage.py`` (default) and any local tooling. Optimised for
fast iteration, with SQLite as a fallback when no MySQL is configured.
"""

from __future__ import annotations

from .base import *  # noqa: F403
from .base import BASE_DIR, env

DEBUG = True

ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    default=["localhost", "127.0.0.1", "0.0.0.0"],
)

# Dev fallback: if no DB_PASSWORD is configured, default to SQLite so that
# `manage.py migrate` and `pytest` work out of the box.
if not env("DB_PASSWORD", default="") and env("DB_ENGINE", default="") != "mysql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(BASE_DIR / "db.sqlite3"),
        }
    }

# Disable static-file manifest in development so missing hashed files don't
# error out before the Tailwind pipeline has produced output.css.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

try:
    import debug_toolbar  # noqa: F401  # optional, not pinned
except ImportError:  # pragma: no cover - optional dev dep
    pass
