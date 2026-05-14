# M01 / 05 — Docs

> **Parent**: [`index.md`](./index.md)

## Goal

Publish user + developer docs for M01 in MkDocs.

## Steps

1. `docs/modules/master/index.md` — overview, scope, ER diagram (mermaid).
2. `docs/modules/master/user-guide.md` — admin-facing walkthrough per screen with screenshots.
3. `docs/modules/master/developer-guide.md` — how to import `apps.master.api_public`, branch context middleware, caching keys.
4. `docs/modules/master/error-codes.md` — full `MST-*` table.
5. ADR `docs/adr/003-branch-context.md` — why thread-local + header pattern.
6. ADR `docs/adr/004-tax-components.md` — why JSON components vs separate rows.
7. Add nav entries via `.pages` (awesome-pages).
8. Run `mkdocs build --strict` → no warnings.
9. Commit: `docs(M01): master management documentation`.

## Verification

### Manual
1. Local MkDocs preview shows all pages.
2. Mermaid ER diagram renders.

### Automated
- `mkdocs build --strict` clean.

## Definition of Done (closes M01)

- [ ] All 5 sub-plans green.
- [ ] Coverage gate met.
- [ ] Docs published.
- [ ] Seeder registered in `seed_all`.
- [ ] Branch switcher in admin shell using real data.
- [ ] `_state.md` History row appended; current step advanced to M02.

## Next step

→ [`../M02-user-role.md`](../M02-user-role.md)

## Previous step

← [`04-tests.md`](./04-tests.md)
