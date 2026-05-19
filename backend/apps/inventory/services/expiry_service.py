"""M05 Inventory — expiry batch service (step 7).

Sweeps :class:`apps.inventory.models.Batch` rows whose ``expiry_date``
has elapsed and whose ``status`` is still ``ACTIVE``, flipping them to
``EXPIRED``. Batches that are already ``CONSUMED`` are left alone (their
``qty_remaining`` is already zero).

The function is invoked by:

* ``python manage.py mark_expired_batches`` (operational tool)
* a scheduled Celery beat task when Celery lands in the platform

It does **not** write any ``InventoryLedger`` rows — expired stock is
written off via the wastage flow (Item 6) which posts ``WASTAGE`` with
``reason_code=EXPIRY``. Marking the batch ``EXPIRED`` only prevents
further allocations (FIFO pickers and availability checks skip non-ACTIVE
batches).
"""

from __future__ import annotations

import datetime as _dt
import logging

from django.db import transaction
from django.utils import timezone

from ..models import Batch, BatchStatus

logger = logging.getLogger(__name__)


@transaction.atomic
def mark_expired_batches(*, as_of: _dt.date | None = None) -> int:
    """Mark all active batches past their ``expiry_date`` as ``EXPIRED``.

    Parameters
    ----------
    as_of:
        Cutoff date (exclusive). Defaults to ``timezone.localdate()`` so
        a batch expiring *today* is **not** marked yet — only those with
        ``expiry_date < today``.

    Returns
    -------
    int
        Number of batches transitioned to ``EXPIRED``.
    """

    if as_of is None:
        as_of = timezone.localdate()

    qs = Batch.all_objects.select_for_update().filter(
        status=BatchStatus.ACTIVE,
        expiry_date__lt=as_of,
        expiry_date__isnull=False,
    )
    count = qs.update(status=BatchStatus.EXPIRED)
    if count:
        logger.info("expiry_service: marked %s batches as EXPIRED (as_of=%s)", count, as_of)
    return count


__all__ = ["mark_expired_batches"]
