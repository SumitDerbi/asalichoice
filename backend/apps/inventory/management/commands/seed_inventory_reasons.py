"""Management command: ``python manage.py seed_inventory_reasons``.

Invokes :func:`apps.inventory.seeders.reason_codes.seed`. Idempotent.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.inventory.seeders.reason_codes import seed


class Command(BaseCommand):
    help = "Seed M05 inventory reason codes (DAMAGE / THEFT / EXPIRY / ...)."

    def handle(self, *args, **options):
        summary = seed()
        self.stdout.write(self.style.SUCCESS(f"inventory reasons: {summary}"))
