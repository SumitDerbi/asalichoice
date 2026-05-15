"""
Custom DRF exception handler producing the standard error envelope.

Envelope shape (per ``plans/_conventions.md`` §5)::

    {
        "error": {
            "code": "<DOMAIN>-<NNN>",
            "message": "Human-readable message",
            "details": { ... }
        }
    }

The handler wraps DRF's default ``exception_handler`` so that all built-in
exceptions (authentication, permission, validation, throttled, ...) keep
producing correct HTTP status codes while their payloads are normalised.
"""

from __future__ import annotations

from typing import Any

from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

# Mapping of DRF/Django exception classes to the error-code prefix and a
# generic numeric suffix. Module-specific handlers (M01+) will register
# more precise codes via their own service layer; this is the fallback.
_DEFAULT_CODE_BY_STATUS: dict[int, str] = {
    status.HTTP_400_BAD_REQUEST: "API-400",
    status.HTTP_401_UNAUTHORIZED: "AUTH-401",
    status.HTTP_403_FORBIDDEN: "AUTH-403",
    status.HTTP_404_NOT_FOUND: "API-404",
    status.HTTP_405_METHOD_NOT_ALLOWED: "API-405",
    status.HTTP_406_NOT_ACCEPTABLE: "API-406",
    status.HTTP_409_CONFLICT: "API-409",
    status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: "API-415",
    status.HTTP_429_TOO_MANY_REQUESTS: "API-429",
    status.HTTP_500_INTERNAL_SERVER_ERROR: "API-500",
}


def _code_for(exc: Exception, response_status: int) -> str:
    """Return the error code for the given exception / status code."""
    if isinstance(exc, exceptions.NotAuthenticated):
        return "AUTH-401"
    if isinstance(exc, exceptions.AuthenticationFailed):
        return "AUTH-401"
    if isinstance(exc, exceptions.PermissionDenied):
        return "AUTH-403"
    if isinstance(exc, exceptions.NotFound):
        return "API-404"
    if isinstance(exc, exceptions.MethodNotAllowed):
        return "API-405"
    if isinstance(exc, exceptions.NotAcceptable):
        return "API-406"
    if isinstance(exc, exceptions.UnsupportedMediaType):
        return "API-415"
    if isinstance(exc, exceptions.Throttled):
        return "API-429"
    if isinstance(exc, exceptions.ValidationError):
        return "API-400"
    return _DEFAULT_CODE_BY_STATUS.get(response_status, "API-500")


def envelope_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """Wrap DRF's default handler with the AsliChoice error envelope."""
    response = drf_exception_handler(exc, context)
    if response is None:
        # Unhandled exception — let Django's 500 handler take over so that
        # DEBUG tracebacks / production 500 pages still work as expected.
        return None

    original = response.data
    message = _extract_message(original, exc)
    details = _extract_details(original)

    response.data = {
        "error": {
            "code": _code_for(exc, response.status_code),
            "message": message,
            "details": details,
        }
    }
    return response


def _extract_message(payload: Any, exc: Exception) -> str:
    """Pick a single human-readable message from a DRF error payload."""
    if isinstance(payload, dict):
        detail = payload.get("detail")
        if isinstance(detail, str):
            return detail
        if detail is not None:
            return str(detail)
        # Validation errors: pick the first message we find.
        for value in payload.values():
            if isinstance(value, list) and value:
                return str(value[0])
            if isinstance(value, str):
                return value
    if isinstance(payload, list) and payload:
        return str(payload[0])
    return str(exc) or "An error occurred."


def _extract_details(payload: Any) -> dict[str, Any]:
    """Return per-field validation errors when present, else an empty dict."""
    if isinstance(payload, dict):
        # Strip the generic ``detail`` key — it's already in ``message``.
        return {k: v for k, v in payload.items() if k != "detail"}
    if isinstance(payload, list):
        return {"errors": payload}
    return {}
