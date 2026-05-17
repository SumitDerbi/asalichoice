"""Seed M02 :class:`apps.users.models.Role` rows and their permission
assignments.

Also keeps the phase-0 :class:`django.contrib.auth.models.Group`
placeholders so admin-side filtering / legacy code does not break.

Roles defined here are marked ``is_system=True`` — the API refuses to
delete them. Permissions referenced must exist (run :command:`seed_permissions`
first); the command in :command:`seed_all` already chains them.
"""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.users.models import Permission, Role, RolePermission

# Phase-0 group names (kept for back-compat with any code that still
# filters by Group rather than Role).
LEGACY_GROUPS: tuple[str, ...] = (
    "SUPER_ADMIN",
    "ADMIN",
    "MANAGER",
    "STAFF",
    "CASHIER",
    "CUSTOMER",
    "PARTNER",
    "VENDOR",
)

# Each entry: (code, name, description, permission-selector)
# permission-selector is either "*" (all) or a tuple of permission code
# prefixes — any Permission whose code starts with one of the prefixes
# is granted.
ROLE_SPECS = (
    ("SUPER_ADMIN", "Super administrator", "Full platform access.", "*"),
    (
        "ADMIN",
        "Administrator",
        "Manage users, roles, and master data.",
        ("users.", "master."),
    ),
    (
        "MANAGER",
        "Branch manager",
        "Manage master data within a branch.",
        ("master.",),
    ),
    (
        "STAFF",
        "Staff",
        "Read-only access to master data.",
        ("master.view_",),
    ),
    (
        "CASHIER",
        "Cashier",
        "POS-facing role; refined in M07.",
        ("master.view_",),
    ),
)


class Command(BaseCommand):
    help = "Seed M02 Role rows (and legacy auth.Group placeholders)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Drop existing seeded Role rows before recreating (requires DEBUG=True).",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            if not settings.DEBUG:
                raise CommandError("--reset is only allowed when DEBUG=True.")
            Role.objects.filter(code__in=[spec[0] for spec in ROLE_SPECS]).delete()

        # Legacy groups (idempotent).
        for name in LEGACY_GROUPS:
            Group.objects.get_or_create(name=name)

        all_perms = list(Permission.objects.all())

        created_roles = 0
        updated_roles = 0
        for code, name, description, selector in ROLE_SPECS:
            role, was_created = Role.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "description": description,
                    "is_system": True,
                },
            )
            created_roles += int(was_created)
            updated_roles += int(not was_created)

            if selector == "*":
                wanted = all_perms
            else:
                wanted = [p for p in all_perms if any(p.code.startswith(pref) for pref in selector)]

            current_ids = set(
                RolePermission.objects.filter(role=role).values_list("permission_id", flat=True),
            )
            wanted_ids = {p.pk for p in wanted}
            for perm in wanted:
                if perm.pk not in current_ids:
                    RolePermission.objects.create(role=role, permission=perm)
            stale = current_ids - wanted_ids
            if stale:
                RolePermission.objects.filter(role=role, permission_id__in=stale).delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"seed_roles done — created={created_roles}, updated={updated_roles}",
            ),
        )
