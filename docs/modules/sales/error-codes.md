# Sales — Error codes

All errors are emitted as the standard core envelope:

```json
{ "error": { "code": "SAL-XXX", "message": "...", "details": {} } }
```

| Code      | HTTP | Meaning                                                           |
| --------- | ---- | ----------------------------------------------------------------- |
| `SAL-001` | 409  | Sale is not in a state that permits the requested action          |
| `SAL-002` | 400  | Sale has no items — cannot post                                   |
| `SAL-010` | 400  | Sum of payments ≠ grand total (and partial not allowed)           |
| `SAL-020` | 400  | Discount does not apply to this sale (conditions not met)         |
| `SAL-021` | 403  | Discount requires approval — actor lacks `sales.discount.approve` |
| `SAL-030` | 403  | Price override forbidden — actor lacks `sales.price.override`     |
| `SAL-040` | 409  | Duplicate offline_uuid — a sale with this UUID already exists     |
| `SAL-050` | 400  | Payment mode is not enabled at this branch                        |

Cross-module errors that surface from the sales API:

| Code      | HTTP | Source                      | Meaning                    |
| --------- | ---- | --------------------------- | -------------------------- |
| `INV-010` | 400  | `apps.inventory.exceptions` | Insufficient stock on post |
| `MST-002` | 403  | `apps.master.middleware`    | Invalid / missing branch   |
