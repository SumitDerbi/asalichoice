# Master Management — Error codes

All errors raised by `apps.master` use the standard error envelope:

```json
{
  "error": {
    "code": "MST-NNN",
    "message": "human-readable message",
    "details": null
  }
}
```

The `MST-*` namespace is reserved for this module. Codes are stable
and **never reused** — even after an exception class is removed, its
code stays retired.

## Reference

| Code      | HTTP | Exception               | When raised                                                                                                  |
| --------- | ---- | ----------------------- | ------------------------------------------------------------------------------------------------------------ |
| `MST-001` | 409  | `BranchCodeDuplicate`   | Creating / updating a `Branch` with a code that already exists (across all branches).                        |
| `MST-002` | 403  | `BranchAccessDenied`    | Authenticated user attempted to operate on a branch they cannot access via `X-Branch-Id`.                    |
| `MST-010` | 400  | `CategoryDepthExceeded` | Creating / moving a `Category` would put it past the maximum depth (4 levels).                               |
| `MST-011` | 400  | `BranchDepthExceeded`   | Creating / moving a `Branch` would put it past the maximum depth (3 levels).                                 |
| `MST-020` | 400  | `TaxComponentsMismatch` | `Tax.components_json` rate sum does not equal `rate_total` (see [ADR-004](../../adr/004-tax-components.md)). |
| `MST-030` | 404  | `PincodeNotInZone`      | `resolve_zone_for_pincode(pincode)` could not find a covering `Zone`.                                        |

## Conventions

- Codes use a 3-digit ascending number with logical buckets:
  - `001 – 009` — uniqueness / existence per branch.
  - `010 – 019` — hierarchy / depth.
  - `020 – 029` — domain validation (tax, payment).
  - `030 – 039` — lookup misses.
- Application code raises the typed exception; viewsets let the global
  DRF handler translate it into the envelope.
- Tests assert on `error.code` (not on the message), e.g.

  ```python
  assert response.status_code == 400
  assert response.json()["error"]["code"] == "MST-020"
  ```

## Frontend handling

`admin-ui/src/lib/api/errors.ts` includes `mapApiErrorToFields(error)`
which knows how to surface the inline-field variants:

| Code      | Surface                             |
| --------- | ----------------------------------- |
| `MST-001` | Inline on `code` field of the form. |
| `MST-002` | Toast + branch-switcher highlight.  |
| `MST-010` | Inline on `parent` picker.          |
| `MST-011` | Inline on `parent_branch` picker.   |
| `MST-020` | Inline on tax components editor.    |
| `MST-030` | Toast on the pincode lookup screen. |

If a code is not in the map, the generic toast falls through and the
error envelope is logged verbatim to the console.
