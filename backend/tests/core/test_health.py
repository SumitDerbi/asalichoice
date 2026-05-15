"""Smoke tests for the public health endpoint."""

from __future__ import annotations

import pytest
from rest_framework import status
from rest_framework.test import APIClient


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
