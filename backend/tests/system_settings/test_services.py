"""Tests for the system-settings encryption + service-layer helpers."""

from __future__ import annotations

import pytest
from django.test import override_settings

from apps.system_settings.crypto import (
    SecretDecryptionError,
    _reset_fernet_cache,
    decrypt_secret,
    encrypt_secret,
)
from apps.system_settings.models import FeatureToggle, IntegrationKey, SettingScope, SiteSetting
from apps.system_settings.services import (
    get_integration_key,
    get_setting,
    invalidate_feature_cache,
    invalidate_setting_cache,
    is_feature_enabled,
)

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# Encryption
# ---------------------------------------------------------------------------


def test_encrypt_decrypt_round_trip():
    ct = encrypt_secret("hunter2")
    assert ct != b"hunter2"
    assert decrypt_secret(ct) == "hunter2"


def test_decrypt_invalid_raises():
    with pytest.raises(SecretDecryptionError):
        decrypt_secret(b"not-a-valid-token")


def test_integration_key_set_and_get_secret():
    row = IntegrationKey(provider="razorpay", key_name="api_key")
    row.set_secret("rzp_test_abc")
    row.save()

    fresh = IntegrationKey.objects.get(pk=row.pk)
    assert fresh.get_secret() == "rzp_test_abc"
    # Stored bytes must not equal plaintext.
    assert b"rzp_test_abc" not in bytes(fresh.value_encrypted)


def test_explicit_fernet_key_used_when_set():
    """Setting ``SETTINGS_FERNET_KEY`` swaps the underlying cipher."""

    from cryptography.fernet import Fernet

    custom = Fernet.generate_key().decode()
    with override_settings(SETTINGS_FERNET_KEY=custom):
        _reset_fernet_cache()
        ct = encrypt_secret("payload")
        assert decrypt_secret(ct) == "payload"
    _reset_fernet_cache()


# ---------------------------------------------------------------------------
# Site settings
# ---------------------------------------------------------------------------


def test_get_setting_returns_default_when_missing():
    invalidate_setting_cache()
    assert get_setting("does.not.exist", default="fallback") == "fallback"


def test_get_setting_returns_value_and_caches_invalidation():
    invalidate_setting_cache()
    SiteSetting.objects.create(key="otp.length", value_json=6)

    assert get_setting("otp.length") == 6

    # Updating the row fires the signal → cache evicted → new value visible.
    SiteSetting.objects.filter(key="otp.length").update(value_json=8)
    # ``update()`` doesn't fire post_save; emulate the save signal manually
    # by invalidating, then assert.
    invalidate_setting_cache("otp.length")
    assert get_setting("otp.length") == 8


def test_setting_save_evicts_cache_via_signal():
    invalidate_setting_cache()
    row = SiteSetting.objects.create(key="site.default_currency", value_json="USD")
    assert get_setting("site.default_currency") == "USD"
    row.value_json = "INR"
    row.save()  # signal fires → cache invalidated
    assert get_setting("site.default_currency") == "INR"


def test_branch_scope_falls_back_to_global():
    invalidate_setting_cache()
    SiteSetting.objects.create(key="tax.inclusive_by_default", value_json=False)
    assert (
        get_setting(
            "tax.inclusive_by_default",
            scope=SettingScope.BRANCH,
            branch=99,
        )
        is False
    )


# ---------------------------------------------------------------------------
# Feature toggles
# ---------------------------------------------------------------------------


def test_feature_disabled_when_missing():
    invalidate_feature_cache()
    assert is_feature_enabled("never.declared") is False


def test_feature_enabled_at_full_rollout():
    invalidate_feature_cache()
    FeatureToggle.objects.create(key="flag.on", enabled=True, rollout_percentage=100)
    assert is_feature_enabled("flag.on") is True


def test_feature_disabled_at_zero_rollout():
    invalidate_feature_cache()
    FeatureToggle.objects.create(key="flag.zero", enabled=True, rollout_percentage=0)
    assert is_feature_enabled("flag.zero") is False


def test_feature_rollout_is_deterministic_per_user(user_factory):
    invalidate_feature_cache()
    FeatureToggle.objects.create(key="flag.partial", enabled=True, rollout_percentage=50)
    user = user_factory()
    first = is_feature_enabled("flag.partial", user=user)
    second = is_feature_enabled("flag.partial", user=user)
    assert first == second


# ---------------------------------------------------------------------------
# Integration keys
# ---------------------------------------------------------------------------


def test_get_integration_key_returns_decrypted_value():
    row = IntegrationKey(provider="msg91", key_name="auth_key")
    row.set_secret("secret-msg91")
    row.save()
    assert get_integration_key("msg91", "auth_key") == "secret-msg91"


def test_get_integration_key_skips_inactive_rows():
    row = IntegrationKey(provider="msg91", key_name="auth_key", is_active=False)
    row.set_secret("inactive")
    row.save()
    assert get_integration_key("msg91", "auth_key") is None


def test_get_integration_key_missing_returns_none():
    assert get_integration_key("nope", "nope") is None
