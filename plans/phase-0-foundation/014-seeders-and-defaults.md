# 014 — Seeders & Default Data

> **Phase**: phase-0-foundation  **Depends on**: 005, 006, 013  **Module**: pre-M01  **Est. effort**: S

## Goal

Establish the seeding pattern: idempotent management commands that populate the DB with the defaults the app needs to start. Phase-0 seeders create the minimum; each module adds its own seeder later.

## Inputs

- [ ] 013 complete.

## Steps

1. `apps/core/management/commands/seed_all.py` — orchestrator command that calls each module's seeder in dependency order (reads `_meta.yaml` order or hardcoded list).
2. Per-module seeders live at `apps/<module>/management/commands/seed_<module>.py`. Each:
   - Is **idempotent** (uses `get_or_create` / `update_or_create`).
   - Accepts `--reset` flag (deletes its own data first; guarded by `DEBUG=True`).
   - Logs `created` vs `updated` counts.
3. Phase-0 seeders to ship now:
   - `seed_superuser` (already from 006).
   - `seed_settings` (already from 013).
   - `seed_roles` — `SUPER_ADMIN`, `ADMIN`, `MANAGER`, `STAFF`, `CASHIER`, `CUSTOMER`, `PARTNER`, `VENDOR` (placeholders; full permission matrix in M02).
   - `seed_default_branch` — single "Head Office" branch (placeholder; real Branch model in M01).
   - `seed_default_currency` — INR (in settings).
   - `seed_default_timezone` — Asia/Kolkata.
4. Add `make seed` / `scripts/seed.{ps1,sh}` calling `python manage.py seed_all`.
5. Document seeders in `docs/operations/seeding.md`. Include: what runs, idempotency guarantee, how to add a new module seeder.
6. Tests: each seeder runs twice without errors and produces same row count.
7. Commit: `feat(core): seeder framework + phase-0 default data`.

## Deliverables

- `seed_all` orchestrator.
- 5 phase-0 seeders.
- `make seed`.
- Docs page.

## Verification

### Manual
1. Fresh DB → `make seed` → all defaults present.
2. Run again → no duplicates.
3. Login still works.

### Automated
- `pytest backend/tests/core/test_seeders.py -q` green.

## Definition of Done

- [ ] Orchestrator + 5 seeders working.
- [ ] Idempotent.
- [ ] Docs written.
- [ ] **Phase 0 COMPLETE**.
- [ ] `_state.md` advanced to `phase-1-modules/README.md`.

## Next step

→ [`../phase-1-modules/README.md`](../phase-1-modules/README.md)

## Previous step

← [`013-site-settings-feature-toggles.md`](./013-site-settings-feature-toggles.md)
