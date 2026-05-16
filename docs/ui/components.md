# Components

Primitives live in `admin-ui/src/components/ui/` (shadcn-generated, do not hand-edit) and app-level wrappers in `admin-ui/src/components/shared/`.

## Shared wrappers

| Component                    | Purpose                                          |
| ---------------------------- | ------------------------------------------------ |
| `PageHeader` / `PageActions` | Standard page title + actions bar.               |
| `DataTable`                  | TanStack Table v8 wrapper with empty-state slot. |
| `Drawer`                     | Right/left Radix Dialog sheet for forms.         |
| `ConfirmDialog`              | Modal confirmation with sane defaults.           |

## Forms package

See [Forms](forms.md). The reusable primitives live under `admin-ui/src/lib/forms/`:

- `useAppForm({ schema, defaultValues, onSubmit })`
- `<Field>` / `<FieldShell>` / `getFieldError()`
- `runSubmit(values, { action, onSuccess, onFieldErrors })`
- `<InlineEditCell>` and `<DrawerForm>`

## Adding a new shadcn primitive

```powershell
cd admin-ui
npx shadcn@latest add <component>
```

Re-export only what your modules actually use from `src/components/shared/` to keep the public surface small.
