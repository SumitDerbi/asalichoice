"""``manage.py bootstrap_homepage`` — create the default AsliChoice HomePage.

Wagtail's initial migration adds a placeholder ``Welcome`` page (slug
``home``) under the tree root and points the default Site at it. This
command replaces it with an :class:`apps.website.models.HomePage` so the
storefront has a hero-rendering homepage at ``/``.

Idempotent: re-running it is a no-op once a HomePage exists.

Usage::

    python manage.py bootstrap_homepage
    python manage.py bootstrap_homepage --hostname storefront.local --port 8001

Plan reference: ``plans/phase-0-foundation/003-website-wagtail-setup.md`` step 8.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError
from wagtail.models import Page, Site

from apps.website.models import HomePage


class Command(BaseCommand):
    help = "Create the default AsliChoice HomePage and point the default Site at it."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--hostname", default="localhost")
        parser.add_argument("--port", type=int, default=80)
        parser.add_argument(
            "--site-name",
            default="AsliChoice",
            help="Wagtail Site display name.",
        )

    def handle(self, *args, **options) -> None:
        if HomePage.objects.exists():
            self.stdout.write(self.style.SUCCESS("HomePage already exists — nothing to do."))
            return

        try:
            root = Page.objects.get(depth=1)
        except Page.DoesNotExist as exc:  # pragma: no cover - corrupt tree
            raise CommandError("Wagtail page tree root not found — run migrate first.") from exc

        home = HomePage(
            title=options["site_name"],
            slug="asalichoice-home",
            hero_title=f"Welcome to {options['site_name']}",
            hero_tagline="A curated omnichannel storefront — coming soon.",
        )
        root.add_child(instance=home)
        home.save_revision().publish()

        site = Site.objects.filter(is_default_site=True).first()
        if site:
            site.root_page = home
            site.hostname = options["hostname"]
            site.port = options["port"]
            site.site_name = options["site_name"]
            site.save()
        else:
            Site.objects.create(
                hostname=options["hostname"],
                port=options["port"],
                root_page=home,
                is_default_site=True,
                site_name=options["site_name"],
            )

        self.stdout.write(
            self.style.SUCCESS(f"Created HomePage #{home.pk} and pointed default Site at it.")
        )
