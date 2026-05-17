"""
Base settings shared by all environments for the AsliChoice backend.

Environment-specific files (``development.py``, ``production.py``) import
from this module and override only what differs.

Configuration is driven by environment variables via ``django-environ``;
see ``.env.example`` at the repo root for the full list of supported keys.
"""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import environ

# ---------------------------------------------------------------------------
# Paths & env loading
# ---------------------------------------------------------------------------
# BASE_DIR = .../backend/
BASE_DIR = Path(__file__).resolve().parent.parent.parent

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
ASGI_APPLICATION = "config.asgi.application"

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
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
]

LOCAL_APPS = [
    "apps.core",
    "apps.users",
    "apps.system_settings",
    "apps.master",
    "apps.catalog",
]

AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = [
    "apps.users.auth_backends.IdentifierBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# OTP / lockout knobs (overridable via env in later milestones).
OTP_LENGTH = env.int("OTP_LENGTH", default=6)
OTP_EXPIRY_MINUTES = env.int("OTP_EXPIRY_MINUTES", default=5)
OTP_MAX_ATTEMPTS = env.int("OTP_MAX_ATTEMPTS", default=5)
LOGIN_LOCKOUT_THRESHOLD = env.int("LOGIN_LOCKOUT_THRESHOLD", default=10)
LOGIN_LOCKOUT_MINUTES = env.int("LOGIN_LOCKOUT_MINUTES", default=15)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ---------------------------------------------------------------------------
# Middleware (security order matters)
# ---------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Must run after AuthenticationMiddleware so request.user is populated
    # before we snapshot it into the request context.
    "apps.core.audit.middleware.RequestContextMiddleware",
    # Resolves the X-Branch-Id header into the active branch (M01/03).
    "apps.master.middleware.BranchContextMiddleware",
]

# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
# Primary engine is MySQL. SQLite is supported as a local-dev fallback when
# the DB_ENGINE env var is set to "sqlite" (or no DB_* vars are configured
# in development). See ``development.py`` for the dev-time fallback.
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
            "NAME": env("DB_NAME", default="asalichoice"),
            "USER": env("DB_USER", default="asalichoice"),
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

# argon2 first (per _conventions.md §8); django's default hashers as fallback.
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
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------------------------
# REST framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "apps.core.api.pagination.DefaultPageNumberPagination",
    "PAGE_SIZE": 25,
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "apps.core.exceptions.envelope_exception_handler",
    "DEFAULT_THROTTLE_RATES": {
        "login": env("THROTTLE_LOGIN_RATE", default="5/min"),
        "burst-anon": env("THROTTLE_ANON_RATE", default="60/min"),
        "burst-user": env("THROTTLE_USER_RATE", default="120/min"),
        "otp": env("THROTTLE_OTP_RATE", default="5/min"),
    },
}

# ---------------------------------------------------------------------------
# JWT (SimpleJWT) — lifetimes per _meta.yaml § security.jwt_lifetime_minutes
# ---------------------------------------------------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=env.int("JWT_ACCESS_MINUTES", default=15),
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        minutes=env.int("JWT_REFRESH_MINUTES", default=60 * 24 * 7),
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "SIGNING_KEY": env("JWT_SIGNING_KEY", default=SECRET_KEY),
}

# ---------------------------------------------------------------------------
# drf-spectacular (OpenAPI)
# ---------------------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    "TITLE": "AsliChoice API",
    "DESCRIPTION": (
        "AsliChoice omnichannel commerce platform API. "
        "See plans/ and docs/ for module-level documentation."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": r"/api/v1",
    "POSTPROCESSING_HOOKS": [
        "apps.core.api.openapi.add_error_envelope",
    ],
}

# ---------------------------------------------------------------------------
# CORS — env-driven allowlist (per _meta.yaml § security.cors)
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = env.bool("CORS_ALLOW_CREDENTIALS", default=True)

# Custom request headers used by the admin-ui (in addition to the corsheaders
# defaults like authorization, content-type, etc.).
from corsheaders.defaults import default_headers as _cors_default_headers  # noqa: E402

CORS_ALLOW_HEADERS = (
    *_cors_default_headers,
    "x-branch-id",
    "idempotency-key",
)

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
# Versioning
# ---------------------------------------------------------------------------
# Exposed via the /api/v1/health/ endpoint.
APP_VERSION = env("APP_VERSION", default="0.1.0")

# ---------------------------------------------------------------------------
# Core platform constants (plan 005)
# ---------------------------------------------------------------------------
# How long audit rows must be retained before a maintenance job may prune
# them. Used as the policy reference; the actual pruning job lands later.
AUDIT_RETENTION_YEARS = env.int("AUDIT_RETENTION_YEARS", default=7)

# When True (default) every concrete ``LedgerEntry`` subclass refuses
# updates / deletes at the application layer. Test fixtures may flip it
# off temporarily; production must leave it True.
LEDGER_IMMUTABLE = env.bool("LEDGER_IMMUTABLE", default=True)

# ---------------------------------------------------------------------------
# System-settings encryption key (plan 013)
# ---------------------------------------------------------------------------
# Fernet key used to encrypt :class:`apps.system_settings.models.IntegrationKey`
# values at rest. Generate with::
#
#     python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
#
# Leave blank in dev — the app derives a Fernet key from ``SECRET_KEY``
# as a fallback. Production **must** set this explicitly.
SETTINGS_FERNET_KEY = env("SETTINGS_FERNET_KEY", default="")
