"""
Pagination classes shared across the API.

Per ``plans/_conventions.md`` §5:
- default page size: 25
- max page size: 200
- page-number pagination by default; ledger endpoints (Phase 1) will use
  ``CursorPagination`` and live alongside this module.
"""

from __future__ import annotations

from rest_framework.pagination import CursorPagination, PageNumberPagination


class DefaultPageNumberPagination(PageNumberPagination):
    """Default page-number pagination for list endpoints."""

    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 200


class LedgerCursorPagination(CursorPagination):
    """Cursor pagination for append-only ledger endpoints (inventory, finance, ...)."""

    page_size = 50
    max_page_size = 200
    ordering = "-id"
    cursor_query_param = "cursor"
