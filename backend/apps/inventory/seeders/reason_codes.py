"""Reason-code seeder for M05 Inventory.

The reason-code catalog itself lives in
:mod:`apps.inventory.reason_codes` (static Python data, shared with the
offline POS bundle and admin-ui). This module exposes a small
``seed`` helper that is idempotent and safe to invoke from
``manage.py`` commands, tests, or the global seeder.
"""

from __future__ import annotations

import logging

from apps.inventory.reason_codes import INVENTORY_REASON_CODES

logger = logging.getLogger(__name__)


def seed() -> dict[str, int]:
    """No-op seed: the catalog is code-resident.

    Returns a small summary dict so the management command can print
    something useful. If a future iteration moves the codes into a DB
    table (``InventoryReasonCode``), the upsert logic lands here.
    """

    count = len(INVENTORY_REASON_CODES)
    logger.info("inventory reason codes resident: %s", count)
    return {"reason_codes": count}


__all__ = ["seed"]
