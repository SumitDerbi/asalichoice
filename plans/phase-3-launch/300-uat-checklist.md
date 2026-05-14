# 300 — UAT Checklist

> **Phase**: phase-3-launch  **Depends on**: Phase 2 complete  **Est. effort**: M

## Goal

User Acceptance Testing with the business stakeholders against a staging environment populated with real-shape data. Sign-off per module before go-live.

## Steps

1. **Staging environment** mirrors production: same versions, similar data volume (seeded from sample dataset).
2. **Test users** created per role: Super Admin, Admin, Manager, Cashier, Delivery, HR, Customer.
3. **UAT scenarios** per module — produced as a checklist spreadsheet (CSV in `docs/uat/scenarios.csv`):
   - M01: create branch, set tax slabs, configure payment modes.
   - M02: invite user via SMS OTP, login, switch branch, view permissions.
   - M03: import 500 products via CSV, edit prices for one branch.
   - M04: full PO→GRN→PI cycle; partial receipt.
   - M05: branch transfer dispatch/receive, physical count.
   - M06: place online order via storefront, pay via Razorpay sandbox, track delivery.
   - M07: open session, ring 20 sales, offline sale, close session with cash variance.
   - M08: invoice generation, FY rollover simulation, reprint, cancel.
   - M09: top up wallet, earn loyalty, redeem at checkout, tier promotion.
   - M10: create segment, send campaign, redeem coupon, referral fraud detection.
   - M11: cross-origin sale list, manual B2B sale.
   - M12: month-end run; reports tally; year-end close simulation.
   - M13: every canonical report; schedule weekly export.
   - M14: full delivery + COD reconcile.
   - M15: in-store return; online return shipment.
   - M16: payroll for a month with 10 employees including 1 in F&F.
   - M17: every event triggers notifications; failover test.
   - M18: settings override per branch; print template rollback.
   - M19: audit viewer; tamper-evident chain verify; export.
   - M20: pair mobile, offline ops, sync, revoke device.
4. **Bug triage process**: Linear/Jira board; per-bug severity (Blocker / Major / Minor / Trivial). Blockers + Majors must be closed before go-live.
5. **Sign-off form** `docs/uat/signoff-template.md`: per module, stakeholder signs.
6. **UAT duration**: minimum 2 weeks recommended (no time estimates given to user; document the **gates**, not the timeline).
7. Commit each fix as it lands with PR linked to UAT bug ID.

## Deliverables

- `docs/uat/scenarios.csv`.
- `docs/uat/findings.md` (running log).
- Signed-off form per module.

## Verification

### Manual
1. Every scenario row marked PASS or FIX-AND-REVERIFY by named tester.
2. All Blockers/Majors closed.

## Definition of Done

- [ ] All scenarios PASS.
- [ ] Sign-offs collected.
- [ ] `_state.md` advanced.

## Next step

→ [`301-data-migration.md`](./301-data-migration.md)

## Previous step

← [`../phase-2-hardening/203-observability.md`](../phase-2-hardening/203-observability.md)
