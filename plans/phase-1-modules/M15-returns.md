# M15 — Returns & RMA

> **Phase**: phase-1-modules  **SRS ref**: Module 15  **Depends on**: M05, M09, M11, M12, M14  **Est. effort**: M

## Goal

Customer return flow (POS counter + online RMA), refund to original/wallet, restock vs scrap decision, return-window policy, return-shipment for online.

## Steps

1. **Models** `apps/returns/`:
   - `ReturnPolicy(code, name, applies_to_categories M2M, days_window, conditions_json, allows_partial bool, restock_allowed bool, is_active)`.
   - `ReturnRequest(rr_no unique, sale FK, customer FK, source=POS|ONLINE, status=REQUESTED|APPROVED|REJECTED|RECEIVED|REFUNDED|CLOSED, items[] -> ReturnItem, reason FK ReasonCode, requested_at, decision_by, decision_at, refund_method=ORIGINAL|WALLET, refund_amount, return_shipment FK Shipment nullable)`.
   - `ReturnItem(rr FK, sale_item FK, qty, reason FK, condition=NEW|USED|DAMAGED, restock_decision=RESTOCK|SCRAP, batch FK nullable)`.
   - `ReasonCode(code, name, kind=RETURN|WASTAGE|...)`.
2. **Services**:
   - `return_service.request(sale, items, reason, refund_method)` — policy check (window + conditions).
   - `return_service.approve/reject`.
   - `return_service.receive_at_pos(rr)` — instant; writes inventory ledger (restock), creates refund payment OR wallet credit.
   - `return_service.receive_online(rr, shipment)` — return shipment received at warehouse → inspector marks restock/scrap → posts ledger + refund.
   - Auto-post to M12 (DR Sales Returns, CR Cash/Bank/Wallet).
3. **Error prefix**: `RET-*`.
4. **Endpoints**: `/api/v1/returns/`.
5. **Admin-UI**:
   - Returns inbox.
   - Return request detail with inspector worksheet (item-by-item condition + decision).
   - POS return shortcut (F-key on POS calls return flow).
6. **Storefront**: customer can request return from order detail page within window.
7. **Permissions**: `returns.request.create`, `returns.approve`, `returns.receive`, `returns.refund.original`, `returns.refund.wallet`.
8. **Tests**: window enforcement, partial returns, refund routing, restock vs scrap correctness, M12 auto-posting.
9. **Docs**: `docs/modules/returns/*` + ADR `018-return-policy-engine.md`.
10. Commit: `feat(M15): returns + RMA`.

## Verification

### Manual
1. POS sale → customer returns next day at counter → refund to original payment → inventory restocked.
2. Online order → customer requests return day-30 (policy 30d) → approved → return shipment → inspector marks 1 item scrap, 1 restock → refund to wallet → ledgers correct.
3. Day-31 attempt → blocked with `RET-010 outside_return_window`.

### Automated
- `pytest backend/tests/returns/ -q` ≥ 85%.
- UI + Playwright + Newman green.

## Definition of Done

- [ ] Policy engine data-driven.
- [ ] Both POS + online return flows work.
- [ ] M12 ledgers correct.
- [ ] `_state.md` advanced.

## Next step

→ [`M12-finance.md`](./M12-finance.md)

## Previous step

← [`M14-delivery.md`](./M14-delivery.md)
