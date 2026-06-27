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
        upper = sql.lstrip().upper()
        if "RETURNING ID" in sql.upper():
            self._conn.seq += 1
            self.description = [("id",)]
            self._result = [{"id": self._conn.seq}]
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
        self.seq = 0
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


def test_execute_insert_translates_appends_returning_and_sets_lastrowid():
    fake = _FakeConnection()
    conn = PgConnection(fake)
    cur = conn.execute("INSERT INTO price_alerts(symbol, target_price) VALUES(?, ?)", ("005930", 70000))
    executed_sql, executed_params = fake.executed[-1]
    assert executed_sql == "INSERT INTO price_alerts(symbol, target_price) VALUES(%s, %s) RETURNING id"
    assert executed_params == ("005930", 70000)
    assert cur.lastrowid == 1
    # A second insert advances the surrogate id.
    cur2 = conn.execute("INSERT INTO price_alerts(symbol, target_price) VALUES(?, ?)", ("000660", 100))
    assert cur2.lastrowid == 2


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
    assert cur.lastrowid is None
    executed_sql, _ = fake.executed[-1]
    assert "RETURNING" not in executed_sql


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
