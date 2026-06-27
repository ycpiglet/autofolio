"""Config-gated Postgres backend adapter for the database seam.

This module is imported **only** when ``DATABASE_URL`` is a Postgres URL; the
default (unset/empty) SQLite path never reaches here, so the existing SQLite
behaviour is untouched.

The adapter mimics the small slice of the ``sqlite3.Connection`` API that
``app/database/repositories.py`` (and a few service modules) actually use:

* context manager — commit on a clean exit, rollback on error, then close;
* ``conn.execute(sql, params)`` returning a cursor;
* cursor ``.fetchone()`` / ``.fetchall()`` / ``.rowcount`` / ``.lastrowid``;
* rows convertible via ``dict(row)`` and subscriptable (``row["col"]``) — psycopg
  ``dict_row`` factory already yields plain ``dict`` rows, so no wrapper needed;
* ``conn.executescript(script)`` for the lazy-DDL service modules.

Dialect gaps handled here so the SQL strings in ``repositories.py`` need not
change:

* **Placeholders** — SQLite ``?`` is translated to psycopg ``%s`` (string-literal
  aware), and literal ``%`` is doubled to ``%%`` when params are bound.
* **lastrowid** — psycopg has no ``lastrowid``. For an ``INSERT`` that lacks a
  ``RETURNING`` clause the adapter appends ``RETURNING id`` and exposes the new
  primary key as ``cursor.lastrowid`` (every Postgres trading table in
  ``supabase/migrations`` uses an ``id`` PK). Callers that do not read
  ``lastrowid`` are unaffected.

``psycopg`` is imported lazily (only inside :func:`connect`) so this module —
and its pure translation helpers — stay importable and unit-testable without the
driver, and the SQLite path never pulls psycopg into the process.
"""

from __future__ import annotations

import re
from typing import Any, Sequence


def is_postgres_url(url: str | None) -> bool:
    """True when *url* selects the Postgres backend (``postgres://``/``postgresql://``)."""
    if not url:
        return False
    lowered = url.strip().lower()
    return lowered.startswith("postgres://") or lowered.startswith("postgresql://")


def translate_placeholders(sql: str, has_params: bool) -> str:
    """Translate SQLite ``?`` placeholders to psycopg ``%s``.

    String-literal aware: ``?`` inside a single-quoted SQL string literal is left
    untouched (and SQLite's ``''`` escape is respected). When *has_params* is
    True, literal ``%`` characters are doubled to ``%%`` everywhere (psycopg
    treats ``%`` as the start of a placeholder during client-side binding).
    """
    out: list[str] = []
    in_string = False
    i = 0
    n = len(sql)
    while i < n:
        char = sql[i]
        if in_string:
            if char == "'":
                if i + 1 < n and sql[i + 1] == "'":  # escaped '' inside literal
                    out.append("''")
                    i += 2
                    continue
                in_string = False
                out.append(char)
            elif char == "%" and has_params:
                out.append("%%")
            else:
                out.append(char)
        else:
            if char == "'":
                in_string = True
                out.append(char)
            elif char == "?":
                out.append("%s")
            elif char == "%" and has_params:
                out.append("%%")
            else:
                out.append(char)
        i += 1
    return "".join(out)


_INSERT_RE = re.compile(r"^\s*INSERT\b", re.IGNORECASE)
_RETURNING_RE = re.compile(r"\bRETURNING\b", re.IGNORECASE)


def needs_returning_id(sql: str) -> bool:
    """True for an ``INSERT`` that has no ``RETURNING`` clause yet.

    Such statements get ``RETURNING id`` appended so the adapter can surface the
    new primary key as ``cursor.lastrowid``.
    """
    return bool(_INSERT_RE.match(sql)) and not _RETURNING_RE.search(sql)


def append_returning_id(sql: str) -> str:
    """Append ``RETURNING id`` to *sql* (after stripping a trailing ``;``)."""
    return sql.rstrip().rstrip(";").rstrip() + " RETURNING id"


class PgCursor:
    """Thin wrapper over a psycopg cursor exposing the sqlite3 cursor surface."""

    def __init__(self, cursor: Any, lastrowid: int | None = None) -> None:
        self._cursor = cursor
        self.lastrowid = lastrowid

    @property
    def rowcount(self) -> int:
        return self._cursor.rowcount

    def fetchone(self) -> Any:
        return self._cursor.fetchone()

    def fetchall(self) -> list[Any]:
        return self._cursor.fetchall()

    def fetchmany(self, size: int | None = None) -> list[Any]:
        if size is None:
            return self._cursor.fetchmany()
        return self._cursor.fetchmany(size)

    def __iter__(self):
        return iter(self._cursor)

    def close(self) -> None:
        self._cursor.close()


class PgConnection:
    """Adapter over a psycopg connection mimicking ``sqlite3.Connection``.

    The context-manager protocol matches sqlite3's: ``__enter__`` returns the
    connection and ``__exit__`` commits on a clean exit / rolls back on error.
    Unlike sqlite3 it also *closes* the underlying connection on exit, because a
    fresh psycopg connection is opened per ``get_connection`` call and must not
    leak (this does not change any observable repository behaviour — the
    ``with`` block is the unit of work either way).
    """

    def __init__(self, connection: Any) -> None:
        self._connection = connection

    def execute(self, sql: str, params: Sequence[Any] | None = None) -> PgCursor:
        has_params = bool(params)
        statement = translate_placeholders(sql, has_params)
        append_id = needs_returning_id(statement)
        if append_id:
            statement = append_returning_id(statement)

        cursor = self._connection.cursor()
        cursor.execute(statement, params if has_params else None)

        lastrowid: int | None = None
        if append_id and cursor.description is not None:
            row = cursor.fetchone()
            if row is not None:
                lastrowid = row["id"] if isinstance(row, dict) else row[0]
        return PgCursor(cursor, lastrowid)

    def executescript(self, script: str) -> "PgConnection":
        """Run a multi-statement DDL script (sqlite3 parity, no params).

        NOTE: callers pass SQLite-dialect DDL. Genuine Postgres deployments rely
        on the pre-applied ``supabase/migrations/*.sql`` schema instead; this
        method exists for API completeness.
        """
        with self._connection.cursor() as cursor:
            cursor.execute(script)
        return self

    def cursor(self) -> PgCursor:
        return PgCursor(self._connection.cursor())

    def commit(self) -> None:
        self._connection.commit()

    def rollback(self) -> None:
        self._connection.rollback()

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "PgConnection":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        try:
            if exc_type is None:
                self._connection.commit()
            else:
                self._connection.rollback()
        finally:
            self._connection.close()
        return False  # never suppress exceptions (matches sqlite3.Connection)


def connect(conninfo: str) -> PgConnection:
    """Open a psycopg connection (``dict_row`` factory) wrapped as :class:`PgConnection`."""
    import psycopg
    from psycopg.rows import dict_row

    connection = psycopg.connect(conninfo, row_factory=dict_row)
    return PgConnection(connection)
