"""Unit tests for the config-gated Postgres adapter (app/database/pg_db.py).

These cover the pure dialect-translation logic (placeholder ?→%s, % doubling,
RETURNING-id detection) and the connection/cursor adapter wiring via a fake
psycopg-shaped driver. A LIVE Postgres round-trip is intentionally NOT run here
(no local Postgres; the staging DB must not be contacted) — see the report.
"""
from __future__ import annotations

import pytest

from app.database import pg_db
from app.database.pg_db import (
    PgConnection,
    append_returning_id,
    is_postgres_url,
    needs_returning_id,
    translate_placeholders,
)


# --------------------------------------------------------------------------- #
# is_postgres_url
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "url,expected",
    [
        ("postgres://u:p@h:5432/db", True),
        ("postgresql://u:p@h:5432/db", True),
        ("POSTGRESQL://H/db", True),
        ("  postgres://h/db  ", True),
        ("", False),
        (None, False),
        ("sqlite:///x.db", False),
        ("trading_bot.db", False),
        ("mysql://h/db", False),
    ],
)
def test_is_postgres_url(url, expected):
    assert is_postgres_url(url) is expected


# --------------------------------------------------------------------------- #
# translate_placeholders
# --------------------------------------------------------------------------- #
def test_translate_basic_single_placeholder():
    assert translate_placeholders("SELECT * FROM t WHERE id = ?", True) == (
        "SELECT * FROM t WHERE id = %s"
    )


def test_translate_multiple_placeholders():
    assert translate_placeholders("INSERT INTO t(a,b,c) VALUES(?,?,?)", True) == (
        "INSERT INTO t(a,b,c) VALUES(%s,%s,%s)"
    )


def test_translate_leaves_question_mark_inside_string_literal():
    sql = "SELECT * FROM t WHERE label = 'a?b' AND id = ?"
    assert translate_placeholders(sql, True) == (
        "SELECT * FROM t WHERE label = 'a?b' AND id = %s"
    )


def test_translate_doubles_percent_only_when_params_present():
    sql = "SELECT * FROM t WHERE c LIKE '%x%'"
    assert translate_placeholders(sql, True) == "SELECT * FROM t WHERE c LIKE '%%x%%'"
    # No params bound → psycopg does no interpolation → % stays literal.
    assert translate_placeholders(sql, False) == sql


def test_translate_respects_escaped_single_quote():
    sql = "SELECT * FROM t WHERE c = 'O''Brien?' AND id = ?"
    assert translate_placeholders(sql, True) == (
        "SELECT * FROM t WHERE c = 'O''Brien?' AND id = %s"
    )


def test_translate_no_params_no_placeholders_unchanged():
    sql = "SELECT 1"
    assert translate_placeholders(sql, False) == sql


# --------------------------------------------------------------------------- #
# needs_returning_id / append_returning_id
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "sql,expected",
    [
        ("INSERT INTO t(a) VALUES(?)", True),
        ("  insert into t(a) values(?)", True),
        ("INSERT INTO t(a) VALUES(?) ON CONFLICT(a) DO UPDATE SET a=excluded.a", True),
        ("INSERT INTO t(a) VALUES(?) RETURNING id", False),
        ("SELECT * FROM t", False),
        ("UPDATE t SET a=? WHERE id=?", False),
        ("DELETE FROM t WHERE id=?", False),
    ],
)
def test_needs_returning_id(sql, expected):
    assert needs_returning_id(sql) is expected


def test_append_returning_id_strips_trailing_semicolon():
    assert append_returning_id("INSERT INTO t(a) VALUES(%s);") == (
        "INSERT INTO t(a) VALUES(%s) RETURNING id"
    )
    assert append_returning_id("INSERT INTO t(a) VALUES(%s)") == (
        "INSERT INTO t(a) VALUES(%s) RETURNING id"
    )


