"""AsliChoice backend config package.

Install PyMySQL as the MySQLdb driver so Django's ``django.db.backends.mysql``
backend works without the mysqlclient C extension (which fails to build on
Windows without the MySQL Connector/C dev headers). This shim is a no-op when
PyMySQL is not installed (e.g. SQLite-only dev environments).
"""

try:  # pragma: no cover - import-time shim
    import pymysql

    pymysql.install_as_MySQLdb()
except ImportError:  # PyMySQL not installed; SQLite or mysqlclient in use.
    pass
