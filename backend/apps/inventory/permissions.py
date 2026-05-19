"""M05 Inventory — permission codes (seeded via ``seed_permissions``)."""

from __future__ import annotations

INVENTORY_PERMISSIONS: tuple[tuple[str, str, str], ...] = (
    ("inventory.view", "View inventory", "Read stock, batches, and ledger."),
    (
        "inventory.manage",
        "Manage inventory",
        "Create and edit inventory documents (default write fallback).",
    ),
    (
        "inventory.adjust",
        "Adjust stock",
        "Create and approve stock adjustments.",
    ),
    (
        "inventory.transfer",
        "Branch transfers",
        "Dispatch / receive / cancel branch transfers.",
    ),
    (
        "inventory.count",
        "Physical count",
        "Start, scan, and finalize physical counts.",
    ),
    (
        "inventory.wastage",
        "Wastage",
        "Record wastage / damage / expiry write-offs.",
    ),
)

__all__ = ["INVENTORY_PERMISSIONS"]
