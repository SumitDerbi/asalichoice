"""Tests for the JWT auth skeleton.

Argon2 isn't part of the minimal dev install (plan 005 conftest fixed
the user-factory accordingly). Tests force PBKDF2 via
``override_settings`` so login / refresh exercise the real hash path.
"""

from __future__ import annotations

import pytest
from django.test import override_settings
from django.urls import reverse
from rest_framework import status

pbkdf2 = override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.PBKDF2PasswordHasher"])

pytestmark = pytest.mark.django_db


@pbkdf2
def test_login_happy_path(api_client, user_factory):
    user = user_factory(email="alice@example.test", password="s3cret-pw")
    resp = api_client().post(
        reverse("users:login"),
        {"email": "alice@example.test", "password": "s3cret-pw"},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["access"]
    assert body["refresh"]
    assert body["user"]["email"] == user.email
    assert "password" not in body["user"]


@pbkdf2
def test_login_wrong_password(api_client, user_factory):
    user_factory(email="bob@example.test", password="correct-horse")
    resp = api_client().post(
        reverse("users:login"),
        {"email": "bob@example.test", "password": "wrong"},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    body = resp.json()
    assert body["error"]["code"] == "API-400"
    assert "invalid" in body["error"]["message"].lower()


@pbkdf2
def test_login_inactive_user_rejected(api_client, user_factory):
    user_factory(
        email="ghost@example.test",
        password="hidden-pw",
        is_active=False,
    )
    resp = api_client().post(
        reverse("users:login"),
        {"email": "ghost@example.test", "password": "hidden-pw"},
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pbkdf2
def test_refresh_returns_new_access(api_client, user_factory):
    user_factory(email="carol@example.test", password="pw-carol")
    login = api_client().post(
        reverse("users:login"),
        {"email": "carol@example.test", "password": "pw-carol"},
        format="json",
    )
    refresh_token = login.json()["refresh"]
    resp = api_client().post(
        reverse("users:refresh"),
        {"refresh": refresh_token},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["access"]


def test_me_requires_auth(api_client):
    resp = api_client().get(reverse("users:me"))
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_me_returns_current_user(api_client, user_factory):
    user = user_factory(email="dave@example.test", name="Dave")
    resp = api_client(user=user).get(reverse("users:me"))
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body["email"] == "dave@example.test"
    assert body["name"] == "Dave"


@pbkdf2
def test_logout_blacklists_refresh(api_client, user_factory):
    user_factory(email="erin@example.test", password="pw-erin")
    login = api_client().post(
        reverse("users:login"),
        {"email": "erin@example.test", "password": "pw-erin"},
        format="json",
    )
    tokens = login.json()
    client = api_client()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    resp = client.post(
        reverse("users:logout"),
        {"refresh": tokens["refresh"]},
        format="json",
    )
    assert resp.status_code == status.HTTP_205_RESET_CONTENT

    again = api_client().post(
        reverse("users:refresh"),
        {"refresh": tokens["refresh"]},
        format="json",
    )
    assert again.status_code == status.HTTP_401_UNAUTHORIZED
