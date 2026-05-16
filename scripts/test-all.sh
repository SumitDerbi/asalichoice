#!/usr/bin/env bash
# AsliChoice — unified test runner (Linux / macOS / WSL).
#
# Order: ruff -> black -> isort -> pytest+cov -> eslint -> vitest+cov -> postman -> playwright.
# Playwright is last because it can be slow and may need a dev server.
#
# Flags:
#   --no-e2e        Skip Playwright.
#   --no-postman    Skip Newman.
#   --backend-only  Only Python lints + pytest.
#   --frontend-only Only ESLint + Vitest.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

RUN_E2E=1
RUN_POSTMAN=1
RUN_BACKEND=1
RUN_FRONTEND=1
for arg in "$@"; do
  case "$arg" in
    --no-e2e) RUN_E2E=0 ;;
    --no-postman) RUN_POSTMAN=0 ;;
    --backend-only) RUN_FRONTEND=0; RUN_E2E=0; RUN_POSTMAN=0 ;;
    --frontend-only) RUN_BACKEND=0; RUN_POSTMAN=0 ;;
  esac
done

section() { printf '\n\033[1;36m== %s ==\033[0m\n' "$1"; }

if [[ $RUN_BACKEND -eq 1 ]]; then
  section "ruff (lint)"
  ruff check .
  section "ruff (format check)"
  ruff format --check .
  section "isort"
  isort --check-only .
  section "pytest (backend) + coverage"
  ( cd backend && python -m pytest --cov=apps --cov-report=term-missing --cov-config=.coveragerc )
fi

if [[ $RUN_FRONTEND -eq 1 ]]; then
  section "eslint"
  npm run lint --workspaces --if-present
  section "vitest + coverage"
  npm run test:coverage --workspace admin-ui
fi

if [[ $RUN_POSTMAN -eq 1 ]]; then
  section "postman / newman"
  node scripts/postman-run.mjs || echo "[postman] skipped or failed (non-blocking if backend not running)"
fi

if [[ $RUN_E2E -eq 1 ]]; then
  section "playwright"
  npm run e2e --workspace admin-ui
fi

section "OK"
