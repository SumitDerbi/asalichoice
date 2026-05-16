"""Smoke tests for the public health endpoint."""

from __future__ import annotations

import pytest
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient

# Health now reports live master-entity counts (M01/03 §6), so each test
# needs DB access.
pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


def test_health_returns_ok(api_client: APIClient) -> None:
    """``GET /api/v1/health/`` returns 200 with status/version/time."""
    response = api_client.get("/api/v1/health/")

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["status"] == "ok"
    assert isinstance(body["version"], str) and body["version"]
    assert isinstance(body["time"], str) and body["time"]
    # Response time is normalized to UTC with a ``Z`` suffix (per OpenAPI example).
    assert body["time"].endswith("Z")


@override_settings(APP_VERSION="9.9.9-test")
def test_health_reads_app_version_setting(api_client: APIClient) -> None:
    """The endpoint must read ``settings.APP_VERSION`` (not a hardcoded value)."""
    response = api_client.get("/api/v1/health/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["version"] == "9.9.9-test"


def test_health_is_public(api_client: APIClient) -> None:
    """Health endpoint must not require authentication."""
    # No credentials set — should still succeed.
    response = api_client.get("/api/v1/health/")
    assert response.status_code == status.HTTP_200_OK


def test_error_envelope_on_method_not_allowed(api_client: APIClient) -> None:
    """DRF-handled errors are wrapped in the standard error envelope."""
    response = api_client.post("/api/v1/health/", data={})

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == "API-405"
    assert isinstance(body["error"]["message"], str) and body["error"]["message"]
    assert isinstance(body["error"]["details"], dict)
