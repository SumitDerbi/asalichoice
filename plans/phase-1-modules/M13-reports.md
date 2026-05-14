# M13 — Reports & Dashboards

> **Phase**: phase-1-modules  **SRS ref**: Module 13  **Depends on**: M03–M12, M14, M15  **Est. effort**: L

## Goal

Unified reporting: sales, inventory, purchase, finance, delivery, CRM, HR. Role-aware dashboards. Scheduled report email/export. Drill-down from KPIs to raw rows.

## Steps

1. **Reporting layer** `apps/reports/`:
   - `Report(code unique, name, module, params_schema_json, query_spec_json, default_layout_json, role_codes[])`.
   - `ReportSchedule(report FK, cron, recipients[], format=CSV|XLSX|PDF, params_json, is_active)`.
   - `ReportRun(report FK, params_json, started_at, finished_at, status, output_path, by FK user)`.
2. **Services**:
   - `report_engine.run(code, params, user)` — validates perm, executes query (read-only DB user where possible), caches per (code, params_hash) for 60s.
   - `schedule_service.dispatch()` — Celery beat scans due schedules.
   - `export_service.to_csv/xlsx/pdf`.
3. **Canonical reports** (each implemented as a query spec, no per-report code):
   - Sales: daily summary, by category, by cashier, by payment mode, top SKUs, hourly heatmap.
   - Inventory: stock on hand, valuation (FIFO/Avg via batches), ageing, expiry, low-stock, dead-stock.
   - Purchase: vendor performance, PO vs GRN variance.
   - Finance: TB, P&L, BS, Cash Flow, AR/AP ageing, GST returns (GSTR-1 prep CSV).
   - Delivery: SLA compliance, COD reconciliation status.
   - CRM: campaign performance, coupon usage, referral funnel.
   - HR: attendance summary, payroll summary.
4. **Dashboards** `apps/dashboard/`:
   - Pluggable widgets; each role has a default layout (stored in DB, editable).
   - Widgets: KPI card, time-series chart, leaderboard, alerts feed.
5. **Endpoints**: `/api/v1/reports/`, `/api/v1/reports/{code}/run/`, `/api/v1/reports/{code}/export/`, `/api/v1/dashboards/me/`.
6. **Error prefix**: `RPT-*`.
7. **Admin-UI**:
   - Reports hub: filterable list, run inline, export.
   - Each report has consistent layout: filters card, table, chart (where applicable), export buttons.
   - Dashboard home with role-default widgets, drag-rearrange + save layout.
8. **Performance**:
   - For heavy reports, write a materialised summary table updated via Celery (e.g., daily sales summary by branch).
   - Cursor pagination for raw rows.
9. **Permissions**: `reports.view.<code>`, `reports.schedule.manage`, `dashboard.layout.manage`.
10. **Tests**: each report query against fixtures, scheduled-run via newman, export round-trip.
11. **Docs**: `docs/modules/reports/*` + ADR `016-reporting-query-spec.md`.
12. Commit: `feat(M13): reports + dashboards`.

## Verification

### Manual
1. Run "Daily sales by branch" → numbers match raw DB sum.
2. Schedule weekly report → email arrives on time (M17 stub OK).
3. Owner dashboard loads under 5s p95 against seeded sample data (≥ 10k sales).

### Automated
- `pytest backend/tests/reports/ -q` ≥ 80%.
- UI + Playwright + Newman green.

## Definition of Done

- [ ] All canonical reports run correctly.
- [ ] Dashboard loads within SLA.
- [ ] Scheduled exports work.
- [ ] `_state.md` advanced.

## Next step

→ [`M16-hr-payroll.md`](./M16-hr-payroll.md)

## Previous step

← [`M12-finance.md`](./M12-finance.md)
