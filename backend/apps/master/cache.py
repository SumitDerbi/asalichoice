"""Versioned cache helper for master-data reads (M01/03 §7).

Keys are namespaced as ``master:v{version}:{domain}:{key}`` where
``version`` comes from the ``master.cache_version`` :class:`SiteSetting`
bumped by :mod:`apps.master.signals`.  Bumping the version effectively
purges every consumer's cache without touching the cache backend.

Per-domain default TTLs (seconds):

* ``taxes``   — 300  (5 minutes)
* ``branches`` —  60  (1 minute)
* ``zones``   — 600  (10 minutes)
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from django.core.cache import cache

T = TypeVar("T")

DEFAULT_TTLS: dict[str, int] = {
    "taxes": 300,
    "branches": 60,
    "zones": 600,
}

_VERSION_KEY = "master.cache_version"


def _current_version() -> int:
    try:
        from apps.system_settings.services import get_setting
    except Exception:  # pragma: no cover - defensive
        return 0
    raw = get_setting(_VERSION_KEY, default=0)
    try:
        return int(raw or 0)
    except (TypeError, ValueError):
        return 0


def cache_key(domain: str, key: str) -> str:
    """Return the fully namespaced cache key."""

    return f"master:v{_current_version()}:{domain}:{key}"


def cached_master(
    domain: str,
    key: str,
    loader: Callable[[], T],
    *,
    ttl: int | None = None,
) -> T:
    """Return the cached value for *key* in *domain*, populating via *loader*."""

    full_key = cache_key(domain, key)
    hit: Any = cache.get(full_key)
    if hit is not None:
        return hit  # type: ignore[no-any-return]
    value = loader()
    cache.set(full_key, value, ttl if ttl is not None else DEFAULT_TTLS.get(domain, 60))
    return value
