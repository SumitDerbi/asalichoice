"""Auth endpoints: login, refresh, logout, current user.

The full identity surface (signup, password reset, OTP, RBAC) lands in
M02. This module provides only what phase 0 needs.
"""

from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from apps.core.audit import audit
from apps.core.audit.models import AuditAction

from .serializers import LoginSerializer, UserSerializer
from .throttling import LoginRateThrottle


class LoginView(APIView):
    """``POST /api/v1/auth/login/`` — exchange email + password for JWTs."""

    permission_classes = (AllowAny,)
    throttle_classes = (LoginRateThrottle,)
    authentication_classes: tuple = ()

    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        audit(
            instance=user,
            action=AuditAction.LOGIN,
            actor=user,
        )
        return Response(
            {
                "access": serializer.validated_data["access"],
                "refresh": serializer.validated_data["refresh"],
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class RefreshView(TokenRefreshView):
    """``POST /api/v1/auth/refresh/`` — rotate a refresh token.

    Thin wrapper around SimpleJWT's view so the URL stays inside the
    ``/auth/`` namespace and we can adjust later without breaking the
    admin-UI client.
    """

    permission_classes = (AllowAny,)
    authentication_classes: tuple = ()


class LogoutView(APIView):
    """``POST /api/v1/auth/logout/`` — blacklist the supplied refresh token.

    The access token is short-lived (15 min) so we only need to revoke
    the refresh side. Always returns 205 to avoid leaking whether a
    given refresh token existed.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request: Request) -> Response:
        token_str = request.data.get("refresh")
        if token_str:
            try:
                RefreshToken(token_str).blacklist()
            except TokenError:
                # Token already expired/blacklisted — treat as success.
                pass
        if request.user.is_authenticated:
            audit(
                instance=request.user,
                action=AuditAction.LOGOUT,
                actor=request.user,
            )
        return Response(status=status.HTTP_205_RESET_CONTENT)


class MeView(APIView):
    """``GET /api/v1/auth/me/`` — return the authenticated user's record."""

    permission_classes = (IsAuthenticated,)

    def get(self, request: Request) -> Response:
        return Response(UserSerializer(request.user).data)
