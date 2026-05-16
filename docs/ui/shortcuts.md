# Keyboard Shortcuts

The admin shell is keyboard-first. The full table is also rendered inside the app via the `?` overlay.

## Global

| Keys               | Action                  |
| ------------------ | ----------------------- |
| `Ctrl+K` / `Cmd+K` | Open command palette    |
| `?`                | Open shortcuts overlay  |
| `[`                | Toggle sidebar          |
| `t`                | Toggle light/dark theme |
| `Esc`              | Close any open overlay  |

## Navigation prefixes

Type the prefix `g` followed by another key within 800 ms.

| Keys  | Action          |
| ----- | --------------- |
| `g d` | Go to Dashboard |
| `g m` | Go to Masters   |

## Adding shortcuts

Modules register shortcuts through the module registry (`src/app/module-registry.ts`). Each entry declares the keys, label, and handler; the global handler in `src/app/layout.tsx` dispatches to it.
