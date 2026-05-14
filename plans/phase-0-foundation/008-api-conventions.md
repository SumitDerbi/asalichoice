# 008 — API Conventions (DRF Baseline)

> **Phase**: phase-0-foundation  **Depends on**: 005, 006  **Module**: --  **Est. effort**: S

## Goal

Codify the DRF baseline so every module's API plan is mechanical: a base viewset, base serializer, base permission, idempotency, pagination, filtering, throttling, error envelope, OpenAPI tags.

## Inputs

- [ ] 005 (core) + 006 (auth) complete.

## Steps

1. `apps/core/api/`:
   - `viewsets.py` → `BaseModelViewSet(ModelViewSet)` injecting audit, soft-delete, branch scoping, idempotency.
   - `serializers.py` → `BaseModelSerializer` with `created_at, updated_at, created_by, updated_by` read-only; consistent error formatting.
   - `permissions.py` → `HasAnyPermission`, `IsBranchScoped`, `IsSuperAdmin`. Plug into `_meta.yaml` security model.
   - `pagination.py` → `StandardPageNumberPagination(page_size=25, max=200)`, `LedgerCursorPagination`.
   - `filters.py` → `BaseFilterBackend` with consistent query params.
   - `idempotency.py` → header `Idempotency-Key` cached in Redis (24h) — fall back to DB table if Redis absent.
   - `exceptions.py` → already created in 001; extend to map domain exceptions to `{code, message, details}`.
2. `apps/core/api/throttling.py`:
   - `BurstAnonThrottle`, `BurstUserThrottle`, `OTPRateThrottle`, `LoginThrottle`. Rates from `_meta.yaml`.
3. OpenAPI: per-module tag registered automatically from viewset's `tags` attribute. Add `drf-spectacular` postprocessing hook to inject error envelope schema.
4. **Service layer convention**: every write goes through `apps/<module>/services.py`. Viewsets do validation + permission, services do business logic + audit + ledger. Document in `docs/adr/002-service-layer.md`.
5. **Domain exception convention**: each module exports `apps/<module>/exceptions.py` with subclasses of `DomainError(code, message)`. Handler maps to envelope.
6. Add `docs/api/conventions.md` mirroring `_conventions.md` §5 for end users.
7. Add a reference example: refactor `apps/users/` viewset to use `BaseModelViewSet` (where applicable) — proves the baseline.
8. Commit: `feat(core/api): drf baseline (viewset, serializer, permissions, pagination, idempotency)`.

## Deliverables

- `apps/core/api/` package complete.
- ADR-002 written.
- Users app refactored as baseline reference.

## Verification

### Manual
1. Create a quick scratch viewset using `BaseModelViewSet` — confirm audit + soft-delete + pagination work out of the box.
2. Send duplicate `Idempotency-Key` → returns cached response.

### Automated
- `pytest backend/tests/core/api/ -q` green (covering pagination, idempotency, error envelope, permissions).

## Definition of Done

- [ ] Baseline classes available.
- [ ] Users app proves the pattern.
- [ ] ADRs written.
- [ ] `_state.md` advanced.

## Next step

→ [`009-forms-validation-zod.md`](./009-forms-validation-zod.md)

## Previous step

← [`007-admin-shell-ui.md`](./007-admin-shell-ui.md)
