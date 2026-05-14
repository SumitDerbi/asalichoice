# M09 — Customer, Wallet & Loyalty

> **Phase**: phase-1-modules  **SRS ref**: Module 9  **Depends on**: M01, M02, M11  **Est. effort**: L

## Goal

Customer master + wallet (cash equivalent stored value) + loyalty points (earn-burn rules) + tiered membership. Wallet & loyalty are independent ledgers; both consumed at checkout (POS + ONLINE).

## Steps

1. **Models** `apps/customer/`:
   - `Customer(code unique, name, mobile unique, email unique-nullable, gender, dob, gst_no nullable, default_address FK, tier FK nullable, kyc_status, is_active)`.
   - `CustomerGroup(code, name, default_discount_percent)`.
   - `LoyaltyTier(code unique, name, min_points, earn_multiplier, perks_json)`.
   - `WalletLedger` subclass: `customer, ref_type=TOPUP|REDEEM|REFUND|ADJUSTMENT, ref_id, amount, balance_after, expires_at nullable, actor, ts`.
   - `LoyaltyLedger` subclass: `customer, ref_type=EARN|REDEEM|EXPIRE|ADJUSTMENT, ref_id, points, balance_after, expires_at, actor, ts`.
   - `LoyaltyRule(code, kind=EARN|BURN, condition_json, value, valid_from, valid_to, is_active)` — examples: "1 point per ₹10", "Tier GOLD earns 2x", "Burn 100 pts = ₹50 off".
2. **Services**:
   - `wallet_service.topup/redeem/refund/adjust` — atomic ledger writes, balance recompute, audit.
   - `loyalty_service.earn(sale)` — runs rules, posts EARN ledger.
   - `loyalty_service.redeem(customer, points, ref)` — validates balance, posts REDEEM ledger.
   - `loyalty_service.expire_points()` — Celery nightly.
   - `tier_service.recompute(customer)` — promotes/demotes based on points.
3. **Sale integration** (M11 hooks):
   - Checkout offers wallet/points redeem.
   - On Sale.post(): loyalty earn rules run; wallet/points captured.
   - On Sale cancel: ledgers reverse.
4. **Endpoints**: `/api/v1/customers/`, `/customers/{id}/wallet/`, `/customers/{id}/loyalty/`, `/loyalty-rules/`, `/tiers/`.
5. **Error prefix**: customer `USR-` overlaps with users; use `CUS-*` for customer-specific. **Update** `_conventions.md` §5.
6. **Admin-UI**:
   - `src/modules/customers/` — list, customer-360 (orders, wallet, loyalty, addresses, referrals).
   - Wallet top-up/refund actions with reason codes.
   - Loyalty rule editor with live "this rule earns X points on a ₹1000 sale" preview.
   - Tier list + perk editor.
7. **Storefront**: account page shows wallet balance + loyalty points + transactions.
8. **Permissions**: `customer.view/manage`, `customer.wallet.adjust`, `customer.loyalty.rule.manage`.
9. **Tests**: ledger math, expiry rules, tier transitions, concurrency on redeem (no double-spend), rule preview.
10. **Docs**: `docs/modules/customer/*` + ADR `012-wallet-vs-loyalty.md`.
11. Commit: `feat(M09): customers, wallet, loyalty, tiers`.

## Verification

### Manual
1. Customer earns points on sale → balance updates → reaches GOLD threshold → tier promoted.
2. Concurrent redeem of last 100 points by two parallel checkouts → only one wins.
3. Cancel sale → both earn and redeem ledgers reverse.

### Automated
- `pytest backend/tests/customer/ -q` ≥ 85% with concurrency test.
- UI + Playwright + Newman green.

## Definition of Done

- [ ] Wallet & loyalty ledgers complete & immutable.
- [ ] Rule engine driven entirely by data (no hardcoded earn rates).
- [ ] `_state.md` advanced.

## Next step

→ [`M10-crm-referral.md`](./M10-crm-referral.md)

## Previous step

← [`M08-invoice-print.md`](./M08-invoice-print.md)
