"""StreamField blocks available on website pages.

Kept intentionally small for the initial scaffold (plan 003):
text + image blocks. Richer blocks (featured products, testimonials,
category grids, etc.) land alongside their respective backend modules.
"""

from __future__ import annotations

from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class HeadingBlock(blocks.CharBlock):
    """Simple section heading."""

    class Meta:
        icon = "title"
        template = "website/blocks/heading_block.html"


class ParagraphBlock(blocks.RichTextBlock):
    """Free-form rich text paragraph."""

    class Meta:
        icon = "pilcrow"
        template = "website/blocks/paragraph_block.html"


class BannerImageBlock(blocks.StructBlock):
    """Full-width image with optional alt text and caption."""

    image = ImageChooserBlock(required=True)
    alt_text = blocks.CharBlock(required=False, max_length=160)
    caption = blocks.CharBlock(required=False, max_length=200)

    class Meta:
        icon = "image"
        template = "website/blocks/banner_image_block.html"


class FeaturedProductsBlock(blocks.StructBlock):
    """Placeholder for a "featured products" carousel.

    The real implementation (fetching products from the backend API) lands
    with the online-store module. For now this block carries a title +
    optional intro so editors can lay out the homepage without blocking on
    backend wiring.
    """

    title = blocks.CharBlock(required=True, max_length=120, default="Featured products")
    intro = blocks.TextBlock(required=False, max_length=400)

    class Meta:
        icon = "pick"
        label = "Featured products (placeholder)"
        template = "website/blocks/featured_products_block.html"


# The StreamField used by HomePage.banner — combination of all blocks above.
HOMEPAGE_BANNER_BLOCKS = [
    ("heading", HeadingBlock()),
    ("paragraph", ParagraphBlock()),
    ("image", BannerImageBlock()),
    ("featured_products", FeaturedProductsBlock()),
]
