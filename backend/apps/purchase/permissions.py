"""M04 Purchase — permission codes (seeded via ``seed_permissions``)."""

from __future__ import annotations

PURCHASE_PERMISSIONS: tuple[tuple[str, str, str], ...] = (
    ("purchase.vendor.view", "View vendors", "Read the vendor master."),
    ("purchase.vendor.manage", "Manage vendors", "Create/update/deactivate vendors."),
    ("purchase.po.view", "View purchase orders", "Read POs."),
    ("purchase.po.create", "Create purchase orders", "Draft and submit POs."),
    ("purchase.po.approve", "Approve purchase orders", "Approve / cancel POs."),
    ("purchase.grn.view", "View GRNs", "Read GRNs."),
    ("purchase.grn.create", "Create GRNs", "Draft and submit GRNs (incl. offline sync)."),
    ("purchase.grn.approve", "Approve GRNs", "Approve / reject GRNs (writes stock)."),
    ("purchase.invoice.view", "View purchase invoices", "Read purchase invoices."),
    ("purchase.invoice.create", "Create purchase invoices", "Draft a PI from approved GRNs."),
    ("purchase.invoice.post", "Post purchase invoices", "Post / cancel a PI."),
    ("purchase.invoice.pay", "Record payments", "Record vendor payments against an invoice."),
    ("purchase.return.view", "View purchase returns", "Read purchase returns."),
    ("purchase.return.create", "Create purchase returns", "Draft and post purchase returns."),
)

__all__ = ["PURCHASE_PERMISSIONS"]
