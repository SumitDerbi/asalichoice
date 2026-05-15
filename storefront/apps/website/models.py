"""Wagtail page models for the public website.

The initial scaffold (plan 003) introduces a single :class:`HomePage`
with a hero (title + tagline + CTA), an optional hero image, and a
``banner`` StreamField for editor-controlled sections.

Page-level SEO fields (meta description, OG image, canonical, JSON-LD
type) come from :class:`wagtailseo.models.SeoMixin`.
"""

from __future__ import annotations

from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtailseo.models import SeoMixin, SeoType

from .blocks import HOMEPAGE_BANNER_BLOCKS


class HomePage(SeoMixin, Page):
    """Site root page.

    Only one HomePage is expected per Wagtail Site (it is created during
    initial setup and replaces Wagtail's default ``Welcome`` page).
    """

    # ----- Hero -----
    hero_title = models.CharField(
        max_length=120,
        blank=True,
        help_text="Main heading shown at the top of the homepage.",
    )
    hero_tagline = models.CharField(
        max_length=240,
        blank=True,
        help_text="Short supporting line under the hero title.",
    )
    hero_cta_text = models.CharField(
        max_length=40,
        blank=True,
        help_text="Call-to-action button text. Leave blank to hide the button.",
    )
    hero_cta_url = models.CharField(
        max_length=500,
        blank=True,
        help_text="Destination URL for the CTA button (absolute or relative).",
    )
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    # ----- Editor-controlled sections -----
    banner = StreamField(
        HOMEPAGE_BANNER_BLOCKS,
        blank=True,
        use_json_field=True,
        help_text="Stackable content sections shown below the hero.",
    )

    # Default SEO type → website root. Page-level overrides still work
    # via the SEO tab in the admin.
    seo_content_type = SeoType.WEBSITE

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("hero_title"),
                FieldPanel("hero_tagline"),
                FieldPanel("hero_cta_text"),
                FieldPanel("hero_cta_url"),
                FieldPanel("hero_image"),
            ],
            heading="Hero",
        ),
        FieldPanel("banner"),
    ]

    promote_panels = SeoMixin.seo_panels

    # Only one HomePage per Site (created at bootstrap).
    max_count_per_parent = 1
    # Allow only as a child of the Wagtail root.
    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["website.ContentPage", "blog.BlogIndexPage"]

    class Meta:
        verbose_name = "Home page"


class ContentPage(SeoMixin, Page):
    """Generic content page for static marketing/landing content."""

    intro = models.CharField(max_length=300, blank=True)
    body = StreamField(
        HOMEPAGE_BANNER_BLOCKS,
        blank=True,
        use_json_field=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
    ]

    promote_panels = SeoMixin.seo_panels

    parent_page_types = ["website.HomePage", "website.ContentPage"]
    subpage_types = ["website.ContentPage"]
