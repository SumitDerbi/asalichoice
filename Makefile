# AsliChoice — Makefile (Linux / macOS / WSL).
# Windows users: prefer scripts/test-all.ps1.

.PHONY: help test test-backend test-frontend test-e2e test-postman lint format clean

help:
	@echo "Targets:"
	@echo "  make test           Run lint + backend + frontend + postman + e2e"
	@echo "  make test-backend   Ruff/Black/Isort + pytest+cov"
	@echo "  make test-frontend  ESLint + Vitest+cov"
	@echo "  make test-e2e       Playwright"
	@echo "  make test-postman   Newman over qa/postman/*"
	@echo "  make lint           Python ruff + ESLint"
	@echo "  make format         ruff format + prettier"

test:
	bash scripts/test-all.sh

test-backend:
	bash scripts/test-all.sh --backend-only

test-frontend:
	bash scripts/test-all.sh --frontend-only

test-e2e:
	npm run e2e --workspace admin-ui

test-postman:
	node scripts/postman-run.mjs

lint:
	ruff check .
	npm run lint --workspaces --if-present

format:
	ruff format .
	npm run format --workspaces --if-present

clean:
	rm -rf admin-ui/dist admin-ui/coverage backend/.coverage backend/htmlcov
