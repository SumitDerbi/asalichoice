"""Tests for the envelope exception handler with DomainError (plan 008)."""

from __future__ import annotations

import pytest
from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.core.api import DomainError


class _BoomError(DomainError):
    default_code = "INV-001"
    default_message = "Insufficient stock"
    default_status = 409


class _BoomView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def get(self, request):
        raise _BoomError(details={"available": 3, "requested": 5})


urlpatterns = [path("boom/", _BoomView.as_view())]

pytestmark = pytest.mark.urls(__name__)


def test_domain_error_renders_envelope():
    from rest_framework.test import APIClient

    client = APIClient()
    resp = client.get("/boom/")
    assert resp.status_code == 409
    assert resp.json() == {
        "error": {
            "code": "INV-001",
            "message": "Insufficient stock",
            "details": {"available": 3, "requested": 5},
        }
    }


def test_openapi_postprocessor_injects_error_envelope():
    from apps.core.api.openapi import add_error_envelope

    schema = {
        "paths": {
            "/api/v1/things/": {
                "get": {"responses": {"200": {"description": "ok"}}},
            }
        },
        "components": {},
    }
    out = add_error_envelope(schema)
    assert "ErrorEnvelope" in out["components"]["schemas"]
    responses = out["paths"]["/api/v1/things/"]["get"]["responses"]
    for code in ("400", "401", "403", "404", "409", "429"):
        assert code in responses
        ref = responses[code]["content"]["application/json"]["schema"]["$ref"]
        assert ref.endswith("/ErrorEnvelope")

    # Idempotent: running again is a no-op (no duplicate keys).
    out2 = add_error_envelope(out)
    assert out2["paths"]["/api/v1/things/"]["get"]["responses"]["400"] == responses["400"]
