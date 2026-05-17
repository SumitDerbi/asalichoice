"""Effective-price lookup with branch scoping + per-(item, branch) cache.

A price band covers ``[valid_from, valid_to or +inf)``. The active band
at moment ``at`` is the most recent ``valid_from <= at`` whose
``valid_to`` is either NULL or > ``at`` and whose ``is_active=True``.

Cache TTL: 60 seconds. Versioned key namespace (``catalog:prices:vN``)
bumped by :mod:`apps.catalog.signals` on any :class:`ProductPrice` save.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal

from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone

from ..exceptions import PriceNotFound, PriceTargetInvalid, PriceWindowInvalid
from ..models import Product, ProductPrice, ProductVariant

_CACHE_VERSION_KEY = "catalog:prices:version"
_DEFAULT_TTL = 60  # seconds


def _version() -> int:
    return cache.get_or_set(_CACHE_VERSION_KEY, 1, timeout=None)


def bump_version() -> None:
    """Invalidate the entire price cache namespace."""

    try:
        cache.incr(_CACHE_VERSION_KEY)
    except ValueError:
        cache.set(_CACHE_VERSION_KEY, 2, timeout=None)


def _cache_key(*, product_id: int | None, variant_id: int | None, branch_id: int) -> str:
    target = f"p{product_id}" if product_id else f"v{variant_id}"
    return f"catalog:prices:v{_version()}:{target}:b{branch_id}"


@dataclass(frozen=True)
class EffectivePrice:
    mrp: Decimal
    sale_price: Decimal
    cost_price: Decimal | None
    band_id: int


def _resolve_target(item: Product | ProductVariant) -> tuple[int | None, int | None]:
    if isinstance(item, Product):
        return item.pk, None
    if isinstance(item, ProductVariant):
        return None, item.pk
    raise TypeError(f"Unsupported pricing target: {type(item)!r}")


def _fetch(
    *,
    product_id: int | None,
    variant_id: int | None,
    branch_id: int,
    at,
) -> EffectivePrice | None:
    qs = ProductPrice.objects.filter(
        branch_id=branch_id,
        is_active=True,
        valid_from__lte=at,
    ).filter(Q(valid_to__isnull=True) | Q(valid_to__gt=at))
    if product_id is not None:
        qs = qs.filter(product_id=product_id)
    else:
        qs = qs.filter(variant_id=variant_id)
    row = qs.order_by("-valid_from").first()
    if row is None:
        return None
    return EffectivePrice(
        mrp=row.mrp,
        sale_price=row.sale_price,
        cost_price=row.cost_price,
        band_id=row.pk,
    )


def get_effective_price(
    item: Product | ProductVariant,
    branch_id: int,
    *,
    at=None,
    use_cache: bool = True,
) -> EffectivePrice:
    """Return the active price band for ``item`` at ``branch_id``.

    Raises :class:`PriceNotFound` if no band applies.
    """

    product_id, variant_id = _resolve_target(item)
    moment = at or timezone.now()
    if use_cache and at is None:
        key = _cache_key(product_id=product_id, variant_id=variant_id, branch_id=branch_id)
        cached = cache.get(key)
        if cached is not None:
            return cached
        result = _fetch(
            product_id=product_id, variant_id=variant_id, branch_id=branch_id, at=moment
        )
        if result is None:
            raise PriceNotFound()
        cache.set(key, result, timeout=_DEFAULT_TTL)
        return result
    result = _fetch(product_id=product_id, variant_id=variant_id, branch_id=branch_id, at=moment)
    if result is None:
        raise PriceNotFound()
    return result


def bulk_lookup(
    targets: Iterable[tuple[Product | ProductVariant, int]],
    *,
    at=None,
) -> dict[tuple[str, int, int], EffectivePrice]:
    """Resolve a batch of (item, branch_id) pairs in a single query.

    Returns a dict keyed by ``("p"|"v", target_id, branch_id)``. Missing
    bands are omitted (callers can detect and fall back per item).
    """

    moment = at or timezone.now()
    pairs = list(targets)
    product_pairs: list[tuple[int, int]] = []
    variant_pairs: list[tuple[int, int]] = []
    for item, branch_id in pairs:
        pid, vid = _resolve_target(item)
        if pid is not None:
            product_pairs.append((pid, branch_id))
        else:
            variant_pairs.append((vid, branch_id))  # type: ignore[arg-type]

    qs = ProductPrice.objects.filter(is_active=True, valid_from__lte=moment).filter(
        Q(valid_to__isnull=True) | Q(valid_to__gt=moment)
    )
    filters = Q()
    if product_pairs:
        for pid, bid in product_pairs:
            filters |= Q(product_id=pid, branch_id=bid)
    if variant_pairs:
        for vid, bid in variant_pairs:
            filters |= Q(variant_id=vid, branch_id=bid)
    if not (product_pairs or variant_pairs):
        return {}
    rows = qs.filter(filters).order_by("-valid_from")

    result: dict[tuple[str, int, int], EffectivePrice] = {}
    for row in rows:
        if row.product_id is not None:
            key = ("p", row.product_id, row.branch_id)
        else:
            key = ("v", row.variant_id, row.branch_id)
        if key in result:  # only keep the most recent (already ordered)
            continue
        result[key] = EffectivePrice(
            mrp=row.mrp,
            sale_price=row.sale_price,
            cost_price=row.cost_price,
            band_id=row.pk,
        )
    return result


def set_price(
    *,
    product: Product | None = None,
    variant: ProductVariant | None = None,
    branch_id: int,
    mrp: Decimal,
    sale_price: Decimal,
    cost_price: Decimal | None = None,
    valid_from=None,
    valid_to=None,
) -> ProductPrice:
    """Insert a new price band. Bumps the cache version on success."""

    if bool(product) == bool(variant):
        raise PriceTargetInvalid()
    if valid_to is not None and valid_from is not None and valid_to <= valid_from:
        raise PriceWindowInvalid()

    band = ProductPrice.objects.create(
        product=product,
        variant=variant,
        branch_id=branch_id,
        mrp=mrp,
        sale_price=sale_price,
        cost_price=cost_price,
        valid_from=valid_from or timezone.now(),
        valid_to=valid_to,
    )
    bump_version()
    return band
