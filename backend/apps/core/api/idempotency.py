"""
Idempotency-Key middleware/mixin.

Convention (``plans/_conventions.md`` §5): mutating endpoints accept
an ``Idempotency-Key`` header. Repeated requests with the same key
within a 24-hour window return the cached response instead of
re-executing the side effect.

Storage strategy:

1. **Django cache** (Redis in prod, locmem in dev) is the primary
   store. Keyed by ``(user_id, method, path, idempotency-key)`` so
   the same key from two different users on two different endpoints
   does not collide.
2. The cache backend is configured globally; this mixin does not
   require Redis to be present. If the cache is the locmem default
   (test / dev), keys still de-dupe inside the same process.
3. A DB-backed fallback table can land alongside Redis hardening in
   phase 2; the contract documented here stays the same.

Usage::

    class OrderViewSet(IdempotencyKeyMixin, BaseModelViewSet):
        idempotent_methods = ("POST",)   # default
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from typing import Any, ClassVar

from django.core.cache import cache
from rest_framework.request import Request
from rest_framework.response import Response

IDEMPOTENCY_HEADER = "Idempotency-Key"
IDEMPOTENCY_TTL_SECONDS = 60 * 60 * 24  # 24h
_CACHE_PREFIX = "idem:v1"


def _cache_key(*, user_id: int | str | None, method: str, path: str, key: str) -> str:
    raw = f"{user_id or 'anon'}|{method.upper()}|{path}|{key}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"{_CACHE_PREFIX}:{digest}"


class IdempotencyKeyMixin:
    """ViewSet mixin: cache successful mutating responses under their key.

    Only responses with a 2xx status are cached — failures should be
    retried until they succeed. The cached payload is a tuple of
    ``(status_code, data)``; headers other than ``Idempotency-Replay``
    are not preserved (clients can re-derive them).
    """

    idempotent_methods: ClassVar[Iterable[str]] = ("POST", "PUT", "PATCH")

    def initial(self, request: Request, *args: Any, **kwargs: Any) -> None:
        super().initial(request, *args, **kwargs)  # type: ignore[misc]
        request._idempotency_cache_key = None  # type: ignore[attr-defined]
        if request.method not in self.idempotent_methods:
            return
        key = request.headers.get(IDEMPOTENCY_HEADER)
        if not key:
            return
        user_id = getattr(getattr(request, "user", None), "pk", None)
        cache_key = _cache_key(user_id=user_id, method=request.method, path=request.path, key=key)
        request._idempotency_cache_key = cache_key  # type: ignore[attr-defined]
        cached = cache.get(cache_key)
        if cached is not None:
            status_code, data = cached
            raise _IdempotencyReplay(status_code=status_code, data=data)

    def handle_exception(self, exc: Exception):  # type: ignore[override]
        if isinstance(exc, _IdempotencyReplay):
            response = Response(exc.data, status=exc.status_code)
            response["Idempotency-Replay"] = "true"
            return response
        return super().handle_exception(exc)  # type: ignore[misc]

    def finalize_response(  # type: ignore[override]
        self,
        request: Request,
        response: Response,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        response = super().finalize_response(request, response, *args, **kwargs)  # type: ignore[misc]
        cache_key = getattr(request, "_idempotency_cache_key", None)
        # Replays already carry the header; do not overwrite their cache.
        if (
            cache_key
            and 200 <= response.status_code < 300
            and response.get("Idempotency-Replay") != "true"
        ):
            cache.set(
                cache_key,
                (response.status_code, response.data),
                IDEMPOTENCY_TTL_SECONDS,
            )
        return response


class _IdempotencyReplay(Exception):  # noqa: N818 - internal sentinel, not a public error
    """Internal sentinel raised from ``initial`` to short-circuit dispatch."""

    def __init__(self, *, status_code: int, data: Any) -> None:
        self.status_code = status_code
        self.data = data
        super().__init__("idempotency replay")
