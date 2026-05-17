"""M02 — auth API integration tests covering identifier-based login + OTP."""

from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework import status

from apps.users.services.notify_service import OTP_SINK

pbkdf2 = pytest.mark.django_db


@pbkdf2
def test_login_with_identifier_email(api_client, user_factory):
    user_factory(email="ident@example.test", password="pw-ident-1")
    resp = api_client().post(
        reverse("users:login"),
        {"identifier": "ident@example.test", "password": "pw-ident-1"},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["access"]


@pbkdf2
def test_login_with_identifier_mobile(api_client, user_factory):
    user_factory(email="m@example.test", mobile="9111111111", password="pw-mobile-1")
    resp = api_client().post(
        reverse("users:login"),
        {"identifier": "9111111111", "password": "pw-mobile-1"},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK


@pbkdf2
def test_login_with_employee_code(api_client, user_factory):
    user_factory(email="emp@example.test", employee_code="EMP-API-1", password="pw-emp-1")
    resp = api_client().post(
        reverse("users:login"),
        {"identifier": "EMP-API-1", "password": "pw-emp-1"},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK


@pbkdf2
def test_login_unknown_identifier_returns_invalid_credentials(api_client):
    resp = api_client().post(
        reverse("users:login"),
        {"identifier": "ghost@nowhere", "password": "x"},
        format="json",
    )
    # Account existence is not leaked: returns AUTH-001 (invalid credentials).
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json()["error"]["code"] == "AUTH-001"


@pbkdf2
def test_otp_request_and_verify_e2e(api_client, user_factory, settings):
    user_factory(email="otp@example.test", mobile="9222222222", password="pw-otp-1")
    settings.OTP_SINK_ALWAYS_ON = True
    client = api_client()
    OTP_SINK.clear()
    resp = client.post(
        reverse("users:otp-request"),
        {"identifier": "otp@example.test"},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    code = OTP_SINK[-1].code
    resp = client.post(
        reverse("users:otp-verify"),
        {"identifier": "otp@example.test", "code": code},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["access"]


@pbkdf2
def test_me_endpoint_returns_payload(api_client, user_factory):
    user_factory(email="me@example.test", password="pw-me-1")
    client = api_client()
    login = client.post(
        reverse("users:login"),
        {"identifier": "me@example.test", "password": "pw-me-1"},
        format="json",
    )
    token = login.json()["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    resp = client.get(reverse("users:me"))
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["email"] == "me@example.test"
    assert "permissions" in body
    assert "branches" in body
