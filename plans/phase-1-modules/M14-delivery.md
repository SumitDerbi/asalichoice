# M14 — Delivery & Logistics

> **Phase**: phase-1-modules  **SRS ref**: Module 14  **Depends on**: M01, M02, M06, M11  **Est. effort**: L

## Goal

Delivery management for online + B2B orders: shipment, route, delivery person assignment, status tracking, OTP-on-delivery, COD reconciliation lifecycle, delivery slot booking. 3PL integration hooks.

## Steps

1. **Models** `apps/delivery/`:
   - `Shipment(shp_no unique, sale FK, branch FK, status=READY|PICKED|OUT_FOR_DELIVERY|DELIVERED|FAILED|RETURNED, assigned_to FK user nullable, delivery_address_snapshot_json, slot FK nullable, otp_hash nullable, dispatched_at, delivered_at, attempts)`.
   - `Route(code, branch, date, driver FK user, vehicle, shipments M2M, status=PLANNED|IN_PROGRESS|COMPLETED, optimised_order_json)`.
   - `ShipmentEvent(shipment FK, status, lat, lng, note, by, at)`.
   - `CODCollection(shipment FK, amount, status=COLLECTED|DEPOSITED_TO_BRANCH|RECONCILED|DISCREPANCY, collected_at, deposited_at, reconciled_at, discrepancy_reason)`.
   - `DeliveryPersonProfile(user FK, vehicle, license_no, document_uploads[], rating)`.
   - `ThreePLProvider(code, name, config_json, is_active)`.
   - `ThreePLShipment(shipment FK, provider FK, awb, label_url, status_raw, last_synced_at)`.
2. **Services**:
   - `shipment_service.create_from_sale(sale)` — invoked on sale.posted for ONLINE/B2B; for POS, only if `requires_delivery`.
   - `route_service.plan(branch, date)` — naive nearest-neighbour now; pluggable optimiser later.
   - `shipment_service.assign(shp, driver)`.
   - `shipment_service.mark_out_for_delivery(shp)` — generates OTP, SMS to customer (M17).
   - `shipment_service.deliver(shp, otp_entered)` — verifies OTP, marks delivered, posts COD collection if applicable.
   - `cod_service.deposit_to_branch(shp_ids[], by)`, `cod_service.reconcile(deposit, bank_txn?)` → triggers M12 JE.
   - `slot_service` (shared with M06).
   - `threepl_service.dispatch(shp, provider)`, `threepl_service.poll_status()` — periodic Celery.
3. **Endpoints**: `/api/v1/delivery/shipments/`, `/routes/`, `/cod/`, `/3pl/`.
4. **Driver app** (PWA in admin-ui under `/driver/`): list of today's shipments, scan to confirm, capture OTP, collect cash dialog, photo proof upload.
5. **Error prefix**: `DEL-*`.
6. **Admin-UI**:
   - Dispatch board: shipments by status, drag-to-assign.
   - Route planner: map placeholder + stop list.
   - COD reconciliation screen (per-driver deposit, variance highlight).
   - 3PL provider config.
7. **Permissions**: `delivery.shipment.view/manage`, `delivery.route.plan`, `delivery.cod.deposit/reconcile`, `delivery.3pl.config`.
8. **Tests**: full happy path, OTP validation, COD lifecycle through M12 JE, failed delivery re-attempt counter, 3PL poll idempotency.
9. **Docs**: `docs/modules/delivery/*` + ADR `017-cod-lifecycle.md`.
10. Commit: `feat(M14): delivery, routes, COD lifecycle, 3PL hooks`.

## Verification

### Manual
1. Online order placed → shipment auto-created → assign driver → OTP SMS sent → mark delivered with OTP → COD collected.
2. Deposit COD to branch → reconcile with bank credit → M12 JE posted.
3. Discrepancy ₹100 short → flagged, audit visible.

### Automated
- `pytest backend/tests/delivery/ -q` ≥ 85%.
- UI + Playwright + Newman green.

## Definition of Done

- [ ] End-to-end delivery flow works.
- [ ] COD reconciliation produces correct ledger entries.
- [ ] Driver PWA works offline (queues events).
- [ ] `_state.md` advanced.

## Next step

→ [`M15-returns.md`](./M15-returns.md)

## Previous step

← [`M10-crm-referral.md`](./M10-crm-referral.md)