# --------------------------------------------------------------------------- #
# Fake psycopg-shaped driver to exercise the adapter wiring without a live DB.
# --------------------------------------------------------------------------- #
class _FakeCursor:
    def __init__(self, conn: "_FakeConnection") -> None:
        self._conn = conn
        self.description = None
        self.rowcount = -1
        self._result: list = []

    def execute(self, sql, params=None):
        self._conn.executed.append((sql, params))
        upper = sql.strip().upper()
        if (
            upper.startswith("SAVEPOINT")
            or upper.startswith("RELEASE SAVEPOINT")
            or upper.startswith("ROLLBACK TO")
        ):
            # Transaction-control statements for the lastval SAVEPOINT probe.
            self.description = None
            self._result = []
            self.rowcount = 0
        elif "SELECT LASTVAL()" in upper:
            # Simulate SELECT lastval(): raise when no sequence has been used
            # in this session (seq == 0), otherwise return the current value.
            if self._conn.seq == 0:
                raise Exception("lastval is not yet defined in this session")
            self.description = [("lastval",)]
            self._result = [{"lastval": self._conn.seq}]
            self.rowcount = 1
        elif upper.startswith("INSERT"):
            # Advance the session sequence counter only for tables that have a
            # serial PK (has_sequence=True, the default).
            if self._conn.has_sequence:
                self._conn.seq += 1
            self.description = None
            self._result = []
            self.rowcount = 1
        elif upper.startswith("SELECT"):
            self.description = [("col",)]
            self._result = [dict(r) for r in self._conn.select_rows]
            self.rowcount = len(self._result)
        elif upper.startswith("UPDATE"):
            self.description = None
            self._result = []
            self.rowcount = self._conn.update_rowcount
        else:
            self.description = None
            self._result = []
            self.rowcount = 0

    def fetchone(self):
        return self._result.pop(0) if self._result else None

    def fetchall(self):
        rows, self._result = self._result, []
        return rows

    def fetchmany(self, size=None):
        n = size if size is not None else 1
        out, self._result = self._result[:n], self._result[n:]
        return out

    def __iter__(self):
        return iter(self._result)

    def close(self):
        self._conn.closed_cursors += 1

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


class _FakeConnection:
    def __init__(self) -> None:
        self.executed: list = []
        self.seq = 0            # last used sequence value (0 = none used yet)
        self.has_sequence = True  # True → INSERT advances seq (serial PK table)
        self.committed = 0
        self.rolledback = 0
        self.closed = 0
        self.closed_cursors = 0
        self.select_rows: list = []
        self.update_rowcount = 0

    def cursor(self):
        return _FakeCursor(self)

    def commit(self):
        self.committed += 1

    def rollback(self):
        self.rolledback += 1

    def close(self):
        self.closed += 1


# --------------------------------------------------------------------------- #
# INSERT wiring — lazy lastval(), no RETURNING rewrite
# --------------------------------------------------------------------------- #

def test_execute_insert_sql_not_modified_lastrowid_via_lastval():
    """INSERT SQL must NOT be rewritten; lastrowid is resolved lazily via lastval()."""
    fake = _FakeConnection()
    conn = PgConnection(fake)
    cur = conn.execute(
        "INSERT INTO price_alerts(symbol, target_price) VALUES(?, ?)",
        ("005930", 70000),
    )
    # Only the INSERT should have been sent at this point (no RETURNING appended).
    insert_sql, insert_params = fake.executed[-1]
    assert "RETURNING" not in insert_sql.upper()
    assert insert_sql == "INSERT INTO price_alerts(symbol, target_price) VALUES(%s, %s)"
    assert insert_params == ("005930", 70000)

    # Reading lastrowid triggers the SELECT lastval() probe.
    assert cur.lastrowid == 1

    # Verify SELECT lastval() was actually called during the probe.
    lastval_calls = [sql for sql, _ in fake.executed if "LASTVAL" in sql.upper()]
    assert len(lastval_calls) >= 1

    # Second insert advances the surrogate sequence value.
    cur2 = conn.execute(
        "INSERT INTO price_alerts(symbol, target_price) VALUES(?, ?)",
        ("000660", 100),
    )
    assert "RETURNING" not in fake.executed[  # the INSERT sql entry
        [i for i, (s, _) in enumerate(fake.executed) if s.strip().upper().startswith("INSERT")][-1]
    ][0].upper()
    assert cur2.lastrowid == 2


def test_execute_insert_no_id_column_sql_unchanged_and_lastrowid_none():
    """INSERT into tables with no serial PK (e.g. investor_profiles, PK=username)
    must pass SQL through unchanged and return lastrowid=None without raising."""
    fake = _FakeConnection()
    fake.has_sequence = False  # no serial column on this table
    fake.seq = 0               # no prior sequence use in session
    conn = PgConnection(fake)
    cur = conn.execute(
        "INSERT INTO investor_profiles(username, completed) VALUES(?, ?) "
        "ON CONFLICT (username) DO UPDATE SET completed = ?",
        ("alice", 1, 1),
    )
    # Find the INSERT statement that was executed.
    insert_rows = [(sql, p) for sql, p in fake.executed if sql.strip().upper().startswith("INSERT")]
    assert len(insert_rows) == 1
    insert_sql, insert_params = insert_rows[0]
    # SQL must be passed through unchanged (no RETURNING id appended).
    assert "RETURNING" not in insert_sql.upper()
    assert insert_sql == (
        "INSERT INTO investor_profiles(username, completed) VALUES(%s, %s) "
        "ON CONFLICT (username) DO UPDATE SET completed = %s"
    )
    assert insert_params == ("alice", 1, 1)
    # lastrowid must be None — no exception must escape.
    assert cur.lastrowid is None


