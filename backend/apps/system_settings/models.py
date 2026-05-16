"""
Models for the system-settings app.

Five concrete models, all inheriting :class:`apps.core.models.BaseModel`:

* :class:`SiteSetting` — generic key/JSON-value store with scope.
* :class:`FeatureToggle` — boolean flag + rollout percentage.
* :class:`IntegrationKey` — secret credential, encrypted at rest.
* :class:`SocialLink` — per-platform URL on the storefront.
* :class:`ContactInfo` — business contact rows.
"""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.models import BaseModel

from .crypto import decrypt_secret, encrypt_secret


class SettingScope(models.TextChoices):
    GLOBAL = "global", "Global"
    BRANCH = "branch", "Branch"


class SiteSetting(BaseModel):
    """Key/value store for runtime configuration.

    The ``value_json`` column accepts any JSON-serialisable value;
    callers cast through :func:`apps.system_settings.services.get_setting`
    which handles defaults.
    """

    key = models.CharField(max_length=128)
    value_json = models.JSONField(null=True, blank=True)
    scope = models.CharField(
        max_length=16,
        choices=SettingScope.choices,
        default=SettingScope.GLOBAL,
    )
    # ``Branch`` lands in M02 — keep as a nullable int until then.
    branch_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    description = models.CharField(max_length=255, blank=True, default="")
    is_secret = models.BooleanField(
        default=False,
        help_text="If True, value is masked in list endpoints until explicitly revealed.",
    )

    class Meta:
        verbose_name = "site setting"
        verbose_name_plural = "site settings"
        ordering = ("key",)
        constraints = [
            # A given key may exist once per (scope, branch_id) combination.
            models.UniqueConstraint(
                fields=("key", "scope", "branch_id"),
                name="uniq_site_setting_key_scope_branch",
            ),
        ]
        indexes = [
            models.Index(fields=("key", "scope")),
        ]

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        suffix = f"@branch:{self.branch_id}" if self.scope == SettingScope.BRANCH else ""
        return f"{self.key}{suffix}"

    def clean(self) -> None:
        if self.scope == SettingScope.BRANCH and self.branch_id is None:
            raise ValidationError({"branch_id": "Required when scope=branch."})
        if self.scope == SettingScope.GLOBAL and self.branch_id is not None:
            raise ValidationError({"branch_id": "Must be null when scope=global."})


class FeatureToggle(BaseModel):
    """Feature flag with optional percentage rollout."""

    key = models.CharField(max_length=128, unique=True)
    enabled = models.BooleanField(default=False)
    rollout_percentage = models.PositiveSmallIntegerField(
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage (0-100) of users the toggle applies to when enabled.",
    )
    description = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        verbose_name = "feature toggle"
        verbose_name_plural = "feature toggles"
        ordering = ("key",)

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return f"{self.key} ({'on' if self.enabled else 'off'} @ {self.rollout_percentage}%)"


class IntegrationKey(BaseModel):
    """Encrypted credential for an external provider (Razorpay, MSG91, ...)."""

    provider = models.CharField(max_length=64)
    key_name = models.CharField(max_length=64)
    value_encrypted = models.BinaryField()
    description = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        verbose_name = "integration key"
        verbose_name_plural = "integration keys"
        ordering = ("provider", "key_name")
        constraints = [
            models.UniqueConstraint(
                fields=("provider", "key_name"),
                name="uniq_integration_key_provider_name",
            ),
        ]

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return f"{self.provider}:{self.key_name}"

    # --- secret helpers --------------------------------------------------
    def set_secret(self, plaintext: str) -> None:
        """Encrypt *plaintext* and stash in :attr:`value_encrypted`."""

        self.value_encrypted = encrypt_secret(plaintext)

    def get_secret(self) -> str:
        """Decrypt and return the stored value."""

        return decrypt_secret(bytes(self.value_encrypted or b""))


class SocialLink(BaseModel):
    """A single social-media URL displayed on the storefront."""

    platform = models.CharField(max_length=32)
    url = models.URLField(max_length=500)

    class Meta:
        verbose_name = "social link"
        verbose_name_plural = "social links"
        ordering = ("platform",)
        constraints = [
            models.UniqueConstraint(fields=("platform",), name="uniq_social_link_platform"),
        ]

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return f"{self.platform}: {self.url}"


class ContactInfo(BaseModel):
    """A contact row (email/phone/address) shown on the storefront."""

    label = models.CharField(max_length=64)
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=32, blank=True, default="")
    address = models.TextField(blank=True, default="")
    is_primary = models.BooleanField(default=False)

    class Meta:
        verbose_name = "contact info"
        verbose_name_plural = "contact info"
        ordering = ("-is_primary", "label")

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return self.label
