"""M05 Inventory — Celery-ready task wrappers.

Celery is not bootstrapped in the platform yet (M01 leaves the broker
config for M11/operational hardening). Tasks here are exposed as plain
callables so they can be promoted to ``@shared_task`` without changing
their call sites once Celery lands.
"""

from __future__ import annotations

import logging

from .services import expiry_service

logger = logging.getLogger(__name__)


def mark_expired_batches_task() -> int:
    """Daily-cron task: flip active-but-expired batches to ``EXPIRED``."""

    count = expiry_service.mark_expired_batches()
    logger.info("mark_expired_batches_task: %s batch(es) expired", count)
    return count


__all__ = ["mark_expired_batches_task"]
