# ADR-003 — Branch context via header + contextvar

- **Status**: Accepted
- **Date**: 2026-05-17
- **Decider**: backend team
- **Context plan**: `plans/phase-1-modules/M01-master-management/03-integration.md`

## Context

Almost every business operation in the platform is scoped to a branch
— a sale, a stock movement, an audit row, a payment mode toggle. The
admin UI is a single-page app, and a user might switch branches
without reloading the page. We need a transport for the current
branch that is:

1. Stateless on the server (no session cookie coupling).
2. Cheap to read inside services, signals, and management commands.
3. Auditable — every audit row must record the branch under which it
   was created, even when the originating ORM call doesn't pass one
   explicitly.
4. Safe under async workers — the value must not leak between requests
   on the same process.

## Decision

### 1. Header transport

Clients send `X-Branch-Id: <int>` on every authenticated request. The
header is allowlisted in `CORS_ALLOW_HEADERS`. Public endpoints accept
the header but treat its absence as "use the global default."

### 2. Validating middleware

`apps.master.middleware.BranchContextMiddleware`:

- Parses `X-Branch-Id`.
- Verifies the branch exists, is active, and (in future, with M02) is
  accessible to the authenticated user.
- Falls back to `SiteSetting key='default.branch_id'` when the header
  is absent. This fallback is **anonymous-safe** — it does not require
  an authenticated user.
- Binds the resolved id to a contextvar via
  `apps.core.context.set_current_branch(branch_id)`.

The middleware runs after `RequestContextMiddleware` so its explicit
value wins over the audit middleware's default `None`.

### 3. Contextvar storage

`apps.core.context.current_branch_id` is a `contextvars.ContextVar[int | None]`.
Services read it via `current_branch_id()` (returns `int | None`) or
`get_current_branch()` (returns `Branch | None`, cached). Celery tasks
that need a branch context wrap their handler in a small contextvar
shim that snapshots the calling request's value.

### 4. No thread locals

We deliberately did **not** use `threading.local()`. Contextvars
behave correctly under `asyncio`, under Django's async views, and
under Celery's threaded executor. Thread-locals leak between async
tasks scheduled on the same thread.

## Consequences

- The header is now part of the contract for every authenticated
  endpoint. Clients without it get the default branch — a server-side
  decision, not a 400. This keeps server endpoints permissive and
  pushes UX choices (force-select-a-branch) to the admin UI.
- Audit rows always carry a branch, even for management commands —
  the seeder, for example, explicitly sets the HQ branch before
  running.
- Service-layer functions can ignore the branch and still get correct
  audit behaviour; or they can read the contextvar explicitly when
  the business logic depends on it.
- Middleware order is now load-bearing. A misorder is caught by the
  `test_branch_context_overrides_request_context` test in
  `tests/master/test_middleware.py`.

## Alternatives considered

- **Per-request kwarg threaded through every service call**: rejected
  because it pollutes every signature with `branch` even for code
  that doesn't care, and is impossible to enforce in audit signals.
- **Session-backed branch selection**: rejected because the admin
  UI is SPA and the storefront is anonymous; session state would be
  inconsistent across surfaces.
- **JWT claim**: rejected because rotating the branch would require
  re-issuing the access token, which kills the "switch branches
  without reload" UX.
- **Thread-local fallback (current_branch via `threading.local()`)**:
  rejected — leaks under async (see Decision §4).

## Follow-ups

- M02 will add user → branch ACLs and the middleware will deny the
  header when the user lacks access (currently any branch is
  accepted).
- M18 (Redis cache pass) will move branch metadata into Redis so
  `get_current_branch()` becomes a sub-millisecond lookup.
