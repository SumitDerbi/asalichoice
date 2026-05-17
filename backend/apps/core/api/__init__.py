"""
Shared DRF baseline for every module's API.

This package codifies the conventions described in
``plans/_conventions.md`` §5 so that module-level API code can stay
thin: pick a viewset base, a serializer base, declare a service, write
the test. The pieces here are intentionally minimal — anything domain-
specific belongs in the module that needs it.

Top-level re-exports keep import paths short for downstream apps::

    from apps.core.api import (
        BaseModelViewSet,
        BaseModelSerializer,
        DefaultPageNumberPagination,
        LedgerCursorPagination,
        DomainError,
        IsSuperAdmin,
        IsBranchScoped,
        HasAnyPermission,
    )
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

# Submodule attribute → (relative module, attribute name).
# Lazy on purpose: importing this package eagerly triggers DRF settings
# resolution (``DEFAULT_PAGINATION_CLASS``) while ``rest_framework`` itself
# is still being imported, which causes a circular ImportError during
# ``manage.py check``. Lazy attribute access sidesteps the cycle while
# keeping the short ``from apps.core.api import X`` form for callers.
_LAZY_EXPORTS: dict[str, tuple[str, str]] = {
    "DomainError": (".exceptions", "DomainError"),
    "BaseSearchFilterBackend": (".filters", "BaseSearchFilterBackend"),
    "IDEMPOTENCY_HEADER": (".idempotency", "IDEMPOTENCY_HEADER"),
    "IdempotencyKeyMixin": (".idempotency", "IdempotencyKeyMixin"),
    "DefaultPageNumberPagination": (".pagination", "DefaultPageNumberPagination"),
    "LedgerCursorPagination": (".pagination", "LedgerCursorPagination"),
    "HasAnyPermission": (".permissions", "HasAnyPermission"),
    "IsBranchScoped": (".permissions", "IsBranchScoped"),
    "IsSuperAdmin": (".permissions", "IsSuperAdmin"),
    "BaseModelSerializer": (".serializers", "BaseModelSerializer"),
    "BurstAnonThrottle": (".throttling", "BurstAnonThrottle"),
    "BurstUserThrottle": (".throttling", "BurstUserThrottle"),
    "BaseModelViewSet": (".viewsets", "BaseModelViewSet"),
}


def __getattr__(name: str):  # PEP 562
    try:
        module_path, attr = _LAZY_EXPORTS[name]
    except KeyError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc
    module = importlib.import_module(module_path, __name__)
    value = getattr(module, attr)
    globals()[name] = value
    return value


if TYPE_CHECKING:  # pragma: no cover - import for type-checkers only
    from .exceptions import DomainError
    from .filters import BaseSearchFilterBackend
    from .idempotency import IDEMPOTENCY_HEADER, IdempotencyKeyMixin
    from .pagination import DefaultPageNumberPagination, LedgerCursorPagination
    from .permissions import HasAnyPermission, IsBranchScoped, IsSuperAdmin
    from .serializers import BaseModelSerializer
    from .throttling import BurstAnonThrottle, BurstUserThrottle
    from .viewsets import BaseModelViewSet

__all__ = [
    "IDEMPOTENCY_HEADER",
    "BaseModelSerializer",
    "BaseModelViewSet",
    "BaseSearchFilterBackend",
    "BurstAnonThrottle",
    "BurstUserThrottle",
    "DefaultPageNumberPagination",
    "DomainError",
    "HasAnyPermission",
    "IdempotencyKeyMixin",
    "IsBranchScoped",
    "IsSuperAdmin",
    "LedgerCursorPagination",
]
