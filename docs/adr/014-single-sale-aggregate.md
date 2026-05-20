# ADR-014 — Single `Sale` aggregate for POS, online, B2B, and manual sales

- **Status**: Accepted
- **Date**: 2026-05-20
- **Decider**: backend team
- **Context plan**: `plans/phase-1-modules/M11-sales-billing.md`

## Context

The SRS lists four sale origins — POS (M07), online store (M06),
B2B / counter-bill (M11 manual entry), and back-office MANUAL
corrections. All four need to:

- deduct stock through the inventory ledger
  ([ADR-008](./008-ledger-driven-stock.md));
- compute tax with `apps.master.api_public.compute_tax`
  ([ADR-004](./004-tax-components.md));
- apply discounts (header + line) with optional approval;
- collect one or more payments;
- be cancellable with a clean reversal (ledger, payments,
  loyalty, invoice);
- feed M08 invoices, M09 loyalty, M10 returns, M12 finance, M13
  reports and M16 GST returns.

The decision is **how to model the persistent shape of "a sale"**.
Candidates considered:

1. **Per-channel sale models** — `POSSale`, `OnlineOrder`,
   `B2BSale`, each with its own items / payments tables.
2. **One denormalized `Invoice` table** — header + line JSON, no
   normalized items, generated at post time from a transient
   in-memory draft.
3. **Event-sourced sales** — only `SaleEvent` rows are persisted;
   the Sale header / items are projections rebuilt on read.
4. **Single `Sale` aggregate with `origin` discriminator** — one
   normalized header (`Sale`), one items table (`SaleItem`), one
   payments table (`SalePayment`), and a `origin` enum
   (POS / ONLINE / B2B / MANUAL).

## Decision

**Adopt option 4: a single `Sale` aggregate with an `origin`
discriminator.** M06 (online checkout) and M07 (POS) both call
`apps.sales.services.sale_service.create_draft(...)` and
`post(...)`; M11 admin-UI exposes manual B2B / counter-bill entry
through the same service surface. Concretely:

- `Sale` is the only sale header in the system. `origin` is a
  closed enum (`POS | ONLINE | B2B | MANUAL`). `status` is the
  canonical lifecycle (`DRAFT → HELD → CONFIRMED → PARTIALLY_PAID
→ PAID | CANCELLED | REFUNDED`).
- `SaleItem` is the only sale line. `XOR(product, variant)` is
  enforced by a DB `CheckConstraint` (`sales_item_xor_target`).
- `SalePayment` is the only payment record. Payment status
  defaults to `SUCCESS`; failed payments are recorded explicitly.
- `sale_service.post()` is `@transaction.atomic`, validates the
  payment sum against `grand_total` (unless `allow_partial_payment`
  is set), and calls `apps.inventory.services.ledger_service.post(
ref_type=InventoryRefType.SALE, ...)` so stock deduction goes
  through the single-writer seam from ADR-008. No other writer
  touches `Stock.qty_*` for sales.
- `sale_service.cancel()` writes a reversing ledger entry with
  `ref_id=f"CANCEL:{sale.pk}"` (positive qty), flips SUCCESS
  payments to REFUNDED, and emits `sale_cancelled`.
- Downstream modules subscribe to the `sale_posted` /
  `sale_cancelled` signals (M08 invoice, M09 loyalty, M10 referral,
  M12 finance, M16 GST, M17 notifications). Subscribers use
  `dispatch_uid` so reconnects are idempotent.
- Idempotency for the offline-POS replay case is handled by a
  unique `offline_uuid` column on `Sale`.

## Why not …

- **Per-channel sale models**: each channel would duplicate the
  same fields (totals, tax breakup, payments, discounts, refunds)
  and force every downstream module (invoice, GST, loyalty,
  returns, reports) to either branch on channel or do a `UNION`.
  Returns are the worst case: an online return that is processed
  in-store would need to read `OnlineOrder` and write a `POSSale`
  reversal — a join across two write models. The unified aggregate
  removes the channel branching from all downstream code.
- **Denormalized `Invoice` table** with line JSON: kills indexed
  reporting (per-product sales, per-tax-slab GST, top SKUs by
  branch) and makes the `XOR(product, variant)` and tax-FK
  integrity checks impossible at the DB layer. Also forces M10
  returns to denormalize back to per-line to do anything sensible.
- **Event sourcing**: tempting for audit, but the rest of the
  stack reads sales as relational rows (reports, GST, invoice
  print, loyalty rules). Projections would have to be eagerly
  maintained, which is just a worse version of option 4 with
  extra moving parts. We already get full audit through the
  inventory ledger and per-row `created_at` / `updated_at` /
  `created_by` / `updated_by` from `BaseModel`.
- **Sub-classed tables (MTI)**: Django multi-table inheritance
  would let `POSSale(Sale)` add POS-only fields, but it costs a
  JOIN on every read and pushes channel-specific shape into the
  schema. The empirical reality after two prior CodeIgniter
  codebases is that channel-specific fields are rare — terminal
  ID, cashier shift, online cart UUID — and fit comfortably as
  nullable columns on the single header (`terminal_id_external`,
  `cashier`, `offline_uuid`).

## Consequences

- M06 (online checkout) and M07 (POS) **MUST** create and post
  sales through `apps.sales.services.sale_service`. They are
  permitted to add channel-specific orchestration (cart timeout,
  cashier-shift binding, gateway callbacks) but not a parallel
  Sale model.
- B2B / counter-bill flow re-uses the standard `SaleEntryPage`
  with `origin=B2B`. The only channel difference is the permission
  gate (`sales.b2b.create`).
- M08 invoice generation subscribes once to `sale_posted` and
  produces an invoice regardless of origin. The invoice template
  may switch on origin for layout (POS receipt vs. B2B tax
  invoice) but the data shape is identical.
- M10 returns target `Sale` / `SaleItem` directly — there is only
  one place to look up a refundable line.
- Reports (M13) and GST (M16) read `Sale` / `SaleItem` with the
  origin filter as an optional facet, never as a switch.
- Per-channel feature flags live on `SiteSetting` keyed by origin
  (e.g. `sales.online.allow_partial_payment`), not on the model.
- The `Sale.totals_json` snapshot is **denormalized intentionally**
  so historic sales survive tax-slab rate changes; downstream
  recompute lives in `sale_builder.recompute()` and is never
  re-run on a posted sale.

## Follow-ups

- **M06 / M07**: implement origin-specific orchestration on top of
  `sale_service` — cart timeouts, cashier shifts, gateway
  callbacks. No direct `Sale.objects.create(...)` outside the
  service.
- **M08**: subscribe to `sale_posted` with a `dispatch_uid` and
  render invoices from `Sale.totals_json` so the invoice is a
  faithful snapshot at post time.
- **M09 / M10 / M12 / M16 / M17**: each subscribes the same way.
  Reverse handlers subscribe to `sale_cancelled`.
- **M13 reports**: index `Sale(origin, billed_at, branch)` once
  reporting cardinality is known.
- **Future channels** (marketplace, kiosk): extend the `origin`
  enum, not the model. New channel-specific columns are nullable
  additions to `Sale`.
