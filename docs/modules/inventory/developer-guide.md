# Inventory — Developer guide

## Layout

```
backend/apps/inventory/
├── models.py             # Stock, Batch, Reservation, transfers, adjustments, …
├── exceptions.py         # INV-010 / INV-020 / INV-030 / INV-031
├── permissions.py        # INVENTORY_PERMISSIONS tuple
├── pagination.py         # InventoryLedgerCursorPagination
├── serializers.py
├── views.py
├── urls.py
├── seeders/reason_codes.py
├── services/
│   ├── ledger_service.py        # the only writer of Stock deltas
│   ├── availability_service.py  # reserve / release / consume
│   ├── transfer_service.py      # dispatch / receive / cancel
│   ├── adjustment_service.py    # post
│   ├── wastage_service.py       # post
│   └── count_service.py         # mark_counted / post
└── management/commands/
    ├── seed_reason_codes.py
    └── expire_batches.py
```

The hot rule: **`apps.inventory.services.ledger_service.write()` is
the only function in the codebase that mutates `Stock.qty_on_hand` /
`Stock.qty_reserved`.** Every other service composes the write by
calling it. See [ADR-008](../../adr/008-ledger-driven-stock.md).

## Concurrency

`Stock` rows are mutated under `SELECT … FOR UPDATE` inside a
`transaction.atomic()` block. The concurrency test
(`tests/inventory/test_concurrency.py`) races two reservations
against a single-unit stock and asserts exactly one winner — it is
skipped on SQLite because SQLite ignores row-level locks.

In production (MySQL), expect:

- `LOCK_WAIT_TIMEOUT` (default 50 s) to surface as a 5xx if the lock
  is held too long. Tune `innodb_lock_wait_timeout` for the inventory
  pool.
- Deadlocks possible when two transfers cross paths between the same
  branches. The viewset retries once on `OperationalError(1213)`;
  beyond that the caller sees a domain error.

## Domain errors

All four `INV-*` codes live in `apps/inventory/exceptions.py` and
ride the standard envelope. See [error codes](./error-codes.md).

## Reservations contract

`availability_service.reserve(*, product=None, variant=None, branch,
qty, ref_type, ref_id, actor=None)`:

- Returns the created `Reservation` row.
- Raises `InsufficientStock` (`INV-010`) if
  `qty_on_hand − qty_reserved < qty`.
- `release(reservation)` and `consume(reservation)` enforce the
  ACTIVE → RELEASED / CONSUMED transitions and emit ledger rows.

Callers should pass either `product` _or_ `variant`, never both.

## Branch transfer hooks

`transfer_service.dispatch(transfer, *, actor)` writes one ledger
entry per item against the source branch and flips status to
`IN_TRANSIT`. `receive(transfer, *, actor, items=None)` writes the
destination-side ledger entries; passing partial qtys leaves the
transfer in `PART_RECEIVED`. `cancel(transfer)` is only legal in
`DRAFT`.

The `transfers/{id}/dispatch/` and `transfers/{id}/receive/`
endpoints call `transfer.refresh_from_db()` after the service
returns — the lock-and-mutate service path uses
`all_objects.select_for_update().get(pk=...)` which does not mutate
the caller's local instance.

## Reason codes

Wastage and adjustment line items require a known `ReasonCode`. The
list ships via `python manage.py seed_reason_codes` and includes
`DAMAGED`, `EXPIRED`, `THEFT`, `SYSTEM_DRIFT`, `RECOUNT`. Add new
codes in `apps/inventory/seeders/reason_codes.py` and re-run the
command (idempotent).

## Public service surface

The stable seam for other modules:

```python
from apps.inventory.services import (
    availability_service,   # reserve / release / consume
    ledger_service,         # write — DO NOT call qty mutations directly
)
```

M06 (online order) and M07 (POS) call `availability_service.reserve`
at order placement and `availability_service.consume` at sale.

## Pagination

`/inventory/ledger/` is the only endpoint that uses a cursor:

```python
class InventoryLedgerCursorPagination(LedgerCursorPagination):
    page_size = 50
    max_page_size = 200
    page_size_query_param = "page_size"
    ordering = "-id"        # monotonic surrogate, safe as a cursor key
```

Filters: `branch`, `product`, `variant`, `ref_type`, `reason_code`,
`actor`, `timestamp_from`, `timestamp_to`.

## Tests + coverage

- Backend: `pytest tests/inventory/ -q` → **57 passed, 1 skipped**
  (SQLite concurrency skip).
- Coverage: **87.58 %** (gate ≥ 85 %).
- Postman: `qa/postman/inventory/collection.json` covers the GET
  smokes and the cursor-shape assertion on `/ledger/`.

## Admin-UI

Module lives at `admin-ui/src/modules/inventory/`. Routes are
registered in `admin-ui/src/app/register-modules.ts` and rendered by
`pages/{stock,batches,ledger,reservations,transfers,adjustments,
wastage,counts}-page.tsx`. The ledger page does not use the shared
`InventoryListPage` shell because it must drive `previous`/`next`
cursor URLs from the API response itself.
