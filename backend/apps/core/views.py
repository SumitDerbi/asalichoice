"""Views for the ``apps.core`` app."""

from __future__ import annotations

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
                },
                response_only=True,
            )
        ],
    )
    def get(self, request: Request) -> Response:
        return Response(
            {
                "status": "ok",
                "version": getattr(settings, "APP_VERSION", "0.0.0"),
                "time": timezone.now().isoformat(),
            },
            status=status.HTTP_200_OK,
        )
