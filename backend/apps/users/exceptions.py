"""Domain exceptions for the users module.

Per ADR-002 every module exports a typed exception module rooted at
:class:`apps.core.api.DomainError`. The DRF exception handler renders
these through the standard error envelope.
"""

from __future__ import annotations

from apps.core.api import DomainError


class InvalidCredentials(DomainError):  # noqa: N818 - domain error name, suffix would be redundant
    """Login attempted with wrong email + password combination."""

    default_code = "AUTH-001"
    default_message = "Invalid email or password."
    default_status = 400


class InactiveAccount(DomainError):  # noqa: N818 - domain error name, suffix would be redundant
    """Login attempted against a disabled user."""

    default_code = "AUTH-002"
    default_message = "This account is disabled. Contact an administrator."
    default_status = 400
