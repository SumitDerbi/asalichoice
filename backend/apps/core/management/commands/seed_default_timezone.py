"""Seed the default timezone (``site.default_timezone = "Asia/Kolkata"``)."""

from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.system_settings.models import SettingScope, SiteSetting

DEFAULT_TIMEZONE = "Asia/Kolkata"


class Command(BaseCommand):
    help = "Seed the default timezone SiteSetting (Asia/Kolkata)."

    def handle(self, *args, **options):
        _, was_created = SiteSetting.objects.get_or_create(
            key="site.default_timezone",
            scope=SettingScope.GLOBAL,
            branch_id=None,
            defaults={
                "value_json": DEFAULT_TIMEZONE,
                "description": "Default timezone.",
            },
        )
        verb = "created" if was_created else "exists"
        self.stdout.write(
            self.style.SUCCESS(
                f"seed_default_timezone: site.default_timezone={DEFAULT_TIMEZONE} ({verb})"
            ),
        )
