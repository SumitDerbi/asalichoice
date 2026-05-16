# Admin UI — Forms

Single forms pattern for the admin UI. **TanStack Form** owns state,
**Zod** owns schemas, and the shared primitives in
[`admin-ui/src/lib/forms`](../../admin-ui/src/lib/forms) wire them together
with shadcn inputs + error mapping from the API envelope.

## Quick start

```tsx
import { z } from "zod";
import { Field, Form, runSubmit, useAppForm } from "@/lib/forms";

const productSchema = z.object({
  name: z.string().min(1, "Name is required"),
  price: z.coerce.number().positive("Must be > 0"),
});

type ProductValues = z.infer<typeof productSchema>;

export function CreateProductForm({ onCreated }: { onCreated: () => void }) {
  const form = useAppForm<ProductValues>({
    schema: productSchema,
    defaultValues: { name: "", price: 0 },
    async onSubmit({ value }) {
      await runSubmit(value, {
        action: (v) => api.post("/v1/products/", v),
        successMessage: "Product created.",
        knownFields: ["name", "price"],
        onSuccess: onCreated,
      });
    },
  });

  return (
    <Form
      onSubmit={(e) => {
        e.preventDefault();
        void form.handleSubmit();
      }}
    >
      <form.Field name="name">
        {(field) => <Field field={field} label="Name" />}
      </form.Field>
      <form.Field name="price">
        {(field) => <Field field={field} label="Price" type="number" />}
      </form.Field>
      <button type="submit">Save</button>
    </Form>
  );
}
```

## Building blocks

### `useAppForm({ schema, defaultValues, onSubmit })`

Thin wrapper around TanStack Form's `useForm` that wires the Zod schema as
both the `onChange` and `onSubmit` validator. Returns the same `FormApi`
TanStack would normally give you — `form.Field`, `form.handleSubmit`,
`form.useStore`, etc. all work as documented upstream.

### `<Form>` + `<Field>`

- `<Form>` is a tagged `<form noValidate className="space-y-4">`. Wire your
  own `onSubmit` (typically calling `form.handleSubmit`).
- `<Field>` renders label + shadcn `<Input>` + description + inline error
  with the right `aria-invalid` / `aria-describedby` plumbing. Pass the
  TanStack field from `form.Field`'s render prop. Optionally pass
  `formErrorMap` (from `form.useStore(s => s.errorMap.onChange)`) so
  Zod's form-level errors get surfaced per field.
- `<FieldShell>` is the same layout without the input. Use when you need a
  `<Select>`, date picker, or custom widget — clone-children of one
  element into the labelled+described region.

### Zod helpers

- `zodFormValidator(schema)` — drop into `validators.onChange` for the
  whole form. Returns `{ fields: { [name]: 'message' } }`.
- `zodFieldValidator(schema)` — drop into a single `<form.Field>`'s
  `validators.onBlur`. Returns the first error string or `undefined`.

### `mapApiErrorToFields(error, { knownFields })`

Convert the API error envelope into `{ fields, formMessage }`.

The mapper recognises two shapes for `error.details`:

1. **Preferred** — `details.fields = { email: 'Already taken' }`. See
   [`docs/api/conventions.md`](../api/conventions.md).
2. **Compatibility** — flat DRF `ValidationError` shape
   `{ email: ['Already taken'] }`.

Pass `knownFields` to drop stray server keys. When unknown keys appear,
the form-level message is preserved as a toast so the error is never
silently swallowed.

### `runSubmit(values, options)`

The recommended action wrapper for `onSubmit`. Returns `true` on success.

```ts
const ok = await runSubmit(values, {
  action: (v) => api.post("/v1/things/", v),
  successMessage: "Saved.", // pass null to skip
  knownFields: ["name", "price"],
  onFieldErrors: (errors) => {
    // Surface per-field errors via form.setFieldMeta / form.setErrorMap.
    // Return true to suppress the form-level toast.
    return false;
  },
  onSuccess: () => navigate("/things"),
});
```

### Inline edit — `<InlineEditCell value onCommit>`

Drop into a `DataTable` cell. Renders as read-only text until clicked,
swaps to an `<Input>`, and PATCHes on blur with **optimistic** UI:

- Cell shows the new value immediately.
- On a rejected `onCommit` (e.g. `throw new ApiError(...)`) the cell rolls
  back to the previous value and `runSubmit` surfaces the envelope
  message as a toast.
- `Enter` commits, `Escape` cancels.

```tsx
<InlineEditCell
  value={row.sku}
  name="sku"
  onCommit={(next) => api.patch(`/v1/products/${row.id}/`, { sku: next })}
/>
```

Optimistic state wins until commit/rollback. If the parent refetches and
needs to force-reset the cell, remount with a `key` (e.g.
`key={row.version}`).

### Drawer forms — `<DrawerForm>`

Wrap a `<Form>` in the right-side `<Drawer>` from
`components/shared/drawer` with a uniform footer (Cancel + Save). The
body slot is yours.

```tsx
<DrawerForm
  open={open}
  onOpenChange={setOpen}
  title="New product"
  submitting={submitting}
  onSubmit={() => form.handleSubmit()}
>
  <Form
    onSubmit={(e) => {
      e.preventDefault();
      form.handleSubmit();
    }}
  >
    <form.Field name="name">
      {(f) => <Field field={f} label="Name" />}
    </form.Field>
    ...
  </Form>
</DrawerForm>
```

### Destructive confirmations

Wire `<ConfirmDialog>` (from
[`components/shared/confirm-dialog.tsx`](../../admin-ui/src/components/shared/confirm-dialog.tsx))
around delete buttons. Forms only fire the destructive action once the
dialog resolves.

## Schema co-location

Module-owned schemas live at:

```
admin-ui/src/modules/<module>/schemas/<entity>.ts
```

Exports per entity:

- `xxxCreateSchema` — for new-record POST forms.
- `xxxUpdateSchema` — for PATCH/PUT forms (typically `.partial()` of
  create).
- `xxxFiltersSchema` — for list-page filter bars.

The login form keeps its schemas at
[`modules/auth/schemas.ts`](../../admin-ui/src/modules/auth/schemas.ts) as
a working reference.

## Testing

See [`admin-ui/tests/forms/`](../../admin-ui/tests/forms) for canonical
patterns:

- `schema-and-mapper.test.ts` — schemas, validators, and the API
  error mapper (including DRF-shape fallback and unknown-field
  collapsing).
- `inline-edit.test.tsx` — happy-path commit, rollback on 4xx, and
  Escape-to-cancel.

The shared test setup (`tests/setup.ts`) already polyfills
`ResizeObserver` and `scrollIntoView`, so drawer + popover-based forms
work in jsdom out of the box.
