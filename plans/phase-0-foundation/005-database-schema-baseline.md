# 005 — Database Schema Baseline

> **Phase**: phase-0-foundation  **Depends on**: 001  **Module**: --  **Est. effort**: S

## Goal

Establish reusable abstract models, audit/ledger primitives, soft-delete manager, and migration conventions that **every module** will build on. Nothing module-specific yet.

## Inputs

- [ ] 001 complete.

## Steps

1. Create `apps/core/models/` with:
   - `TimeStampedModel` (`created_at`, `updated_at`).
   - `SoftDeleteModel` (`is_active: bool default True`, `deleted_at: datetime | null`). Manager: `objects` returns active only; `all_objects` returns everything.
   - `AuditableModel` (`created_by`, `updated_by` FKs to `users.User` — placeholder until M02; use `settings.AUTH_USER_MODEL`).
   - `BaseModel(TimeStamped, SoftDelete, Auditable, abstract=True)`.
2. Create `apps/core/audit/`:
   - `AuditLog(model, action, object_id, before, after, actor, branch, ip, user_agent, timestamp)`.
   - `audit(...)` service function used by every write path.
   - Middleware `RequestContextMiddleware` storing actor + IP + UA in thread-local for the service layer.
3. Create `apps/core/ledger/`:
   - Abstract `LedgerEntry` (`reference_type, reference_id, amount, balance_before, balance_after, actor, branch_id, timestamp, remarks`).
   - Concrete ledgers will subclass per domain (inventory, wallet, vendor, customer, finance).
4. Create `apps/core/branch_context.py`:
   - Thread-local current-branch resolver, used to scope queries.
5. Add settings constants `AUDIT_RETENTION_YEARS = 7`, `LEDGER_IMMUTABLE = True`.
6. Add a `check` (`django.core.checks`) that flags any non-abstract model not inheriting `BaseModel` (warning, can be silenced per-model).
7. Migration policy in `docs/adr/001-migrations.md`:
   - One migration per logical change.
   - Squash only at module boundaries before module-merge.
   - Data migrations separate from schema migrations.
   - Never edit a merged migration.
8. Add `pytest` fixtures `tests/conftest.py`: authenticated client factory, branch fixture, audit-capturing helper.
9. Commit: `feat(core): baseline abstract models + audit + ledger primitives`.

## Deliverables

- `apps/core/models/`, `apps/core/audit/`, `apps/core/ledger/`.
- Middleware registered.
- ADR-001 written.
- Conftest fixtures.

## Verification

### Manual
1. `python manage.py makemigrations core` produces a clean initial migration.
2. Create a throwaway model inheriting `BaseModel` in a scratch test → audit entry is recorded on save.

### Automated
- `pytest backend/tests/core/test_audit.py -q` green.
- `pytest backend/tests/core/test_soft_delete.py -q` green.
- `python manage.py check` clean.

## Definition of Done

- [ ] Primitives importable across modules.
- [ ] Audit middleware live.
- [ ] Tests green.
- [ ] ADR-001 written.
- [ ] `_state.md` advanced.

## Next step

→ [`006-auth-skeleton.md`](./006-auth-skeleton.md)

## Previous step

← [`004-tooling-linting-husky.md`](./004-tooling-linting-husky.md)
