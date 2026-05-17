"""M02 — auth_service + permission_service unit tests."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.users.exceptions import (
    AccountLocked,
    IdentifierUnknown,
    InactiveAccount,
    InvalidCredentials,
    OTPAttemptsExceeded,
    OTPExpired,
    OTPInvalid,
)
from apps.users.models import LoginAttempt, OTPPurpose, Permission, Role, RolePermission, UserRole
from apps.users.services import auth_service, permission_service, request_otp, verify_otp

pytestmark = pytest.mark.django_db


@pytest.fixture
def alice(user_factory):
    return user_factory(
        email="alice@example.test",
        mobile="9000000001",
        employee_code="EMP-A1",
        password="correct-horse",
    )


# ---------------------------------------------------------------------------
# resolve_identifier
# ---------------------------------------------------------------------------


def test_resolve_identifier_by_email(alice):
    user, _ = auth_service.resolve_identifier("alice@example.test")
    assert user.pk == alice.pk


def test_resolve_identifier_by_mobile(alice):
    user, _ = auth_service.resolve_identifier("9000000001")
    assert user.pk == alice.pk


def test_resolve_identifier_by_emp_code(alice):
    user, _ = auth_service.resolve_identifier("emp-a1")  # case-insensitive
    assert user.pk == alice.pk


def test_resolve_identifier_unknown_raises():
    with pytest.raises(IdentifierUnknown):
        auth_service.resolve_identifier("nope@example.test")


# ---------------------------------------------------------------------------
# password_login + lockout
# ---------------------------------------------------------------------------


def test_password_login_success(alice):
    user = auth_service.password_login("alice@example.test", "correct-horse")
    assert user.pk == alice.pk
    assert LoginAttempt.objects.filter(ok=True, identifier="alice@example.test").exists()


def test_password_login_wrong_password_raises(alice):
    with pytest.raises(InvalidCredentials):
        auth_service.password_login("alice@example.test", "nope")


def test_password_login_inactive_raises(user_factory):
    user_factory(email="ghost@example.test", password="x" * 12, is_active=False)
    with pytest.raises(InactiveAccount):
        auth_service.password_login("ghost@example.test", "x" * 12)


def test_password_login_locks_after_threshold(alice):
    for _ in range(auth_service.LOCKOUT_THRESHOLD):
        with pytest.raises(InvalidCredentials):
            auth_service.password_login("alice@example.test", "wrong")
    with pytest.raises(AccountLocked):
        auth_service.password_login("alice@example.test", "correct-horse")


# ---------------------------------------------------------------------------
# OTP request + verify
# ---------------------------------------------------------------------------


def test_request_otp_creates_log(alice):
    log = request_otp("alice@example.test", purpose=OTPPurpose.LOGIN)
    assert log.identifier == "alice@example.test"
    # Default smart-fallback prefers SMS when mobile is on file.
    assert log.channel == "SMS"
    assert log.code_hash and len(log.code_hash) == 64


def test_request_otp_smart_fallback_to_email(alice, settings):
    settings.OTP_FORCE_FAIL_CHANNELS = {"SMS"}
    log = request_otp("alice@example.test")
    assert log.channel == "EMAIL"


def test_verify_otp_succeeds_with_known_code(alice, settings):
    from apps.users.services.notify_service import OTP_SINK

    settings.OTP_SINK_ALWAYS_ON = True
    OTP_SINK.clear()
    request_otp("alice@example.test")
    code = OTP_SINK[-1].code
    user = verify_otp("alice@example.test", code)
    assert user.pk == alice.pk


def test_verify_otp_wrong_code_raises(alice):
    request_otp("alice@example.test")
    with pytest.raises(OTPInvalid):
        verify_otp("alice@example.test", "000000")


def test_verify_otp_expired_raises(alice):
    log = request_otp("alice@example.test")
    log.expires_at = timezone.now() - timedelta(seconds=1)
    log.save(update_fields=["expires_at"])
    with pytest.raises(OTPExpired):
        verify_otp("alice@example.test", "000000")


def test_verify_otp_attempts_exceeded(alice):
    log = request_otp("alice@example.test")
    log.attempts = auth_service.OTP_MAX_ATTEMPTS
    log.save(update_fields=["attempts"])
    with pytest.raises(OTPAttemptsExceeded):
        verify_otp("alice@example.test", "000000")


# ---------------------------------------------------------------------------
# permission_service
# ---------------------------------------------------------------------------


def test_user_has_returns_true_for_assigned_permission(user_factory):
    user = user_factory()
    role = Role.objects.create(code="R1", name="R1")
    perm = Permission.objects.create(code="x.view_item", name="View", module="x")
    RolePermission.objects.create(role=role, permission=perm)
    UserRole.objects.create(user=user, role=role)
    assert permission_service.user_has(user, "x.view_item")


def test_user_has_returns_false_when_not_assigned(user_factory):
    user = user_factory()
    assert not permission_service.user_has(user, "x.manage_item")


def test_user_has_superuser_wildcard(user_factory):
    user = user_factory(is_superuser=True, is_staff=True)
    assert permission_service.user_has(user, "literally.anything")
