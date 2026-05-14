# 002 — Frontend (Admin UI) Setup

> **Phase**: phase-0-foundation  **Depends on**: 001  **Module**: --  **Est. effort**: M

## Goal

Scaffold `admin-ui/` as a React + Vite + TypeScript app with Tailwind, shadcn/ui, TanStack Query, TanStack Form, Zod, and a typed API client pointing at the backend. Includes app shell with sidebar, top bar, command palette stub, and `/login` placeholder.

## Inputs

- [ ] 001 complete and `/api/v1/health/` reachable.
- [ ] Node 20+ and pnpm.

## Steps

1. `pnpm create vite admin-ui --template react-ts` (run from repo root; replace generated folder if needed).
2. Install runtime deps: `react-router-dom` (or `@tanstack/react-router` — decide here; recommend React Router for simpler learning curve initially), `@tanstack/react-query`, `@tanstack/react-query-devtools`, `@tanstack/react-form`, `zod`, `axios`, `lucide-react`, `zustand`, `clsx`, `tailwind-merge`, `framer-motion`, `cmdk` (command palette), `sonner` (toasts).
3. Install dev deps: `tailwindcss`, `postcss`, `autoprefixer`, `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `jsdom`, `playwright`, `eslint`, `prettier`, `eslint-config-prettier`, `eslint-plugin-react`, `eslint-plugin-react-hooks`, `@typescript-eslint/{eslint-plugin,parser}`, `stylelint`, `husky`, `lint-staged` (root-installed in 004; here keep `admin-ui` scoped).
4. Init Tailwind: `pnpm dlx tailwindcss init -p`. Configure `tailwind.config.ts` (content paths, theme tokens, dark mode `class`).
5. Init shadcn/ui: `pnpm dlx shadcn@latest init` → pick defaults; pick `slate` base. Add primitives: `button, input, label, dialog, drawer, dropdown-menu, sheet, table, toast, tooltip, command, popover, select, separator, skeleton, badge, tabs, scroll-area, form`.
6. Folder layout per `_conventions.md` §1 (`src/app`, `src/modules`, `src/components/{ui,shared}`, `src/lib`, `src/hooks`).
7. Build `src/lib/api/client.ts` — Axios instance reading `VITE_API_BASE_URL`. Request interceptor: attach JWT from auth store; refresh on 401. Response interceptor: unwrap error envelope to `{ code, message, details }`.
8. Build `src/lib/api/query-client.ts` — TanStack `QueryClient` with sensible defaults (`staleTime: 30s`, retry 1 except for 4xx).
9. Build app shell `src/app/layout.tsx`: sidebar (placeholder nav), top bar (user menu, command palette trigger), main outlet, toast region.
10. Add global `?` shortcut overlay (kbar-style) listing shortcuts (empty for now).
11. Add `Ctrl+K` command palette (cmdk) — empty registry, ready for modules to register.
12. Add `/login` page (UI only, no auth yet — wired in 006).
13. Add `.env.example` in `admin-ui/`: `VITE_API_BASE_URL=http://localhost:8000/api/v1`.
14. Add `vitest.config.ts` and a smoke test for `App.tsx`.
15. Add `eslint` + `prettier` configs; `package.json` scripts: `dev, build, preview, test, test:ui, e2e, e2e:install, lint, format`.
16. Commit: `feat(admin-ui): scaffold react + tailwind + shadcn shell`.

## Deliverables

- `admin-ui/` running on `pnpm dev` at `http://localhost:5173`.
- App shell visible, command palette opens with `Ctrl+K` (empty state OK).
- Typed API client + query client wired.
- Smoke vitest test green.

## Verification

### Manual
1. `pnpm --filter admin-ui dev` → page loads at `:5173`.
2. `Ctrl+K` opens palette; `?` shows shortcuts overlay.
3. Sidebar collapses; top bar renders.

### Automated
- `pnpm --filter admin-ui test` green.
- `pnpm --filter admin-ui lint` clean.

## Definition of Done

- [ ] Shell + palette + shortcut overlay working.
- [ ] API + query clients exported.
- [ ] Lint + test green.
- [ ] `_state.md` advanced.

## Next step

→ [`003-website-wagtail-setup.md`](./003-website-wagtail-setup.md)

## Previous step

← [`001-backend-django-setup.md`](./001-backend-django-setup.md)
