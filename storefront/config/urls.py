"""URL configuration for the AsliChoice storefront."""

from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps import Sitemap as WagtailSitemap
from wagtail.documents import urls as wagtaildocs_urls

from apps.core import views as core_views

sitemaps = {"wagtail": WagtailSitemap}

urlpatterns = [
    # Django + Wagtail admins.
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    # SEO endpoints.
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", core_views.robots_txt, name="robots"),
    # Internal: storefront -> backend reachability probe (server-side).
    path("internal/backend-health/", core_views.backend_health, name="backend-health"),
    # Wagtail serves all remaining URLs from the page tree.
    path("", include(wagtail_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
