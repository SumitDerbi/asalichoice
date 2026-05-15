"""Tests for the storefront -> backend reachability probe."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests
from django.test import Client


@pytest.mark.django_db
def test_backend_health_reachable(client: Client) -> None:
    """When the backend returns 200, the probe returns reachable=true."""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.status_code = 200

    with patch("apps.core.views.requests.get", return_value=mock_response) as mock_get:
        response = client.get("/internal/backend-health/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["reachable"] is True
    assert payload["status_code"] == 200
    assert payload["upstream"].endswith("/health/")
    mock_get.assert_called_once()


@pytest.mark.django_db
def test_backend_health_unreachable(client: Client) -> None:
    """Network errors are translated into HTTP 502 with reachable=false."""
    with patch(
        "apps.core.views.requests.get",
        side_effect=requests.ConnectionError("connection refused"),
    ):
        response = client.get("/internal/backend-health/")

    assert response.status_code == 502
    payload = response.json()
    assert payload["reachable"] is False
    # Error message is a fixed, non-sensitive identifier — exception text
    # is logged server-side only (see apps.core.views.backend_health).
    assert payload["error"] == "backend_unreachable"
