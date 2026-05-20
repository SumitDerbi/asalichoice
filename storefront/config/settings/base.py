"""
Base settings shared by all environments for the AsliChoice storefront.

Environment-specific files (``development.py``, ``production.py``) import
from this module and override only what differs.

Configuration is driven by environment variables via ``django-environ``;
see ``.env.example`` at the repo root for the full list of supported keys.

The storefront is a separate Django + Wagtail project that, per plan 003,
will eventually consume the backend over HTTP only — it does NOT share the
backend's database directly.
"""

from __future__ import annotations

from pathlib import Path

import environ

# ---------------------------------------------------------------------------
# Paths & env loading
# ---------------------------------------------------------------------------
# BASE_DIR = .../storefront/
BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_DIR = BASE_DIR / "config"

env = environ.Env(
    DEBUG=(bool, False),
)

# Load .env if present (local dev). In production, env vars come from
# ~/deploy_config/<env>/<env>.env via deploy.sh.
_env_file = BASE_DIR / ".env"
if _env_file.exists():
    environ.Env.read_env(str(_env_file))

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
SECRET_KEY = env("SECRET_KEY", default="django-insecure-change-me-in-env")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
]

# Wagtail and its required dependencies. Order follows the upstream
# recommendation from `wagtail start`.
WAGTAIL_APPS = [
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    # Required by wagtailseo (registers @register_setting → wagtailsettings
    # URL namespace). Without this the Wagtail admin sidebar crashes with
    # NoReverseMatch: 'wagtailsettings'.
    "wagtail.contrib.settings",
    "modelcluster",
    "taggit",
    # SEO helpers (page-level meta, OG, Twitter, canonical, JSON-LD).
    "wagtailseo",
]

LOCAL_APPS = [
    "apps.website",
    "apps.blog",
    "apps.core",
    # The theme app holds shared templates + Tailwind-built static assets;
    # listed last so its templates / static dirs are discovered after
    # everything else.
    "theme",
]

INSTALLED_APPS = DJANGO_APPS + WAGTAIL_APPS + LOCAL_APPS

# ---------------------------------------------------------------------------
# Middleware (security order matters)
# ---------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise serves collected static files in production. Must sit
    # directly after SecurityMiddleware per the whitenoise docs.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "theme" / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Exposes wagtailseo's settings model in templates.
                "wagtail.contrib.settings.context_processors.settings",
                "apps.core.context_processors.site_meta",
            ],
        },
    },
]

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
# Primary engine is MySQL (eventually pointing at a separate storefront DB —
# the backend's DB is consumed via API, not directly). SQLite is supported as
# a local-dev fallback when DB_ENGINE=sqlite or DB_PASSWORD is empty in dev.
DB_ENGINE = env("DB_ENGINE", default="mysql")

if DB_ENGINE == "sqlite":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": env("DB_NAME", default=str(BASE_DIR / "db.sqlite3")),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": env("DB_NAME", default="asalichoice_storefront"),
            "USER": env("DB_USER", default="asalichoice_storefront"),
            "PASSWORD": env("DB_PASSWORD", default=""),
            "HOST": env("DB_HOST", default="127.0.0.1"),
            "PORT": env("DB_PORT", default="3306"),
            "OPTIONS": {
                "charset": "utf8mb4",
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
            "CONN_MAX_AGE": env.int("DB_CONN_MAX_AGE", default=60),
        }
    }

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# argon2 first (per _conventions.md §8); Django default hashers as fallback.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = env("TIME_ZONE", default="Asia/Kolkata")
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static & media
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# Tailwind-built CSS is emitted under theme/static/ by the build pipeline in
# theme/static_src/. AppDirs finder picks it up via the `theme` app.
STATICFILES_DIRS: list[str] = []
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# WhiteNoise: serve compressed + hashed static files in production.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------------------------
# Wagtail
# ---------------------------------------------------------------------------
WAGTAIL_SITE_NAME = "AsliChoice"
WAGTAILADMIN_BASE_URL = env("WAGTAILADMIN_BASE_URL", default="http://localhost:8001")
WAGTAILDOCS_EXTENSIONS = [
    "csv",
    "docx",
    "key",
    "odt",
    "pdf",
    "pptx",
    "rtf",
    "txt",
    "xlsx",
    "zip",
]
# Use the default Wagtail search backend (sqlite/db). Elastic/OpenSearch
# integration is deferred until the products module lands.
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}

# ---------------------------------------------------------------------------
# Backend reachability
# ---------------------------------------------------------------------------
# The storefront talks to the backend over HTTP only — never the database.
# This URL is used by ``apps.core.views.backend_health`` to verify the
# backend is reachable from the storefront process.
BACKEND_API_URL = env("BACKEND_API_URL", default="http://localhost:8000/api/v1")
BACKEND_API_TIMEOUT = env.float("BACKEND_API_TIMEOUT", default=5.0)

# ---------------------------------------------------------------------------
# Logging — minimal sane default; overridden per environment.
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"handlers": ["console"], "level": env("LOG_LEVEL", default="INFO")},
}

# ---------------------------------------------------------------------------
# Versioning & site metadata (exposed to templates via context processor)
# ---------------------------------------------------------------------------
APP_VERSION = env("APP_VERSION", default="0.1.0")
SITE_NAME = env("SITE_NAME", default="AsliChoice")
SITE_DESCRIPTION = env(
    "SITE_DESCRIPTION",
    default="AsliChoice — curated omnichannel storefront.",
)
