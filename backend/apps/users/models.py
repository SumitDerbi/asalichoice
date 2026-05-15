"""
Custom user model for AsliChoice (phase-0 skeleton).

Why custom now: switching ``AUTH_USER_MODEL`` later is painful and
forces a rebuild of every migration that FKs to it. We pay the cost
once, here, with a deliberately minimal shape:

* ``email`` is the login identifier (unique, required).
* ``mobile`` is optional in phase 0; M02 adds a proper identifier
  strategy (email-or-mobile + OTP).
* ``name`` is a single free-text field — splitting into first/last
  is not worth the i18n cost for this product.
* Soft-delete + audit fields come from :class:`apps.core.models.BaseModel`.

The full role / permission stack lands in M02; for now we lean on
Django's :class:`PermissionsMixin` so ``is_staff`` / ``is_superuser``
work out of the box.
"""

from __future__ import annotations

from typing import Any

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from apps.core.models import BaseModel


class UserManager(BaseUserManager):
    """Manager that knows how to hash passwords and build superusers."""

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

    def create_user(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: Any,
    ):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: Any,
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    """Phase-0 custom user. M02 will extend this with roles + OTP."""

    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=20, blank=True, default="")
    name = models.CharField(max_length=150, blank=True, default="")

    is_staff = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into the Django admin.",
    )
    # ``is_active`` is inherited from SoftDeleteModel and doubles as
    # Django's auth "is this account allowed to log in" flag.

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
