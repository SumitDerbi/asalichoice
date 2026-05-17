"""
Project-wide system checks.

``W001`` flags any concrete project-local model that does not inherit
from :class:`apps.core.models.BaseModel`. Lookup tables and other
intentional exceptions can be added to :data:`BASE_MODEL_EXEMPTIONS`.

The check is registered from :meth:`apps.core.apps.CoreConfig.ready`.
"""

from __future__ import annotations

from django.apps import apps
from django.core.checks import Warning as DjangoWarning

# Model labels (``app_label.ModelName``) explicitly opted out of BaseModel.
# Add an entry with a short rationale comment whenever you exempt a model.
BASE_MODEL_EXEMPTIONS: set[str] = {
    # Audit log is append-only and must not soft-delete itself.
    "core.AuditLog",
    # Vendor ledger entries are immutable financial postings (LedgerEntry).
    "purchase.VendorLedger",
}


def check_models_inherit_base_model(app_configs=None, **kwargs):
    """Warn about project-local models missing the :class:`BaseModel` mixins."""

    from .models import BaseModel  # local import to avoid app-loading cycles

    warnings: list[DjangoWarning] = []
    iter_configs = app_configs if app_configs is not None else apps.get_app_configs()
    for app_config in iter_configs:
        # Only project-local apps (those under apps/<name>/).
        if not app_config.name.startswith("apps."):
            continue
        for model in app_config.get_models():
            if model._meta.abstract or model._meta.proxy:
                continue
            if model._meta.label in BASE_MODEL_EXEMPTIONS:
                continue
            if issubclass(model, BaseModel):
                continue
            warnings.append(
                DjangoWarning(
                    f"{model._meta.label} does not inherit apps.core.models.BaseModel.",
                    hint=(
                        "Inherit BaseModel for timestamps + soft-delete + audit fields, "
                        "or add the label to apps.core.checks.BASE_MODEL_EXEMPTIONS with "
                        "a comment explaining why."
                    ),
                    obj=model,
                    id="asalichoice.W001",
                ),
            )
    return warnings
