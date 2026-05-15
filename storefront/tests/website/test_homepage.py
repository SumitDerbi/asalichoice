"""Smoke tests for the homepage.

Per plan 003: ``pytest storefront/tests/test_homepage.py -q`` must pass.
The test creates a HomePage under the default Wagtail root, points the
default Site at it, and asserts the public URL renders 200 with the
expected hero content.
"""

from __future__ import annotations

import pytest
from django.test import Client
from wagtail.models import Page, Site

from apps.website.models import HomePage


@pytest.fixture
def homepage(db) -> HomePage:
    """Create a HomePage and make it the root of the default Wagtail Site.

    Wagtail's initial migration creates a default "Welcome" page (slug
    ``home``) beneath the tree root and points the default Site at it. We
    keep that page so ``Site`` references stay intact, but add a new
    :class:`HomePage` with a distinct slug and re-point the default Site
    at it.
    """
    root = Page.objects.get(depth=1)
    home = HomePage(
        title="AsliChoice",
        slug="asalichoice-home",
        hero_title="Curated for you",
        hero_tagline="Discover the AsliChoice catalogue.",
        hero_cta_text="Shop now",
        hero_cta_url="/shop/",
    )
    root.add_child(instance=home)
    home.save_revision().publish()

    site = Site.objects.get(is_default_site=True)
    site.root_page = home
    site.hostname = "localhost"
    site.port = 80
    site.save()
    return home


def test_homepage_renders(client: Client, homepage: HomePage) -> None:
    response = client.get("/", HTTP_HOST="localhost")
    assert response.status_code == 200
    body = response.content.decode()
    assert "Curated for you" in body
    assert "Discover the AsliChoice catalogue." in body
    # Site-wide Organization JSON-LD must be present.
    assert '"@type": "Organization"' in body


def test_robots_txt_renders(client: Client, homepage: HomePage) -> None:
    response = client.get("/robots.txt", HTTP_HOST="localhost")
    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/plain")
    body = response.content.decode()
    assert "User-agent: *" in body
    assert "Sitemap:" in body
    assert "/sitemap.xml" in body


def test_sitemap_xml_renders(client: Client, homepage: HomePage) -> None:
    response = client.get("/sitemap.xml", HTTP_HOST="localhost")
    assert response.status_code == 200
    assert "xml" in response["Content-Type"]
    assert b"<urlset" in response.content
