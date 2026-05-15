"""Cross-cutting views for the storefront.

Currently provides:

* ``robots_txt`` — small allow-all robots file referencing the sitemap.
* ``backend_health`` — server-side probe that calls the backend's public
  ``/health/`` endpoint to confirm cross-app reachability. Not surfaced in
  the public UI yet (per plan 003 step 11); intended for ops + smoke tests.
"""

from __future__ import annotations

import logging

import requests
from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)


@require_GET
def robots_txt(request: HttpRequest) -> HttpResponse:
    """Return a minimal allow-all robots.txt pointing at the sitemap."""
    sitemap_url = request.build_absolute_uri(reverse("sitemap"))
    body = "\n".join(
        [
            "User-agent: *",
            "Disallow: /admin/",
            "Disallow: /django-admin/",
            f"Sitemap: {sitemap_url}",
            "",
        ]
    )
    return HttpResponse(body, content_type="text/plain; charset=utf-8")


@require_GET
def backend_health(request: HttpRequest) -> JsonResponse:
    """Probe the backend ``/health/`` endpoint from the storefront process.

    Returns ``{reachable, status_code, upstream}`` so ops can confirm the
    storefront can reach the backend without exposing backend internals to
    the public UI. Never raises — network errors are reported as
    ``reachable: false`` with HTTP 502.
    """
    upstream = settings.BACKEND_API_URL.rstrip("/") + "/health/"
    timeout = settings.BACKEND_API_TIMEOUT
    try:
        response = requests.get(upstream, timeout=timeout)
    except requests.RequestException as exc:
        # Log the full exception for ops; do not echo it back to the
        # client — request exception messages can include the resolved
        # upstream URL, proxy details, or library internals.
        logger.warning("Backend health probe to %s failed: %s", upstream, exc)
        return JsonResponse(
            {
                "reachable": False,
                "upstream": upstream,
                "error": "backend_unreachable",
            },
            status=502,
        )

    return JsonResponse(
        {
            "reachable": response.ok,
            "status_code": response.status_code,
            "upstream": upstream,
        },
        status=200 if response.ok else 502,
    )
