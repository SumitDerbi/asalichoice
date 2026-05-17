# Users — User guide

This page covers the day-to-day flows for end users of the admin UI.

## Logging in

The login screen at `/login` has one identifier field and one password
field. Type any of the following into the identifier field:

- your **email** (`alice@example.com`)
- your **mobile number** (`9876543210`)
- your **employee code** (`EMP-0042`)

…then enter your password and click **Sign in**. The same account is
reached regardless of which identifier you used.

If your account is deactivated, you'll see "Account is inactive."
(error `AUTH-002`). Contact your administrator.

If the identifier or password is wrong, you'll see "Invalid identifier
or password." (error `AUTH-001`).

## Logging in with an OTP

If you've forgotten your password (or your account is configured for
OTP-only login), use **Sign in with a one-time code**:

1. Enter your identifier.
2. Click **Send code**. The system picks the best channel for you —
   SMS first (if you have a mobile on file), then email, then
   WhatsApp. The screen tells you which channel was used.
3. Enter the 6-digit code within 10 minutes.
4. You can request a new code up to 5 times in 15 minutes. After that
   you'll see "Too many OTP requests" (error `AUTH-013`).

If you didn't receive a code, click **Try another channel** — the
system will pick the next channel in the fallback chain. See
[ADR-005](../../adr/005-otp-smart-fallback.md) for the exact order.

## Resetting your password

From the login screen, click **Forgot password?**:

1. Enter your identifier and click **Send code**.
2. Enter the OTP you received.
3. Choose a new password (minimum 8 characters, must not be
   all-numeric, must not be your old password).
4. You'll be returned to the login screen.

## Switching branches

If you have access to more than one branch, the top bar shows a
branch switcher. Choose the branch you want to work in — every
subsequent API call carries the branch context, and any data you
create / edit is scoped to that branch.

If you only have access to one branch the switcher is hidden.

## Your profile

The avatar menu (top-right) shows:

- Your name and primary identifier.
- The roles you currently hold.
- A **Sign out** button that invalidates your current refresh token
  (you'll be asked to log in again on next visit).

## Permissions cheat-sheet for admins

| Permission code              | What it grants                 |
| ---------------------------- | ------------------------------ |
| `users.read`                 | View user list and details.    |
| `users.write`                | Create / edit users.           |
| `users.deactivate`           | Soft-delete users.             |
| `users.assign-role`          | Bind users to roles.           |
| `users.assign-branch`        | Grant branch access.           |
| `roles.read` / `roles.write` | Manage non-system roles.       |
| `*`                          | Superuser — grants everything. |

Permissions are aggregated from every role the user holds. A
permission granted on _any_ role wins.
