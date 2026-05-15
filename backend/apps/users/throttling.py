"""Throttle classes for the auth endpoints."""

from __future__ import annotations

from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """Cap unauthenticated login attempts to 5/min per source IP.

    Configured in ``REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]`` under the
    ``login`` scope. M02 will add account-level lockouts on top of this.
    """

    scope = "login"
