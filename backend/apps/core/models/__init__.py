"""Abstract model primitives — re-exported for convenient imports.

The concrete :class:`AuditLog` model is also re-exported here so Django's
app-loading machinery (which imports ``<app>.models``) discovers and
registers it during ``makemigrations`` / ``migrate``.
"""

from __future__ import annotations

from ..audit.models import AuditLog
from .base import ActiveOnlyManager, AuditableModel, BaseModel, SoftDeleteModel, TimeStampedModel

__all__ = [
    "ActiveOnlyManager",
    "AuditLog",
    "AuditableModel",
    "BaseModel",
    "SoftDeleteModel",
    "TimeStampedModel",
]
