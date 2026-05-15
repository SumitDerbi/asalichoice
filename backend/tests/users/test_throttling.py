"""LoginRateThrottle: caps anonymous login attempts per IP.

DRF's :class:`SimpleRateThrottle` snapshots ``THROTTLE_RATES`` at class
definition time, so a plain ``override_settings`` of the rate has no
effect at runtime. We monkey-patch the class attribute directly to a
lower bound so the test stays fast.
"""

from __future__ import annotations

import pytest
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from rest_framework import status

from apps.users.throttling import LoginRateThrottle

pbkdf2 = override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.PBKDF2PasswordHasher"])

pytestmark = pytest.mark.django_db


@pbkdf2
def test_login_throttled_after_burst(api_client, user_factory, monkeypatch):
    cache.clear()
    monkeypatch.setattr(
        LoginRateThrottle,
        "THROTTLE_RATES",
        {**LoginRateThrottle.THROTTLE_RATES, "login": "3/min"},
    )
    user_factory(email="hammer@example.test", password="pw-hammer")
    client = api_client()
    url = reverse("users:login")
    payload = {"email": "hammer@example.test", "password": "pw-hammer"}

    for _ in range(3):
        resp = client.post(url, payload, format="json")
        assert resp.status_code == status.HTTP_200_OK

    blocked = client.post(url, payload, format="json")
    assert blocked.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert blocked.json()["error"]["code"] == "API-429"
