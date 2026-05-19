"""M05 Inventory — pagination tuned for the ledger endpoint.

DRF's :class:`CursorPagination` keys the cursor on a single field. For
the inventory ledger we want newest-first ordering with a stable
tiebreak. ``id`` is monotonic with insertion order (and therefore with
``timestamp`` for the append-only ledger), so ``-id`` is the safest
cursor key — it cannot collide and survives clock skew on the server.

This subclass also opts in to a tunable ``page_size`` via query param
because the admin UI needs to page through long histories quickly.
"""

from __future__ import annotations

from apps.core.api.pagination import LedgerCursorPagination


class InventoryLedgerCursorPagination(LedgerCursorPagination):
    """Cursor pagination for ``/api/v1/inventory/ledger/``.

    * ``ordering = "-id"`` — newest first, stable, collision-free.
    * ``page_size`` defaults to 50 and is overridable via
      ``?page_size=<n>`` up to 200.
    """

    page_size = 50
    max_page_size = 200
    page_size_query_param = "page_size"
    ordering = "-id"


__all__ = ["InventoryLedgerCursorPagination"]
