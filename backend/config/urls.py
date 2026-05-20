"""
Root URL configuration for the AsliChoice backend.

All API routes are versioned under ``/api/v1/``. Module routers append to
this prefix in subsequent plan steps (M01 onward).
"""

from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

_NOT_FOUND_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>AsliChoice API</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  :root{color-scheme:light dark}
  html,body{height:100%;margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
  body{display:flex;align-items:center;justify-content:center;background:#0b0c0f;color:#e7e9ee}
  .card{max-width:560px;padding:2.5rem 2rem;border-radius:14px;background:#14161b;
        box-shadow:0 10px 40px rgba(0,0,0,.4);text-align:center}
  h1{margin:0 0 .25rem;font-size:3rem;letter-spacing:-.02em}
  h2{margin:0 0 1rem;font-size:1.1rem;font-weight:500;color:#9aa3b2}
  p{margin:.5rem 0;color:#c2c8d3;line-height:1.55}
  a{color:#7aa7ff;text-decoration:none}
  a:hover{text-decoration:underline}
  code{background:#1f232c;padding:.15rem .4rem;border-radius:6px;font-size:.9em}
</style>
</head>
<body>
  <div class="card">
    <h1>404</h1>
    <h2>This isn\u2019t a page \u2014 it\u2019s an API.</h2>
    <p>You\u2019ve reached the AsliChoice backend.</p>
    <p>API root: <code><a href="/api/v1/">/api/v1/</a></code><br>
       Docs: <code><a href="/api/v1/docs/">/api/v1/docs/</a></code></p>
  </div>
</body>
</html>"""


def custom_404(request, exception=None):
    return HttpResponse(_NOT_FOUND_HTML, status=404, content_type="text/html; charset=utf-8")


handler404 = "config.urls.custom_404"


urlpatterns = [
    path("admin/", admin.site.urls),
    # API v1
    path("api/v1/", include("apps.core.urls")),
    path("api/v1/", include("apps.users.urls")),
    path("api/v1/", include("apps.system_settings.urls")),
    path("api/v1/master/", include("apps.master.urls")),
    path("api/v1/catalog/", include("apps.catalog.urls")),
    path("api/v1/purchase/", include("apps.purchase.urls")),
    path("api/v1/inventory/", include("apps.inventory.urls")),
    path("api/v1/", include("apps.sales.urls")),
    path(
        "api/v1/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),
    path(
        "api/v1/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
