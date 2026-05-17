"""
User identity + RBAC models (M02).

Phase-0 shipped a minimal :class:`User` (email + password) backed by
SimpleJWT. M02 layers on:

* multi-identifier login (email | mobile | employee_code) with a
  ``primary_identifier`` hint and the matching auth backend in
  :mod:`apps.users.auth_backends`;
* :class:`Role` + :class:`Permission` + :class:`RolePermission` for
  RBAC, with :class:`UserRole` providing optional per-branch scoping;
* :class:`UserBranchAccess` — the explicit allow-list the
  ``BranchContextMiddleware`` consults (see ADR-003);
* :class:`OTPLog` and :class:`LoginAttempt` for audit + lockout +
  smart-fallback OTP delivery (see ADR-005).

All concrete models inherit :class:`apps.core.models.BaseModel` so they
get the audit / soft-delete columns; the system check in
``apps.core.checks`` enforces this.
"""

from __future__ import annotations

from typing import Any

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import BaseModel


class PrimaryIdentifier(models.TextChoices):
    EMAIL = "EMAIL", "Email"
    MOBILE = "MOBILE", "Mobile"
    EMP_CODE = "EMP_CODE", "Employee Code"


class UserManager(BaseUserManager):
    """Email-based manager (mobile / employee_code login goes through the
    custom auth backend, not :meth:`create_user`)."""

    use_in_migrations = True

    def _create_user(
        self,
        email: str,
        password: str | None,
        **extra_fields: Any,
    ):
        if not email:
            raise ValueError("Users must have an email address.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra_fields: Any):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str | None = None, **extra_fields: Any):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    """Custom user with multi-identifier login (M02).

    ``email`` remains required and unique (it is still
    ``USERNAME_FIELD``); ``mobile`` and ``employee_code`` are optional
    unique columns that the :mod:`apps.users.auth_backends` backend
    resolves at login time. ``primary_identifier`` is a UI hint —
    services use whichever identifier the caller supplied.
    """

    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=20, unique=True, null=True, blank=True)
    employee_code = models.CharField(max_length=32, unique=True, null=True, blank=True)
    name = models.CharField(max_length=150, blank=True, default="")

    primary_identifier = models.CharField(
        max_length=16,
        choices=PrimaryIdentifier.choices,
        default=PrimaryIdentifier.EMAIL,
        help_text="Preferred identifier surfaced in the login UI.",
    )

    is_staff = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into the Django admin.",
    )

    objects = UserManager()  # type: ignore[misc]

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ("email",)

    def __str__(self) -> str:
        return self.email

    @property
    def display_name(self) -> str:
        return self.name or self.email

    def clean(self) -> None:
        super().clean()
        # Normalise blank strings to NULL so the unique index treats
        # them as "no value" (multiple NULLs allowed) instead of ""
        # (which the unique index would reject on the second insert).
        if self.mobile == "":
            self.mobile = None
        if self.employee_code == "":
            self.employee_code = None
        if not (self.email or self.mobile or self.employee_code):
            raise ValidationError(
                "At least one of email, mobile, or employee_code is required.",
            )


# ---------------------------------------------------------------------------
# RBAC: Permission, Role, RolePermission, UserRole, UserBranchAccess
# ---------------------------------------------------------------------------


class Permission(BaseModel):
    """Application-defined permission row.

    Distinct from Django's built-in ``auth.Permission`` — those are tied
    to ContentTypes and CRUD-shaped; ours are free-form
    ``module.verb_resource`` strings declared in each app's
    ``permissions.py``. The :command:`seed_permissions` command scans
    those modules and upserts rows here.
    """

    code = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=150)
    module = models.CharField(max_length=64, db_index=True)
    description = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        ordering = ("module", "code")

    def __str__(self) -> str:
        return self.code


class Role(BaseModel):
    """Named bundle of :class:`Permission` rows."""

    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=255, blank=True, default="")
    is_system = models.BooleanField(
        default=False,
        help_text="System roles are seeded and cannot be deleted via the UI.",
    )

    permissions = models.ManyToManyField(
        Permission,
        through="RolePermission",
        related_name="roles",
        blank=True,
    )

    class Meta:
        ordering = ("code",)

    def __str__(self) -> str:
        return self.code


class RolePermission(BaseModel):
    """Through-table for :attr:`Role.permissions`.

    Modelled explicitly so we can audit grant/revoke events and add
    per-row metadata later.
    """

    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="role_permissions")
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name="role_permissions",
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("role", "permission"),
                name="uniq_role_permission",
            ),
        )

    def __str__(self) -> str:
        return f"{self.role_id}:{self.permission_id}"


class UserRole(BaseModel):
    """Assignment of a :class:`Role` to a :class:`User`.

    ``branch`` is optional — ``NULL`` means the role applies globally.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_roles",
    )
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="user_roles")
    branch = models.ForeignKey(
        "master.Branch",
        on_delete=models.CASCADE,
        related_name="user_roles",
        null=True,
        blank=True,
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("user", "role", "branch"),
                name="uniq_user_role_branch",
            ),
        )

    def __str__(self) -> str:
        scope = f"@{self.branch_id}" if self.branch_id else "@global"
        return f"{self.user_id}:{self.role_id}{scope}"


class UserBranchAccess(BaseModel):
    """Explicit user→branch allow-list consulted by ``BranchContextMiddleware``.

    A user with no rows here cannot pass an ``X-Branch-Id`` header
    (except superusers). ``is_default`` marks the branch the UI should
    pre-select on login.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="branch_access",
    )
    branch = models.ForeignKey(
        "master.Branch",
        on_delete=models.CASCADE,
        related_name="user_access",
    )
    is_default = models.BooleanField(default=False)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("user", "branch"),
                name="uniq_user_branch_access",
            ),
        )

    def __str__(self) -> str:
        return f"{self.user_id}@{self.branch_id}"


# ---------------------------------------------------------------------------
# OTP + LoginAttempt
# ---------------------------------------------------------------------------


class OTPChannel(models.TextChoices):
    SMS = "SMS", "SMS"
    EMAIL = "EMAIL", "Email"
    WHATSAPP = "WHATSAPP", "WhatsApp"


class OTPPurpose(models.TextChoices):
    LOGIN = "LOGIN", "Login"
    RESET = "RESET", "Password reset"
    VERIFY = "VERIFY", "Verify identifier"


class OTPLog(BaseModel):
    """Audit row for every OTP issued.

    ``code_hash`` stores the SHA-256 hash — the plaintext only lives in
    the response body of the issuing request (and in the dev console
    sink). ``verified_at`` flips on successful redemption; ``attempts``
    counts failed verify calls and feeds the per-OTP lockout.
    """

    identifier = models.CharField(max_length=128, db_index=True)
    channel = models.CharField(max_length=16, choices=OTPChannel.choices)
    code_hash = models.CharField(max_length=64)
    purpose = models.CharField(max_length=16, choices=OTPPurpose.choices)
    sent_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True, default="")

    class Meta:
        ordering = ("-sent_at",)
        indexes = (models.Index(fields=("identifier", "purpose", "-sent_at")),)


class LoginAttempt(BaseModel):
    """Every login attempt, success or failure, for audit + lockout."""

    identifier = models.CharField(max_length=128, db_index=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    ok = models.BooleanField(default=False)
    reason = models.CharField(max_length=64, blank=True, default="")
    user_agent = models.CharField(max_length=512, blank=True, default="")
    ts = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-ts",)
        indexes = (models.Index(fields=("identifier", "-ts")),)
