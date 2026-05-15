"""
Phusion Passenger WSGI entrypoint for the AsliChoice backend.

This is a stub — full cPanel wiring (interpreter path, virtualenv activation,
``~/deploy_config/<env>/`` env loading) is configured in plan
``phase-0-foundation/012-deploy-sh.md``.

Until then, this file is enough for Passenger to import the Django WSGI
application using the system / virtualenv interpreter selected in cPanel.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure the backend root is on sys.path so that ``config`` is importable
# when Passenger boots this module from an arbitrary CWD.
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

from config.wsgi import application  # noqa: E402,F401
