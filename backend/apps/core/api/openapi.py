"""
drf-spectacular postprocessing hook — injects the AsliChoice error
envelope schema into every operation's documented responses.

Wire in ``config/settings/base.py``::

    SPECTACULAR_SETTINGS["POSTPROCESSING_HOOKS"] = [
        "apps.core.api.openapi.add_error_envelope",
    ]

The hook is idempotent: running it on an already-processed schema is a
no-op.
"""

from __future__ import annotations

from typing import Any

ERROR_ENVELOPE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["error"],
    "properties": {
        "error": {
            "type": "object",
            "required": ["code", "message"],
            "properties": {
                "code": {
                    "type": "string",
                    "example": "API-400",
                    "description": (
                        "Stable error code; namespace prefixes are listed in "
                        "plans/_conventions.md §5."
                    ),
                },
                "message": {
                    "type": "string",
                    "example": "Validation failed.",
                },
                "details": {
                    "type": "object",
                    "additionalProperties": True,
                    "description": (
                        "Optional per-field validation errors or domain-" "specific context."
                    ),
                    "default": {},
                },
            },
        }
    },
}

_ENVELOPE_REF = "#/components/schemas/ErrorEnvelope"
_DEFAULT_RESPONSES: dict[str, str] = {
    "400": "Validation failed.",
    "401": "Authentication required.",
    "403": "Forbidden.",
    "404": "Not found.",
    "409": "Conflict.",
    "429": "Throttled.",
}


def add_error_envelope(result: dict[str, Any], **_: Any) -> dict[str, Any]:
    """Inject the ``ErrorEnvelope`` component + default error responses."""
    components = result.setdefault("components", {})
    schemas = components.setdefault("schemas", {})
    schemas.setdefault("ErrorEnvelope", ERROR_ENVELOPE_SCHEMA)

    paths = result.get("paths", {}) or {}
    for _path, methods in paths.items():
        if not isinstance(methods, dict):
            continue
        for method, operation in methods.items():
            if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                continue
            responses = operation.setdefault("responses", {})
            for status_code, description in _DEFAULT_RESPONSES.items():
                responses.setdefault(
                    status_code,
                    {
                        "description": description,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": _ENVELOPE_REF},
                            }
                        },
                    },
                )
    return result
