"""M05 reason-code catalog.

Static registry mapped by code → (label, description, applies_to).
Used by the reason-code seeder and validated by adjustment / wastage /
count services. Kept in code (not a DB lookup) because the values are
shared with the offline POS bundle and the admin-ui dropdowns.
"""

from __future__ import annotations

# applies_to: one or more of {"ADJUSTMENT", "WASTAGE", "COUNT"}
INVENTORY_REASON_CODES: tuple[tuple[str, str, str, frozenset[str]], ...] = (
    ("DAMAGE", "Damage", "Goods damaged in storage or handling", frozenset({"WASTAGE"})),
    ("THEFT", "Theft", "Theft / shrinkage", frozenset({"WASTAGE", "ADJUSTMENT"})),
    ("EXPIRY", "Expiry", "Expired stock written off", frozenset({"WASTAGE"})),
    (
        "COUNT_DIFF",
        "Count difference",
        "Physical count reconciliation difference",
        frozenset({"COUNT", "ADJUSTMENT"}),
    ),
    (
        "MANUAL",
        "Manual adjustment",
        "Manual correction by store manager",
        frozenset({"ADJUSTMENT"}),
    ),
)


def reason_codes_for(doc_type: str) -> set[str]:
    """Return the set of valid reason codes for the given document type."""

    doc_type = doc_type.upper()
    return {code for code, _, _, applies in INVENTORY_REASON_CODES if doc_type in applies}


def is_valid_reason_code(code: str, doc_type: str) -> bool:
    return code in reason_codes_for(doc_type)


__all__ = [
    "INVENTORY_REASON_CODES",
    "reason_codes_for",
    "is_valid_reason_code",
]
