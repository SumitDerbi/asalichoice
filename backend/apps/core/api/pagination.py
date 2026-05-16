"""
Pagination classes — canonical home is ``apps.core.api.pagination``.

The legacy ``apps.core.pagination`` module re-exports these names so
old import paths (and the ``REST_FRAMEWORK['DEFAULT_PAGINATION_CLASS']``
setting) keep working.
"""

from __future__ import annotations

from rest_framework.pagination import CursorPagination, PageNumberPagination


class DefaultPageNumberPagination(PageNumberPagination):
    """Page-number pagination for list endpoints (default page size 25)."""

    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 200


class LedgerCursorPagination(CursorPagination):
    """Cursor pagination for append-only ledger endpoints.

    DRF's :class:`CursorPagination` enforces a fixed ``page_size`` and
    does not honour ``page_size_query_param``; ledger subclasses can
    override ``get_page_size`` if they need a configurable size.
    """

    page_size = 50
    ordering = "-id"
    cursor_query_param = "cursor"
