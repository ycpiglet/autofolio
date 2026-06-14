"""TASK-060: SQLite WAL mode + FK enforcement tests.

TDD contract:
  1. Every new connection has foreign_keys=ON (per-connection pragma).
  2. initialize_database() activates WAL mode (persistent per-DB).
  3. Inserting a child row (execution_logs) with a non-existent parent (order_log_id)
     raises sqlite3.IntegrityError — orphan inserts are blocked.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from app.database.repositories import Repository, WhitelistSymbol
from app.database.sqlite_db import get_connection, initialize_database


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def db_path(tmp_path):
    """Return path to a freshly initialised test DB."""
    path = tmp_path / "wal_fk_test.db"
    initialize_database(path)
    return path


# ---------------------------------------------------------------------------
# 1. PRAGMA foreign_keys=ON — every connection
# ---------------------------------------------------------------------------

def test_get_connection_enables_foreign_keys(db_path):
    """PRAGMA foreign_keys must be ON on every connection returned by get_connection()."""
    with get_connection(db_path) as conn:
        row = conn.execute("PRAGMA foreign_keys").fetchone()
        assert row[0] == 1, "foreign_keys should be 1 (ON) on every connection"


def test_foreign_keys_on_independent_second_connection(db_path):
    """A second independent connection also has foreign_keys=ON."""
    with get_connection(db_path) as conn1:
        pass  # close first
    with get_connection(db_path) as conn2:
        row = conn2.execute("PRAGMA foreign_keys").fetchone()
        assert row[0] == 1


# ---------------------------------------------------------------------------
# 2. WAL mode — persistent per-DB
# ---------------------------------------------------------------------------

def test_initialize_database_sets_wal_mode(db_path):
    """journal_mode should be 'wal' after initialize_database()."""
    with get_connection(db_path) as conn:
        row = conn.execute("PRAGMA journal_mode").fetchone()
        assert row[0].lower() == "wal", f"Expected WAL, got {row[0]}"


def test_wal_mode_survives_reconnect(db_path):
    """WAL is persistent — a fresh connection to the same file still reports WAL."""
    # Open and close a connection (no explicit journal_mode call)
    with get_connection(db_path) as conn:
        row = conn.execute("PRAGMA journal_mode").fetchone()
    assert row[0].lower() == "wal"


# ---------------------------------------------------------------------------
# 3. FK enforcement — orphan inserts are blocked
# ---------------------------------------------------------------------------

def test_execution_log_fk_blocks_nonexistent_order_log(db_path):
    """Inserting execution_logs with non-existent order_log_id must raise IntegrityError."""
    with get_connection(db_path) as conn:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO execution_logs(order_log_id, symbol, filled_price, filled_quantity)
                VALUES (99999, '005930', 70000.0, 1)
                """
            )


def test_execution_log_fk_allows_valid_parent(db_path):
    """Inserting execution_logs with a valid order_log_id must succeed."""
    repo = Repository(db_path)
    repo.add_whitelist_symbol(
        WhitelistSymbol(symbol="005930", name="삼성전자", market="KRX", role="LARGE_CAP_TEST")
    )
    order_log_id = repo.create_order_log(
        condition_id=None,
        symbol="005930",
        side="BUY",
        order_type="LIMIT",
        order_price=70_000.0,
        current_price=70_000.0,
        quantity=1,
        kis_order_id="TEST-001",
        order_status="PENDING",
    )
    exec_id = repo.create_execution_log(
        order_log_id=order_log_id,
        symbol="005930",
        filled_price=70_000.0,
        filled_quantity=1,
    )
    assert exec_id is not None and exec_id > 0


def test_order_log_condition_fk_blocks_nonexistent_condition(db_path):
    """Inserting order_logs with a non-existent condition_id must raise IntegrityError."""
    with get_connection(db_path) as conn:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO order_logs(
                    condition_id, symbol, side, order_type, order_price,
                    current_price, quantity, order_status, fallback_to_market
                ) VALUES (99999, '005930', 'BUY', 'LIMIT', 70000.0, 70000.0, 1, 'PENDING', 0)
                """
            )


def test_order_log_null_condition_id_is_allowed(db_path):
    """condition_id is nullable — NULL must not trigger FK violation."""
    repo = Repository(db_path)
    repo.add_whitelist_symbol(
        WhitelistSymbol(symbol="005930", name="삼성전자", market="KRX", role="LARGE_CAP_TEST")
    )
    log_id = repo.create_order_log(
        condition_id=None,
        symbol="005930",
        side="BUY",
        order_type="MARKET",
        order_price=None,
        current_price=70_000.0,
        quantity=1,
        kis_order_id=None,
        order_status="PENDING",
    )
    assert log_id is not None and log_id > 0
