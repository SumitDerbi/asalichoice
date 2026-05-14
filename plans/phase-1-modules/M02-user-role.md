# M02 — User & Role Management

> **Phase**: phase-1-modules  **SRS ref**: Module 2  **Depends on**: M01  **Est. effort**: L

## Goal

Full user lifecycle: identifier strategy (email/mobile/employee-code), OTP login with smart-fallback (preferred channel + fail-over), password login, role + permission system, per-branch access, session/JWT management, user profile, password reset.

## Inputs

- [ ] M01 done — `Branch`, `Department`, `Designation` available.
- [ ] Phase-0 auth skeleton (006) exists.

## Steps

1. **Models** in `apps/users/` (extend from Phase 0):
   - Add `mobile`, `email` both unique-nullable; at least one required. `employee_code` unique-nullable for staff.
   - `primary_identifier` enum (EMAIL|MOBILE|EMP_CODE) — used for login by default.
   - `Role(code unique, name, is_system bool, description)`.
   - `Permission(code unique, name, module, description)` — seeded from each module's `permissions.py` via management command.
   - `RolePermission(role, permission)` M2M.
   - `UserRole(user, role, branch nullable)` — branch-scoped role; null = global.
   - `UserBranchAccess(user, branch, is_default)` — explicit branch access list.
   - `OTPLog(identifier, channel=SMS|EMAIL|WHATSAPP, code_hash, purpose=LOGIN|RESET|VERIFY, sent_at, expires_at, verified_at, attempts, ip, user_agent)`.
   - `LoginAttempt(identifier, ip, ok bool, reason, ts)` — for lockout + audit.
2. **Services**:
   - `auth_service.resolve_identifier(value) -> (user, identifier_type)` matches across email/mobile/employee_code.
   - `auth_service.request_otp(identifier, purpose, preferred_channel)` — picks channel, falls back per SystemSetting policy, logs.
   - `auth_service.verify_otp(identifier, code, purpose) -> User`.
   - `auth_service.password_login(identifier, password)` with argon2 + lockout after 10 fails (per `_meta.yaml` security).
   - `auth_service.issue_tokens(user, branch=None)` — embeds `branch_id` claim.
   - `auth_service.refresh(token)` with rotation + Redis revocation.
   - `auth_service.logout(token)` — blacklist.
   - `permission_service.user_has(user, perm_code, branch=None)`.
3. **Permission seeder** `seed_permissions.py` — scans all installed apps for `permissions.py`, upserts Permission rows.
4. **Role seeder** — assigns starter perms to roles defined in 014.
5. **Endpoints** `/api/v1/auth/`:
   - `POST /otp/request` (rate-limited 5/15min/identifier via Redis).
   - `POST /otp/verify` → tokens.
   - `POST /login` (password) → tokens; lockout enforced.
   - `POST /refresh`, `POST /logout`, `GET /me` (extend Phase-0 versions).
   - `POST /password/reset/request`, `POST /password/reset/confirm`.
   - `/api/v1/users/`, `/roles/`, `/permissions/`, `/branch-access/` — admin CRUD with proper perms.
6. **Error codes**: `AUTH-*` (auth failures), `USR-*` (user CRUD).
7. **Admin-UI**:
   - Update `/login` to support identifier (auto-detect type) + password **or** OTP toggle.
   - `/auth/otp` flow with channel chooser when fallback triggered.
   - `src/modules/users/` — list, drawer-edit (assign roles + branches), invite flow.
   - `src/modules/roles/` — role list + permission matrix editor (compact grid: rows = perms, columns = roles).
   - Permission-aware UI via `useHasPermission(code, branch?)` hook backed by `/me`'s permission payload.
8. **Notification integration** (stub now, M17 fills): `notify_service.send_otp(channel, identifier, code)`. Phase 1 dev mode logs to console + DB.
9. **Sessions panel** in user profile: list active refresh tokens with revoke buttons.
10. Tests, Postman, Playwright as per `_conventions.md` §9.
11. Docs: `docs/modules/users/{index,user-guide,developer-guide,error-codes}.md` + ADR `005-otp-smart-fallback.md`.
12. Commit: `feat(M02): users, roles, permissions, otp smart fallback`.

## Verification

### Manual
1. New user via admin → invite email/SMS sent (logged in dev) → user sets password → logs in.
2. OTP request to email when SMS provider stubbed-failing → email used; UI shows "Sent via Email".
3. 11th wrong password attempt → 15-min lockout response.
4. Revoke a session → that refresh token fails next refresh.
5. User without `master.manage_branch` perm cannot see Branch "Manage" actions in UI.

### Automated
- `pytest backend/tests/users/ -q` ≥ 85% on services.
- `pnpm --filter admin-ui test -- modules/users modules/roles` green.
- Playwright: OTP login, password login + lockout, role assignment, permission gating.
- Newman: `qa/postman/users/`.

## Definition of Done

- [ ] All identifier types log in.
- [ ] OTP fallback verified.
- [ ] Lockout + rate-limits verified.
- [ ] Permission matrix usable.
- [ ] Docs + ADR published.
- [ ] `_state.md` advanced.

## Next step

→ [`M03-catalog.md`](./M03-catalog.md)

## Previous step

← [`M01-master-management/05-docs.md`](./M01-master-management/05-docs.md)
