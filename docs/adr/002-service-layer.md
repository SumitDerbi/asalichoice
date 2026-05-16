# ADR-002 — Service layer + domain exceptions

- **Status**: Accepted
- **Date**: 2026-05-16
- **Decider**: backend team
- **Context plan**: `plans/phase-0-foundation/008-api-conventions.md`

## Context

Every module is going to ship CRUD viewsets, business operations, audit
trails, and a ledger of some sort. Without a hard rule on _where_ each
of those lives, business logic ends up spread across serializers,
viewsets, signal handlers, and `save()` overrides — making it hard to
review, hard to test, and impossible to audit consistently.

We also need a stable error contract so the admin UI (and future API
consumers) can render typed messages instead of free-form strings.

## Decision

### 1. Three layers, one direction

```
View / ViewSet      →   validation, permission, pagination, serialization
       │
       ▼
Service             →   business logic, audit, ledger entries, side effects
       │
       ▼
ORM / Repository    →   persistence
```

- **Viewsets** must not touch the ORM directly for writes. They call a
  module-level service function and serialize the result.
- **Services** live in `apps/<module>/services.py` (or
  `apps/<module>/services/` for larger modules). They are plain Python
  callables — _not_ classes, _not_ DRF objects — so they can be invoked
  from management commands, Celery tasks, and tests without booting DRF.
- **Services own the audit trail.** Every state change calls
  `apps.core.audit.audit(...)` with the relevant `before` / `after`.
- **Services own ledger entries** for modules listed in
  `plans/_meta.yaml § principles.ledger_driven`.
- **Reads** _may_ go through a service if there's logic to share, but
  simple list/retrieve can live entirely in the viewset.

### 2. Idempotency belongs to the boundary

The `Idempotency-Key` replay cache (see
`apps/core/api/idempotency.py`) sits on the viewset. Services do not
need to know they were called twice — the second call never happens.

### 3. Domain exceptions over `ValidationError`

Business-rule violations raise a `DomainError` subclass declared in
`apps/<module>/exceptions.py`. The DRF exception handler renders them
through the standard envelope:

```json
{
  "error": {
    "code": "INV-001",
    "message": "Insufficient stock",
    "details": { "available": 3, "requested": 5 }
  }
}
```

- Use `serializers.ValidationError` only for **field validation**
  (shape, required, type, format). Anything that requires consulting
  the DB — stock levels, balance limits, status transitions — is a
  `DomainError`.
- Prefixes follow the namespace table in `plans/_conventions.md §5`.

### 4. Default permissions stack

`BaseModelViewSet.permission_classes = (IsAuthenticated, HasAnyPermission)`
plus an optional `IsBranchScoped` for branch-scoped writes. Modules
opt into additional checks via `required_perms` (RBAC details land in
M02).

## Consequences

- **+** A single audit trail for every write. Compliance + 7-year
  retention story (`AUDIT_RETENTION_YEARS`) becomes trivial.
- **+** Services are unit-testable without HTTP / DRF.
- **+** Module API plans become mechanical — fill in five files, done.
- **−** A small amount of ceremony for trivial CRUD (POST → service →
  return saved instance). Worth it for the consistency.
- **−** Two ways to surface errors (`ValidationError` vs `DomainError`).
  The split is the point — reviewers should challenge any
  `ValidationError` that depends on DB lookups.

## Notes

- The thin viewset wrappers in `apps.core.api.viewsets` provide
  `service_create` / `service_update` / `service_destroy` hooks that
  modules can override to plug in their services without re-implementing
  `perform_*`. Until a module needs them they remain pass-throughs to
  the default ORM-backed implementation.
- Tests live under `backend/tests/<module>/test_services.py` for the
  pure-Python service tests and `test_api.py` for the HTTP surface.
