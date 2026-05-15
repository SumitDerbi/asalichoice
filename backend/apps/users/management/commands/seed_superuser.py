"""Seed the bootstrap superuser from environment variables.

Reads ``SEED_SUPERUSER_EMAIL`` and ``SEED_SUPERUSER_PASSWORD`` from the
environment (via Django settings → django-environ). Re-runnable: if a
user with the target email already exists it is left untouched unless
``--update-password`` is passed.
"""

from __future__ import annotations

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create or refresh the bootstrap superuser from environment variables."

    def add_arguments(self, parser) -> None:  # type: ignore[override]
        parser.add_argument(
            "--update-password",
            action="store_true",
            help="If the user already exists, reset their password to the env value.",
        )

    def handle(self, *args, **options) -> None:  # type: ignore[override]
        email = os.environ.get("SEED_SUPERUSER_EMAIL", "").strip().lower()
        password = os.environ.get("SEED_SUPERUSER_PASSWORD", "")
        if not email or not password:
            raise CommandError("Both SEED_SUPERUSER_EMAIL and SEED_SUPERUSER_PASSWORD must be set.")

        user_model = get_user_model()
        user = user_model.all_objects.filter(email__iexact=email).first()

        if user is None:
            user_model.objects.create_superuser(email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Created superuser {email}"))
            return

        changed = False
        if not user.is_superuser or not user.is_staff or not user.is_active:
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.deleted_at = None
            changed = True
        if options["update_password"]:
            user.set_password(password)
            changed = True
        if changed:
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Updated superuser {email}"))
        else:
            self.stdout.write(f"Superuser {email} already present; nothing to do.")
