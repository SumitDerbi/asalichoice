"""
Development settings for the AsliChoice backend.

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

# Permissive CORS in development if no explicit allowlist is set.
if not env.list("CORS_ALLOWED_ORIGINS", default=[]):
    CORS_ALLOW_ALL_ORIGINS = True
