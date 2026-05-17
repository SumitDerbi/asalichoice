"""Public seam exposed by the catalog module.

Other apps must import catalog primitives from here, not from
``apps.catalog.models`` or ``apps.catalog.services`` directly.
See ADR-002.
"""

from __future__ import annotations

from .services.pricing_service import EffectivePrice, bulk_lookup, get_effective_price, set_price

__all__ = [
    "EffectivePrice",
    "bulk_lookup",
    "get_effective_price",
    "set_price",
]
