# M06 — Online Order

> **Phase**: phase-1-modules  **SRS ref**: Module 6  **Depends on**: M01–M05, M11, M07  **Est. effort**: L

## Goal

Storefront cart → checkout → order → payment → fulfillment. Backed by the same `Sale` aggregate as POS (from M11), with origin=ONLINE. Includes registration approval flow, abandoned cart recovery, address book, delivery slot booking, and webhook handlers for payment gateways.

## Steps

1. **Models** `apps/online_order/`:
   - `Cart(customer FK nullable, session_key, branch FK nullable, items[], coupons[], totals_json, abandoned_at nullable, recovered_at nullable)`.
   - `CartItem(cart, product/variant, qty, price_snapshot, tax_snapshot)`.
   - `OnlineOrder(sale FK 1:1 from M11, registration_status=APPROVED|PENDING|REJECTED, slot FK nullable, address FK, payment_method, payment_status=INITIATED|PAID|FAILED|REFUNDED, gateway, gateway_ref, abandoned_recovery_link nullable)`.
   - `CustomerAddress(customer FK, label, line1, line2, pincode FK, city, state, country, is_default_billing, is_default_shipping)`.
   - `DeliverySlot(branch FK, date, slot_start, slot_end, capacity, booked_count, is_active)`.
   - `RegistrationRequest(mobile, email, name, status, requested_at, approved_by, approved_at, reject_reason)` — partner/B2B registration; auto-approved for retail per SystemSetting.
2. **Services**:
   - `cart_service.add/update/remove/apply_coupon/clear`.
   - `cart_service.detect_abandoned()` — Celery task; emails reminder (M17).
   - `checkout_service.place_order(cart, address, slot, payment_method)`:
     - Reserve stock (M05 reservation).
     - Initiate payment gateway txn.
     - Create Sale (M11) with status=PENDING_PAYMENT.
   - `payment_webhook_service.handle(provider, payload)` — verify signature, mark Sale paid or failed, release reservation on failure.
   - `slot_service.available_slots(branch, date)`.
   - `registration_service.request/approve/reject`.
3. **Idempotency**: webhook handlers use `Idempotency-Key` = gateway txn id; replay-safe.
4. **Payment providers** (config via M18 IntegrationKey): Razorpay (primary), Stripe (placeholder). Plugin interface `apps/online_order/payments/base.py`.
5. **Error prefix**: `ONL-*`.
6. **Storefront (Wagtail)**:
   - Product page, category page, cart page, checkout page, order-confirmation page.
   - Account pages: orders, addresses, wallet (M09), referrals (M10).
   - Server-rendered with Tailwind; minimal JS (htmx-style or Alpine).
   - SEO: schema.org Product + BreadcrumbList JSON-LD.
7. **Admin-UI**:
   - `src/modules/online-orders/` — order list (filters: status, payment, slot, branch), order detail page.
   - Registration approval inbox.
   - Abandoned cart dashboard.
   - Delivery slot capacity editor.
8. **Permissions**: `online.order.view/manage`, `online.registration.approve`, `online.slot.manage`.
9. **Tests**: cart edge cases, slot capacity overflow, payment webhook replay, abandoned-cart recovery, registration approval auto/manual.
10. **Docs**: `docs/modules/online-order/*` + ADR `009-payment-webhook-idempotency.md`.
11. Commit: `feat(M06): online order with cart, checkout, webhooks, slots`.

## Verification

### Manual
1. Storefront checkout flows end-to-end with Razorpay sandbox.
2. Simulate webhook replay → no double-credit, no double-stock-decrement.
3. Abandon cart → reminder email after configured delay.
4. Book last slot; concurrent second book fails politely.

### Automated
- `pytest backend/tests/online_order/ -q` ≥ 85%.
- Storefront Playwright `e2e/storefront/checkout.spec.ts` green.
- Admin-UI tests + Newman green.

## Definition of Done

- [ ] End-to-end order flow works on storefront.
- [ ] Payment webhooks idempotent & verified.
- [ ] Slot capacity enforced.
- [ ] Abandoned cart recovery live.
- [ ] `_state.md` advanced.

## Next step

→ [`M08-invoice-print.md`](./M08-invoice-print.md)

## Previous step

← [`M07-pos.md`](./M07-pos.md)
