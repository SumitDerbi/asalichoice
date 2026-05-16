"""Signal wiring — cache invalidation on save/delete."""

from __future__ import annotations

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import FeatureToggle, SiteSetting
from .services import invalidate_feature_cache, invalidate_setting_cache


@receiver([post_save, post_delete], sender=SiteSetting)
def _evict_setting(sender, instance, **kwargs):
    invalidate_setting_cache(instance.key)


@receiver([post_save, post_delete], sender=FeatureToggle)
def _evict_toggle(sender, instance, **kwargs):
    invalidate_feature_cache(instance.key)
