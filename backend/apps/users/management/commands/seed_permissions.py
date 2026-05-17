"""Seed :class:`apps.users.models.Permission` rows from each app's
``permissions.py``.

Convention: each app exposes a module-level tuple named
``<APP>_PERMISSIONS`` containing ``(code, name)`` pairs. We walk every
installed app and upsert one Permission row per pair, tagged with the
app label as ``module``.
"""

from __future__ import annotations

import importlib

from django.apps import apps as django_apps
from django.core.management.base import BaseCommand

from apps.users.models import Permission


class Command(BaseCommand):
    help = "Seed Permission rows from each app's permissions.py."

    def handle(self, *args, **options):
        created = 0
        updated = 0
        for app_config in django_apps.get_app_configs():
            module_name = f"{app_config.name}.permissions"
            try:
                module = importlib.import_module(module_name)
            except ModuleNotFoundError:
                continue

            for attr in dir(module):
                if not attr.endswith("_PERMISSIONS") or attr.startswith("_"):
                    continue
                value = getattr(module, attr)
                if not isinstance(value, list | tuple):
                    continue
                for entry in value:
                    if not isinstance(entry, list | tuple) or len(entry) < 2:
                        continue
                    code, name = entry[0], entry[1]
                    description = entry[2] if len(entry) > 2 else ""
                    obj, was_created = Permission.objects.update_or_create(
                        code=code,
                        defaults={
                            "name": name,
                            "module": app_config.label,
                            "description": description,
                        },
                    )
                    if was_created:
                        created += 1
                    else:
                        updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"seed_permissions done — created={created}, updated={updated}",
            ),
        )
