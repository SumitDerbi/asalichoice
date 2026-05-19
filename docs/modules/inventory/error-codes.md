# Inventory — Error codes

Every error is rendered through the standard envelope (see
[API conventions](../../api/conventions.md)):

```json
{
  "error": {
    "code": "INV-NNN",
    "message": "Human-readable summary.",
    "details": { "...": "..." }
  }
}
```

All `INV-*` codes are declared as `DomainError` subclasses in
`apps/inventory/exceptions.py`.

## Catalogue

| Code      | HTTP | Exception              | Raised when …                                                                                               |
| --------- | ---- | ---------------------- | ----------------------------------------------------------------------------------------------------------- |
| `INV-010` | 409  | `InsufficientStock`    | `availability_service.reserve` / `consume` or a transfer dispatch finds `qty_on_hand − qty_reserved < qty`. |
| `INV-020` | 409  | `InvalidTransferState` | Transfer action not legal in current status (e.g. dispatch on `IN_TRANSIT`).                                |
| `INV-030` | 409  | `InvalidDocumentState` | Adjustment / wastage / count posted from a non-DRAFT state (or count posted from non-COUNTED).              |
| `INV-031` | 400  | `UnknownReasonCode`    | Wastage or adjustment line references a reason code not present in `ReasonCode`.                            |

## Frontend handling

The admin-UI maps `details.fields` to per-field errors via
`mapApiErrorToFields`. Form-level fallbacks toast through `sonner`.
Action buttons (`Release`, `Consume`, `Dispatch`, `Receive`, `Cancel`,
`Post`, `Mark counted`) catch `ApiError` and surface the
server-provided `message`.

## Cross-module references

- `MST-002 branch_access_denied` may pre-empt any `/inventory/*`
  endpoint that requires an `X-Branch-Id` the caller cannot access.
- `PUR-*` codes from the purchase module precede `INV-*` writes
  because GRN approval is the inbound seam — see
  [ADR-008](../../adr/008-ledger-driven-stock.md).
- M06 / M07 will surface `INV-010` to end-users when stock runs out
  at checkout.
