"""Seed the default site settings + feature toggles for first-time deploys.

Idempotent — re-running won't clobber operator-modified values. Each
setting is upserted via ``update_or_create(..., defaults={...})`` but
only when the row does **not** already exist; existing rows are left
alone.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.system_settings.models import (
    ContactInfo,
    FeatureToggle,
    SettingScope,
    SiteSetting,
    SocialLink,
)

DEFAULT_SETTINGS: list[dict] = [
    {"key": "otp.length", "value_json": 6, "description": "Default OTP length."},
    {"key": "otp.expiry_seconds", "value_json": 300, "description": "OTP validity window."},
    {"key": "site.default_currency", "value_json": "INR", "description": "Default currency code."},
    {
        "key": "site.default_timezone",
        "value_json": "Asia/Kolkata",
        "description": "Default timezone.",
    },
    {
        "key": "tax.inclusive_by_default",
        "value_json": False,
        "description": "Are listed prices tax-inclusive by default.",
    },
    {
        "key": "orders.allow_guest_checkout",
        "value_json": True,
        "description": "Allow non-authenticated checkout.",
    },
]

DEFAULT_TOGGLES: list[dict] = [
    {"key": "checkout.payments.razorpay", "enabled": False, "description": "Razorpay checkout."},
    {"key": "checkout.payments.cod", "enabled": True, "description": "Cash on delivery."},
    {"key": "notifications.sms.msg91", "enabled": False, "description": "MSG91 transactional SMS."},
    {"key": "storefront.show_blog", "enabled": True, "description": "Show blog section."},
]

DEFAULT_SOCIAL_LINKS: list[dict] = [
    {"platform": "facebook", "url": "https://www.facebook.com/asalichoice"},
    {"platform": "instagram", "url": "https://www.instagram.com/asalichoice"},
    {"platform": "twitter", "url": "https://twitter.com/asalichoice"},
]

DEFAULT_CONTACT_INFO: list[dict] = [
    {
        "label": "Head Office",
        "email": "hello@asalichoice.example",
        "phone": "+91-0000000000",
        "address": "Update via admin.",
        "is_primary": True,
    },
]


class Command(BaseCommand):
    help = "Seed default site settings, feature toggles, social links, and contact info."

    def add_arguments(self, parser):
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Force-update existing rows to the seeded defaults.",
        )

    def handle(self, *args, **options):
        overwrite = options["overwrite"]
        created = updated = 0

        for spec in DEFAULT_SETTINGS:
            row, was_created = SiteSetting.objects.get_or_create(
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
            elif overwrite:
                row.value_json = spec["value_json"]
                row.description = spec["description"]
                row.save(update_fields=["value_json", "description", "updated_at"])
                updated += 1

        for spec in DEFAULT_TOGGLES:
            row, was_created = FeatureToggle.objects.get_or_create(
                key=spec["key"],
                defaults={
                    "enabled": spec["enabled"],
                    "description": spec["description"],
                },
            )
            if was_created:
                created += 1
            elif overwrite:
                row.enabled = spec["enabled"]
                row.description = spec["description"]
                row.save(update_fields=["enabled", "description", "updated_at"])
                updated += 1

        for spec in DEFAULT_SOCIAL_LINKS:
            _, was_created = SocialLink.objects.get_or_create(
                platform=spec["platform"],
                defaults={"url": spec["url"]},
            )
            if was_created:
                created += 1

        for spec in DEFAULT_CONTACT_INFO:
            _, was_created = ContactInfo.objects.get_or_create(
                label=spec["label"],
                defaults={
                    "email": spec["email"],
                    "phone": spec["phone"],
                    "address": spec["address"],
                    "is_primary": spec["is_primary"],
                },
            )
            if was_created:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"seed_settings done — created={created}, updated={updated}",
            ),
        )
