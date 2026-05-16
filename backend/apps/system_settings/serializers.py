"""DRF serializers for system-settings resources."""

from __future__ import annotations

from typing import Any

from rest_framework import serializers

from apps.core.api.serializers import BaseModelSerializer

from .models import ContactInfo, FeatureToggle, IntegrationKey, SiteSetting, SocialLink


class SiteSettingSerializer(BaseModelSerializer):
    class Meta:
        model = SiteSetting
        fields = (
            "id",
            "key",
            "value_json",
            "scope",
            "branch_id",
            "description",
            "is_secret",
            "created_at",
            "updated_at",
        )

    def to_representation(self, instance: SiteSetting) -> dict[str, Any]:
        data = super().to_representation(instance)
        if instance.is_secret and not self.context.get("reveal_secret", False):
            data["value_json"] = "***"
        return data

    def validate(self, attrs):
        instance = SiteSetting(**{**({"id": self.instance.id} if self.instance else {}), **attrs})
        instance.clean()
        return attrs


class FeatureToggleSerializer(BaseModelSerializer):
    class Meta:
        model = FeatureToggle
        fields = (
            "id",
            "key",
            "enabled",
            "rollout_percentage",
            "description",
            "created_at",
            "updated_at",
        )


class IntegrationKeySerializer(BaseModelSerializer):
    """Hides the encrypted bytes; accepts plaintext via the write-only ``value``."""

    value = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = IntegrationKey
        fields = (
            "id",
            "provider",
            "key_name",
            "description",
            "is_active",
            "value",
            "created_at",
            "updated_at",
        )

    def to_representation(self, instance: IntegrationKey) -> dict[str, Any]:
        data = super().to_representation(instance)
        if self.context.get("reveal_secret", False):
            data["value"] = instance.get_secret()
        else:
            data["value"] = "***" if instance.value_encrypted else ""
        return data

    def create(self, validated_data):
        plaintext = validated_data.pop("value", "")
        instance = IntegrationKey(**validated_data)
        if plaintext:
            instance.set_secret(plaintext)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        plaintext = validated_data.pop("value", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if plaintext:
            instance.set_secret(plaintext)
        instance.save()
        return instance


class SocialLinkSerializer(BaseModelSerializer):
    class Meta:
        model = SocialLink
        fields = ("id", "platform", "url", "is_active", "created_at", "updated_at")


class ContactInfoSerializer(BaseModelSerializer):
    class Meta:
        model = ContactInfo
        fields = (
            "id",
            "label",
            "email",
            "phone",
            "address",
            "is_primary",
            "is_active",
            "created_at",
            "updated_at",
        )
