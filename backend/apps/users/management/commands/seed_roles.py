"""Seed phase-0 role placeholders as Django ``auth.Group`` rows.

The real role / permission stack lands in M02. For now we just
materialise the canonical role names so other code can FK or filter
against them without conditional logic.

Idempotent — re-running leaves existing rows untouched. ``--reset``
deletes the seeded groups first (only allowed when ``DEBUG=True`` to
prevent accidental production wipes).
"""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError

DEFAULT_ROLES: tuple[str, ...] = (
    "SUPER_ADMIN",
    "ADMIN",
    "MANAGER",
    "STAFF",
    "CASHIER",
    "CUSTOMER",
    "PARTNER",
    "VENDOR",
)


class Command(BaseCommand):
    help = "Seed phase-0 role placeholder groups (SUPER_ADMIN, ADMIN, ...)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete the seeded groups before recreating them (requires DEBUG=True).",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            if not settings.DEBUG:
                raise CommandError("--reset is only allowed when DEBUG=True.")
            Group.objects.filter(name__in=DEFAULT_ROLES).delete()

        created = 0
        for name in DEFAULT_ROLES:
            _, was_created = Group.objects.get_or_create(name=name)
            if was_created:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"seed_roles done — created={created}, existing={len(DEFAULT_ROLES) - created}",
            ),
        )
