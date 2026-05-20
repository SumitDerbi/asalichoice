"""Signal handlers for M11 Sales.

The cross-module signals (``sale_posted`` and ``sale_cancelled``) live
here as in-process :class:`django.dispatch.Signal` instances. Receivers
in other modules (M08 invoice, M09 wallet, M10 referral, M12 finance,
M17 notifications) connect at their own ``AppConfig.ready`` time.

Importing this module from :meth:`SalesConfig.ready` is sufficient to
publish the signal symbols.
"""

from __future__ import annotations

from django.dispatch import Signal

# ``sender`` is the :class:`apps.sales.models.Sale` class; ``sale`` is the
# instance. We deliberately keep payload minimal — receivers can re-fetch
# items, payments, etc. via ORM as needed.
sale_posted = Signal()
sale_cancelled = Signal()

__all__ = ["sale_cancelled", "sale_posted"]
