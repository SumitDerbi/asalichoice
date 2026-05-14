# M11 — Sales & Billing Core

> **Phase**: phase-1-modules  **SRS ref**: Module 11  **Depends on**: M01, M02, M03, M05  **Est. effort**: L
> **Pulled forward** in `_meta.yaml` order: built right after M05, before M07/M06, so both POS and online orders write into the same Sale aggregate.

## Goal

The single source of truth for "a sale" regardless of origin (POS, ONLINE, B2B). Owns Sale, SaleItem, SalePayment, discount engine (header + line + tax-adjusted), tax computation (inclusive/exclusive), price overrides with permission, and the canonical sale lifecycle.

## Steps

1. **Models** `apps/sales/`:
   - `Sale(sale_no unique, origin=POS|ONLINE|B2B|MANUAL, branch FK, customer FK nullable, cashier FK nullable, terminal FK nullable, status=DRAFT|HELD|CONFIRMED|PARTIALLY_PAID|PAID|CANCELLED|REFUNDED, billed_at, payment_terms_json, totals_json (subtotal, discount_total, tax_total, round_off, grand_total), tax_mode=INCLUSIVE|EXCLUSIVE, notes, offline_uuid nullable unique)`.
   - `SaleItem(sale FK, product/variant FK, qty, uom FK, mrp, sale_price, discount_amount, line_subtotal, tax FK, tax_breakup_json, line_total, batch FK nullable, hsn FK)`.
   - `SalePayment(sale FK, payment_mode FK, amount, ref_no, gateway_txn nullable, status=PENDING|SUCCESS|FAILED|REFUNDED, at)`.
   - `Discount(code, scope=HEADER|LINE, kind=PERCENT|FLAT, condition_json, value, requires_approval bool)`.
   - `PriceOverride(sale_item FK, original_price, new_price, reason, by FK user, perm_check_passed bool)`.
2. **Services**:
   - `sale_builder.build(items[], customer?, branch, tax_mode)` — pure computation, returns Sale draft with totals. Used by POS + ONLINE checkout.
   - `discount_engine.apply(sale_draft, discounts[])` — order: line discounts → header discounts → tax recompute.
   - `tax_engine.compute(item, tax, inclusive)` — returns line tax breakup; reuses M01 `tax_service`.
   - `sale_service.post(draft)` — atomic: validate stock, reserve, write ledger (M05), persist Sale, emit `sale.posted` signal → M08 invoice + M09 loyalty + M10 referral + M12 finance.
   - `sale_service.cancel(sale, reason)` — atomic reversal: ledger reverse, invoice cancel, wallet/loyalty reverse, refund payments.
3. **Idempotency**: `offline_uuid` unique guarantees POS replays don't dupe.
4. **Signals** (Django signals or in-process pub-sub):
   - `sale.posted` → M08, M09, M10, M12, M17.
   - `sale.cancelled` → same modules to reverse.
5. **Error prefix**: `SAL-*`.
6. **Endpoints**: `/api/v1/sales/`, `/api/v1/sales/{id}/cancel/`, `/api/v1/sales/{id}/payments/`, `/api/v1/discounts/`.
7. **Admin-UI**:
   - `src/modules/sales/` — sale list with rich filters (origin, status, date, branch, cashier, customer), sale detail page, manual sale entry (B2B).
   - Discount admin (CRUD).
8. **Permissions**: `sales.view/manage/cancel`, `sales.price.override`, `sales.discount.apply`, `sales.b2b.create`.
9. **Tests**: tax math (multiple slabs in one sale, inclusive vs exclusive, rounding), discount engine (stacking, exclusivity), cancel reversal correctness, idempotency.
10. **Docs**: `docs/modules/sales/*` + ADR `014-single-sale-aggregate.md` (why one Sale model for POS+ONLINE+B2B).
11. Commit: `feat(M11): sales aggregate, discount + tax engines, lifecycle`.

## Verification

### Manual
1. Create POS sale (via M07 placeholder later) and ONLINE sale (via M06 placeholder later) → both write to same Sale table with `origin` set.
2. Sale with items at 5%, 18%, 28% tax → tax_breakup correct in totals_json.
3. Inclusive vs exclusive tax: same item produces correct different totals.
4. Cancel a paid sale → inventory restored, invoice marked cancelled, wallet/loyalty reversed.

### Automated
- `pytest backend/tests/sales/ -q` ≥ 90% (this is critical) including property-based tests on tax math.
- UI + Playwright + Newman green.

## Definition of Done

- [ ] Sale aggregate stable.
- [ ] Tax + discount engines fully data-driven.
- [ ] Cancel reversal proven.
- [ ] `_state.md` advanced — next: M07.

## Next step

→ [`M07-pos.md`](./M07-pos.md)

## Previous step

← [`M05-inventory.md`](./M05-inventory.md)
