# Admin UI

The AsliChoice admin UI is a React + Vite + TypeScript single-page app. It is keyboard-first (every primary action has a shortcut), branch-aware (a branch switcher in the top bar persists across reloads), and follows a strict shell + module-registry pattern.

## At a glance

- **Layout**: collapsible sidebar by category, top bar with branch switcher + theme toggle + user menu.
- **Routing**: `react-router-dom`. Modules register routes via [`src/app/module-registry.ts`](https://github.com/SumitDerbi/asalichoice/blob/main/admin-ui/src/app/module-registry.ts).
- **State**: `zustand` for global stores (`auth`, `branch`, `theme`), `@tanstack/react-query` for server cache.
- **Forms**: TanStack Form + Zod — see [Forms](forms.md).
- **Shortcuts**: see [Shortcuts](shortcuts.md).
- **Primitives**: shadcn/ui in `src/components/ui/`, app-level wrappers in `src/components/shared/` — see [Components](components.md).
