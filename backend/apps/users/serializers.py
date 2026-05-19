"""DRF serializers for the users module."""

from __future__ import annotations

from typing import Any

from rest_framework import serializers

from apps.core.api import BaseModelSerializer

from .exceptions import DuplicateIdentifier, SystemRoleProtected
from .models import OTPChannel, Permission, Role, User, UserBranchAccess, UserRole

# ---------------------------------------------------------------------------
# Auth payloads
# ---------------------------------------------------------------------------


class IdentifierLoginSerializer(serializers.Serializer):
    """Identifier + password login (extends the phase-0 email-only flow)."""

    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)


class OTPRequestSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    purpose = serializers.ChoiceField(
        choices=("LOGIN", "RESET", "VERIFY"),
        default="LOGIN",
    )
    preferred_channel = serializers.ChoiceField(
        choices=OTPChannel.choices,
        required=False,
        allow_null=True,
        default=None,
    )


class OTPVerifySerializer(serializers.Serializer):
    identifier = serializers.CharField()
    code = serializers.CharField(min_length=4, max_length=8)
    purpose = serializers.ChoiceField(
        choices=("LOGIN", "RESET", "VERIFY"),
        default="LOGIN",
    )
    branch_id = serializers.IntegerField(required=False, allow_null=True, default=None)


class PasswordResetRequestSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    preferred_channel = serializers.ChoiceField(
        choices=OTPChannel.choices,
        required=False,
        allow_null=True,
        default=None,
    )


class PasswordResetConfirmSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    code = serializers.CharField(min_length=4, max_length=8)
    new_password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)


# ---------------------------------------------------------------------------
# Resource serializers
# ---------------------------------------------------------------------------


class PermissionSerializer(BaseModelSerializer):
    class Meta:
        model = Permission
        fields = ("id", "code", "name", "module", "description", "is_active")
        read_only_fields = ("id", "is_active")


class RoleSerializer(BaseModelSerializer):
    permission_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permission.objects.all(),
        source="permissions",
        required=False,
    )

    class Meta:
        model = Role
        fields = (
            "id",
            "code",
            "name",
            "description",
            "is_system",
            "permission_ids",
            "is_active",
        )
        read_only_fields = ("id", "is_system", "is_active")

    def update(self, instance: Role, validated_data: dict[str, Any]) -> Role:
        if instance.is_system and ("code" in validated_data or "permissions" in validated_data):
            raise SystemRoleProtected()
        return super().update(instance, validated_data)


class UserRoleSerializer(BaseModelSerializer):
    role_code = serializers.CharField(source="role.code", read_only=True)
    branch_id = serializers.IntegerField(allow_null=True, required=False)

    class Meta:
        model = UserRole
        fields = ("id", "user", "role", "role_code", "branch", "branch_id", "is_active")
        read_only_fields = ("id", "is_active", "branch_id", "role_code")


class UserBranchAccessSerializer(BaseModelSerializer):
    class Meta:
        model = UserBranchAccess
        fields = ("id", "user", "branch", "is_default", "is_active")
        read_only_fields = ("id", "is_active")


class UserSerializer(BaseModelSerializer):
    """Full user payload (admin-side)."""

    display_name = serializers.CharField(read_only=True)
    date_joined = serializers.DateTimeField(source="created_at", read_only=True)
    password = serializers.CharField(write_only=True, required=False, min_length=8)
    role_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Role.objects.all(),
        required=False,
        write_only=True,
    )
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "mobile",
            "employee_code",
            "name",
            "display_name",
            "primary_identifier",
            "is_staff",
            "is_superuser",
            "is_active",
            "date_joined",
            "password",
            "role_ids",
            "roles",
        )
        read_only_fields = ("id", "display_name", "date_joined", "is_superuser", "roles")

    def get_roles(self, obj: User) -> list[dict]:
        return [
            {"id": ur.role_id, "code": ur.role.code, "branch_id": ur.branch_id}
            for ur in obj.user_roles.select_related("role").filter(is_active=True)
        ]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        # Block duplicate email / mobile / employee_code (case-insensitive
        # for email + employee_code).
        instance = getattr(self, "instance", None)
        for field, lookup in (
            ("email", "iexact"),
            ("mobile", "exact"),
            ("employee_code", "iexact"),
        ):
            value = attrs.get(field)
            if not value:
                continue
            qs = User.objects.filter(**{f"{field}__{lookup}": value})
            if instance is not None:
                qs = qs.exclude(pk=instance.pk)
            if qs.exists():
                raise DuplicateIdentifier(f"User with {field}={value!r} already exists.")
        # Empty strings → None for nullable uniques.
        for field in ("mobile", "employee_code"):
            if attrs.get(field) == "":
                attrs[field] = None
        return attrs

    def create(self, validated_data: dict[str, Any]) -> User:
        from .services import send_user_invite

        roles = validated_data.pop("role_ids", [])
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        for role in roles:
            UserRole.objects.create(user=user, role=role)
        # If no password was provided, trigger invite flow
        if not password:
            send_user_invite(user)
        return user

    def update(self, instance: User, validated_data: dict[str, Any]) -> User:
        roles = validated_data.pop("role_ids", None)
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save(update_fields=["password", "updated_at"])
        if roles is not None:
            existing = {ur.role_id: ur for ur in user.user_roles.filter(branch__isnull=True)}
            wanted_ids = {r.pk for r in roles}
            # Add missing.
            for role in roles:
                if role.pk not in existing:
                    UserRole.objects.create(user=user, role=role)
            # Hard-delete stale (no audit trail value for a placeholder
            # assignment that was probably created seconds ago).
            for role_id, ur in existing.items():
                if role_id not in wanted_ids:
                    ur.delete()
        return user
