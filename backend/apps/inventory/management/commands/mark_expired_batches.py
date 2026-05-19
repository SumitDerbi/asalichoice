"""Management command: ``python manage.py mark_expired_batches``.

Flips :class:`apps.inventory.models.Batch` rows whose ``expiry_date`` has
elapsed and whose status is still ``ACTIVE`` to ``EXPIRED``. Idempotent.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.inventory.services.expiry_service import mark_expired_batches


class Command(BaseCommand):
    help = "Mark active batches past their expiry_date as EXPIRED."

    def handle(self, *args, **options):
        count = mark_expired_batches()
        self.stdout.write(self.style.SUCCESS(f"expired batches: {count}"))
