# 009 — Forms & Validation (Zod + TanStack Form)

> **Phase**: phase-0-foundation  **Depends on**: 007, 008  **Module**: --  **Est. effort**: S

## Goal

Lock in a single forms pattern: TanStack Form for state, Zod for schema, shared `<Form>` primitives over shadcn, with error mapping from API envelope to fields.

## Inputs

- [ ] 007 + 008 complete.

## Steps

1. `admin-ui/src/lib/forms/`:
   - `form.tsx` — thin wrapper around TanStack Form bound to Zod via `@tanstack/zod-form-adapter`.
   - `field.tsx` — `<Field>` connecting label + input + error message + description.
   - `api-error.ts` — `mapApiErrorToFields(error, schema)` mapping `error.details.fields` to field-level errors; falls back to form-level toast.
   - `submit-handler.ts` — boilerplate: optimistic update hook, success toast (sonner), error toast.
2. Schema co-location convention: `src/modules/<module>/schemas/<entity>.ts` exports `xxxCreateSchema`, `xxxUpdateSchema`, `xxxFiltersSchema`.
3. Inline-edit pattern: `<InlineEditCell>` for `DataTable` cells (PATCH on blur with optimistic update + rollback on 4xx).
4. Drawer form pattern: `<DrawerForm title actions>` standardises Create/Edit drawers.
5. Confirm pattern: `<ConfirmDialog>` already from 007 — wire to destructive form actions.
6. Refactor `/login` page (006) to use new `<Form>` + `<Field>` to prove pattern.
7. Tests: schema unit tests, error-mapper tests, inline-edit happy + rollback.
8. Document in `docs/ui/forms.md`.
9. Commit: `feat(admin-ui): unified form pattern (tanstack-form + zod)`.

## Deliverables

- `src/lib/forms/` package.
- Login page refactored.
- Form docs page.

## Verification

### Manual
1. Login form shows inline field errors when server returns `details.fields`.
2. Inline-edit on a sample table cell updates optimistically and rolls back on simulated 400.

### Automated
- `pnpm --filter admin-ui test -- lib/forms` green.

## Definition of Done

- [ ] Pattern locked in.
- [ ] Login uses it.
- [ ] Docs written.
- [ ] `_state.md` advanced.

## Next step

→ [`010-testing-setup.md`](./010-testing-setup.md)

## Previous step

← [`008-api-conventions.md`](./008-api-conventions.md)
