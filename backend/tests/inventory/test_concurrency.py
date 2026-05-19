"""M05 concurrency tests (Item 10).

These exercise the row-level lock that ``availability_service.reserve``
takes through ``Stock.all_objects.select_for_update()``. SQLite does
not implement ``SELECT … FOR UPDATE`` (Django logs a NOTE and skips
the clause) and serialises writes at the database level, so the
property cannot be verified there. We therefore ``skipif`` on the
SQLite test backend and gate the real assertion on MySQL — the
production engine — where row locks are honoured.
"""

from __future__ import annotations

import threading
from decimal import Decimal

import pytest
from django.db import close_old_connections, connection

from apps.inventory.exceptions import InsufficientStock
from apps.inventory.models import Reservation, ReservationRefType, ReservationStatus, Stock
from apps.inventory.services import availability_service


@pytest.mark.skipif(
    connection.vendor == "sqlite",
    reason="SELECT FOR UPDATE is a no-op on SQLite; concurrency lock requires MySQL.",
)
@pytest.mark.django_db(transaction=True)
def test_reserve_is_safe_under_concurrent_threads(product, branch):
    """Two threads race for the last unit; exactly one wins."""

    Stock.objects.create(product=product, branch=branch, qty_on_hand=Decimal("1"))

    barrier = threading.Barrier(2)
    results: list[tuple[str, Exception | None]] = []
    lock = threading.Lock()

    def worker(tag: str) -> None:
        barrier.wait()
        try:
            availability_service.reserve(
                product,
                branch,
                Decimal("1"),
                ReservationRefType.ORDER,
                f"SO-RACE-{tag}",
            )
            with lock:
                results.append((tag, None))
        except InsufficientStock as exc:  # pragma: no cover - branch depends on race
            with lock:
                results.append((tag, exc))
        finally:
            close_old_connections()

    t1 = threading.Thread(target=worker, args=("A",))
    t2 = threading.Thread(target=worker, args=("B",))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    # Exactly one winner.
    winners = [r for r in results if r[1] is None]
    losers = [r for r in results if isinstance(r[1], InsufficientStock)]
    assert len(winners) == 1, results
    assert len(losers) == 1, results

    # Stock invariants hold.
    stock = Stock.objects.get(product=product, branch=branch)
    assert stock.qty_on_hand == Decimal("1")
    assert stock.qty_reserved == Decimal("1")

    # Exactly one ACTIVE reservation.
    assert (
        Reservation.objects.filter(
            product=product, branch=branch, status=ReservationStatus.ACTIVE
        ).count()
        == 1
    )
