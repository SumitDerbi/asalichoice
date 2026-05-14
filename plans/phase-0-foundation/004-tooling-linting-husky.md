# 004 — Tooling, Linting, Husky

> **Phase**: phase-0-foundation  **Depends on**: 000, 001, 002  **Module**: --  **Est. effort**: S

## Goal

Lock in formatters, linters, pre-commit hooks, conventional commit enforcement, and `lint-staged` so quality is automatic from day 1.

## Inputs

- [ ] 000, 001, 002 complete.

## Steps

1. **Python** (`pyproject.toml` at root):
   - `[tool.ruff]` with rules: E, F, I, B, UP, S (security), N, RUF; line-length 100.
   - `[tool.black]` line-length 100.
   - `[tool.isort]` profile = black.
   - `[tool.pytest.ini_options]` `DJANGO_SETTINGS_MODULE=config.settings.development`.
2. **Pre-commit** (`.pre-commit-config.yaml`):
   - `ruff` (lint + format), `black`, `isort`, `trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `check-json`, `mixed-line-ending`, `detect-private-key`.
3. **Husky + lint-staged** (root `package.json`):
   - `pnpm dlx husky init`.
   - `.husky/pre-commit` → `pnpm exec lint-staged && pre-commit run --hook-stage commit`.
   - `lint-staged`:
     - `*.{ts,tsx,js,jsx}`: `eslint --fix`, `prettier --write`.
     - `*.{css,scss}`: `stylelint --fix`, `prettier --write`.
     - `*.{json,md,yml,yaml}`: `prettier --write`.
4. **commitlint** (`@commitlint/cli` + `@commitlint/config-conventional`):
   - `.commitlintrc.cjs` extends conventional.
   - `.husky/commit-msg` → `pnpm exec commitlint --edit "$1"`.
5. **EditorConfig** already added in 000 — verify.
6. **Stylelint** config: `.stylelintrc.json` with `stylelint-config-standard` + Tailwind-friendly rules.
7. **ESLint root config** with TS + React rules; per-workspace `.eslintrc.cjs` extending root.
8. Add `scripts` to root `package.json`: `lint`, `lint:fix`, `format`, `format:check`, `test`, `e2e`.
9. Add `Makefile` (optional, dev convenience): `make backend-test`, `make ui-test`, `make lint`.
10. Document in [`_conventions.md` §3](../_conventions.md#3-code-quality) — verify nothing drifts.
11. Commit: `chore: enable pre-commit, husky, lint-staged, commitlint`.

## Deliverables

- Root tooling configs.
- `.husky/` hooks active.
- `pre-commit` installed in venv (`pre-commit install`).
- All hooks pass on a clean repo.

## Verification

### Manual
1. Make a trivial change → `git commit` runs lint-staged + pre-commit + commitlint.
2. Try a commit with a non-conventional message → blocked.

### Automated
- `pre-commit run --all-files` green.
- `pnpm lint && pnpm format:check` green.

## Definition of Done

- [ ] Hooks enforced.
- [ ] Conventional commits required.
- [ ] All hooks green on full repo.
- [ ] `_state.md` advanced.

## Next step

→ [`005-database-schema-baseline.md`](./005-database-schema-baseline.md)

## Previous step

← [`003-website-wagtail-setup.md`](./003-website-wagtail-setup.md)
