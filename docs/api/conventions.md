# API Conventions

> Audience: AsliChoice module authors + API consumers. Source of truth:
> [`plans/_conventions.md`](https://github.com/SumitDerbi/asalichoice/blob/main/plans/_conventions.md) §5. This page
> mirrors the contract in user-facing form.

## Base URL

All endpoints are versioned under `/api/v1/`. Breaking changes ship as
`/api/v2/`; minor additions stay under `v1`.

## Authentication

JWT bearer (SimpleJWT). Obtain via `POST /api/v1/auth/login/`, refresh
via `POST /api/v1/auth/refresh/`, revoke via `POST /api/v1/auth/logout/`.
Inspect the current user with `GET /api/v1/auth/me/`.

```http
Authorization: Bearer <access-token>
```

## Standard verbs

| Verb     | Semantic                                                        |
| -------- | --------------------------------------------------------------- |
| `GET`    | List / retrieve. Paginated by default.                          |
| `POST`   | Create or perform action. Accepts `Idempotency-Key`.            |
| `PUT`    | Full update of an existing resource. Accepts `Idempotency-Key`. |
| `PATCH`  | Partial update. Accepts `Idempotency-Key`.                      |
| `DELETE` | Soft-delete (flips `is_active=false`, sets `deleted_at`).       |

## Pagination

- **Default**: page-number pagination (`?page=2&page_size=50`). Page
  size default 25, max 200.
- **Ledgers**: cursor pagination (`?cursor=…`) for append-only
  endpoints.

Response shape:

```json
{
  "count": 137,
  "next": "https://…/?page=3",
  "previous": "https://…/?page=1",
  "results": [ … ]
}
```

## Filtering, search, ordering

- `?search=<text>` — text search on configured fields.
- `?ordering=field` / `?ordering=-field` — sort ascending / descending.
- `?include_inactive=true` — include soft-deleted rows (admin only).
- Module-specific filters are documented in the endpoint's OpenAPI
  schema.

## Idempotency

Pass `Idempotency-Key: <opaque-string>` on any mutating request.
Repeating the same request with the same key within 24 hours returns
the original response with `Idempotency-Replay: true`. Generate keys
client-side (UUIDv4 recommended).

## Error envelope

Every non-2xx response uses the same shape:

```json
{
  "error": {
    "code": "INV-001",
    "message": "Insufficient stock",
    "details": { "available": 3, "requested": 5 }
  }
}
```

Code prefixes (from `plans/_conventions.md` §5):

| Prefix | Domain                              |
| ------ | ----------------------------------- |
| `AUTH` | authentication / OTP                |
| `USR`  | users / roles                       |
| `MST`  | master data                         |
| `VEN`  | vendor                              |
| `PUR`  | purchase / GRN                      |
| `INV`  | inventory                           |
| `POS`  | retail POS                          |
| `ONL`  | online store                        |
| `SAL`  | sales / orders                      |
| `CRM`  | customer / CRM                      |
| `REF`  | referral / wallet                   |
| `NTF`  | notifications                       |
| `FIN`  | finance / ledger                    |
| `RPT`  | reports                             |
| `DEL`  | delivery / fulfillment              |
| `RET`  | returns / QC                        |
| `HR`   | HR / payroll                        |
| `DOC`  | documents / media                   |
| `CFG`  | system settings                     |
| `SEC`  | super admin / audit                 |
| `API`  | API / sync / device-level fallbacks |

`API-400`, `AUTH-401`, `AUTH-403`, `API-404`, `API-409`, `API-429`,
`API-500` are the generic fallbacks emitted by DRF itself.

## Rate limits

| Scope        | Default rate     | Env override          |
| ------------ | ---------------- | --------------------- |
| `login`      | 5 / min / IP     | `THROTTLE_LOGIN_RATE` |
| `burst-anon` | 60 / min / IP    | `THROTTLE_ANON_RATE`  |
| `burst-user` | 120 / min / user | `THROTTLE_USER_RATE`  |
| `otp`        | 5 / 15min        | `THROTTLE_OTP_RATE`   |

Throttle hits return HTTP 429 with envelope code `API-429` and a
`Retry-After` header in seconds.

## Audit

Every write goes through a module service which records an
`AuditLog` row (actor, before, after, IP, user-agent, branch). The log
is append-only and retained for 7 years (`AUDIT_RETENTION_YEARS`).

## OpenAPI

The full schema is available at `GET /api/v1/schema/` (drf-spectacular)
and rendered as Swagger / ReDoc at `/api/v1/schema/swagger/` and
`/api/v1/schema/redoc/` (mounted in `config/urls.py`). Every operation
documents `ErrorEnvelope` for 4xx / 5xx responses via the
`apps.core.api.openapi.add_error_envelope` postprocessor.
