"""Custom authentication backend supporting multi-identifier login.

Resolves ``identifier`` (passed as ``username=`` in
``django.contrib.auth.authenticate``) by matching against ``email``,
``mobile``, or ``employee_code`` in turn. The OTP flow doesn't go
through Django's auth backend at all — it issues tokens directly from
:mod:`apps.users.services.auth_service`.
"""

from __future__ import annotations

from typing import Any

from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from .models import User


class IdentifierBackend(ModelBackend):
    """Authenticate by email OR mobile OR employee_code."""

    def authenticate(  # type: ignore[override]
        self,
        request: Any = None,
        username: str | None = None,
        password: str | None = None,
        **kwargs: Any,
    ) -> User | None:
        if not username or password is None:
            return None
        identifier = username.strip()
        user = User.objects.filter(
            Q(email__iexact=identifier)
            | Q(mobile=identifier)
            | Q(employee_code__iexact=identifier),
        ).first()
        if user is None:
            return None
        if not user.check_password(password):
            return None
        if not self.user_can_authenticate(user):
            return None
        return user
