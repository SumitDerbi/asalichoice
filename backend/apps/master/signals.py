"""Master-app signal definitions and hooks (M01/03 §3).

Two responsibilities:

1. Publish ``branch_changed`` so other modules (catalog, inventory, …)
   can react to branch CRUD without importing :mod:`apps.master.models`.
2. Bump the ``master.cache_version`` :class:`SiteSetting` whenever a
   cacheable master row changes — :mod:`apps.master.cache` keys its
   entries off that version so a bump invalidates every consumer atomically.
"""

from __future__ import annotations

import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import Signal, receiver

from .models import Branch, HSNCode, Pincode, Tax, Zone

log = logging.getLogger(__name__)

# Public signal — receivers connect from other modules.
branch_changed = Signal()


CACHE_VERSION_KEY = "master.cache_version"


def _bump_cache_version() -> None:
    """Increment ``SiteSetting[master.cache_version]`` and invalidate cache."""

    try:
        from apps.system_settings.models import SettingScope, SiteSetting
        from apps.system_settings.services import invalidate_setting_cache
    except Exception:  # pragma: no cover - defensive
        log.exception("system_settings unavailable; skipping cache-version bump")
        return

    row, created = SiteSetting.objects.get_or_create(
        key=CACHE_VERSION_KEY,
        scope=SettingScope.GLOBAL,
        defaults={"value_json": 1},
    )
    if not created:
        try:
            current = int(row.value_json or 0)
        except (TypeError, ValueError):
            current = 0
        row.value_json = current + 1
        row.save(update_fields=["value_json", "updated_at"])
    invalidate_setting_cache(CACHE_VERSION_KEY)


@receiver(post_save, sender=Branch)
def _branch_saved(sender, instance, created, **kwargs):
    branch_changed.send(sender=Branch, instance=instance, created=created)
    _bump_cache_version()


@receiver(post_delete, sender=Branch)
def _branch_deleted(sender, instance, **kwargs):
    branch_changed.send(sender=Branch, instance=instance, created=False)
    _bump_cache_version()


@receiver(post_save, sender=Tax)
@receiver(post_save, sender=HSNCode)
@receiver(post_save, sender=Zone)
@receiver(post_save, sender=Pincode)
def _master_row_saved(sender, instance, **kwargs):
    _bump_cache_version()


@receiver(post_delete, sender=Tax)
@receiver(post_delete, sender=HSNCode)
@receiver(post_delete, sender=Zone)
@receiver(post_delete, sender=Pincode)
def _master_row_deleted(sender, instance, **kwargs):
    _bump_cache_version()
