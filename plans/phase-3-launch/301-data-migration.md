# 301 — Data Migration

> **Phase**: phase-3-launch  **Depends on**: 300  **Est. effort**: M

## Goal

Bring real production data from legacy systems (existing inventory, customers, GL balances, employee records) into AsliChoice cleanly, with rollback, validation, and reconciliation.

## Steps

1. **Inventory of legacy sources**: list each (Excel, Tally, old POS DB, CRM exports). Owner per source.
2. **Extract**:
   - For each source produce a CSV in a canonical staging schema, stored under `migration/staging/<source>/`.
   - Reproducible scripts in `migration/extract/`.
3. **Transform & validate**:
   - Python notebooks/scripts in `migration/transform/` mapping to AsliChoice canonical models.
   - Validation rules: unique keys, referential integrity, value domains. Output: pass + fail rows. **Zero fails before load** (or documented exception).
4. **Load**:
   - Idempotent Django management commands: `python manage.py migrate_<source>` reading staging CSVs. Wrap in transactions; use `--dry-run`.
   - Audit each load run; record source-id → AsliChoice-id mapping in `migration_audit` table for traceability.
5. **Reconciliation**:
   - Row counts: legacy vs new.
   - Financial totals: legacy GL trial balance vs M12 trial balance on cutover date — must match to the rupee (or differences documented).
   - Inventory valuation: legacy vs M05 on cutover.
   - Customer wallet balances: legacy vs M09.
6. **Cutover plan**:
   - Freeze period (no new transactions in legacy for X hours; document length).
   - Final delta extract.
   - Load.
   - Reconcile.
   - Switch DNS / go live.
7. **Rollback plan**:
   - If reconciliation fails, revert DNS, unfreeze legacy, investigate. Migration scripts must be idempotent so re-run is safe.
8. **Data sanity checks** post-load:
   - Random sample of 100 SKUs: prices match.
   - 50 customers: wallet/loyalty match.
   - 20 vendors: outstanding matches.
9. **Docs**: `docs/operations/data-migration.md` with the full runbook, mappings, exceptions log.
10. Commit: `chore(migration): legacy data migration scripts + reconciliation`.

## Verification

### Manual
1. Dry-run on staging produces zero fails.
2. Reconciliation report shows zero variance (or documented variance signed off).

### Automated
- `python manage.py migration_verify` reports OK against staging snapshot.

## Definition of Done

- [ ] Dry-run clean.
- [ ] Reconciliation signed off.
- [ ] Runbook published.
- [ ] `_state.md` advanced.

## Next step

→ [`302-go-live-runbook.md`](./302-go-live-runbook.md)

## Previous step

← [`300-uat-checklist.md`](./300-uat-checklist.md)
