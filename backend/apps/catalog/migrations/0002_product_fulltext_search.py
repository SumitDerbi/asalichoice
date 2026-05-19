"""Add a MySQL FULLTEXT index on ``catalog_product (name, sku, code)``.

Only applied on the MySQL backend. SQLite (dev) is a no-op — the
``ProductViewSet`` falls back to ``icontains`` filters there.
"""

from __future__ import annotations

from django.db import migrations


CREATE_SQL = (
    "ALTER TABLE catalog_product "
    "ADD FULLTEXT INDEX catalog_product_name_sku_code_fts (name, sku, code)"
)
DROP_SQL = "ALTER TABLE catalog_product DROP INDEX catalog_product_name_sku_code_fts"


def add_fulltext(apps, schema_editor):  # noqa: ARG001
    if schema_editor.connection.vendor != "mysql":
        return
    schema_editor.execute(CREATE_SQL)


def drop_fulltext(apps, schema_editor):  # noqa: ARG001
    if schema_editor.connection.vendor != "mysql":
        return
    schema_editor.execute(DROP_SQL)


class Migration(migrations.Migration):

    # MySQL can't roll back DDL, so we must disable Django's transactional
    # migration wrapper for this RunPython that issues ALTER TABLE.
    atomic = False

    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(add_fulltext, drop_fulltext),
    ]
