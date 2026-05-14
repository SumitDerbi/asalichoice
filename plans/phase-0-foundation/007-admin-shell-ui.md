# 007 — Admin Shell UI

> **Phase**: phase-0-foundation  **Depends on**: 006  **Module**: --  **Est. effort**: M

## Goal

Finalise the admin-UI shell with module-driven sidebar, global search (Ctrl+K), keyboard shortcuts overlay (?), breadcrumbs, branch switcher (placeholder until M01), theme toggle, and a per-module registry pattern that future modules plug into.

## Inputs

- [ ] 006 complete; user can log in.

## Steps

1. **Module registry** at `src/app/module-registry.ts`:
   ```ts
   export type ModuleDef = {
     id: string;           // e.g. 'master'
     label: string;
     icon: LucideIcon;
     routes: RouteObject[];
     commands?: CommandDef[]; // for cmdk
     shortcuts?: ShortcutDef[];
     order: number;
   };
   ```
   Each module exports a `register()` that returns `ModuleDef`. `App.tsx` aggregates all.
2. **Sidebar**: collapsible, sections grouped by module category (Operations / Catalog / People / Finance / System). Active route highlighted. Keyboard nav with `j/k`.
3. **Top bar**: breadcrumbs (route-driven), branch switcher (stub), theme toggle, command palette button, user menu, notifications bell (stub).
4. **Command palette (`Ctrl+K`)**:
   - Searches: routes, customers, products, orders (stubs now; modules populate later).
   - Action items: "Create product", "Open POS" (link-only stubs).
   - Use `cmdk`; each module registers commands via `module.commands`.
5. **Shortcuts overlay (`?`)**: lists currently-mounted module shortcuts.
6. **Branch context**: Zustand store `useBranchStore` with `branches`, `currentBranch`, `setBranch`. Persist in `localStorage`. Top-bar dropdown switches it. Real branches populated by M01.
7. **Empty states**, **error boundary** (`react-error-boundary`), **404 page**, **403 page**.
8. **Layout primitives**: `PageHeader`, `PageActions`, `DataTable` (shadcn + TanStack Table), `Drawer`, `ConfirmDialog`.
9. **Tests**: layout renders, sidebar collapses, palette opens with `Ctrl+K`, branch switcher persists.
10. Commit: `feat(admin-ui): module registry + shell primitives`.

## Deliverables

- `src/app/module-registry.ts` and an example dummy module registered.
- Sidebar, top bar, palette, shortcut overlay, branch store.
- Shared `DataTable`, `Drawer`, `ConfirmDialog`, `PageHeader` components.

## Verification

### Manual
1. Login → shell renders.
2. `Ctrl+K` opens palette; type filters items.
3. `?` shows shortcuts.
4. Sidebar collapses; theme toggle flips dark/light.
5. Branch switcher persists across refresh.

### Automated
- `pnpm --filter admin-ui test` green (shell tests added).
- `pnpm --filter admin-ui e2e -- shell.spec.ts` green.

## Definition of Done

- [ ] Registry pattern documented in `admin-ui/src/app/README.md`.
- [ ] All shell pieces working.
- [ ] Tests green.
- [ ] `_state.md` advanced.

## Next step

→ [`008-api-conventions.md`](./008-api-conventions.md)

## Previous step

← [`006-auth-skeleton.md`](./006-auth-skeleton.md)
