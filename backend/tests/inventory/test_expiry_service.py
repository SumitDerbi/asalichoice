"""Tests for ``apps.inventory.services.expiry_service`` (M05 Item 7)."""

from __future__ import annotations

import datetime as _dt
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.inventory.models import Batch, BatchStatus
from apps.inventory.services.expiry_service import mark_expired_batches
from apps.inventory.tasks import mark_expired_batches_task

pytestmark = pytest.mark.django_db


def _make_batch(product, branch, *, expiry, status=BatchStatus.ACTIVE, batch_no="B1"):
    return Batch.objects.create(
        product=product,
        branch=branch,
        batch_no=batch_no,
        expiry_date=expiry,
        cost_price=Decimal("10.0000"),
        qty_received=Decimal("5.000"),
        qty_remaining=Decimal("5.000"),
        status=status,
    )


def test_marks_active_past_expiry_as_expired(product, branch):
    yesterday = timezone.localdate() - _dt.timedelta(days=1)
    b = _make_batch(product, branch, expiry=yesterday, batch_no="OLD")

    count = mark_expired_batches()

    b.refresh_from_db()
    assert count == 1
    assert b.status == BatchStatus.EXPIRED


def test_leaves_future_expiry_alone(product, branch):
    tomorrow = timezone.localdate() + _dt.timedelta(days=1)
    b = _make_batch(product, branch, expiry=tomorrow, batch_no="FUT")

    count = mark_expired_batches()

    b.refresh_from_db()
    assert count == 0
    assert b.status == BatchStatus.ACTIVE


def test_leaves_today_expiry_alone(product, branch):
    today = timezone.localdate()
    b = _make_batch(product, branch, expiry=today, batch_no="TDY")

    count = mark_expired_batches()

    b.refresh_from_db()
    assert count == 0
    assert b.status == BatchStatus.ACTIVE


def test_skips_consumed_batches(product, branch):
    yesterday = timezone.localdate() - _dt.timedelta(days=1)
    b = _make_batch(product, branch, expiry=yesterday, status=BatchStatus.CONSUMED, batch_no="CON")

    count = mark_expired_batches()

    b.refresh_from_db()
    assert count == 0
    assert b.status == BatchStatus.CONSUMED


def test_skips_batches_without_expiry(product, branch):
    b = _make_batch(product, branch, expiry=None, batch_no="NOEXP")

    count = mark_expired_batches()

    b.refresh_from_db()
    assert count == 0
    assert b.status == BatchStatus.ACTIVE


def test_returns_zero_when_nothing_to_do():
    assert mark_expired_batches() == 0


def test_as_of_override(product, branch):
    expiry = timezone.localdate() - _dt.timedelta(days=10)
    b = _make_batch(product, branch, expiry=expiry, batch_no="ASOF")

    # Cutoff *before* the expiry → no-op.
    assert mark_expired_batches(as_of=expiry) == 0
    b.refresh_from_db()
    assert b.status == BatchStatus.ACTIVE

    # Cutoff *after* the expiry → expires.
    assert mark_expired_batches(as_of=expiry + _dt.timedelta(days=1)) == 1
    b.refresh_from_db()
    assert b.status == BatchStatus.EXPIRED


def test_task_wrapper_invokes_service(product, branch):
    yesterday = timezone.localdate() - _dt.timedelta(days=1)
    _make_batch(product, branch, expiry=yesterday, batch_no="TASK")

    assert mark_expired_batches_task() == 1
