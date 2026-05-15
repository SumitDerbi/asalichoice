"""
Audit log — every write goes through the service layer which calls
:func:`apps.core.audit.audit` to record an entry here.

Per ``_meta.yaml`` the retention is seven years; pruning is handled by
a future maintenance task, not by this app.
"""

from __future__ import annotations

from .models import AuditLog
from .service import audit

__all__ = ["AuditLog", "audit"]
