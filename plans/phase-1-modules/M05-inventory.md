# M05 — Inventory & Branch Transfer

> **Phase**: phase-1-modules  **SRS ref**: Module 5  **Depends on**: M01, M02, M03, M04  **Est. effort**: L

## Goal

Ledger-driven inventory: every stock change goes through `InventoryLedger`. Supports batch/expiry, multiple branches/warehouses, branch transfers (with in-transit state), physical count, wastage/damage, opening stock import. **Negative stock is a hard block, including offline POS.**

## Steps

1. **Models** `apps/inventory/`:
   - `Stock(product/variant FK, branch FK, warehouse FK, qty_on_hand decimal, qty_reserved decimal, qty_in_transit decimal, last_movement_at)` — derived; recomputed from ledger snapshots.
   - `Batch(product/variant FK, branch FK, batch_no, mfg_date, expiry_date, cost_price, qty_remaining, status=ACTIVE|EXPIRED|CONSUMED)`.
   - `InventoryLedger(ledger_entry...)` subclass: `product, variant, batch nullable, branch, warehouse, qty_change, qty_before, qty_after, ref_type=GRN|SALE|TRANSFER|ADJUSTMENT|RETURN|WASTAGE, ref_id, reason_code nullable, actor, ts`.
   - `BranchTransfer(tr_no unique, from_branch, to_branch, status=DRAFT|DISPATCHED|IN_TRANSIT|RECEIVED|CANCELLED, dispatched_at, received_at, vehicle, items[])`.
   - `BranchTransferItem(tr, product/variant, batch, qty_sent, qty_received, qty_lost)`.
   - `StockAdjustment(adj_no, branch, reason_code, status, items[], approved_by, approved_at)`.
   - `PhysicalCount(pc_no, branch, scope=FULL|CATEGORY|LOCATION, status, scheduled_for, items[])` + `PhysicalCountItem(...)`.
   - `Wastage(wt_no, branch, items[], reason_code, value_total)`.
   - `Reservation(product/variant, branch, qty, ref_type=ORDER|HOLD, ref_id, expires_at)` — used by M06 to soft-block stock before payment.
2. **Services**:
   - `ledger_service.post(ref_type, ref_id, items[], actor, branch)` — single atomic write; recomputes Stock row.
   - `availability_service.available(item, branch) -> on_hand - reserved`.
   - `availability_service.reserve(item, branch, qty, ref) -> Reservation`.
   - `transfer_service.dispatch/receive/cancel` — dispatch reduces source; receive increases destination & resolves in-transit.
   - `count_service.start/scan/finalize` — finalize posts adjustments.
   - `expiry_service.mark_expired_batches()` — nightly Celery task.
   - **Negative-stock guard** at ledger boundary: any call resulting in `qty_after < 0` raises `INV-010 insufficient_stock`. Applies to offline POS replays too.
3. **Reason code masters** under `apps/inventory/seeders/`: DAMAGE, THEFT, EXPIRY, COUNT_DIFF, etc.
4. **Endpoints**: `/api/v1/inventory/stock/`, `/batches/`, `/ledger/`, `/transfers/`, `/adjustments/`, `/counts/`, `/wastage/`, `/reservations/`.
5. **Cursor pagination** on `/ledger/` (large dataset).
6. **Admin-UI**:
   - Stock dashboard (per branch, low-stock alerts).
   - Ledger viewer (cursor-paginated, filters).
   - Transfer wizard (dispatch + receive screens).
   - Physical count with mobile-friendly scan UI.
   - Wastage entry form.
7. **Caching**: stock snapshot per (item, branch) 30s; busted on ledger write.
8. **Permissions**: `inventory.view/manage/adjust/transfer/count/wastage`.
9. **Tests**: concurrency test (two parallel reservations on last unit → exactly one wins). Negative-stock guard.
10. **Docs**: `docs/modules/inventory/*` + ADR `008-ledger-driven-stock.md`.
11. Commit: `feat(M05): inventory + transfers + counts + wastage`.

## Verification

### Manual
1. PO→GRN→stock up; sale (placeholder via M11) → stock down through ledger.
2. Transfer dispatch reduces source, in-transit visible; receive increases destination.
3. Reserve last unit; second reserve fails with `INV-010`.
4. Schedule count → mobile scan → finalize → ledger entries equal count diff.

### Automated
- `pytest backend/tests/inventory/ -q` ≥ 85% on services, including concurrency test.
- UI + Playwright + Newman green.

## Definition of Done

- [ ] Ledger is the only writer.
- [ ] Negative-stock guard verified.
- [ ] Concurrency safe.
- [ ] `_state.md` advanced — **next: M11 (sales-billing pulled early)**.

## Next step

→ [`M11-sales-billing.md`](./M11-sales-billing.md)

## Previous step

← [`M04-vendor-purchase.md`](./M04-vendor-purchase.md)
