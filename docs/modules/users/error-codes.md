# Users — Error codes

All errors raised by `apps.users` use the standard error envelope:

```json
{
  "error": {
    "code": "AUTH-NNN" | "USR-NNN",
    "message": "human-readable message",
    "details": null
  }
}
```

The `AUTH-*` namespace covers authentication / OTP flows. The
`USR-*` namespace covers user / role administration. Codes are stable
and **never reused** — retired exception classes leave their code
permanently retired.

## AUTH-\* (authentication)

| Code       | HTTP | Exception             | When raised                                                                              |
| ---------- | ---- | --------------------- | ---------------------------------------------------------------------------------------- |
| `AUTH-001` | 400  | `InvalidCredentials`  | Login with a wrong identifier / password combination.                                    |
| `AUTH-002` | 400  | `InactiveAccount`     | Login attempt against a deactivated user.                                                |
| `AUTH-003` | 423  | `AccountLocked`       | Too many failed attempts — account temporarily locked.                                   |
| `AUTH-004` | 400  | `IdentifierUnknown`   | OTP / password-reset for an identifier we don't recognise.                               |
| `AUTH-010` | 400  | `OTPInvalid`          | Submitted OTP does not match.                                                            |
| `AUTH-011` | 400  | `OTPExpired`          | OTP older than its TTL (10 min default).                                                 |
| `AUTH-012` | 400  | `OTPAttemptsExceeded` | More than 5 verify attempts on a single code.                                            |
| `AUTH-013` | 429  | `OTPRateLimited`      | More than 5 OTP requests in 15 minutes for the same identifier.                          |
| `AUTH-014` | 503  | `OTPDeliveryFailed`   | Every channel in the [smart-fallback chain](../../adr/005-otp-smart-fallback.md) failed. |

## USR-\* (user / role administration)

| Code      | HTTP | Exception              | When raised                                                                  |
| --------- | ---- | ---------------------- | ---------------------------------------------------------------------------- |
| `USR-001` | 409  | `DuplicateIdentifier`  | Creating / updating a user with an email/mobile/employee-code already taken. |
| `USR-010` | 400  | `CannotDeleteSelf`     | Authenticated user tried to soft-delete their own account.                   |
| `USR-020` | 400  | `SystemRoleProtected`  | Edit / delete attempt against a `Role` flagged `is_system=True`.             |
| `USR-030` | 400  | `BranchAccessRequired` | `set_default_branch` called for a user with zero `UserBranchAccess` rows.    |

## Conventions

- Codes use a 3-digit ascending number with logical buckets:
  - `AUTH-001 – 009` — credential outcomes (login).
  - `AUTH-010 – 019` — OTP issuance & verification.
  - `USR-001 – 009` — uniqueness / identity conflicts.
  - `USR-010 – 019` — destructive operations on users.
  - `USR-020 – 029` — role administration.
  - `USR-030 – 039` — branch access.
- Application code raises the typed exception; the global DRF
  handler translates it into the envelope.
- Tests assert on `error.code` (not on the message):

  ```python
  assert response.status_code == 400
  assert response.json()["error"]["code"] == "AUTH-001"
  ```

## Frontend handling

`admin-ui/src/lib/api/errors.ts::mapApiErrorToFields()` surfaces:

| Code       | Surface                                         |
| ---------- | ----------------------------------------------- |
| `AUTH-001` | Inline on the password field.                   |
| `AUTH-002` | Toast — sign-out + redirect to login.           |
| `AUTH-003` | Toast — show "Account locked, try again later". |
| `AUTH-010` | Inline on the OTP code field.                   |
| `AUTH-011` | Inline on OTP form + "Resend" CTA.              |
| `AUTH-013` | Toast — disable resend for 15 min.              |
| `USR-001`  | Inline on the offending identifier field.       |

Anything not mapped falls through to the generic toast.
