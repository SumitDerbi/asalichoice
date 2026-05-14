# 303 — Post-Launch

> **Phase**: phase-3-launch  **Depends on**: 302  **Est. effort**: S

## Goal

Establish the operating cadence after go-live: hyper-care window, support tiers, weekly health review, monthly roadmap planning, and known-deferred items.

## Steps

1. **Hyper-care window** (first 30 days):
   - Daily 15-min standup: incidents, hot bugs, top user feedback.
   - On-call rota with escalation matrix in `docs/operations/oncall.md`.
   - Daily error/alert digest emailed to engineering lead.
2. **Support tiers**:
   - L1: branch managers / store staff handle UI issues.
   - L2: AsliChoice support team handles config + data.
   - L3: engineering for code/data fixes.
   - Ticket system + SLAs in `docs/operations/support.md`.
3. **Weekly health review** (recurring):
   - Uptime, error budget burn, p95 latencies vs SLA, top 10 errors, queue depths, backup status, security findings.
   - Output: short note appended to `docs/operations/weekly-review/YYYY-MM-DD.md`.
4. **Monthly KPI review**: business KPIs (GMV, orders, ATV, return rate, NPS) shared with leadership.
5. **Backup drills**: full restore drill quarterly. Result logged.
6. **DR drill**: switch to standby (if/when DR site exists) annually; for now, document the RPO ≤ 15min / RTO ≤ 4hr expectation per Appendix E + the gap-to-target.
7. **Roadmap parking lot** `docs/roadmap/parking-lot.md`:
   - Multi-currency.
   - UI localisation (Hindi, regional).
   - Native mobile apps.
   - Marketplace integration (Amazon/Flipkart).
   - Advanced analytics / AI-driven reordering.
   - OpenTelemetry tracing.
8. **Deprecation policy** `docs/operations/deprecation.md`: how API versions sunset; minimum overlap 6 months for breaking changes.
9. **Documentation freshness**: monthly audit — each module page links to latest screenshots; ADR list reviewed.
10. **Plan-system continuity**: any new feature gets a new plan file under `plans/post-launch-features/` following the same template. Update `_state.md` accordingly.

## Deliverables

- `docs/operations/oncall.md`, `support.md`, `weekly-review/`, `deprecation.md`.
- `docs/roadmap/parking-lot.md`.
- `plans/post-launch-features/` folder placeholder.

## Verification

### Manual
1. First weekly review meeting held; note committed.
2. First on-call rotation actually responded to a synthetic alert.

## Definition of Done

- [ ] Operating cadence running.
- [ ] Docs published.
- [ ] **Phase 3 COMPLETE**.
- [ ] Project handed over to BAU.
- [ ] `_state.md` final history entry written.

## Next step

→ Continuous improvement (`plans/post-launch-features/`).

## Previous step

← [`302-go-live-runbook.md`](./302-go-live-runbook.md)
