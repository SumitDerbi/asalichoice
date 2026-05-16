"""DRF serializers for the auth + users endpoints."""

from __future__ import annotations

from typing import Any

from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.api import BaseModelSerializer

from .models import User


class LoginSerializer(serializers.Serializer):
    """Validates credentials and mints an access + refresh pair."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        email = attrs["email"].strip().lower()
        password = attrs["password"]
        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password,
        )
        if user is None or not user.is_active:
            # Django's authenticate() returns None for inactive accounts
            # too, so this branch covers both bad creds and disabled users.
            raise serializers.ValidationError(
                {"detail": "Invalid email or password."},
                code="authentication_failed",
            )
        refresh = RefreshToken.for_user(user)
        attrs["user"] = user
        attrs["access"] = str(refresh.access_token)
        attrs["refresh"] = str(refresh)
        return attrs


class UserSerializer(BaseModelSerializer):
    """Public representation of a user — never includes secrets.

    Inherits :class:`apps.core.api.BaseModelSerializer` (plan 008) which
    marks the BaseModel audit + soft-delete columns read-only by
    default. All fields here happen to be read-only too — the serializer
    is currently only used by ``GET`` endpoints — but the inheritance
    documents the canonical pattern for module serializers.
    """

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "mobile",
            "name",
            "display_name",
            "is_staff",
            "is_superuser",
            "is_active",
            "date_joined",
        )
        read_only_fields = fields

    display_name = serializers.CharField(read_only=True)
    date_joined = serializers.DateTimeField(source="created_at", read_only=True)
