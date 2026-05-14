# 006 — Auth Skeleton

> **Phase**: phase-0-foundation  **Depends on**: 005  **Module**: pre-M02  **Est. effort**: M

## Goal

Stand up a **minimal** auth surface (custom user model, JWT login, refresh, logout, current-user endpoint, admin-UI login flow) that the rest of Phase 0 can use. Full Module 2 (roles, OTP, permissions, smart fallback) lands in M02.

## Inputs

- [ ] 005 complete.

## Steps

1. Create `apps/users/` Django app.
2. Custom user model `User(AbstractBaseUser, PermissionsMixin)`:
   - `mobile` (unique, optional in this phase), `email` (unique, optional), `name`, `is_active`, `is_staff`, `is_superuser`, soft-delete, audit fields.
   - Manager with `create_user`, `create_superuser`.
   - `USERNAME_FIELD = 'email'` (provisional; M02 may add identifier strategy).
3. Set `AUTH_USER_MODEL = 'users.User'`. Run initial migration **before any other module migration touches users**.
4. Endpoints under `/api/v1/auth/`:
   - `POST /login/` → email + password → access + refresh.
   - `POST /refresh/` → refresh → new access.
   - `POST /logout/` → blacklist refresh.
   - `GET /me/` → current user payload.
5. Use `djangorestframework-simplejwt` with token blacklist app. Configure short access (15m) + long refresh (7d).
6. Add throttle classes `LoginRateThrottle` (5/min/IP), apply on `/login/`.
7. Add management command `seed_superuser` reading from env (`SEED_SUPERUSER_EMAIL`, `SEED_SUPERUSER_PASSWORD`). **Idempotent.**
8. Admin-UI:
   - `src/lib/auth/store.ts` — Zustand store: `accessToken`, `refreshToken`, `user`, `login()`, `logout()`, `bootstrap()`.
   - Persist refresh token in `localStorage`; access in memory only.
   - `src/lib/api/client.ts` — refresh-on-401 interceptor wired.
   - `/login` page form (TanStack Form + Zod) calls `POST /auth/login/`, stores tokens, navigates to `/`.
   - Route guard `RequireAuth` redirects unauthenticated users to `/login`.
   - `/me` shown in top-bar user menu.
9. Tests:
   - Pytest: login happy path, login wrong password, refresh, throttled, `/me` requires auth.
   - Vitest: `auth-store.test.ts`, `login-page.test.tsx`.
   - Playwright: `login.spec.ts` — successful login flow.
10. Postman collection `qa/postman/auth/`: login, refresh, me, logout, with env variables.
11. Commit: `feat(auth): jwt skeleton + admin-ui login`.

## Deliverables

- `apps/users/` with custom user model.
- 4 auth endpoints + throttling.
- Admin-UI login flow.
- Seed-superuser command.
- Tests + Postman collection.

## Verification

### Manual
1. `python manage.py seed_superuser` creates user.
2. Admin-UI `/login` accepts those creds → lands on `/`.
3. Refresh page → still authenticated.
4. Wrong password → friendly error envelope surfaced.

### Automated
- `pytest backend/tests/users/ -q` green.
- `pnpm --filter admin-ui test` green.
- `pnpm --filter admin-ui e2e -- login.spec.ts` green.
- `newman run qa/postman/auth/collection.json -e qa/postman/local.env.json` green.

## Definition of Done

- [ ] All endpoints + UI working.
- [ ] All test suites green.
- [ ] Refresh-on-401 verified manually.
- [ ] `_state.md` advanced.

## Next step

→ [`007-admin-shell-ui.md`](./007-admin-shell-ui.md)

## Previous step

← [`005-database-schema-baseline.md`](./005-database-schema-baseline.md)
