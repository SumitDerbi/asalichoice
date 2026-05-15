"""
``RequestContextMiddleware`` — populates the per-request context with
actor, IP, and user-agent so the service layer (and :func:`audit`) can
access them without holding a reference to the request object.
"""

from __future__ import annotations

from collections.abc import Callable

from django.http import HttpRequest, HttpResponse

from ..context import RequestContext, reset_request_context, set_request_context


def _client_ip(request: HttpRequest) -> str | None:
    """Best-effort client IP extraction.

    Honours ``X-Forwarded-For`` (left-most value) because the cPanel /
    Passenger deployment terminates TLS behind Apache; falls back to
    ``REMOTE_ADDR`` otherwise.
    """

    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip() or None
    return request.META.get("REMOTE_ADDR") or None


class RequestContextMiddleware:
    """Bind a :class:`RequestContext` for the duration of the request."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        user = getattr(request, "user", None)
        actor = user if user is not None and getattr(user, "is_authenticated", False) else None
        ctx = RequestContext(
            actor=actor,
            ip=_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:512] or None,
            branch_id=None,  # branch resolution lands in M02; left None here.
        )
        token = set_request_context(ctx)
        try:
            return self.get_response(request)
        finally:
            reset_request_context(token)
