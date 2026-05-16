"""URL routes for the system-settings API (``/api/v1/``)."""

from __future__ import annotations

from rest_framework.routers import DefaultRouter

from .views import (
    ContactInfoViewSet,
    FeatureToggleViewSet,
    IntegrationKeyViewSet,
    SiteSettingViewSet,
    SocialLinkViewSet,
)

app_name = "system_settings"

router = DefaultRouter()
router.register("system-settings", SiteSettingViewSet, basename="site-setting")
router.register("feature-toggles", FeatureToggleViewSet, basename="feature-toggle")
router.register("integration-keys", IntegrationKeyViewSet, basename="integration-key")
router.register("social-links", SocialLinkViewSet, basename="social-link")
router.register("contact-info", ContactInfoViewSet, basename="contact-info")

urlpatterns = router.urls
