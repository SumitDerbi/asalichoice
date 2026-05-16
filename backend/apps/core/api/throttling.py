"""
Shared throttle classes.

Scope names ``burst-anon``, ``burst-user``, ``login``, and ``otp`` map
to ``REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']`` (see
``config/settings/base.py``). Per ``plans/_meta.yaml`` § security.rate_limits
the defaults are:

- anon:  60 / min  (env: ``THROTTLE_ANON_RATE``)
- user:  120 / min (env: ``THROTTLE_USER_RATE``)
- login: 5  / min  (env: ``THROTTLE_LOGIN_RATE``, configured in 006)
- otp:   5  / 15min per identifier (lands fully in M02)
"""

from __future__ import annotations

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class BurstAnonThrottle(AnonRateThrottle):
    """Per-IP burst throttle for anonymous traffic."""

    scope = "burst-anon"


class BurstUserThrottle(UserRateThrottle):
    """Per-user burst throttle for authenticated traffic."""

    scope = "burst-user"


class OTPRateThrottle(AnonRateThrottle):
    """Throttle OTP issuance per identifier (used by M02).

    The scope is registered here so OpenAPI / settings discover it
    early. The full implementation (per-identifier bucket instead of
    per-IP) lands with the OTP serializer in M02.
    """

    scope = "otp"
