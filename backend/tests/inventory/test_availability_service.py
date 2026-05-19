"""Tests for M05 availability_service (step 4)."""

from decimal import Decimal

import pytest
from django.utils import timezone

from apps.inventory.models import ReservationRefType, ReservationStatus
from apps.inventory.services import availability_service

pytestmark = pytest.mark.django_db


def test_available_returns_zero_for_missing_stock(product, branch):
    assert availability_service.available(product, branch) == Decimal("0")


def test_reserve_and_release_increments_and_decrements_qty_reserved(product, branch):
    # Create stock row
    from apps.inventory.models import Stock

    stock = Stock.objects.create(product=product, branch=branch, qty_on_hand=Decimal("10"))
    # Reserve 3 units
    reservation = availability_service.reserve(
        product, branch, Decimal("3"), ReservationRefType.ORDER, "SO-1"
    )
    stock.refresh_from_db()
    assert stock.qty_reserved == Decimal("3")
    # Release
    availability_service.release(reservation)
    stock.refresh_from_db()
    assert stock.qty_reserved == Decimal("0")
    reservation.refresh_from_db()
    assert reservation.status == ReservationStatus.RELEASED


def test_reserve_and_consume(product, branch):
    from apps.inventory.models import Stock

    stock = Stock.objects.create(product=product, branch=branch, qty_on_hand=Decimal("5"))
    reservation = availability_service.reserve(
        product, branch, Decimal("2"), ReservationRefType.ORDER, "SO-2"
    )
    stock.refresh_from_db()
    assert stock.qty_reserved == Decimal("2")
    availability_service.consume(reservation)
    stock.refresh_from_db()
    assert stock.qty_reserved == Decimal("0")
    reservation.refresh_from_db()
    assert reservation.status == ReservationStatus.CONSUMED


def test_reserve_blocks_if_insufficient_stock(product, branch):
    from apps.inventory.models import Stock

    Stock.objects.create(product=product, branch=branch, qty_on_hand=Decimal("1"))
    with pytest.raises(Exception) as excinfo:
        availability_service.reserve(
            product, branch, Decimal("2"), ReservationRefType.ORDER, "SO-3"
        )
    assert "Insufficient" in str(excinfo.value)


def test_expire_stale_reservations(product, branch):
    from apps.inventory.models import Stock

    stock = Stock.objects.create(product=product, branch=branch, qty_on_hand=Decimal("10"))
    # Create two reservations, one expired
    now = timezone.now()
    r1 = availability_service.reserve(
        product,
        branch,
        Decimal("2"),
        ReservationRefType.ORDER,
        "SO-4",
        expires_at=now - timezone.timedelta(days=1),
    )
    r2 = availability_service.reserve(
        product,
        branch,
        Decimal("2"),
        ReservationRefType.ORDER,
        "SO-5",
        expires_at=now + timezone.timedelta(days=1),
    )
    count = availability_service.expire_stale_reservations()
    assert count == 1
    r1.refresh_from_db()
    r2.refresh_from_db()
    assert r1.status == ReservationStatus.EXPIRED
    assert r2.status == ReservationStatus.ACTIVE
    stock.refresh_from_db()
    assert stock.qty_reserved == Decimal("2")
