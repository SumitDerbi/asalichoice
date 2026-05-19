"""M05 Inventory — availability and reservations service (step 4).

Provides concurrency-safe reservation and availability logic for stock rows.
"""

from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.inventory.models import (
    Branch,
    Product,
    ProductVariant,
    Reservation,
    ReservationStatus,
    Stock,
)


def available(item: Product | ProductVariant, branch: Branch) -> Decimal:
    """Returns available quantity (qty_on_hand - qty_reserved) for the given item and branch."""
    stock = _get_stock_row(item, branch)
    if not stock:
        return Decimal("0")
    return stock.qty_on_hand - stock.qty_reserved


def reserve(
    item: Product | ProductVariant,
    branch: Branch,
    qty: Decimal,
    ref_type: str,
    ref_id: str,
    expires_at: timezone.datetime | None = None,
) -> Reservation:
    """Creates a reservation and bumps qty_reserved. Uses select_for_update for concurrency safety."""
    with transaction.atomic():
        stock = _lock_stock_row(item, branch)
        if stock.qty_on_hand - stock.qty_reserved < qty:
            from apps.inventory.exceptions import InsufficientStock

            raise InsufficientStock()
        reservation = Reservation.objects.create(
            product=item if isinstance(item, Product) else None,
            variant=item if isinstance(item, ProductVariant) else None,
            branch=branch,
            qty=qty,
            ref_type=ref_type,
            ref_id=ref_id,
            expires_at=expires_at,
            status=ReservationStatus.ACTIVE,
        )
        stock.qty_reserved += qty
        stock.save(update_fields=["qty_reserved"])
        return reservation


def release(reservation: Reservation) -> None:
    """Releases a reservation and decrements qty_reserved."""
    with transaction.atomic():
        if reservation.status != ReservationStatus.ACTIVE:
            return
        stock = _lock_stock_row(reservation.product or reservation.variant, reservation.branch)
        stock.qty_reserved -= reservation.qty
        stock.save(update_fields=["qty_reserved"])
        reservation.status = ReservationStatus.RELEASED
        reservation.save(update_fields=["status"])


def consume(reservation: Reservation) -> None:
    """Consumes a reservation and decrements qty_reserved."""
    with transaction.atomic():
        if reservation.status != ReservationStatus.ACTIVE:
            return
        stock = _lock_stock_row(reservation.product or reservation.variant, reservation.branch)
        stock.qty_reserved -= reservation.qty
        stock.save(update_fields=["qty_reserved"])
        reservation.status = ReservationStatus.CONSUMED
        reservation.save(update_fields=["status"])


def expire_stale_reservations() -> int:
    """Expires all ACTIVE reservations past their expires_at. Returns count expired."""
    now = timezone.now()
    qs = Reservation.objects.filter(status=ReservationStatus.ACTIVE, expires_at__lt=now)
    count = 0
    for reservation in qs:
        release(reservation)
        reservation.status = ReservationStatus.EXPIRED
        reservation.save(update_fields=["status"])
        count += 1
    return count


def _get_stock_row(item, branch) -> Stock | None:
    if isinstance(item, Product):
        return Stock.objects.filter(product=item, branch=branch).first()
    else:
        return Stock.objects.filter(variant=item, branch=branch).first()


def _lock_stock_row(item, branch) -> Stock:
    if isinstance(item, Product):
        stock = Stock.all_objects.select_for_update().filter(product=item, branch=branch).first()
    else:
        stock = Stock.all_objects.select_for_update().filter(variant=item, branch=branch).first()
    if not stock:
        raise ValueError("Stock row does not exist for reservation target.")
    return stock
