# M10 — CRM & Referral

> **Phase**: phase-1-modules  **SRS ref**: Module 10  **Depends on**: M02, M09, M17  **Est. effort**: M

## Goal

Lead/opportunity tracking, customer segmentation, broadcast campaigns (SMS/Email/WhatsApp via M17), referral program with fraud detection, coupon engine.

## Steps

1. **Models** `apps/crm/`:
   - `Lead(name, mobile, email, source, status=NEW|CONTACTED|QUALIFIED|CONVERTED|LOST, owner FK user, score, custom_fields_json)`.
   - `LeadActivity(lead FK, type=CALL|EMAIL|NOTE|MEETING, body, at, by FK user)`.
   - `Segment(code, name, definition_json: rule tree on customer attrs/behaviour, member_count cached)`.
   - `Campaign(code, name, channel=SMS|EMAIL|WHATSAPP, segment FK, template FK (M17), schedule_at, status=DRAFT|SCHEDULED|RUNNING|DONE|CANCELLED, stats_json)`.
   - `Coupon(code unique, kind=PERCENT|FLAT|FREESHIP|BOGO, value, conditions_json (min cart, category, customer tier, max uses, max per customer, valid_from, valid_to), is_active, usage_count)`.
   - `CouponRedemption(coupon FK, sale FK, customer FK, discount_amount, at)`.
   - `Referral(referrer_customer FK, code unique, link_token, status=ACTIVE|DISABLED)`.
   - `ReferralEvent(referral FK, referred_customer FK, sale FK, reward_amount, reward_type=WALLET|POINTS, status=PENDING|CREDITED|FRAUD, ts)`.
   - `ReferralFraudLog(referral FK, reason, evidence_json, action=BLOCK|REVIEW, by, at)` — already named in PROJECT_DETAILS.md.
2. **Services**:
   - `segment_service.evaluate(segment) -> queryset`.
   - `segment_service.materialise(segment)` — caches member set for big campaigns.
   - `campaign_service.schedule/run/cancel` — Celery task dispatches per-recipient send via M17.
   - `coupon_service.validate(code, cart, customer) -> (ok, reason, discount)`.
   - `coupon_service.redeem(...)` — atomic, idempotent on sale id.
   - `referral_service.attribute(sale)` — links sale to referrer if referral cookie/code present.
   - `referral_fraud_service.check(event)` — checks: same device fingerprint, same IP cluster, mutual referrals, velocity, address proximity. Flags vs auto-blocks per SystemSetting threshold.
3. **Endpoints**: `/api/v1/crm/leads/`, `/segments/`, `/campaigns/`, `/coupons/`, `/referrals/`.
4. **Error prefix**: `CRM-*`, `REF-*`.
5. **Admin-UI**:
   - Lead kanban + table views.
   - Segment builder (rule tree UI).
   - Campaign wizard (channel → segment → template → schedule → review).
   - Coupon list + builder with live "X customers eligible" preview.
   - Referral dashboard with fraud queue (review/approve/block).
6. **Storefront**: referral code share page (whatsapp, email, copy link).
7. **Permissions**: `crm.lead.*`, `crm.segment.*`, `crm.campaign.*`, `crm.coupon.*`, `crm.referral.*`, `crm.referral.fraud.review`.
8. **Tests**: segment evaluation correctness, coupon stacking rules, referral fraud rules, campaign idempotency.
9. **Docs**: `docs/modules/crm/*` + ADR `013-referral-fraud.md`.
10. Commit: `feat(M10): crm leads, segments, campaigns, coupons, referrals`.

## Verification

### Manual
1. Create segment "Customers with 0 purchases in last 60 days" → matches preview count.
2. Schedule campaign → at run-time, M17 sends; stats update (sent/delivered/opened).
3. Create coupon → invalid for tier MEMBER → rejected at checkout with reason.
4. Two referrals from same device → fraud queue, auto-blocked.

### Automated
- `pytest backend/tests/crm/ -q` ≥ 85%.
- UI + Playwright + Newman green.

## Definition of Done

- [ ] Campaign sends actually reach test inboxes.
- [ ] Fraud rules configurable (SystemSetting), not hardcoded.
- [ ] `_state.md` advanced — next: M14.

## Next step

→ [`M14-delivery.md`](./M14-delivery.md)

## Previous step

← [`M09-customer-wallet-loyalty.md`](./M09-customer-wallet-loyalty.md)
