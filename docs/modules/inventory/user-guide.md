# Inventory — User guide

The Inventory module is reached from the left sidebar under
**Operations → Inventory**. The landing page exposes eight tabs in
the secondary nav; permissions decide which actions you see.

## Stock

Read-only list of branch × product balances. Filter by branch or
product. The **Available** column is computed as
`qty_on_hand − qty_reserved` and is the number sales screens should
trust when placing an order.

## Batches

Lot-level view for items that track expiry. Filter by branch and
status (`ACTIVE` / `EXPIRED` / `CONSUMED`). Run
`python manage.py expire_batches` on a nightly cron to flip stale
lots — the admin UI is read-only.

## Ledger

Cursor-paginated journal of every quantity change. Use the filter
row to scope by branch, product, reference type, or reason code.
Previous / Next buttons walk the cursor; switching filters resets to
the head of the stream.

## Reservations

Soft-holds against an order or POS ticket. The list shows the
reference, qty, and status. With the **inventory.manage** permission
you can:

- **Release** an `ACTIVE` reservation (returns qty to available).
- **Consume** an `ACTIVE` reservation (paired with a sale).

`RELEASED` / `CONSUMED` rows are final and read-only.

## Transfers

Branch-to-branch stock movement. Create a draft, add line items,
then:

1. **Dispatch** (requires **inventory.transfer**) — decrements
   source branch stock, moves the document to `IN_TRANSIT`.
2. **Receive** — increments destination branch stock. Partial
   receipts move the document to `PART_RECEIVED`; the remainder can
   be received later, or **Cancel**led (only from `DRAFT`).

## Adjustments

Manual corrections (over-count, breakage at receiving, system drift).
Create a draft listing each `qty_change` (negative = decrement) and
its reason code, then **Post** (requires **inventory.adjust**). Posted
documents are immutable — to reverse an error, raise another
adjustment.

## Wastage

Damaged / expired / unsellable goods. The flow mirrors adjustments:
draft → post (requires **inventory.wastage**). Wastage entries always
decrement stock and always require a reason code (e.g. `EXPIRED`,
`DAMAGED`).

## Counts

Physical / cycle counts. The lifecycle has four states:

1. **Draft** — list the items you plan to count.
2. **Mark counted** — snapshots the expected qty from `Stock` so the
   document captures what the system thought you had _at count time_.
3. **Post** (requires **inventory.count**) — compares counted vs
   expected and writes the diff to the ledger.
4. **Cancel** — only allowed before posting.

## Troubleshooting

- **"Insufficient stock"** when reserving / consuming / dispatching:
  someone else holds an active reservation, or the on-hand qty is
  lower than you think. Check the ledger filtered to that product +
  branch for the last few entries.
- **"Invalid transition"** on dispatch / receive / post: the action
  is not legal in the document's current status. Refresh the page —
  another user may have advanced it.
- **Cursor "Previous" returns no rows**: you are already at the head
  of the stream; clear filters or change ordering to scroll further.
