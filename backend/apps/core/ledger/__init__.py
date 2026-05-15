"""
Ledger primitives.

Per ``_conventions.md`` everything that touches money or stock is
ledger-driven: a write produces an append-only ledger row with the
balance before and after. Concrete subclasses live next to the
domain that owns them (inventory, wallet, vendor, customer, finance).
"""

from __future__ import annotations

from .models import LedgerEntry

__all__ = ["LedgerEntry"]
