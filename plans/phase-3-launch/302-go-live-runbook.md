# 302 — Go-Live Runbook

> **Phase**: phase-3-launch  **Depends on**: 301  **Est. effort**: S

## Goal

The exact, step-by-step procedure to flip the switch from legacy to AsliChoice in production with minimal downtime and a known-good rollback path.

## Steps (the runbook itself)

### T-7 days
- [ ] Communicate cutover window to all stakeholders.
- [ ] Final UAT sign-offs collected.
- [ ] Production cPanel account provisioned: virtualenvs, DBs, subdomains, SSL certs.
- [ ] `~/deploy_config/production/` populated with `production.config` + `production.env`.
- [ ] DNS TTLs lowered to 300s.
- [ ] Backups verified (restore test on staging from latest prod-shape backup).

### T-1 day
- [ ] Final code freeze on `main`.
- [ ] Deploy to production using `./deploy.sh main production` (apps live but legacy still authoritative).
- [ ] Smoke test admin login, OPS dashboard, storefront home — all on production URLs.
- [ ] Verify monitoring + alerting flowing.

### T-0 cutover (off-hours)
1. **Freeze legacy** writes (lock POS terminals; put storefront in maintenance).
2. **Final delta migration** per [`301`](./301-data-migration.md). Reconcile. Sign off.
3. **Switch DNS** for storefront + API + admin to production.
4. **Smoke test in production**:
   - Login as each role.
   - Place a real test sale (₹1, refunded).
   - Place a real test online order (₹1, refunded).
   - Verify M17 notifications fire.
   - Verify M12 JE posted.
   - Verify reports load.
5. **Unfreeze**: allow real users in.
6. **Announce** go-live to internal teams + customer base via M17 broadcast.

### T+1 hour
- [ ] Hyper-care: engineers on standby; alert channels watched.
- [ ] Spot-check first 50 real sales for correctness end-to-end.

### T+24 hours
- [ ] Pull go-live report: transactions count, errors, alerts fired, MTTR.
- [ ] Triage any minor issues into next sprint.

## Rollback procedure
- If reconciliation fails or critical bug surfaces within first 4 hours:
  1. Switch DNS back to legacy.
  2. Unfreeze legacy.
  3. Drain in-flight production transactions to a holding table for later reconciliation.
  4. Post-mortem within 48 hours.

## Deliverables

- This runbook becomes `docs/operations/go-live.md`.
- Filled-in checklist after go-live.

## Verification

### Manual
- Each checkbox above ticked by named on-call engineer.

## Definition of Done

- [ ] Go-live completed.
- [ ] No P1/P2 open at T+24h.
- [ ] Post-mortem (positive or negative) written.
- [ ] `_state.md` advanced.

## Next step

→ [`303-post-launch.md`](./303-post-launch.md)

## Previous step

← [`301-data-migration.md`](./301-data-migration.md)
