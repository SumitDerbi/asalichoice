"""
Domain exceptions + envelope helpers.

Module-specific subclasses live in ``apps/<module>/exceptions.py`` and
all derive from :class:`DomainError`. The DRF exception handler at
:func:`apps.core.exceptions.envelope_exception_handler` catches them
and renders the standard ``{error: {code, message, details}}`` envelope.

Usage::

    from apps.core.api import DomainError

    class InsufficientStock(DomainError):
        default_code = "INV-001"
        default_message = "Insufficient stock"
        default_status = 409
"""

from __future__ import annotations

from typing import Any


class DomainError(Exception):
    """Business-rule violation that must surface as a typed API error.

    Subclasses set ``default_code`` (matches the prefix table in
    ``plans/_conventions.md`` §5), ``default_message`` (human-readable),
    and ``default_status`` (HTTP status code, defaults to 400).
    Per-instance overrides accepted via ``__init__`` kwargs.
    """

    default_code: str = "API-400"
    default_message: str = "Domain error."
    default_status: int = 400

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | None = None,
        status: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.code = code or self.default_code
        self.message = message or self.default_message
        self.status = status or self.default_status
        self.details = details or {}
        super().__init__(self.message)

    def to_envelope(self) -> dict[str, Any]:
        """Return the JSON envelope payload for this error."""
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }
