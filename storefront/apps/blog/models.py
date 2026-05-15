"""Placeholder blog models.

Only :class:`BlogIndexPage` ships in plan 003 so the homepage can link
to ``/blog/`` immediately. Individual ``BlogPost`` pages land with the
content/marketing module.
"""

from __future__ import annotations

from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtailseo.models import SeoMixin


class BlogIndexPage(SeoMixin, Page):
    """Top-level landing page for the (future) blog."""

    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [FieldPanel("intro")]
    promote_panels = SeoMixin.seo_panels

    parent_page_types = ["website.HomePage"]
    subpage_types: list[str] = []  # BlogPost lands later.
    max_count = 1

    class Meta:
        verbose_name = "Blog index"
