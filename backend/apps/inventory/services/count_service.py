"""M05 Inventory — physical count service (step 6).

OPEN → COUNTED → POSTED.

* :func:`mark_counted` snapshots :attr:`PhysicalCountItem.qty_expected`
  from the current :class:`Stock` rows. Tellers update ``qty_counted`` on
  the items, then call :func:`post`.
* :func:`post` computes ``diff = qty_counted - qty_expected`` per line
  and writes one signed ledger entry per non-zero diff (ref_type=COUNT,
  reason_code=COUNT_DIFF).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from ..exceptions import InvalidDocumentState
from ..models import InventoryRefType, PhysicalCount, PhysicalCountStatus, Stock
from . import ledger_service


def _expected_for(item, branch_id: int) -> Decimal:
    qs = Stock.objects.filter(
        branch_id=branch_id,
        product_id=item.product_id,
        variant_id=item.variant_id,
        warehouse_id=None,
    )
    row = qs.first()
    return Decimal(str(row.qty_on_hand)) if row else Decimal("0")


@transaction.atomic
def mark_counted(count: PhysicalCount) -> PhysicalCount:
    locked = PhysicalCount.all_objects.select_for_update().get(pk=count.pk)
    if locked.status != PhysicalCountStatus.OPEN:
        raise InvalidDocumentState()
    for it in locked.items.all():
        it.qty_expected = _expected_for(it, locked.branch_id)
        it.save(update_fields=["qty_expected", "updated_at"])
    locked.status = PhysicalCountStatus.COUNTED
    locked.save(update_fields=["status", "updated_at"])
    return locked


@transaction.atomic
def post(count: PhysicalCount, *, actor=None) -> PhysicalCount:
    locked = PhysicalCount.all_objects.select_for_update().get(pk=count.pk)
    if locked.status != PhysicalCountStatus.COUNTED:
        raise InvalidDocumentState()

    items: list[dict[str, Any]] = []
    for it in locked.items.all():
        diff = Decimal(str(it.qty_counted)) - Decimal(str(it.qty_expected))
        if diff == 0:
            continue
        line: dict[str, Any] = {"qty_change": diff}
        if it.product_id is not None:
            line["product_id"] = it.product_id
        else:
            line["variant_id"] = it.variant_id
        items.append(line)

    if items:
        ledger_service.post(
            ref_type=InventoryRefType.COUNT,
            ref_id=locked.pk,
            items=items,
            branch=locked.branch_id,
            actor=actor,
            reason_code="COUNT_DIFF",
            remarks=f"COUNT {locked.count_no} posted",
        )

    locked.status = PhysicalCountStatus.POSTED
    locked.posted_at = timezone.now()
    locked.save(update_fields=["status", "posted_at", "updated_at"])
    return locked


__all__ = ["mark_counted", "post"]
