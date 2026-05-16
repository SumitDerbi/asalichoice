"""
Fernet-based symmetric encryption helpers for :class:`IntegrationKey`.

The key is sourced from ``settings.SETTINGS_FERNET_KEY`` which in turn
reads ``SETTINGS_FERNET_KEY`` from the environment. Generate one with::

    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

A development fallback derives a Fernet key from ``settings.SECRET_KEY``
(SHA-256 -> urlsafe base64) so the dev box doesn't fail on first run;
production must set ``SETTINGS_FERNET_KEY`` explicitly — the
:func:`apps.system_settings.checks` system-check warns otherwise.
"""

from __future__ import annotations

import base64
import hashlib
from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class SecretDecryptionError(Exception):
    """Raised when a stored ciphertext can't be decrypted."""


def _derive_key_from_secret(secret_key: str) -> bytes:
    """Derive a 32-byte urlsafe-base64 Fernet key from ``SECRET_KEY``."""

    digest = hashlib.sha256(secret_key.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


@lru_cache(maxsize=1)
def _get_fernet() -> Fernet:
    raw = getattr(settings, "SETTINGS_FERNET_KEY", "") or ""
    if not raw:
        # Dev fallback only — production must set the key explicitly.
        raw_bytes = _derive_key_from_secret(settings.SECRET_KEY)
    else:
        raw_bytes = raw.encode("utf-8") if isinstance(raw, str) else raw
    try:
        return Fernet(raw_bytes)
    except (ValueError, TypeError) as exc:
        raise ImproperlyConfigured(
            "SETTINGS_FERNET_KEY is not a valid Fernet key. "
            "Generate one with `Fernet.generate_key()`.",
        ) from exc


def _reset_fernet_cache() -> None:
    """Test hook — clears the cached Fernet so a settings override takes effect."""

    _get_fernet.cache_clear()


def encrypt_secret(plaintext: str) -> bytes:
    return _get_fernet().encrypt(plaintext.encode("utf-8"))


def decrypt_secret(ciphertext: bytes) -> str:
    if not ciphertext:
        return ""
    try:
        return _get_fernet().decrypt(bytes(ciphertext)).decode("utf-8")
    except InvalidToken as exc:
        raise SecretDecryptionError(
            "Stored secret could not be decrypted with the current Fernet key.",
        ) from exc
