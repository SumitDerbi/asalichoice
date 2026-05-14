# M18 — System Settings (full)

> **Phase**: phase-1-modules  **SRS ref**: Module 18  **Depends on**: Phase-0 013 (partial)  **Est. effort**: M

## Goal

Complete the System Settings module beyond Phase-0's slice: per-branch overrides, print template management UI (full editor), invoice prefix & FY reset config, feature toggles UI with audit, integration keys vault with rotation, role-permission matrix admin, public site config (logo, social links, contact, hero banners).

## Steps

1. **Extend models** from Phase-0 013:
   - `SiteSetting`: add `branch_id` nullable for per-branch override (lookup: branch-specific first, fallback to global).
   - `InvoicePrefixConfig(branch FK, fy_start, prefix, padding, current_number)` — referenced by M08.
   - `PrintTemplateRevision(template FK, html, css, by, at)` — version history with rollback.
   - `WebsiteConfig(key, value_json)` — logo URLs, hero slides, footer links, contact, social.
   - `BannerImage(slot, image, link, sort, valid_from, valid_to, is_active)`.
2. **Services**:
   - `setting_service.get(key, branch=None)` — resolution order: per-branch → global → default.
   - `template_service.save_revision/rollback`.
   - `key_rotation_service.rotate(provider, key_name)` — generates new key, marks old, supports dual-active window.
3. **Endpoints**: extend `/api/v1/system-settings/`, add `/invoice-prefix/`, `/print-templates/`, `/website-config/`, `/banners/`.
4. **Admin-UI**:
   - Settings home: searchable list grouped by category, branch selector.
   - Print template editor with split-pane (HTML/CSS left, live preview right).
   - Invoice prefix config table.
   - Website config (logo, hero slides drag-sort, social links, contact info, footer links).
   - Permission matrix (M02 covers core; here adds drag UX + bulk-toggle).
   - Audit log of every setting change visible from each setting row.
5. **Error prefix**: `CFG-*`.
6. **Permissions**: `settings.view/manage`, `settings.print_template.manage`, `settings.invoice_prefix.manage`, `settings.website.manage`, `settings.integration_key.rotate`.
7. **Tests**: per-branch override resolution, template revision rollback, key rotation dual-active behaviour.
8. **Docs**: `docs/modules/system-settings/*`.
9. Commit: `feat(M18): system settings complete`.

## Verification

### Manual
1. Set tax-inclusive ON globally; override OFF for Branch B → POS at B uses exclusive.
2. Save print template revision → rollback to previous → POS print uses old template.
3. Rotate Razorpay key → both old and new accepted during overlap window.

### Automated
- `pytest backend/tests/system_settings/ -q` ≥ 85%.
- UI + Playwright + Newman green.

## Definition of Done

- [ ] All non-code config lives in DB.
- [ ] Per-branch overrides work.
- [ ] Audit on every change.
- [ ] `_state.md` advanced.

## Next step

→ [`M19-audit-log.md`](./M19-audit-log.md)

## Previous step

← [`M17-notifications.md`](./M17-notifications.md)
