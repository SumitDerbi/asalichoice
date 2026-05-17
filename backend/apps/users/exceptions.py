"""Domain exceptions for the users module.

Two prefixes:

* ``AUTH-*`` covers authentication failures (login, OTP, password
  reset).
* ``USR-*`` covers user / role / permission CRUD.
"""

from __future__ import annotations

from apps.core.api import DomainError

# ---------------------------------------------------------------------------
# AUTH-*
# ---------------------------------------------------------------------------


class InvalidCredentials(DomainError):  # noqa: N818
    """Login attempted with wrong identifier / password combination."""

    default_code = "AUTH-001"
    default_message = "Invalid identifier or password."
    default_status = 400


class InactiveAccount(DomainError):  # noqa: N818
    """Login attempted against a disabled user."""

    default_code = "AUTH-002"
    default_message = "This account is disabled. Contact an administrator."
    default_status = 400


class AccountLocked(DomainError):  # noqa: N818
    """Too many failed login attempts — temporarily locked."""

    default_code = "AUTH-003"
    default_message = "Account temporarily locked due to repeated failed logins."
    default_status = 423  # Locked


class IdentifierUnknown(DomainError):  # noqa: N818
    """OTP / password-reset requested for an identifier we don't know."""

    default_code = "AUTH-004"
    default_message = "No user matches that identifier."
    default_status = 404


class OTPInvalid(DomainError):  # noqa: N818
    """OTP code does not match the latest issued code for the identifier."""

    default_code = "AUTH-010"
    default_message = "Invalid or expired OTP."
    default_status = 400


class OTPExpired(DomainError):  # noqa: N818
    default_code = "AUTH-011"
    default_message = "OTP has expired. Please request a new one."
    default_status = 400


class OTPAttemptsExceeded(DomainError):  # noqa: N818
    default_code = "AUTH-012"
    default_message = "Too many invalid OTP attempts. Request a new code."
    default_status = 429


class OTPRateLimited(DomainError):  # noqa: N818
    default_code = "AUTH-013"
    default_message = "Too many OTP requests. Please wait before requesting again."
    default_status = 429


class OTPDeliveryFailed(DomainError):  # noqa: N818
    """All channels (primary + fallbacks) failed to deliver the OTP."""

    default_code = "AUTH-014"
    default_message = "Could not deliver OTP on any configured channel."
    default_status = 503


# ---------------------------------------------------------------------------
# USR-*
# ---------------------------------------------------------------------------


class DuplicateIdentifier(DomainError):  # noqa: N818
    default_code = "USR-001"
    default_message = "Another user already has this identifier."
    default_status = 409


class CannotDeleteSelf(DomainError):  # noqa: N818
    default_code = "USR-010"
    default_message = "You cannot delete your own account."
    default_status = 400


class SystemRoleProtected(DomainError):  # noqa: N818
    default_code = "USR-020"
    default_message = "System roles cannot be modified or deleted."
    default_status = 400


class BranchAccessRequired(DomainError):  # noqa: N818
    """User has zero branch-access rows and tried to switch branch."""

    default_code = "USR-030"
    default_message = "User has no branches assigned."
    default_status = 400
