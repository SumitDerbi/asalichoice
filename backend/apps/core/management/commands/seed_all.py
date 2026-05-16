"""Orchestrator: run every phase-0 seeder in dependency order.

Calls each module's ``seed_*`` command via :func:`call_command`, in the
canonical order:

1. ``seed_roles`` — placeholder role groups.
2. ``seed_settings`` — default site settings + feature toggles.
3. ``seed_default_currency`` / ``seed_default_timezone`` —
   idempotent reinforcement of the two keys.
4. ``seed_default_branch`` — placeholder branch as SiteSetting rows.
5. ``seed_superuser`` — only if ``SEED_SUPERUSER_EMAIL`` and
   ``SEED_SUPERUSER_PASSWORD`` are set in the environment; otherwise
   logged and skipped.

Re-runnable: every downstream command is idempotent on its own.
"""

from __future__ import annotations

import os

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

SEEDERS: tuple[str, ...] = (
    "seed_roles",
    "seed_settings",
    "seed_default_currency",
    "seed_default_timezone",
    "seed_default_branch",
    "seed_master",
)


class Command(BaseCommand):
    help = "Run every phase-0 seeder in dependency order (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-superuser",
            action="store_true",
            help="Do not attempt to run seed_superuser even if env vars are set.",
        )

    def handle(self, *args, **options):
        for cmd in SEEDERS:
            self.stdout.write(self.style.MIGRATE_HEADING(f"→ {cmd}"))
            call_command(cmd, stdout=self.stdout, stderr=self.stderr)

        if options["skip_superuser"]:
            self.stdout.write("Skipping seed_superuser (--skip-superuser).")
            return

        has_email = bool(os.environ.get("SEED_SUPERUSER_EMAIL"))
        has_password = bool(os.environ.get("SEED_SUPERUSER_PASSWORD"))
        if not (has_email and has_password):
            self.stdout.write(
                "Skipping seed_superuser — SEED_SUPERUSER_EMAIL / "
                "SEED_SUPERUSER_PASSWORD not set.",
            )
            return

        self.stdout.write(self.style.MIGRATE_HEADING("→ seed_superuser"))
        try:
            call_command("seed_superuser", stdout=self.stdout, stderr=self.stderr)
        except CommandError as exc:
            self.stderr.write(self.style.WARNING(f"seed_superuser skipped: {exc}"))

        self.stdout.write(self.style.SUCCESS("seed_all complete."))
