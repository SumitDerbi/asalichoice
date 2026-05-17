"""
Service-layer helpers for system settings.

These are the canonical accessors the rest of the codebase should use;
they handle defaults, an in-process TTL cache, and feature-toggle
rollout hashing.
"""

from __future__ import annotations

import hashlib
import time
from threading import RLock
from typing import Any

from django.db.models import Q

from .models import FeatureToggle, IntegrationKey, SettingScope, SiteSetting

# In-process TTL cache. Per-worker; invalidation on save fires via the
# ``post_save`` signal in ``signals.py``.
_CACHE_TTL_SECONDS = 60
_cache: dict[tuple[str, str, int | None], tuple[float, Any]] = {}
_toggle_cache: dict[str, tuple[float, FeatureToggle]] = {}
_lock = RLock()


def _now() -> float:
    return time.monotonic()


def invalidate_setting_cache(key: str | None = None) -> None:
    """Drop cached settings; pass ``key`` to evict only that key."""

    with _lock:
        if key is None:
            _cache.clear()
        else:
            for cache_key in [k for k in _cache if k[0] == key]:
                _cache.pop(cache_key, None)


def invalidate_feature_cache(key: str | None = None) -> None:
    with _lock:
        if key is None:
            _toggle_cache.clear()
        else:
            _toggle_cache.pop(key, None)


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------


_MISSING = object()


def get_setting(
    key: str,
    scope: str = SettingScope.GLOBAL,
    branch: int | None = None,
    default: Any = None,
) -> Any:
    """Return the JSON value for *key* — falls back to *default* on miss.

    Lookup order when ``scope=branch`` and the row is missing: a branch
    miss transparently falls back to the GLOBAL row with the same key,
    so module code can read one accessor regardless of whether the
    operator has overridden the value per-branch.
    """

    cache_key = (key, scope, branch)
    with _lock:
        hit = _cache.get(cache_key)
        if hit is not None and hit[0] > _now():
            return hit[1]

    value: Any = _MISSING
    qs = SiteSetting.objects.filter(key=key)
    if scope == SettingScope.BRANCH:
        row = qs.filter(scope=SettingScope.BRANCH, branch_id=branch).first()
        if row is not None:
            value = row.value_json
    if value is _MISSING:
        row = qs.filter(scope=SettingScope.GLOBAL).first()
        if row is not None:
            value = row.value_json
    if value is _MISSING:
        value = default

    with _lock:
        _cache[cache_key] = (_now() + _CACHE_TTL_SECONDS, value)
    return value


# ---------------------------------------------------------------------------
# Feature toggles
# ---------------------------------------------------------------------------


def _rollout_bucket(key: str, identifier: str) -> int:
    """Stable 0-99 bucket derived from key + user identifier."""

    digest = hashlib.sha256(f"{key}:{identifier}".encode()).digest()
    # Take the first 4 bytes as an int and mod 100.
    return int.from_bytes(digest[:4], "big") % 100


def _get_toggle(key: str) -> FeatureToggle | None:
    with _lock:
        hit = _toggle_cache.get(key)
        if hit is not None and hit[0] > _now():
            return hit[1]
    toggle = FeatureToggle.objects.filter(key=key).first()
    if toggle is not None:
        with _lock:
            _toggle_cache[key] = (_now() + _CACHE_TTL_SECONDS, toggle)
    return toggle


def is_feature_enabled(key: str, user: Any | None = None) -> bool:
    """Return True if *key* is on for *user*.

    ``rollout_percentage`` of 100 means everyone, 0 means no one. For
    intermediate values the user is bucketed deterministically by
    ``sha256(key + identifier) % 100``; unauthenticated callers are
    bucketed by an anonymous tag so the rollout is consistent on a
    per-session basis (cookie-driven splitting lands later).
    """

    toggle = _get_toggle(key)
    if toggle is None or not toggle.enabled:
        return False
    if toggle.rollout_percentage >= 100:
        return True
    if toggle.rollout_percentage <= 0:
        return False
    identifier = str(getattr(user, "pk", "anon") or "anon")
    return _rollout_bucket(key, identifier) < toggle.rollout_percentage


# ---------------------------------------------------------------------------
# Integration keys
# ---------------------------------------------------------------------------


def get_integration_key(provider: str, key_name: str) -> str | None:
    """Return the decrypted secret for ``provider/key_name`` or ``None``.

    Only active rows (``is_active=True``) are considered. Decryption
    errors propagate — see :class:`SecretDecryptionError`.
    """

    row = (
        IntegrationKey.objects.filter(provider=provider, key_name=key_name)
        .filter(Q(is_active=True))
        .first()
    )
    if row is None:
        return None
    return row.get_secret()


__all__ = [
    "get_integration_key",
    "get_setting",
    "invalidate_feature_cache",
    "invalidate_setting_cache",
    "is_feature_enabled",
]