def test_execute_select_returns_dict_rows():
    fake = _FakeConnection()
    fake.select_rows = [{"value": "true"}]
    conn = PgConnection(fake)
    cur = conn.execute("SELECT value FROM system_state WHERE key = ?", ("auto_trading_enabled",))
    row = cur.fetchone()
    assert isinstance(row, dict)
    assert row["value"] == "true"          # subscript access (repositories use row["value"])
    assert dict(row) == {"value": "true"}  # dict(row) conversion used everywhere
    # placeholder translated, no RETURNING appended on SELECT
    executed_sql, executed_params = fake.executed[-1]
    assert executed_sql == "SELECT value FROM system_state WHERE key = %s"
    assert "RETURNING" not in executed_sql
    assert executed_params == ("auto_trading_enabled",)


def test_execute_select_fetchall_dict_rows():
    fake = _FakeConnection()
    fake.select_rows = [{"id": 1}, {"id": 2}]
    conn = PgConnection(fake)
    rows = [dict(r) for r in conn.execute("SELECT id FROM t").fetchall()]
    assert rows == [{"id": 1}, {"id": 2}]


def test_execute_update_passes_rowcount_and_no_returning():
    fake = _FakeConnection()
    fake.update_rowcount = 1
    conn = PgConnection(fake)
    cur = conn.execute(
        "UPDATE trade_conditions SET status='PROCESSING' WHERE id=? AND status='ACTIVE'",
        (5,),
    )
    assert cur.rowcount == 1
    # No prior sequence in session → lastval() probe raises → None returned safely.
    assert cur.lastrowid is None
    # The UPDATE SQL itself must not have RETURNING.
    update_sqls = [
        sql for sql, _ in fake.executed if sql.strip().upper().startswith("UPDATE")
    ]
    assert len(update_sqls) == 1
    assert "RETURNING" not in update_sqls[0].upper()


def test_context_manager_commits_and_closes_on_clean_exit():
    fake = _FakeConnection()
    with PgConnection(fake) as conn:
        conn.execute("SELECT 1")
    assert fake.committed == 1
    assert fake.rolledback == 0
    assert fake.closed == 1


def test_context_manager_rolls_back_and_closes_and_propagates_on_error():
    fake = _FakeConnection()
    with pytest.raises(ValueError):
        with PgConnection(fake) as conn:
            conn.execute("SELECT 1")
            raise ValueError("boom")
    assert fake.committed == 0
    assert fake.rolledback == 1
    assert fake.closed == 1


def test_executescript_runs_script_on_cursor():
    fake = _FakeConnection()
    conn = PgConnection(fake)
    conn.executescript("CREATE TABLE x(id int);")
    assert fake.executed[-1][0] == "CREATE TABLE x(id int);"
    assert fake.closed_cursors >= 1


def test_connect_uses_dict_row_factory(monkeypatch):
    """connect() must request the dict_row factory so rows are dict-shaped."""
    captured = {}

    class _StubModule:
        def connect(self, conninfo, row_factory=None):
            captured["conninfo"] = conninfo
            captured["row_factory"] = row_factory
            return _FakeConnection()

    import sys
    import types

    stub = _StubModule()
    rows_mod = types.ModuleType("psycopg.rows")
    rows_mod.dict_row = "DICT_ROW_SENTINEL"
    psycopg_mod = types.ModuleType("psycopg")
    psycopg_mod.connect = stub.connect
    psycopg_mod.rows = rows_mod

    monkeypatch.setitem(sys.modules, "psycopg", psycopg_mod)
    monkeypatch.setitem(sys.modules, "psycopg.rows", rows_mod)

    conn = pg_db.connect("postgresql://u:p@h/db")
    assert isinstance(conn, PgConnection)
    assert captured["conninfo"] == "postgresql://u:p@h/db"
    assert captured["row_factory"] == "DICT_ROW_SENTINEL"
