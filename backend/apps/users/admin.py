"""Django admin registration for the User model."""

from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import (
    LoginAttempt,
    OTPLog,
    Permission,
    Role,
    RolePermission,
    User,
    UserBranchAccess,
    UserRole,
)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Minimal admin form for the phase-0 user model."""

    ordering = ("email",)
    list_display = ("email", "name", "is_staff", "is_superuser", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("email", "name", "mobile", "employee_code")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Profile", {"fields": ("name", "mobile", "employee_code", "primary_identifier")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Audit", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff", "is_superuser"),
            },
        ),
    )
    readonly_fields = ("last_login",)
    filter_horizontal = ("groups", "user_permissions")


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "module", "is_active")
    list_filter = ("module", "is_active")
    search_fields = ("code", "name", "module")
    ordering = ("module", "code")


class RolePermissionInline(admin.TabularInline):
    model = RolePermission
    extra = 0
    autocomplete_fields = ("permission",)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_system", "is_active")
    list_filter = ("is_system", "is_active")
    search_fields = ("code", "name")
    inlines = (RolePermissionInline,)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "branch", "is_active")
    list_filter = ("role", "is_active")
    autocomplete_fields = ("user", "role")
    raw_id_fields = ("branch",)
    search_fields = ("user__email", "role__code")


@admin.register(UserBranchAccess)
class UserBranchAccessAdmin(admin.ModelAdmin):
    list_display = ("user", "branch", "is_default", "is_active")
    list_filter = ("is_default", "is_active")
    autocomplete_fields = ("user",)
    raw_id_fields = ("branch",)
    search_fields = ("user__email",)


@admin.register(OTPLog)
class OTPLogAdmin(admin.ModelAdmin):
    list_display = ("identifier", "channel", "purpose", "sent_at", "verified_at", "attempts")
    list_filter = ("channel", "purpose")
    search_fields = ("identifier",)
    readonly_fields = (
        "identifier",
        "channel",
        "code_hash",
        "purpose",
        "sent_at",
        "expires_at",
        "verified_at",
        "attempts",
        "ip",
        "user_agent",
    )


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ("identifier", "ok", "reason", "ip", "ts")
    list_filter = ("ok",)
    search_fields = ("identifier", "ip")
    readonly_fields = ("identifier", "ip", "ok", "reason", "user_agent", "ts")
