"""
``AuditLog`` model.

Append-only record of every state-changing operation on the platform.
Stored as a concrete model on the ``core`` app so that all modules share
one immutable timeline; per-domain filtering happens via ``model`` /
``action`` / ``branch_id``.

Schema rationale:
    * ``model`` stores the Django model label (``app_label.ModelName``)
      rather than a ``ContentType`` FK — keeps the row self-contained
      and lets us audit cross-DB or removed models without dangling FKs.
    * ``before`` / ``after`` are ``JSONField`` snapshots. They're
      intentionally schemaless so future model changes don't break old
      rows.
    * ``branch_id`` is an int rather than an FK. The ``Branch`` model
      lands in M02; using an int now keeps core decoupled.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models


class AuditAction(models.TextChoices):
    CREATE = "create", "Create"
    UPDATE = "update", "Update"
    DELETE = "delete", "Delete"
    RESTORE = "restore", "Restore"
    LOGIN = "login", "Login"
    LOGOUT = "logout", "Logout"
    OTHER = "other", "Other"


class AuditLog(models.Model):
    """Immutable audit entry."""

    model = models.CharField(max_length=120, db_index=True)
    action = models.CharField(
        max_length=16,
        choices=AuditAction.choices,
        db_index=True,
    )
    object_id = models.CharField(max_length=64, db_index=True, blank=True)
    before = models.JSONField(null=True, blank=True)
    after = models.JSONField(null=True, blank=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    branch_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        app_label = "core"
        verbose_name = "audit log"
        verbose_name_plural = "audit logs"
        ordering = ("-timestamp",)
        indexes = [
            models.Index(fields=["model", "object_id"]),
            models.Index(fields=["actor", "timestamp"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return f"{self.action} {self.model}#{self.object_id} @ {self.timestamp:%Y-%m-%dT%H:%M:%SZ}"

    def save(self, *args, **kwargs):
        """Audit log is append-only — refuse updates after creation."""

        if self.pk is not None:
            raise RuntimeError("AuditLog rows are immutable; create a new row instead.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Audit log rows must not be deleted from application code."""

        raise RuntimeError(
            "AuditLog rows are immutable; deletion is restricted to retention jobs.",
        )
