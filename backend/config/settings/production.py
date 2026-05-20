"""
Production settings for the AsliChoice backend.

Used by ``wsgi.py`` / ``asgi.py`` and the cPanel ``passenger_wsgi.py``.
All sensitive values are required via the environment — there are no
fallbacks here on purpose.
"""

from __future__ import annotations

from .base import *  # noqa: F403
from .base import env

DEBUG = False

# Hard requirement in production — fail loudly if absent.
SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# ---------------------------------------------------------------------------
# Static files — serve via WhiteNoise (Passenger does not serve /static/).
# Insert WhiteNoise right after SecurityMiddleware (recommended position).
# ---------------------------------------------------------------------------
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ---------------------------------------------------------------------------
# Security headers (per _conventions.md §8)
# ---------------------------------------------------------------------------
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)  # 1y
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"
