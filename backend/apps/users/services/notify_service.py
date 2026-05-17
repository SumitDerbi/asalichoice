"""Notification adapter — phase-1 stub.

The real SMS / Email / WhatsApp providers land in M17. Until then we
write every outbound OTP to:

* the application logger (INFO level), and
* the module-level :data:`OTP_SINK` list when ``DEBUG`` is True, so
  tests + the dev admin-UI can read back the most recent code without
  scraping logs.

The signature mirrors what the real M17 service will expose, so
swapping the implementation is a no-touch change for callers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal

from django.conf import settings

logger = logging.getLogger(__name__)

ChannelLiteral = Literal["SMS", "EMAIL", "WHATSAPP"]


@dataclass
class _SinkEntry:
    channel: ChannelLiteral
    identifier: str
    code: str
    purpose: str


#: In-process ring buffer of recent OTP codes (DEBUG-only).
OTP_SINK: list[_SinkEntry] = []

#: Max entries kept in :data:`OTP_SINK` before we drop the oldest.
_SINK_CAPACITY = 50


def send_otp(channel: ChannelLiteral, identifier: str, code: str, purpose: str = "LOGIN") -> bool:
    """Send (or pretend to send) an OTP. Returns True on success.

    The phase-1 implementation always succeeds for SMS / EMAIL and
    deliberately fails for WHATSAPP so the smart-fallback path is
    exercisable end-to-end without a real provider. Override via
    ``settings.OTP_FORCE_FAIL_CHANNELS = {"SMS", ...}`` to drive
    failure scenarios in tests.
    """

    force_fail = getattr(settings, "OTP_FORCE_FAIL_CHANNELS", set()) or set()
    if channel in force_fail:
        logger.warning("OTP send forced-fail on channel=%s identifier=%s", channel, identifier)
        return False
    if channel == "WHATSAPP":
        # No provider wired up yet — smart fallback will pick another.
        logger.warning("OTP channel=WHATSAPP not configured; smart fallback will retry")
        return False

    logger.info(
        "OTP send channel=%s identifier=%s purpose=%s code=%s",
        channel,
        identifier,
        purpose,
        code if settings.DEBUG else "***",
    )
    if settings.DEBUG or getattr(settings, "OTP_SINK_ALWAYS_ON", False):
        OTP_SINK.append(
            _SinkEntry(channel=channel, identifier=identifier, code=code, purpose=purpose)
        )
        if len(OTP_SINK) > _SINK_CAPACITY:
            del OTP_SINK[: len(OTP_SINK) - _SINK_CAPACITY]
    return True
