"""Views for the ``apps.core`` app."""

from __future__ import annotations

try:
    from datetime import UTC  # Python 3.11+
except ImportError:  # pragma: no cover - Python 3.10 fallback
    UTC = UTC

from django.conf import settings
from django.utils import timezone
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    """Liveness / readiness probe.

    Returns service status, application version, and the current server time.
    Public (no auth) so that load balancers and uptime monitors can hit it.
    """

    authentication_classes: list = []
    permission_classes = [AllowAny]

    @extend_schema(
        operation_id="health",
        summary="Service health check",
        description=(
            "Returns ``{status: ok, version, time}`` when the service is up. "
            "Intended for load balancers and uptime monitors — no authentication required."
        ),
        responses={
            200: {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "example": "ok"},
                    "version": {"type": "string", "example": "1.0.0"},
                    "time": {"type": "string", "format": "date-time"},
                    "masters": {
                        "type": "object",
                        "additionalProperties": {"type": "integer"},
                    },
                },
                "required": ["status", "version", "time"],
            }
        },
        examples=[
            OpenApiExample(
                "Healthy",
                value={
                    "status": "ok",
                    "version": "1.0.0",
                    "time": "2026-05-15T02:56:29Z",
                    "masters": {
                        "branches": 1,
                        "taxes": 3,
                        "categories": 12,
                        "brands": 8,
                    },
                },
                response_only=True,
            )
        ],
    )
    def get(self, request: Request) -> Response:
        # Normalize the timestamp to UTC with a ``Z`` suffix so the response
        # matches the documented OpenAPI example shape.
        now_utc = timezone.now().astimezone(UTC).replace(microsecond=0)
        return Response(
            {
                "status": "ok",
                "version": getattr(settings, "APP_VERSION", "0.0.0"),
                "time": now_utc.isoformat().replace("+00:00", "Z"),
                "masters": _master_counts(),
            },
            status=status.HTTP_200_OK,
        )


def _master_counts() -> dict[str, int]:
    """Return live counts of core master entities for the health probe."""

    try:
        from apps.master.models import Branch, Brand, Category, Tax
    except Exception:  # pragma: no cover - master app may be uninstalled
        return {}
    return {
        "branches": Branch.objects.filter(is_active=True).count(),
        "taxes": Tax.objects.filter(is_active=True).count(),
        "categories": Category.objects.filter(is_active=True).count(),
        "brands": Brand.objects.filter(is_active=True).count(),
    }
