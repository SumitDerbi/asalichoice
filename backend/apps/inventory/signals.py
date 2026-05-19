"""Signal handlers for M05 Inventory.

Wiring (cache-bust on ledger write, audit hooks, etc.) lands alongside
the services. Importing this module from :meth:`InventoryConfig.ready`
is sufficient to register them.
"""

from __future__ import annotations
