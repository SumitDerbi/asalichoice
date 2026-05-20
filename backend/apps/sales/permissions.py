"""M11 Sales — permission codes (seeded via ``seed_permissions``)."""

from __future__ import annotations

SALES_PERMISSIONS: tuple[tuple[str, str, str], ...] = (
    ("sales.view", "View sales", "Read sales, sale items, payments."),
    (
        "sales.manage",
        "Manage sales",
        "Create/edit drafts and post sales.",
    ),
    (
        "sales.cancel",
        "Cancel sales",
        "Cancel a posted sale (triggers ledger reversal).",
    ),
    (
        "sales.price.override",
        "Override sale line price",
        "Set a line ``sale_price`` different from the master price.",
    ),
    (
        "sales.discount.apply",
        "Apply discounts",
        "Apply discount codes that don't require approval.",
    ),
    (
        "sales.discount.approve",
        "Approve discounts",
        "Apply discounts flagged ``requires_approval``.",
    ),
    (
        "sales.b2b.create",
        "Create B2B sale",
        "Create a sale with ``origin=B2B`` (off-counter wholesale).",
    ),
)

__all__ = ["SALES_PERMISSIONS"]
