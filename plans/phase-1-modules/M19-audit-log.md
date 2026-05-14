# M19 — Audit & Activity Log (full)

> **Phase**: phase-1-modules  **SRS ref**: Module 19  **Depends on**: Phase-0 005  **Est. effort**: M

## Goal

Productionise the audit infrastructure introduced in Phase-0/005: structured viewers, search, filters, retention enforcement, tamper-evidence (hash chain), export for compliance, sensitive-field redaction.

## Steps

1. **Extend `AuditLog`** model:
   - Add `prev_hash`, `hash` columns (SHA-256 over canonical JSON + prev_hash) for tamper-evident chain.
   - Add indices: `(model, object_id)`, `(actor, ts)`, `(branch, ts)`.
2. **Sensitive-field policy**:
   - Per-model `AUDIT_REDACT_FIELDS = ['password', 'aadhaar', 'pan', ...]` honored by audit serializer.
   - Display-time masking; raw values never stored.
3. **Retention service**:
   - `retention_service.purge_old()` Celery nightly — purges per `AUDIT_RETENTION_YEARS` (7 default per `_meta.yaml` cross-cutting), respects per-model overrides.
   - Operational logs (request log etc.) at 12 months.
4. **Tamper check command**: `python manage.py audit_verify --from=DATE --to=DATE` walks chain & reports breaks.
5. **Endpoints**: `/api/v1/audit/logs/` with rich filters (actor, model, object, action, date range, branch).
6. **Admin-UI**:
   - Global audit viewer (Super Admin / Auditor only).
   - Per-record audit drawer on every detail page ("Activity" tab) — diff view (before/after).
   - Export CSV for date range.
7. **Error prefix**: `SEC-*` (security/audit category).
8. **Permissions**: `audit.view`, `audit.export`, `audit.verify`.
9. **Tests**: hash chain integrity, redaction, retention purge, diff renderer.
10. **Docs**: `docs/modules/audit/*` + ADR `021-tamper-evident-audit.md`.
11. Commit: `feat(M19): audit log productionised`.

## Verification

### Manual
1. Edit a record → audit log row created with `before/after` JSON.
2. Sensitive fields appear redacted in viewer.
3. `audit_verify` reports OK; tamper a row manually → command reports break.

### Automated
- `pytest backend/tests/audit/ -q` ≥ 90% (security-critical).
- UI + Playwright + Newman green.

## Definition of Done

- [ ] Tamper-evident chain proven.
- [ ] Retention enforced.
- [ ] PII redacted.
- [ ] `_state.md` advanced.

## Next step

→ [`M20-mobile-api-sync.md`](./M20-mobile-api-sync.md)

## Previous step

← [`M18-system-settings.md`](./M18-system-settings.md)
