"""Django admin registrations for system-settings models."""

from __future__ import annotations

from django.contrib import admin

from .models import ContactInfo, FeatureToggle, IntegrationKey, SiteSetting, SocialLink


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ("key", "scope", "branch_id", "is_secret", "updated_at")
    list_filter = ("scope", "is_secret")
    search_fields = ("key", "description")


@admin.register(FeatureToggle)
class FeatureToggleAdmin(admin.ModelAdmin):
    list_display = ("key", "enabled", "rollout_percentage", "updated_at")
    list_filter = ("enabled",)
    search_fields = ("key", "description")


@admin.register(IntegrationKey)
class IntegrationKeyAdmin(admin.ModelAdmin):
    list_display = ("provider", "key_name", "is_active", "updated_at")
    list_filter = ("provider", "is_active")
    search_fields = ("provider", "key_name", "description")
    readonly_fields = ("value_encrypted",)


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ("platform", "url", "is_active")
    list_filter = ("is_active",)


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ("label", "email", "phone", "is_primary", "is_active")
    list_filter = ("is_primary", "is_active")
    search_fields = ("label", "email", "phone")
