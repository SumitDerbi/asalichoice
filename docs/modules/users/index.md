# Users, Roles & Permissions (M02)

The users module owns identity, authentication, and role-based access
control (RBAC) for the entire system. Every downstream module checks
permissions issued here; every authenticated request resolves a user
that lives in `apps.users`.

![tests](https://img.shields.io/badge/backend_tests-162_passing-brightgreen)
![admin-ui](https://img.shields.io/badge/admin--ui_tests-55_passing-brightgreen)

## Scope

In scope:

- Custom `User` model with three login identifiers — email, mobile,
  employee code. Any one of them logs the same user in.
- Password login and OTP login (SMS → EMAIL → WHATSAPP smart
  fallback — see [ADR-005](../../adr/005-otp-smart-fallback.md)).
- Password reset via OTP.
- `Role`, `Permission`, `UserRole`, `UserBranchAccess` and a
  branch-scoped permission resolver.
- JWT issuance (access + refresh) with rotation and refresh
  blacklisting after rotation.
- Login attempt + OTP delivery audit (`LoginAttempt`, `OTPLog`,
  `LoginSession`).

Out of scope (later modules):

- Customer & vendor identity (M03 / M04 — separate models).
- SSO / external IdP (deferred to phase-2).
- 2FA TOTP — phase-2.

## Entities

| Group    | Models                                   |
| -------- | ---------------------------------------- |
| Identity | `User`                                   |
| RBAC     | `Role`, `Permission`, `UserRole`         |
| Access   | `UserBranchAccess`                       |
| Audit    | `LoginAttempt`, `OTPLog`, `LoginSession` |

All models inherit `apps.core.models.BaseModel` (soft-delete + audit
timestamps). Use `User.all_objects` to see deactivated rows.

## Identifiers

`User` defines three unique login identifiers:

| Field                | Constraint                           | Notes                        |
| -------------------- | ------------------------------------ | ---------------------------- |
| `email`              | `unique=True, null=True, blank=True` | Case-insensitive lookup.     |
| `mobile`             | `unique=True, null=True, blank=True` | Stored E.164-ish, no spaces. |
| `employee_code`      | `unique=True, null=True, blank=True` | Case-insensitive lookup.     |
| `primary_identifier` | Char(16), one of `EMAIL/MOBILE/CODE` | UI display hint.             |

The auth backend
(`apps.users.auth_backends.IdentifierBackend`) resolves an identifier
to a `User` via case-insensitive match on any of the three columns.

## RBAC

- `Permission(code, name, category)` is the atomic capability. Codes
  use dotted namespaces, e.g. `users.read`, `master.branch.write`.
  Wildcard `*` grants everything (superuser only).
- `Role(code, name, is_system, permissions M2M)` aggregates
  permissions. System roles (`SUPER_ADMIN`, `OPS_ADMIN`, etc.) are
  protected from edits / deletion (raises `SystemRoleProtected` →
  `USR-020`).
- `UserRole(user, role, branch=nullable)` assigns a role with an
  optional branch scope — a NULL branch means _all branches_.
- `UserBranchAccess(user, branch, is_default)` controls which branches
  a user can switch into via the `X-Branch-Id` header.

The permission resolver (`apps.users.services.permission_service`) is
cached per request: `user_permissions(user, branch_id=None)` returns
the merged set of permission codes the user holds for that branch.

```python
from apps.users.api_public import user_can_access_branch
if not user_can_access_branch(request.user, request.branch_id):
    raise BranchAccessDenied()
```

## Auth surface (`/api/v1/auth/`)

| Method | Path                            | Notes                                                                     |
| ------ | ------------------------------- | ------------------------------------------------------------------------- |
| POST   | `/auth/login/`                  | Body: `{identifier, password}`. Returns access + refresh + user envelope. |
| POST   | `/auth/refresh/`                | Body: `{refresh}`. Rotates refresh, blacklists old.                       |
| POST   | `/auth/logout/`                 | Body: `{refresh}`. Blacklists token, ends session.                        |
| GET    | `/auth/me/`                     | Returns user + permissions[] + branches[].                                |
| POST   | `/auth/otp/request/`            | Body: `{identifier, purpose?, preferred_channel?}`.                       |
| POST   | `/auth/otp/verify/`             | Body: `{identifier, code, purpose?}`. Returns JWT pair on `LOGIN`.        |
| POST   | `/auth/password-reset/request/` | Body: `{identifier}`. Sends OTP.                                          |
| POST   | `/auth/password-reset/confirm/` | Body: `{identifier, code, new_password}`.                                 |

## Admin surface

CRUD routers under `/api/v1/`:

| Resource           | Path                        |
| ------------------ | --------------------------- |
| Users              | `/users/`                   |
| Roles              | `/roles/`                   |
| Permissions        | `/permissions/` (read-only) |
| User-role bindings | `/user-roles/`              |
| Branch access      | `/branch-access/`           |

All admin routes require an authenticated user holding the matching
`users.*` permission for the branch context in `X-Branch-Id`.

## Throttles

DRF throttle scopes:

| Scope     | Rate     | Applied to                                 |
| --------- | -------- | ------------------------------------------ |
| `auth`    | `20/min` | login, refresh, logout                     |
| `otp`     | `5/min`  | otp/request, otp/verify, password-reset/\* |
| `default` | `60/min` | everything else                            |

OTP throttling is additionally enforced inside `request_otp` over a
15-minute window (see service).

## Seed data

```bash
python manage.py seed_permissions   # all Permission rows (idempotent)
python manage.py seed_roles         # SUPER_ADMIN + default roles
```

## Test coverage

Backend: **162 tests passing** including 28 dedicated M02 tests
covering models, services (auth + OTP smart-fallback + permissions),
and API endpoints.

```bash
cd backend
pytest tests/users/ --cov=apps.users --cov-report=term-missing
```

## See also

- [User guide](user-guide.md) — login flows for end users.
- [Developer guide](developer-guide.md) — wiring into apps.users.
- [Error codes](error-codes.md) — `AUTH-*` / `USR-*` envelope reference.
- [ADR-005 — OTP smart fallback](../../adr/005-otp-smart-fallback.md)
