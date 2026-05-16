"""End-to-end tests for the idempotency mixin (plan 008).

We mount a throwaway viewset under a test URLconf so we can exercise
the mixin against real DRF dispatch.
"""

from __future__ import annotations

import pytest
from django.core.cache import cache
from django.urls import include, path
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.test import APIClient
from rest_framework.viewsets import GenericViewSet

from apps.core.api import IDEMPOTENCY_HEADER, IdempotencyKeyMixin

_call_count = {"n": 0}


class _DummyViewSet(IdempotencyKeyMixin, GenericViewSet):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def create(self, request, *args, **kwargs):
        _call_count["n"] += 1
        return Response({"n": _call_count["n"]}, status=201)

    @action(detail=False, methods=["post"], url_path="non-idem")
    def non_idem(self, request, *args, **kwargs):
        _call_count["n"] += 1
        return Response({"n": _call_count["n"]}, status=200)


_router = DefaultRouter()
_router.register("things", _DummyViewSet, basename="things")
urlpatterns = [path("api/", include(_router.urls))]


pytestmark = pytest.mark.urls(__name__)


@pytest.fixture(autouse=True)
def _reset():
    cache.clear()
    _call_count["n"] = 0
    yield
    cache.clear()


def test_repeat_key_returns_cached_response():
    client = APIClient()
    headers = {f"HTTP_{IDEMPOTENCY_HEADER.replace('-', '_').upper()}": "abc-123"}

    r1 = client.post("/api/things/", {}, format="json", **headers)
    assert r1.status_code == 201
    assert r1.data == {"n": 1}

    r2 = client.post("/api/things/", {}, format="json", **headers)
    assert r2.status_code == 201
    assert r2.data == {"n": 1}  # cached, not 2
    assert r2["Idempotency-Replay"] == "true"

    # Server-side: handler only ran once.
    assert _call_count["n"] == 1


def test_different_keys_run_independently():
    client = APIClient()
    h_a = {f"HTTP_{IDEMPOTENCY_HEADER.replace('-', '_').upper()}": "key-a"}
    h_b = {f"HTTP_{IDEMPOTENCY_HEADER.replace('-', '_').upper()}": "key-b"}

    r1 = client.post("/api/things/", {}, format="json", **h_a)
    r2 = client.post("/api/things/", {}, format="json", **h_b)
    assert r1.data == {"n": 1}
    assert r2.data == {"n": 2}
    assert _call_count["n"] == 2


def test_no_key_means_no_cache():
    client = APIClient()
    r1 = client.post("/api/things/", {}, format="json")
    r2 = client.post("/api/things/", {}, format="json")
    assert r1.data == {"n": 1}
    assert r2.data == {"n": 2}
