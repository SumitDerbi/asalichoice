"""Authentication services: identifier resolution, OTP smart-fallback,
password login with lockout, JWT issuance.

The DRF views in :mod:`apps.users.views` are thin shells around these
functions — see ADR-002 (service layer).
"""

from __future__ import annotations

import hashlib
import logging
import secrets
from collections.abc import Iterable
from datetime import timedelta

from django.contrib.auth import authenticate
from django.db.models import Q
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.audit import audit
from apps.core.audit.models import AuditAction

from ..exceptions import (
    AccountLocked,
    IdentifierUnknown,
    InactiveAccount,
    InvalidCredentials,
    OTPAttemptsExceeded,
    OTPDeliveryFailed,
    OTPExpired,
    OTPInvalid,
    OTPRateLimited,
)
from ..models import LoginAttempt, OTPLog, OTPPurpose, PrimaryIdentifier, User
from . import notify_service

logger = logging.getLogger(__name__)

# Knobs (overridable via SiteSetting in M18; hardcoded here for M02).
OTP_LENGTH = 6
OTP_EXPIRY_SECONDS = 300  # 5 min
OTP_MAX_ATTEMPTS = 5
OTP_RATE_LIMIT_PER_15MIN = 5

LOCKOUT_THRESHOLD = 10
LOCKOUT_WINDOW_MINUTES = 15


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Identifier resolution
# ---------------------------------------------------------------------------


def resolve_identifier(value: str) -> tuple[User, str]:
    """Return ``(user, identifier_type)`` for an inbound identifier.

    Raises :class:`IdentifierUnknown` if nothing matches.
    """

    ident = (value or "").strip()
    if not ident:
        raise IdentifierUnknown()

    user = User.objects.filter(
        Q(email__iexact=ident) | Q(mobile=ident) | Q(employee_code__iexact=ident),
    ).first()
    if user is None:
        raise IdentifierUnknown()

    if user.email and user.email.lower() == ident.lower():
        return user, PrimaryIdentifier.EMAIL
    if user.mobile == ident:
        return user, PrimaryIdentifier.MOBILE
    return user, PrimaryIdentifier.EMP_CODE


# ---------------------------------------------------------------------------
# OTP request + verify
# ---------------------------------------------------------------------------


def _channel_priority(user: User, identifier_type: str, preferred: str | None) -> list[str]:
    """Order channels by smart-fallback policy.

    Phase-1 policy:

    1. ``preferred`` (when supplied and the user has the matching
       contact) wins.
    2. Otherwise SMS first if a mobile is on file, then EMAIL, then
       WHATSAPP last (phase-1 stub always fails for whatsapp so we keep
       the fallback testable).
    """

    seen: set[str] = set()
    ordered: list[str] = []

    def push(channel: str) -> None:
        if channel in seen:
            return
        seen.add(channel)
        ordered.append(channel)

    if preferred:
        push(preferred)

    if user.mobile:
        push("SMS")
    if user.email:
        push("EMAIL")
    if user.mobile:
        push("WHATSAPP")

    return ordered


def _otp_window_count(identifier: str, purpose: str) -> int:
    cutoff = timezone.now() - timedelta(minutes=15)
    return OTPLog.objects.filter(
        identifier=identifier,
        purpose=purpose,
        sent_at__gte=cutoff,
    ).count()


def request_otp(
    identifier: str,
    *,
    purpose: str = OTPPurpose.LOGIN,
    preferred_channel: str | None = None,
    ip: str | None = None,
    user_agent: str = "",
) -> OTPLog:
    """Issue an OTP via the first channel that succeeds.

    Returns the :class:`OTPLog` row on success. Raises
    :class:`OTPRateLimited`, :class:`IdentifierUnknown`,
    :class:`InactiveAccount`, or :class:`OTPDeliveryFailed` otherwise.
    """

    user, _ = resolve_identifier(identifier)  # raises IdentifierUnknown
    if not user.is_active:
        raise InactiveAccount()

    if _otp_window_count(identifier, purpose) >= OTP_RATE_LIMIT_PER_15MIN:
        raise OTPRateLimited()

    code = "".join(secrets.choice("0123456789") for _ in range(OTP_LENGTH))
    code_hash = _sha256(code)
    expires_at = timezone.now() + timedelta(seconds=OTP_EXPIRY_SECONDS)

    channels = _channel_priority(user, identifier_type="", preferred=preferred_channel)
    chosen_channel: str | None = None
    for channel in channels:
        # Skip channels the user has no contact for.
        if channel in {"SMS", "WHATSAPP"} and not user.mobile:
            continue
        if channel == "EMAIL" and not user.email:
            continue
        if notify_service.send_otp(channel, identifier, code, purpose=purpose):  # type: ignore[arg-type]
            chosen_channel = channel
            break

    if chosen_channel is None:
        raise OTPDeliveryFailed()

    return OTPLog.objects.create(
        identifier=identifier,
        channel=chosen_channel,
        code_hash=code_hash,
        purpose=purpose,
        expires_at=expires_at,
        ip=ip,
        user_agent=user_agent[:512],
    )


