# M07 — Point of Sale (POS)

> **Phase**: phase-1-modules  **SRS ref**: Module 7  **Depends on**: M01–M05, M11  **Est. effort**: XL

## Goal

Fast, keyboard-driven POS for cashiers. Online + **offline-capable** with deterministic sync. Supports device registration, terminal binding, tax-inclusive & tax-exclusive billing, split payments, holds/recall, cash drawer, receipt printing, day-close.

## Steps

1. **Models** `apps/pos/`:
   - `POSTerminal(code unique, branch FK, device_fingerprint, registered_by, registered_at, status=ACTIVE|SUSPENDED, last_seen, cash_drawer_balance)`.
   - `POSSession(terminal FK, cashier FK, started_at, ended_at, opening_cash, closing_cash, expected_cash, variance, status=OPEN|CLOSED|RECONCILED)`.
   - `Hold(terminal FK, ref_no, items_json, totals_json, created_at, recovered_at nullable)`.
   - POS uses **M11 Sale** for the actual transaction record (origin=POS).
   - `OfflineSaleQueue(terminal FK, offline_uuid unique, payload_json, created_at, synced_at nullable, conflict_reason nullable)`.
2. **Services**:
   - `terminal_service.register(device, branch, by_user)` — issues device-bound API key.
   - `session_service.open/close/reconcile`.
   - `sale_builder.build(items, payments, customer)` — computes tax inclusive/exclusive based on SystemSetting + per-product flag. Returns Sale draft.
   - `pos_checkout.commit(sale_draft, terminal, cashier)` — atomic: ledger reserve→write, Sale post, payment record, ledger update, audit. Idempotent on `offline_uuid`.
   - `offline_sync.replay(queue_entries)` — applies in order; conflicts → quarantine + report.
3. **Offline mode** (PWA):
   - Service worker caches catalog (price/tax) for the cashier's branch.
   - IndexedDB stores offline sales until online.
   - Stock reservation is **optimistic** offline; on sync, negative-stock check is **server-authoritative** → on conflict, sale is quarantined (`POS-040 stock_conflict`) and surfaced to manager.
4. **Receipt printing**:
   - Template engine reads from M18 print templates.
   - ESC/POS for thermal printers via QZ Tray bridge or WebUSB (configurable).
   - A4 / 80mm / 58mm variants.
5. **Keyboard UX**:
   - F-keys: F2 customer, F3 hold, F4 recall, F6 payment, F9 print, Ctrl+N new sale.
   - Barcode scan auto-focuses item input.
   - Numpad for qty/price overrides (perm-gated).
6. **Payment screen**:
   - Split tenders (cash + UPI + card).
   - Wallet redeem (M09).
   - Loyalty points redeem (M09).
   - Coupon apply (M10).
7. **Returns at POS** placeholder; full M15.
8. **Day close**:
   - Counts cash by denomination → variance → close session → emits FIN ledger entry.
9. **Error prefix**: `POS-*`.
10. **Admin-UI vs POS-UI**: POS lives in admin-ui under `/pos/` route, but uses a dedicated full-screen layout (no sidebar). Mobile-tablet responsive.
11. **Tests**: pytest (sale_builder math, idempotency), vitest (POS UI keyboard handlers), Playwright (full sale + offline simulation), Newman.
12. **Docs**: `docs/modules/pos/*` + ADR `010-offline-pos-sync.md`.
13. Commit: `feat(M07): pos with offline sync, terminal binding, day close`.

## Verification

### Manual
1. Register terminal → bind device → open session.
2. Scan 5 items → split payment cash+UPI → print receipt.
3. Disconnect network → ring 3 sales → reconnect → 3 sales sync, ledgers updated, no duplicates.
4. Force a stock conflict offline → quarantined and manager sees alert.
5. Close session with deliberate ₹50 short → variance recorded, FIN ledger entry posted.

### Automated
- `pytest backend/tests/pos/ -q` ≥ 85% on services + idempotency tests.
- Playwright POS spec green.
- Newman green.

## Definition of Done

- [ ] Online + offline flows verified.
- [ ] Negative-stock guard enforced server-side regardless of offline.
- [ ] Receipt printing works on at least 80mm thermal + A4.
- [ ] `_state.md` advanced — next: M06.

## Next step

→ [`M06-online-order.md`](./M06-online-order.md)

## Previous step

← [`M11-sales-billing.md`](./M11-sales-billing.md)
