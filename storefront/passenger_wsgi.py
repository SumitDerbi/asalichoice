"""
Phusion Passenger entry point for the AsliChoice storefront on cPanel.

This is a *stub* — full cPanel wiring (PYTHONPATH, venv discovery, env loading
from ``~/deploy_config/<env>/<env>.env``) is configured in plan
``plans/phase-0-foundation/012-deploy-sh.md``. The current file makes the
storefront runnable under Passenger using production settings once the venv
and env are in place.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Make the project root importable.
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
