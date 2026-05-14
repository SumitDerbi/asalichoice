# 013 — Site Settings, Feature Toggles, API Keys

> **Phase**: phase-0-foundation  **Depends on**: 005, 006, 007  **Module**: pre-M18  **Est. effort**: M

## Goal

Implement the **earliest slice** of Module 18 (System Settings) so every later module can read settings, feature toggles, and integration API keys from DB rather than hardcoding. Admin UI page exposes these for Super Admin.

## Inputs

- [ ] 005, 006, 007 complete.

## Steps

1. `apps/system_settings/` (Django app):
   - `models.SiteSetting(key: unique, value_json, scope=GLOBAL|BRANCH, branch_id?, description, is_secret: bool, updated_by, updated_at)`.
   - `models.FeatureToggle(key, enabled, rollout_percentage, description)`.
   - `models.IntegrationKey(provider, key_name, value_encrypted, is_active, description)` — values encrypted at rest using `cryptography` Fernet; key from env.
   - `models.SocialLink(platform, url, is_active)`.
   - `models.ContactInfo(label, email, phone, address, is_primary)`.
2. Services:
   - `get_setting(key, scope, branch=None, default=None)` with in-process LRU cache (TTL 60s) + cache invalidation on save.
   - `is_feature_enabled(key, user=None)` with rollout-percentage hash.
   - `get_integration_key(provider, key_name)` returning decrypted value.
3. Admin-only endpoints (`/api/v1/system-settings/`, `/feature-toggles/`, `/integration-keys/`, `/social-links/`, `/contact-info/`) — `IsSuperAdmin` only.
4. Admin-UI module `src/modules/system-settings/`:
   - List + edit pages per resource.
   - Secrets masked; reveal-button audit-logged.
   - Feature toggles screen: enable/disable + rollout %.
   - Integration keys screen: per provider (Razorpay, MSG91, etc.).
   - Social/contact: single-form layout.
5. Seeders (`apps/system_settings/management/commands/seed_settings.py`): create defaults (OTP length=6, expiry=300s, default currency=INR, default timezone=Asia/Kolkata, default tax inclusive=false, etc.).
6. Hook into [`014-seeders-and-defaults.md`](./014-seeders-and-defaults.md) — settings seeders run there too.
7. Tests: CRUD, cache invalidation, encryption round-trip, permission enforcement.
8. Docs: `docs/modules/system-settings.md` (full doc lands when M18 fully built; this is the early slice).
9. Commit: `feat(M18-partial): site settings, feature toggles, integration keys`.

## Deliverables

- `apps/system_settings/` minimal viable.
- Encrypted secrets.
- Admin-UI screens.
- Seeders.

## Verification

### Manual
1. Create a setting via UI → reload another module's page → setting visible via API.
2. Reveal a secret → audit log entry created.
3. Toggle a feature off → relevant code path (use a dummy `health-extra` route gated by a flag) returns 404.

### Automated
- `pytest backend/tests/system_settings/ -q` green.
- Postman collection `qa/postman/system-settings/` green.

## Definition of Done

- [ ] All resources CRUD-able.
- [ ] Secrets encrypted at rest.
- [ ] Seeders idempotent.
- [ ] `_state.md` advanced.

## Next step

→ [`014-seeders-and-defaults.md`](./014-seeders-and-defaults.md)

## Previous step

← [`012-deploy-sh.md`](./012-deploy-sh.md)
