# Vendor & Purchase — Error codes

Every error is rendered through the standard envelope (see
[API conventions](../../api/conventions.md)):

```json
{
  "error": {
    "code": "VEN-NNN | PUR-NNN",
    "message": "Human-readable summary.",
    "details": { "...": "..." }
  }
}
```

All `VEN-*` and `PUR-*` codes are declared as `DomainError` subclasses
in `apps/purchase/exceptions.py`.

## Catalogue

### Vendor (`VEN-*`)

| Code      | HTTP | Exception             | Raised when …                                   |
| --------- | ---- | --------------------- | ----------------------------------------------- |
| `VEN-001` | 409  | `VendorCodeDuplicate` | `Vendor.code` collides with an existing vendor. |
| `VEN-002` | 400  | `VendorGSTINInvalid`  | GSTIN does not match the 15-character format.   |
| `VEN-010` | 400  | `VendorInactive`      | Attempt to transact with an inactive vendor.    |

### Purchase Order (`PUR-0**`)

| Code      | HTTP | Exception             | Raised when …                              |
| --------- | ---- | --------------------- | ------------------------------------------ |
| `PUR-001` | 409  | `PODuplicate`         | `po_no` collides.                          |
| `PUR-009` | 400  | `POInvalidTransition` | Action not legal in current PO status.     |
| `PUR-010` | 400  | `POAlreadyApproved`   | Approve called twice.                      |
| `PUR-011` | 400  | `POClosedForChanges`  | Edit attempted on a CLOSED / CANCELLED PO. |

### GRN (`PUR-02*`)

| Code      | HTTP | Exception              | Raised when …                                    |
| --------- | ---- | ---------------------- | ------------------------------------------------ |
| `PUR-020` | 409  | `GRNDuplicate`         | `grn_no` collides.                               |
| `PUR-021` | 400  | `GRNNegativeQty`       | Any received / accepted / rejected qty is `< 0`. |
| `PUR-022` | 400  | `GRNOverReceive`       | Received qty exceeds open PO qty.                |
| `PUR-023` | 400  | `GRNInvalidTransition` | Action not legal in current GRN status.          |

### Purchase Invoice (`PUR-03*`)

| Code      | HTTP | Exception          | Raised when …                               |
| --------- | ---- | ------------------ | ------------------------------------------- |
| `PUR-030` | 409  | `PIDuplicate`      | `pi_no` collides.                           |
| `PUR-031` | 400  | `PINoApprovedGRNs` | `from-grns` called with zero approved GRNs. |

### Offline sync (`PUR-04*`)

| Code      | HTTP | Exception             | Raised when …                                         |
| --------- | ---- | --------------------- | ----------------------------------------------------- |
| `PUR-040` | 409  | `OfflineGRNPOClosed`  | Offline payload's PO is no longer open.               |
| `PUR-041` | 409  | `OfflineUUIDConflict` | `offline_uuid` already exists with different payload. |

### Returns (`PUR-05*`)

| Code      | HTTP | Exception                 | Raised when …                                  |
| --------- | ---- | ------------------------- | ---------------------------------------------- |
| `PUR-050` | 400  | `ReturnQtyExceedsReceipt` | Return qty for a line exceeds the GRN receipt. |

## Frontend handling

The admin-UI maps `details.fields` to per-field errors via
`mapApiErrorToFields`. Form-level fallbacks toast through `sonner`.
Action buttons (`Submit`, `Approve`, `Post`, `Pay`, `Reject`) catch
`ApiError` and surface the server-provided `message`.

## Cross-module references

- `MST-002 branch_access_denied` may pre-empt any `/purchase/*`
  endpoint that requires an `X-Branch-Id` the caller cannot access.
- M05 inventory will introduce `INV-*` codes for the stock-write seam
  invoked from `grn_service.approve_grn`.
