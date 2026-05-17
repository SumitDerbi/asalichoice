"""Central permissions registry for the users module.

Each app exports a ``<APP>_PERMISSIONS`` tuple from its ``permissions``
module (see ``apps.master.permissions.MASTER_PERMISSIONS``). The
:command:`seed_permissions` command walks these and upserts
:class:`apps.users.models.Permission` rows.
"""

from __future__ import annotations

# User / role / permission management itself.
USERS_PERMISSIONS: tuple[tuple[str, str], ...] = (
    ("users.view_user", "View users"),
    ("users.manage_user", "Create / update / disable users"),
    ("users.view_role", "View roles"),
    ("users.manage_role", "Create / update / delete roles"),
    ("users.assign_role", "Assign roles to users"),
    ("users.view_permission", "View the permission catalog"),
    ("users.view_branch_access", "View per-user branch access"),
    ("users.manage_branch_access", "Grant / revoke branch access for users"),
    ("users.view_audit", "View login + audit logs"),
)

__all__ = ["USERS_PERMISSIONS"]
