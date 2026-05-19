# ADR-008 — Ledger-driven stock

- **Status**: Accepted
- **Date**: 2026-05-19
- **Decider**: backend team
- **Context plan**: `plans/phase-1-modules/M05-inventory.md`

## Context

M04 deferred all inventory writes to M05 (see
[ADR-007](./007-grn-only-stock-write.md)). M05 now has to decide
**how** stock balances are mutated. The candidates:

1. **Service-owned writes**: each service (GRN approve, transfer
   dispatch, adjustment post, sale, return) mutates `Stock` directly
   and emits a parallel ledger row.
2. **Ledger-driven writes**: every service writes a row to
   `InventoryLedger`, and a single helper `ledger_service.write()`
   applies the delta to `Stock` atomically with the journal insert.
   No other code path touches `Stock` mutating columns.
3. **Event-sourced rebuild**: only `InventoryLedger` is persisted;
   `Stock` is a materialised view rebuilt from the journal.

We have two prior CodeIgniter codebases where option 1 led to drift
that nobody could explain — a "missing" ledger row, a service that
forgot to emit one, a manual SQL fix that bypassed both. The
post-mortem was always _"the journal and the balance were written by
different code"_.

## Decision

**Adopt option 2: `ledger_service.write()` is the only function in
the codebase that mutates `Stock.qty_on_hand` /
`Stock.qty_reserved`.** Every quantity change is therefore guaranteed
to have a matching journal row, by construction.

Concretely:

- `apps.inventory.services.ledger_service.write(*, product, branch,
qty_delta, reserved_delta=Decimal("0"), ref_type, ref_id, …)`
  opens a `transaction.atomic()` block, takes a row lock with
  `Stock.objects.select_for_update().get_or_create(...)`, inserts
  the `InventoryLedger` row, and updates the `Stock` columns —
  all inside the same transaction.
- Every other inventory service (`availability_service`,
  `transfer_service`, `adjustment_service`, `wastage_service`,
  `count_service`) calls `ledger_service.write()`. None of them
  carry their own `Stock.objects.update(...)` calls.
- `InventoryLedger` is immutable (`save()` rejects updates with a
  pk; `delete()` always raises) and ordered `-id`.

To enforce the rule outside service code, a `pre_save` hook on
`Stock` asserts that the change is happening inside
`ledger_service.write()` (a contextvar flag set on entry, cleared in
the `finally`). Any other writer triggers a domain error in dev /
staging and a structured log + Sentry breadcrumb in production.

## Why not …

- **Service-owned writes**: the drift mode described above. Every
  drift incident we have seen comes from a writer that forgot the
  paired emit. A single seam removes the entire class of bugs.
- **Event-sourced rebuild**: tempting, but a 200K-SKU catalog with
  100K daily ledger rows means a full rebuild is too slow for read
  paths (POS scan, online checkout). Snapshots would put us back in
  the position of having two writers (the rebuilder and the
  snapshotter); we keep `Stock` as a materialised balance row and
  `InventoryLedger` as the append-only audit, and `ledger_service`
  is the only thing that updates either.
- **DB triggers**: would work, but moves business logic out of the
  Django service layer where the rest of the codebase reasons about
  permissions, audit, and idempotency. Triggers also can't easily
  use the `actor` / `branch` from `apps.core.context`.
- **Optimistic concurrency (version column)**: spurious 409s under
  POS bursts (multi-cashier same SKU). `SELECT … FOR UPDATE` is
  cheaper at retail scale.

## Consequences

- M05 ships a single `Stock` writer. M06 (online order) and M07
  (POS) write their sales movements through `ledger_service.write()`
  via `availability_service.consume`. Same for M08 invoices and
  M10 returns when they land.
- The `pre_save` allowlist is **enforced in code, not by schema**
  (same reasoning as ADR-007): the seam set grows per module, an
  enum in the table would require a migration each time.
- Postgres-equivalent isolation: MySQL InnoDB's `REPEATABLE READ` +
  row locks is sufficient. SQLite tests skip the concurrency case
  because SQLite ignores `SELECT … FOR UPDATE` — we annotate the
  test with `pytest.mark.skipif(connection.vendor == "sqlite", …)`.
- The journal becomes the **debugging surface of last resort**. When
  a balance looks wrong, sum the ledger filtered to
  `(product, branch)` and the answer is by construction the
  expected `qty_on_hand`.
- Reads do _not_ go through the ledger. They hit `Stock` directly
  with `select_related("branch", "product")`. The journal stays
  cheap because nothing reads it except the ledger viewset and
  ops queries.

## Follow-ups

- **M06 / M07**: route sale reservation and consume through
  `availability_service`, never call `ledger_service.write()`
  directly from a view.
- **M10 returns**: writes positive deltas via a dedicated
  `return_service` that calls `ledger_service.write()`.
- **M11 sales / M13 accounting**: read the ledger for valuation
  rebuilds. Never write to it.
- **Ops runbook**: document the "sum the ledger" reconciliation
  procedure in `docs/operations/`.
