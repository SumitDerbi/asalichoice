# admin-ui/src/app — Shell architecture

The admin-UI shell is **module-driven**. Each functional area (Dashboard, Masters, POS, Inventory, …) is a self-contained module that contributes routes, navigation entries, command-palette items, and keyboard shortcuts to a central registry.

## Files

| Path                    | Purpose                                                                                                                                                                                                                                            |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `App.tsx`               | Top-level `<Routes>`. Wraps everything in `AppErrorBoundary`. Calls `registerAllModules()` at module-load time, then renders `listRoutes()` underneath the authenticated `AppShell` outlet. `/login`, `/403` and `*` (404) live outside the shell. |
| `layout.tsx`            | `AppShell` — sidebar (categorized by `ModuleCategory`), top bar (breadcrumbs, command palette button, branch switcher, theme toggle, user menu, sign-out), keyboard hotkeys (Ctrl+K, ?, [, t, g d, g m).                                           |
| `module-registry.ts`    | Pure-TS registry. Modules call `registerModule(def)`; the shell calls `listModules()`, `listRoutes()`, `listCommands()`, `listShortcuts()`, `listModulesByCategory()`.                                                                             |
| `register-modules.ts`   | Idempotent boot helper that imports every module's `register()` factory and registers it. Tests can re-import after calling `__resetRegistryForTests()`.                                                                                           |
| `command-palette.tsx`   | `cmdk` palette. Reads commands from the registry plus a few hard-coded navigation entries.                                                                                                                                                         |
| `shortcuts-overlay.tsx` | `?` overlay listing global + module-contributed shortcuts.                                                                                                                                                                                         |
| `error-boundary.tsx`    | `react-error-boundary` wrapper used at the top of the route tree.                                                                                                                                                                                  |
| `status-pages.tsx`      | `NotFoundPage` (404) + `ForbiddenPage` (403).                                                                                                                                                                                                      |

## Module contract

```ts
import type { ModuleDef } from '@/app/module-registry';

export function someModule(): ModuleDef {
  return {
    id: 'my-module',           // unique
    label: 'My Module',
    icon: SomeLucideIcon,
    category: 'Operations',    // Operations | Catalog | People | Finance | System
    order: 50,                 // ascending; lower = first in sidebar group
    routes: [
      { path: 'my-module', element: <ListPage /> },
      { path: 'my-module/:id', element: <DetailPage /> },
    ],
    nav: [{ to: '/my-module', label: 'My Module' }],
    commands: [
      { id: 'my-module.open', label: 'Open My Module', group: 'Navigation', perform: () => {/* … */} },
    ],
    shortcuts: [{ keys: 'g x', label: 'Go to My Module' }],
  };
}
```

Then register it in `register-modules.ts`:

```ts
import { someModule } from '@/modules/my-module';
// …
registerModule(someModule());
```

## Branch context

`@/lib/branch/store.ts` exposes a `useBranchStore` (zustand + `persist` under `asalichoice.branch.v1`). `branches` is stubbed with `HQ`/`WH1` today; module M02 will replace it with the real API list. The top-bar `BranchSwitcher` reads/writes `currentBranchId`. Downstream modules should call `useBranchStore((s) => s.currentBranchId)` (and re-fetch on change) when their queries depend on the active branch.

## Theme

`@/lib/theme/store.ts` persists the selected theme to `asalichoice.theme.v1` and toggles the `dark` class on `<html>`. `bootstrapTheme()` is called once from `main.tsx` before React mounts so there's no FOUC.

## Layout primitives

Shared building blocks live under `@/components/shared/`:

- `PageHeader` (+ `PageActions`) — page title, description, right-side action slot.
- `DataTable` — minimal TanStack-Table-v8 wrapper; modules extend with pagination/sort/filter.
- `Drawer` — right-side sheet built on Radix Dialog. Use for create/edit forms.
- `ConfirmDialog` — destructive/confirmation modal.

## Keyboard shortcuts

| Key                    | Action                      |
| ---------------------- | --------------------------- |
| `Ctrl + K` / `Cmd + K` | Open command palette        |
| `?`                    | Show shortcuts overlay      |
| `[`                    | Toggle sidebar              |
| `t`                    | Toggle theme                |
| `g d`                  | Go to Dashboard             |
| `g m`                  | Go to Masters               |
| `Esc`                  | Close current dialog/drawer |

Global handlers ignore keys typed in `input`/`textarea`/`contentEditable`. `Ctrl + K` works everywhere.

## Testing

Module registration is idempotent, but `vitest` reuses the same module instance across tests, so if a test mounts `<App />` twice it should not re-register. If a test needs a clean registry, import `__resetRegistryForTests` from `module-registry.ts` and call `registerAllModules()` again.
