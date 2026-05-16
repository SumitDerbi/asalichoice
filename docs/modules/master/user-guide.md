# Master Management — User guide

This guide walks through the master-data screens in the admin UI
(`admin-ui/src/modules/masters/`). All screens follow the same pattern:
a paginated list with toolbar, a drawer/form for create + edit, and a
soft-delete confirmation dialog.

## Prerequisites

- A staff account with the `master.view_*` permissions for the screens
  you intend to open.
- A current branch selected via the **branch switcher** in the top bar.
  The branch is sent on every request as `X-Branch-Id`; some screens
  (e.g. payment modes) scope their list to that branch.

## Common toolbar actions

| Action          | Notes                                                                                                |
| --------------- | ---------------------------------------------------------------------------------------------------- |
| **New**         | Opens the form drawer. The form blocks submit while invalid.                                         |
| **Search**      | Free-text search on the indexed columns (name, code).                                                |
| **Filters**     | Per-screen — e.g. `Branch type` on the Branches screen.                                              |
| **Export CSV**  | Downloads the currently filtered page (not the full dataset).                                        |
| **Soft delete** | Available from the row menu. Hidden rows can be restored from the **Show archived** filter (admins). |

## Screen reference

### Geography → Branches

- **Code** must be unique across all branches. Duplicate submissions
  return `MST-001` and surface inline on the form.
- **Parent branch** is optional. The form rejects depth ≥ 3 with
  `MST-011`.
- Soft-deleting a branch hides it from the branch switcher; pending
  records that FK to it keep working until they are reassigned.

### Geography → Cities / States / Pincodes

- States are unique per `(country, code)`; cities are unique per
  `(state, name)`. The form surfaces these as inline errors.
- Pincodes can be associated with a zone — see the Zone form for
  bulk-assigning pincodes to a zone.

### Organisation → Departments, Designations, Warehouses

- Designations are scoped under a department. Selecting a different
  department clears the designation picker.
- Warehouses are scoped under a branch and inherit the branch's
  address by default; override per warehouse if required.

### Catalog → Categories

- Tree view with drag-and-drop reordering. Moves rejected with
  `MST-010` exceed maximum depth (4 levels).
- The form's **Parent** picker hides the current node and all of its
  descendants to prevent cycles.

### Catalog → Brands & HSN codes

- Brand logos are optional; max 2 MB, PNG/JPEG/WebP only.
- HSN codes can carry a **default tax** which prefills the product
  form in M03.

### Catalog → Units of measure

- Used by products and stock entries. Code is unique and uppercased on
  save.

### Finance → Tax

- Components editor: add one row per GST component
  (CGST / SGST / IGST / CESS). The form shows a live total; the server
  enforces the same sum with `MST-020` on mismatch.
- Toggling **Active** is non-destructive; only active taxes show up in
  the product form.

### Finance → Payment modes

- The toggle column **Enabled at this branch** writes to a per-branch
  join table; the column shows the state for the current
  `X-Branch-Id`.

## Tips and troubleshooting

- If a list endpoint returns 403 with `MST-002`, your account is not
  permitted on the active branch. Switch branches or ask an admin for
  access.
- The **Refresh** button clears the client cache and re-fetches; the
  server-side cache is invalidated automatically on every save (see
  the developer guide).
- Bulk-import via CSV is **not** part of M01 and is tracked under a
  future module.
