"""
Abstract model primitives shared by every module.

Every concrete model in the platform inherits from :class:`BaseModel`
unless it has a strong reason not to (raw lookup tables, throughput-
critical ledgers that opt out — they must still document why and add
their model label to :data:`apps.core.checks.BASE_MODEL_EXEMPTIONS`).

Composition:
    TimeStampedModel  → created_at / updated_at
    SoftDeleteModel   → is_active / deleted_at / objects vs all_objects
    AuditableModel    → created_by / updated_by (settings.AUTH_USER_MODEL)
    BaseModel         → all three, abstract

The auditing of *changes* is handled by :func:`apps.core.audit.audit`
on the service layer — these fields just record provenance.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


# ---------------------------------------------------------------------------
# TimeStamped
# ---------------------------------------------------------------------------
class TimeStampedModel(models.Model):
    """Adds ``created_at`` / ``updated_at`` columns auto-managed by Django."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ---------------------------------------------------------------------------
# Soft delete
# ---------------------------------------------------------------------------
class ActiveOnlyManager(models.Manager):
    """Default manager: only returns rows where ``is_active=True``."""

    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(is_active=True)


class SoftDeleteModel(models.Model):
    """Soft-delete mixin.

    ``objects`` is restricted to active rows; ``all_objects`` is the
    unfiltered manager and must be used for admin / restore flows.

    Calling :meth:`delete` performs a soft delete (sets ``is_active=False``
    and ``deleted_at`` to now). Use :meth:`hard_delete` for the rare cases
    where a real ``DELETE`` is required (e.g. GDPR erasure jobs).
    """

    is_active = models.BooleanField(default=True, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = ActiveOnlyManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
        base_manager_name = "all_objects"

    def delete(self, using=None, keep_parents=False):  # type: ignore[override]
        """Soft delete: flag the row inactive instead of removing it."""

        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_active", "deleted_at"], using=using)
        # Return a (count, by_label) tuple compatible with QuerySet.delete().
        return (1, {self._meta.label: 1})

    def hard_delete(self, using=None, keep_parents=False):
        """Permanently remove the row from the database."""

        return super().delete(using=using, keep_parents=keep_parents)

    def restore(self) -> None:
        """Undo a previous soft delete."""

        self.is_active = True
        self.deleted_at = None
        self.save(update_fields=["is_active", "deleted_at"])


# ---------------------------------------------------------------------------
# Auditable
# ---------------------------------------------------------------------------
class AuditableModel(models.Model):
    """Records the actor that created / last updated the row.

    The ``users.User`` model lands in M02; until then we point at
    ``settings.AUTH_USER_MODEL`` (which falls back to Django's default
    user). Both fields are nullable so background jobs and migrations
    that don't carry an actor still work.
    """

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        editable=False,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        editable=False,
    )

    class Meta:
        abstract = True


# ---------------------------------------------------------------------------
# BaseModel
# ---------------------------------------------------------------------------
class BaseModel(TimeStampedModel, SoftDeleteModel, AuditableModel):
    """Default base for every concrete model in the platform."""

    class Meta:
        abstract = True
        base_manager_name = "all_objects"
