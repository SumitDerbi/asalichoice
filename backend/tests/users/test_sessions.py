import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

pytestmark = pytest.mark.django_db


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh), str(refresh.access_token)


def test_sessions_list_and_revoke(api_client, user_factory):
    user = user_factory(email="sessiontest@example.com", password="pw1234")
    refresh1, access1 = get_tokens_for_user(user)
    refresh2, access2 = get_tokens_for_user(user)
    client = api_client(user=user)
    # List sessions
    resp = client.get(reverse("users:sessions"))
    assert resp.status_code == status.HTTP_200_OK
    sessions = resp.json()["sessions"]
    assert len(sessions) >= 2
    jtis = [s["jti"] for s in sessions]
    # Revoke one session
    resp2 = client.post(reverse("users:sessions"), {"jti": jtis[0]}, format="json")
    assert resp2.status_code == status.HTTP_200_OK
    # List again, should show blacklisted
    resp3 = client.get(reverse("users:sessions"))
    assert resp3.status_code == status.HTTP_200_OK
    sessions2 = resp3.json()["sessions"]
    found = [s for s in sessions2 if s["jti"] == jtis[0]]
    assert found and found[0]["blacklisted"]
