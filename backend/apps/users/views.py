"""Auth + user/role/permission endpoints for M02."""

from __future__ import annotations

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from apps.core.api.viewsets import BaseModelViewSet
from apps.core.audit import audit
from apps.core.audit.models import AuditAction

from .exceptions import CannotDeleteSelf, SystemRoleProtected
from .models import Permission, Role, User, UserBranchAccess, UserRole
from .serializers import (
    IdentifierLoginSerializer,
    OTPRequestSerializer,
    OTPVerifySerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    PermissionSerializer,
    RoleSerializer,
    UserBranchAccessSerializer,
    UserRoleSerializer,
    UserSerializer,
)
from .services import (
    confirm_password_reset,
    issue_tokens,
    password_login,
    request_otp,
    request_password_reset,
    serialize_me,
    verify_otp,
)
from .throttling import LoginRateThrottle

# ---------------------------------------------------------------------------
# Sessions (refresh token listing/revoke)
# ---------------------------------------------------------------------------


class SessionsView(APIView):
    """GET: List all active refresh tokens (sessions) for the current user.
    POST: Revoke (blacklist) a specific refresh token for the current user.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        tokens = OutstandingToken.objects.filter(user=user).order_by("-created_at")
        sessions = []
        for t in tokens:
            sessions.append(
                {
                    "jti": t.jti,
                    "created_at": t.created_at,
                    "expires_at": t.expires_at,
                    "ip": t.ip if hasattr(t, "ip") else None,
                    "user_agent": t.user_agent if hasattr(t, "user_agent") else None,
                    "blacklisted": BlacklistedToken.objects.filter(token=t).exists(),
                }
            )
        return Response({"sessions": sessions})

    def post(self, request):
        """Revoke (blacklist) a specific refresh token by JTI."""
        jti = request.data.get("jti")
        if not jti:
            return Response({"error": "Missing jti"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = OutstandingToken.objects.get(user=request.user, jti=jti)
        except OutstandingToken.DoesNotExist:
            return Response({"error": "Token not found"}, status=status.HTTP_404_NOT_FOUND)
        if BlacklistedToken.objects.filter(token=token).exists():
            return Response({"detail": "Already revoked"}, status=status.HTTP_200_OK)
        BlacklistedToken.objects.create(token=token)
        return Response({"detail": "Revoked"}, status=status.HTTP_200_OK)


def _client_ip(request: Request) -> str | None:
    xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _ua(request: Request) -> str:
    return request.META.get("HTTP_USER_AGENT", "")[:512]


# ---------------------------------------------------------------------------
# Login + refresh + logout + me
# ---------------------------------------------------------------------------


class LoginView(APIView):
    """``POST /api/v1/auth/login/`` — identifier + password.

    Accepts ``identifier`` (email / mobile / employee_code) and
    ``password``; falls back to ``email`` for phase-0 compatibility.
    """

    permission_classes = (AllowAny,)
    throttle_classes = (LoginRateThrottle,)
    authentication_classes: tuple = ()

    def post(self, request: Request) -> Response:
        # Phase-0 compat: accept ``email`` as an alias for ``identifier``.
        if "identifier" not in request.data and "email" in request.data:
            data = {**request.data, "identifier": request.data["email"]}
        else:
            data = request.data
        ser = IdentifierLoginSerializer(data=data)
        ser.is_valid(raise_exception=True)
        user = password_login(
            ser.validated_data["identifier"],
            ser.validated_data["password"],
            ip=_client_ip(request),
            user_agent=_ua(request),
        )
        tokens = issue_tokens(user)
        audit(instance=user, action=AuditAction.LOGIN, actor=user)
        return Response(
            {**tokens, "user": serialize_me(user)},
            status=status.HTTP_200_OK,
        )


class RefreshView(TokenRefreshView):
    permission_classes = (AllowAny,)
    authentication_classes: tuple = ()


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request: Request) -> Response:
        token_str = request.data.get("refresh")
        if token_str:
            try:
                RefreshToken(token_str).blacklist()
            except TokenError:
                pass
        if request.user.is_authenticated:
            audit(instance=request.user, action=AuditAction.LOGOUT, actor=request.user)
        return Response(status=status.HTTP_205_RESET_CONTENT)


class MeView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request) -> Response:
        from apps.core.context import current_branch_id

        return Response(serialize_me(request.user, branch_id=current_branch_id()))


# ---------------------------------------------------------------------------
# OTP + password reset
# ---------------------------------------------------------------------------


class _OTPRequestThrottle(ScopedRateThrottle):
    scope_attr = "throttle_scope"


class OTPRequestView(APIView):
    permission_classes = (AllowAny,)
    throttle_classes = (_OTPRequestThrottle,)
    throttle_scope = "otp"
    authentication_classes: tuple = ()

    def post(self, request: Request) -> Response:
        ser = OTPRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        otp = request_otp(
            ser.validated_data["identifier"],
            purpose=ser.validated_data["purpose"],
            preferred_channel=ser.validated_data.get("preferred_channel"),
            ip=_client_ip(request),
            user_agent=_ua(request),
        )
        return Response(
            {
                "channel": otp.channel,
                "expires_at": otp.expires_at.isoformat(),
                "identifier": otp.identifier,
            },
            status=status.HTTP_200_OK,
        )


class OTPVerifyView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes: tuple = ()

    def post(self, request: Request) -> Response:
        ser = OTPVerifySerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = verify_otp(
            ser.validated_data["identifier"],
            ser.validated_data["code"],
            purpose=ser.validated_data["purpose"],
        )
        tokens = issue_tokens(user, branch_id=ser.validated_data.get("branch_id"))
        audit(instance=user, action=AuditAction.LOGIN, actor=user, after={"channel": "OTP"})
        return Response(
            {**tokens, "user": serialize_me(user)},
            status=status.HTTP_200_OK,
        )


class PasswordResetRequestView(APIView):
    permission_classes = (AllowAny,)
    throttle_classes = (_OTPRequestThrottle,)
    throttle_scope = "otp"
    authentication_classes: tuple = ()

    def post(self, request: Request) -> Response:
        ser = PasswordResetRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        otp = request_password_reset(
            ser.validated_data["identifier"],
            preferred_channel=ser.validated_data.get("preferred_channel"),
            ip=_client_ip(request),
            user_agent=_ua(request),
        )
        return Response(
            {"channel": otp.channel, "expires_at": otp.expires_at.isoformat()},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes: tuple = ()

    def post(self, request: Request) -> Response:
        ser = PasswordResetConfirmSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        confirm_password_reset(
            ser.validated_data["identifier"],
            ser.validated_data["code"],
            ser.validated_data["new_password"],
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Admin CRUD: users / roles / permissions / user-roles / branch-access
# ---------------------------------------------------------------------------


class UserViewSet(BaseModelViewSet):
    @action(
        detail=True,
        methods=["post"],
        url_path="resend-invite",
        permission_classes=[IsAuthenticated],
    )
    def resend_invite(self, request, pk=None):
        """Resend an invite (password-reset OTP) to the user."""
        from .services import send_user_invite

        user = self.get_object()
        send_user_invite(
            user,
            ip=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        return Response({"detail": "Invite resent."}, status=200)

    queryset = User.objects.all().prefetch_related("user_roles__role", "branch_access")
    serializer_class = UserSerializer
    required_perms = ("users.view_user", "users.manage_user")
    search_fields = ("email", "mobile", "employee_code", "name")

    def perform_destroy(self, instance: User) -> None:
        if instance.pk == self.request.user.pk:
            raise CannotDeleteSelf()
        super().perform_destroy(instance)


class RoleViewSet(BaseModelViewSet):
    queryset = Role.objects.all().prefetch_related("permissions")
    serializer_class = RoleSerializer
    required_perms = ("users.view_role", "users.manage_role")
    search_fields = ("code", "name")

    def perform_destroy(self, instance: Role) -> None:
        if instance.is_system:
            raise SystemRoleProtected()
        super().perform_destroy(instance)


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """Catalog endpoint — permissions are seeded, never user-created."""

    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = None  # small enumerated list; client renders as a grid


class UserRoleViewSet(BaseModelViewSet):
    queryset = UserRole.objects.all().select_related("role", "user", "branch")
    serializer_class = UserRoleSerializer
    required_perms = ("users.assign_role",)


class UserBranchAccessViewSet(BaseModelViewSet):
    queryset = UserBranchAccess.objects.all().select_related("user", "branch")
    serializer_class = UserBranchAccessSerializer
    required_perms = ("users.view_branch_access", "users.manage_branch_access")

    @action(detail=False, methods=["post"], url_path="set-default")
    def set_default(self, request: Request) -> Response:
        user_id = request.data.get("user_id")
        branch_id = request.data.get("branch_id")
        if not user_id or not branch_id:
            return Response({"detail": "user_id and branch_id are required."}, status=400)
        UserBranchAccess.objects.filter(user_id=user_id).update(is_default=False)
        UserBranchAccess.objects.filter(user_id=user_id, branch_id=branch_id).update(
            is_default=True
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
