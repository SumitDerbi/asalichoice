# Seeding & Default Data

Phase-0 ships a small set of **idempotent** management commands that populate
the database with the defaults the app needs to start. Each module gets its
own seeder; an orchestrator (`seed_all`) runs them in dependency order.

## Quick start

```bash
make seed              # bash/wsl/linux/mac
scripts\seed.ps1       # Windows PowerShell
python manage.py seed_all   # direct invocation
```

Re-running is safe — every seeder is idempotent.

## What ships in phase 0

| Command                 | Owner app              | What it seeds                                                                                                                                                                                                                         |
| ----------------------- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `seed_roles`            | `apps.users`           | 8 placeholder `auth.Group` rows: `SUPER_ADMIN`, `ADMIN`, `MANAGER`, `STAFF`, `CASHIER`, `CUSTOMER`, `PARTNER`, `VENDOR`. Full permission matrix lands in M02.                                                                         |
| `seed_settings`         | `apps.system_settings` | Default `SiteSetting`s (OTP length/expiry, currency, timezone, tax, guest checkout), `FeatureToggle`s (COD on, Razorpay/SMS off, blog on), 3 social links, primary contact row. See [System Settings](../modules/system-settings.md). |
| `seed_default_currency` | `apps.core`            | Ensures `site.default_currency = "INR"`.                                                                                                                                                                                              |
| `seed_default_timezone` | `apps.core`            | Ensures `site.default_timezone = "Asia/Kolkata"`.                                                                                                                                                                                     |
| `seed_default_branch`   | `apps.core`            | Placeholder branch (`HQ` / `Head Office`) stored as `SiteSetting`s — the real `Branch` model arrives in M01.                                                                                                                          |
| `seed_superuser`        | `apps.users`           | Bootstrap superuser from `SEED_SUPERUSER_EMAIL` + `SEED_SUPERUSER_PASSWORD`. Skipped by `seed_all` if either env var is unset.                                                                                                        |

## Idempotency guarantee

Every seeder reaches for `get_or_create(...)` (or `update_or_create` when
overwriting is intentional). Re-running produces zero new rows after the
first successful invocation. Tests in
`backend/tests/core/test_seeders.py` enforce this by running each seeder
twice and asserting the row count is unchanged.

## `--reset` semantics

Seeders that own destructive state expose `--reset`:

- Deletes rows the seeder is responsible for, then re-creates them.
- Guarded by `DEBUG=True` — fails loudly in production-like envs.
- Currently implemented by `seed_roles` and `seed_default_branch`.

`seed_settings` exposes `--overwrite` (force-update existing rows to the
seeded defaults) instead, since operators routinely tweak its values via
the admin UI.

## Adding a new module seeder

1. Place the command at
   `apps/<module>/management/commands/seed_<module>.py`.
2. Subclass `BaseCommand`, expose a `handle()` that uses `get_or_create`
   / `update_or_create` for every row.
3. Add `--reset` (DEBUG-gated) if the seeder owns destructive state.
4. Log `created=N, existing=M` (or similar) on completion.
5. Register the command in `SEEDERS` inside
   `apps/core/management/commands/seed_all.py` in the right slot
   (respect module dependency order from `plans/_meta.yaml`).
6. Add an idempotency test under `backend/tests/<module>/`.

## Order matters

`seed_all` runs in this exact order:

```
seed_roles
seed_settings
seed_default_currency
seed_default_timezone
seed_default_branch
seed_superuser   (only if env vars set)
```

Currency / timezone / branch all touch `SiteSetting`, so they sit after
`seed_settings` — but they're written to be safe regardless of order
(idempotent `get_or_create`).
