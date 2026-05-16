"""Per-resource permission strings for M01.

Real role↔permission mappings land in M02. Until then these strings are
declared centrally so future modules can reference them without
hardcoding.
"""

from __future__ import annotations

# Format: "master.<verb>_<entity>". Verbs follow Django defaults
# (view/add/change/delete) plus a "manage" alias for combined write access.
MASTER_PERMISSIONS: tuple[str, ...] = (
    "master.view_branch",
    "master.manage_branch",
    "master.view_department",
    "master.manage_department",
    "master.view_designation",
    "master.manage_designation",
    "master.view_unitofmeasure",
    "master.manage_unitofmeasure",
    "master.view_tax",
    "master.manage_tax",
    "master.view_hsncode",
    "master.manage_hsncode",
    "master.view_paymentmode",
    "master.manage_paymentmode",
    "master.view_category",
    "master.manage_category",
    "master.view_brand",
    "master.manage_brand",
    "master.view_warehouse",
    "master.manage_warehouse",
    "master.view_zone",
    "master.manage_zone",
    "master.view_geography",
    "master.manage_geography",
)

__all__ = ["MASTER_PERMISSIONS"]
