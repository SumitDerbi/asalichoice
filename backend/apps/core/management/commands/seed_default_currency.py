"""Seed the default currency (``site.default_currency = "INR"``).

Thin wrapper around :class:`apps.system_settings.models.SiteSetting`
kept as its own command so operators can re-run just the currency
default without touching the rest of ``seed_settings``.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.system_settings.models import SettingScope, SiteSetting

DEFAULT_CURRENCY = "INR"


class Command(BaseCommand):
    help = "Seed the default currency SiteSetting (INR)."

    def handle(self, *args, **options):
        _, was_created = SiteSetting.objects.get_or_create(
            key="site.default_currency",
            scope=SettingScope.GLOBAL,
            branch_id=None,
            defaults={
                "value_json": DEFAULT_CURRENCY,
                "description": "Default currency code.",
            },
        )
        verb = "created" if was_created else "exists"
        self.stdout.write(
            self.style.SUCCESS(
                f"seed_default_currency: site.default_currency={DEFAULT_CURRENCY} ({verb})"
            ),
        )
