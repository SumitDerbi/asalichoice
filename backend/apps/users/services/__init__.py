"""Service-layer entry points for the users module.

See ADR-002 (service layer) for the layering rules.
"""

from .auth_service import (
    LOCKOUT_THRESHOLD,
    LOCKOUT_WINDOW_MINUTES,
    OTP_EXPIRY_SECONDS,
    OTP_LENGTH,
    OTP_MAX_ATTEMPTS,
    confirm_password_reset,
    issue_tokens,
    password_login,
    request_otp,
    request_password_reset,
    resolve_identifier,
    verify_otp,
)
from .notify_service import OTP_SINK, send_otp
from .permission_service import get_user_permissions, serialize_me, user_branches, user_has

__all__ = [
    "LOCKOUT_THRESHOLD",
    "LOCKOUT_WINDOW_MINUTES",
    "OTP_EXPIRY_SECONDS",
    "OTP_LENGTH",
    "OTP_MAX_ATTEMPTS",
    "OTP_SINK",
    "confirm_password_reset",
    "get_user_permissions",
    "issue_tokens",
    "password_login",
    "request_otp",
    "request_password_reset",
    "resolve_identifier",
    "send_otp",
    "serialize_me",
    "user_branches",
    "user_has",
    "verify_otp",
]