def verify_otp(
    identifier: str,
    code: str,
    *,
    purpose: str = OTPPurpose.LOGIN,
) -> User:
    """Validate an OTP and return the matching user.

    Marks the OTP row verified on success; increments ``attempts`` and
    raises an appropriate exception on failure.
    """

    user, _ = resolve_identifier(identifier)

    otp = (
        OTPLog.objects.filter(identifier=identifier, purpose=purpose, verified_at__isnull=True)
        .order_by("-sent_at")
        .first()
    )
    if otp is None:
        raise OTPInvalid()

    if otp.expires_at <= timezone.now():
        raise OTPExpired()

    if otp.attempts >= OTP_MAX_ATTEMPTS:
        raise OTPAttemptsExceeded()

    if _sha256(code) != otp.code_hash:
        otp.attempts += 1
        otp.save(update_fields=["attempts", "updated_at"])
        raise OTPInvalid()

    otp.verified_at = timezone.now()
    otp.save(update_fields=["verified_at", "updated_at"])
    return user


# ---------------------------------------------------------------------------
# Password login + lockout
# ---------------------------------------------------------------------------


def _recent_failed_count(identifier: str) -> int:
    cutoff = timezone.now() - timedelta(minutes=LOCKOUT_WINDOW_MINUTES)
    return LoginAttempt.objects.filter(
        identifier=identifier,
        ok=False,
        ts__gte=cutoff,
    ).count()


def password_login(
    identifier: str,
    password: str,
    *,
    ip: str | None = None,
    user_agent: str = "",
) -> User:
    """Authenticate by identifier + password.

    Records every attempt in :class:`LoginAttempt`. Raises
    :class:`AccountLocked` once the failure threshold is hit within the
    lockout window.
    """

    ident = (identifier or "").strip()
    if _recent_failed_count(ident) >= LOCKOUT_THRESHOLD:
        LoginAttempt.objects.create(
            identifier=ident,
            ip=ip,
            ok=False,
            reason="locked",
            user_agent=user_agent[:512],
        )
        raise AccountLocked()

    user = authenticate(username=ident, password=password)
    if user is None:
        # `authenticate` returns None for both wrong-password and inactive-user
        # cases (ModelBackend.user_can_authenticate). Disambiguate explicitly.
        existing = User.all_objects.filter(
            Q(email__iexact=ident) | Q(mobile=ident) | Q(employee_code__iexact=ident),
        ).first()
        if existing is not None and not existing.is_active:
            LoginAttempt.objects.create(
                identifier=ident,
                ip=ip,
                ok=False,
                reason="inactive",
                user_agent=user_agent[:512],
            )
            raise InactiveAccount()
        LoginAttempt.objects.create(
            identifier=ident,
            ip=ip,
            ok=False,
            reason="invalid",
            user_agent=user_agent[:512],
        )
        raise InvalidCredentials()

    if not user.is_active:
        LoginAttempt.objects.create(
            identifier=ident,
            ip=ip,
            ok=False,
            reason="inactive",
            user_agent=user_agent[:512],
        )
        raise InactiveAccount()

    LoginAttempt.objects.create(
        identifier=ident,
        ip=ip,
        ok=True,
        reason="",
        user_agent=user_agent[:512],
    )
    return user


# ---------------------------------------------------------------------------
# JWT issuance
# ---------------------------------------------------------------------------


def issue_tokens(user: User, *, branch_id: int | None = None) -> dict[str, str]:
    """Mint an access + refresh pair, optionally embedding ``branch_id``.

    The branch_id claim lets downstream services pick a default branch
    without consulting the DB; :class:`apps.master.middleware.BranchContextMiddleware`
    still validates the X-Branch-Id header on every request.
    """

    refresh = RefreshToken.for_user(user)
    if branch_id is not None:
        refresh["branch_id"] = branch_id
        refresh.access_token["branch_id"] = branch_id
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


# ---------------------------------------------------------------------------
# Password reset (uses OTP under the hood)
# ---------------------------------------------------------------------------


def request_password_reset(
    identifier: str,
    *,
    preferred_channel: str | None = None,
    ip: str | None = None,
    user_agent: str = "",
) -> OTPLog:
    return request_otp(
        identifier,
        purpose=OTPPurpose.RESET,
        preferred_channel=preferred_channel,
        ip=ip,
        user_agent=user_agent,
    )


def confirm_password_reset(identifier: str, code: str, new_password: str) -> User:
    user = verify_otp(identifier, code, purpose=OTPPurpose.RESET)
    user.set_password(new_password)
    user.save(update_fields=["password", "updated_at"])
    audit(instance=user, action=AuditAction.OTHER, after={"password_reset": True}, actor=user)
    return user


def send_user_invite(
    user: User, *, preferred_channel: str | None = None, ip: str | None = None, user_agent: str = ""
) -> None:
    """Generate a password-reset OTP and send an invite notification to the user."""
    # Pick identifier: prefer email, then mobile, then employee_code
    identifier = user.email or user.mobile or user.employee_code
    if not identifier:
        raise ValueError("User has no identifier to send invite.")
    # Generate password-reset OTP
    request_otp(
        identifier,
        purpose="RESET",
        preferred_channel=preferred_channel,
        ip=ip,
        user_agent=user_agent,
    )
    # Compose invite message (stub: just logs OTP)
    # In real implementation, this would send a link or code to set password
    # For now, the OTP is sent via notify_service.send_otp inside request_otp
    # Optionally, you could add a custom message or audit here
    return


__all__: Iterable[str] = (
    "LOCKOUT_THRESHOLD",
    "LOCKOUT_WINDOW_MINUTES",
    "OTP_EXPIRY_SECONDS",
    "OTP_LENGTH",
    "OTP_MAX_ATTEMPTS",
    "confirm_password_reset",
    "issue_tokens",
    "password_login",
    "request_otp",
    "request_password_reset",
    "resolve_identifier",
    "verify_otp",
)
