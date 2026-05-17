# ADR-007 — GRN-only stock write

- **Status**: Accepted
- **Date**: 2026-06-08
- **Decider**: backend team
- **Context plan**: `plans/phase-1-modules/M04-vendor-purchase.md`

## Context

The procure-to-pay chain has four touch-points where someone might
naively think to mutate inventory:

1. **PO approval** — "reserve" qty against the warehouse.
2. **GRN approval** — increment warehouse stock by what was received.
3. **PI post** — adjust valuation against the new cost.
4. **PR post** — reverse stock on a return.

Inventory itself lands in M05. The question for M04 is: **which of
these steps should be the single inventory writer**, so that M05 can
slot in cleanly without rewriting M04?

We have prior bruising from CodeIgniter codebases that wrote stock at
multiple points (PO reserve, GRN receipt, manual adjust, sales-bill
reverse) and ended up with reconciliation drift no one could explain.

## Decision

**GRN approval is the single inventory write seam for inbound stock,
and Purchase Return post is the single seam for return-out.** All
other steps are read-only against inventory.

Concretely:

- `grn_service.approve_grn` calls a single private helper
  `_write_inventory_movement(grn)` which is the **only** place the
  purchase app touches warehouse balances. In M04 this helper logs
  the intended movement; in M05 it will write to the real
  `StockMovement` table.
- `purchase_return_service.post_return` calls
  `_write_reverse_movement(pr)` — again the **only** seam for
  return-out movements.
- PO approval writes nothing to inventory. It only changes
  `PurchaseOrder.status` and the approval chain.
- PI post and PI pay write ledger entries (`VendorLedger`), not
  stock.

To make this enforceable, M05 will introduce a `pre_save` hook on
`StockMovement` that asserts `created_by_service in
{"purchase.grn_service", "purchase.purchase_return_service", ...}`.
Any other writer triggers a domain error in dev / staging.

## Why not …

- **Write at PO approve (reservation)**: A "reserved but not received"
  qty is conceptually different from on-hand stock. Mixing them in
  one table caused two of our prior projects to misreport sellable
  stock. If we ever need reservations, M05 will add a separate
  `StockReservation` table with its own writers — it will **not**
  decrement on-hand at PO approve.
- **Write at PI post (invoice-driven)**: Invoices arrive _after_ the
  goods are physically on the shelf. Driving stock off the invoice
  guarantees a window where the receiver can see goods they cannot
  yet sell. Killed.
- **Multiple writers, one journal**: "Just write everywhere and trust
  the journal" is what we did before. Drift was untraceable because
  every caller had its own definition of "receipt qty".
- **Ledger-as-truth (event sourcing)**: Tempting, but rebuilding
  current on-hand stock for a 200K-SKU catalog from a movement log on
  every read is too slow without snapshots. We keep a materialised
  balance table and append-only movement rows — but the write seam
  count is what we're tightening here, not the storage shape.

## Consequences

- M04 ships **without** the inventory tables — the seam logs at
  `INFO` level today and is the M05 implementation hook. There is no
  ambiguity about where the M05 patch lands:
  - `apps/purchase/services/grn_service.py::_write_inventory_movement`
  - `apps/purchase/services/purchase_return_service.py::_write_reverse_movement`
- Tests assert that the seam is **called exactly once per GRN
  approve** and **never called from any other M04 service**. This is
  the contract M05 builds on.
- `approve_grn` is irreversible by design — once stock is written, a
  reversal must go through a Purchase Return, not by editing the
  GRN. Hence `GRNStatus.APPROVED` has no outbound transition.
- Audit becomes simple: the auditor finds every stock movement by
  filtering `StockMovement.created_by_service`. Two values cover
  inbound, M05 will add `inventory.adjustment_service` for manual
  corrections, M08 will add `sales.invoice_service` for sales
  outbound. The list stays short and reviewable.
- The constraint is **enforced in code, not by schema**. The reason:
  the seam-set will grow (M08, M11 promotions, M18 transfers), and a
  schema-level enum would force a migration per module. A `pre_save`
  assertion on an enum of allowed writers is the cheaper guard.

## Follow-ups

- **M05** lands `StockMovement` + the `pre_save` writer-allowlist.
- **M08** adds the sales outbound writer to the allowlist with its
  own ADR section.
- **M18** (multi-warehouse transfers) becomes the third allowed
  writer — and the ADR for transfers must explicitly explain why a
  transfer is not modeled as a paired GRN + sale.
