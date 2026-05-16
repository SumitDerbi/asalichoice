"""Seed the default branch placeholder.

The real ``Branch`` model lands in M01. Until then we stash the
default branch's code + display name as :class:`SiteSetting` rows so
the admin-ui and storefront have something to reference.

Idempotent — re-running leaves existing rows untouched. ``--reset``
deletes the two seeded keys first (DEBUG=True only).
"""

from __future__ import annotations

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.system_settings.models import SettingScope, SiteSetting

DEFAULT_BRANCH: dict[str, object] = {
    "code": "HQ",
    "name": "Head Office",
}

_KEYS = ("branch.default_code", "branch.default_name")


class Command(BaseCommand):
    help = "Seed the default branch placeholder (HQ / Head Office) as SiteSetting rows."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete the seeded keys before recreating them (requires DEBUG=True).",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            if not settings.DEBUG:
                raise CommandError("--reset is only allowed when DEBUG=True.")
            SiteSetting.objects.filter(
                key__in=_KEYS,
                scope=SettingScope.GLOBAL,
                branch_id=None,
            ).delete()

        specs = [
            {
                "key": "branch.default_code",
                "value_json": DEFAULT_BRANCH["code"],
                "description": "Default branch code (placeholder until M01 ships Branch model).",
            },
            {
                "key": "branch.default_name",
                "value_json": DEFAULT_BRANCH["name"],
                "description": "Default branch display name.",
            },
        ]
        created = 0
        for spec in specs:
            _, was_created = SiteSetting.objects.get_or_create(
                key=spec["key"],
                scope=SettingScope.GLOBAL,
                branch_id=None,
                defaults={
                    "value_json": spec["value_json"],
                    "description": spec["description"],
                },
            )
            if was_created:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"seed_default_branch done — created={created}, existing={len(specs) - created}",
            ),
        )
