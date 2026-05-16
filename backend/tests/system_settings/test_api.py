"""API endpoint tests for the system-settings resources."""

from __future__ import annotations

import pytest

from apps.system_settings.models import (
    ContactInfo,
    FeatureToggle,
    IntegrationKey,
    SiteSetting,
    SocialLink,
)

pytestmark = pytest.mark.django_db


def _super(user_factory):
    return user_factory(is_staff=True, is_superuser=True)


def _staff(user_factory):
    return user_factory(is_staff=True, is_superuser=False)


# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------


def test_anonymous_cannot_list_settings(api_client):
    client = api_client()
    resp = client.get("/api/v1/system-settings/")
    assert resp.status_code == 401


def test_staff_without_super_role_forbidden(api_client, user_factory):
    client = api_client(_staff(user_factory))
    resp = client.get("/api/v1/system-settings/")
    assert resp.status_code == 403


def test_super_admin_can_list_settings(api_client, user_factory):
    client = api_client(_super(user_factory))
    resp = client.get("/api/v1/system-settings/")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Site settings CRUD
# ---------------------------------------------------------------------------


def test_create_setting(api_client, user_factory):
    client = api_client(_super(user_factory))
    resp = client.post(
        "/api/v1/system-settings/",
        {
            "key": "otp.length",
            "value_json": 6,
            "scope": "global",
            "description": "OTP length.",
        },
        format="json",
    )
    assert resp.status_code == 201, resp.content
    assert SiteSetting.objects.filter(key="otp.length").exists()


def test_secret_value_masked_in_list(api_client, user_factory):
    SiteSetting.objects.create(
        key="payments.secret",
        value_json="supersecret",
        is_secret=True,
    )
    client = api_client(_super(user_factory))
    resp = client.get("/api/v1/system-settings/")
    assert resp.status_code == 200
    body = resp.json()
    results = body.get("results", body)
    masked = [r for r in results if r["key"] == "payments.secret"]
    assert masked
    assert masked[0]["value_json"] == "***"


# ---------------------------------------------------------------------------
# Feature toggles CRUD
# ---------------------------------------------------------------------------


def test_create_feature_toggle(api_client, user_factory):
    client = api_client(_super(user_factory))
    resp = client.post(
        "/api/v1/feature-toggles/",
        {"key": "checkout.cod", "enabled": True, "rollout_percentage": 100},
        format="json",
    )
    assert resp.status_code == 201, resp.content
    assert FeatureToggle.objects.filter(key="checkout.cod").exists()


# ---------------------------------------------------------------------------
# Integration keys CRUD + reveal
# ---------------------------------------------------------------------------


def test_create_integration_key_encrypts_value(api_client, user_factory):
    client = api_client(_super(user_factory))
    resp = client.post(
        "/api/v1/integration-keys/",
        {
            "provider": "razorpay",
            "key_name": "api_key",
            "value": "rzp_test_xyz",
        },
        format="json",
    )
    assert resp.status_code == 201, resp.content
    row = IntegrationKey.objects.get(provider="razorpay", key_name="api_key")
    assert bytes(row.value_encrypted) != b""
    assert b"rzp_test_xyz" not in bytes(row.value_encrypted)
    # List response masks value.
    body = resp.json()
    assert body["value"] == "***"


def test_reveal_integration_key_returns_plaintext_and_audits(
    api_client, user_factory, capture_audit
):
    row = IntegrationKey(provider="msg91", key_name="auth_key")
    row.set_secret("plaintext-msg91")
    row.save()
    client = api_client(_super(user_factory))
    resp = client.get(f"/api/v1/integration-keys/{row.pk}/reveal/")
    assert resp.status_code == 200, resp.content
    assert resp.json()["value"] == "plaintext-msg91"
    # An audit row was emitted.
    rows = capture_audit()
    assert any(r.model == "system_settings.IntegrationKey" for r in rows)


# ---------------------------------------------------------------------------
# Other resources — smoke
# ---------------------------------------------------------------------------


def test_social_link_crud(api_client, user_factory):
    client = api_client(_super(user_factory))
    resp = client.post(
        "/api/v1/social-links/",
        {"platform": "facebook", "url": "https://example.com/fb"},
        format="json",
    )
    assert resp.status_code == 201, resp.content
    assert SocialLink.objects.count() == 1


def test_contact_info_crud(api_client, user_factory):
    client = api_client(_super(user_factory))
    resp = client.post(
        "/api/v1/contact-info/",
        {
            "label": "HQ",
            "email": "ops@example.test",
            "phone": "+91-1234567890",
            "is_primary": True,
        },
        format="json",
    )
    assert resp.status_code == 201, resp.content
    assert ContactInfo.objects.count() == 1


# ---------------------------------------------------------------------------
# Seeder
# ---------------------------------------------------------------------------


def test_seed_settings_is_idempotent(db):
    from django.core.management import call_command

    call_command("seed_settings")
    first_count = SiteSetting.objects.count()
    assert first_count > 0
    call_command("seed_settings")
    assert SiteSetting.objects.count() == first_count
