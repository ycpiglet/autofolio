"""Multitenant Phase 1: schema migration + repository scoping tests."""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

import pytest

from app.database.repositories import Repository, WhitelistSymbol
from app.database.sqlite_db import (
    initialize_database,
    get_connection,
    _apply_multitenant_migration,
    _MULTITENANT_COLUMNS,
)


@pytest.fixture
def repo(tmp_path):
    db = tmp_path / "test.db"
    initialize_database(db)
    return Repository(db), db


def test_user_id_column_exists_in_all_trading_tables(repo):
    """After initialize_database, all 7 tables must have a user_id column."""
    _, db = repo
    tables = [
        "trade_conditions", "order_logs", "execution_logs",
        "price_alerts", "trade_journal", "system_state", "risk_limits",
    ]
    with get_connection(db) as conn:
        for table in tables:
            info = conn.execute(f"PRAGMA table_info({table})").fetchall()
            col_names = [row[1] for row in info]
            assert "user_id" in col_names, f"user_id missing from {table}"


def test_migration_is_idempotent_on_existing_db(tmp_path):
    """Calling initialize_database twice does not raise (migration is idempotent)."""
    db = tmp_path / "existing.db"
    initialize_database(db)
    initialize_database(db)  # second call — must not raise
    with get_connection(db) as conn:
        info = conn.execute("PRAGMA table_info(trade_conditions)").fetchall()
        col_names = [row[1] for row in info]
        assert "user_id" in col_names


def test_migration_adds_user_id_to_legacy_table_without_column(tmp_path):
    """The ALTER path: a pre-Task-1 table lacking user_id gets the column added.

    Simulates a database created BEFORE the schema.sql change (Task 1) where
    `CREATE TABLE IF NOT EXISTS` would skip the table on re-init and never add
    the new column. This is the safety-critical existing-DB path; the columns
    must end up present so scoped queries can filter on them.
    """
    db = tmp_path / "legacy.db"
    # Build a legacy table WITHOUT user_id (the pre-migration shape).
    with sqlite3.connect(db) as conn:
        for table, column, _ in _MULTITENANT_COLUMNS:
            conn.execute(f"CREATE TABLE {table} (id INTEGER PRIMARY KEY, payload TEXT)")
            cols_before = [r[1] for r in conn.execute(f"PRAGMA table_info({table})")]
            assert column not in cols_before  # RED precondition: column absent

    # Apply the migration.
    with sqlite3.connect(db) as conn:
        _apply_multitenant_migration(conn)

    # GREEN: every table now has user_id.
    with sqlite3.connect(db) as conn:
        for table, column, _ in _MULTITENANT_COLUMNS:
            cols_after = [r[1] for r in conn.execute(f"PRAGMA table_info({table})")]
            assert column in cols_after, f"{column} not added to legacy {table}"


def test_migration_preserves_existing_rows_with_null_user_id(tmp_path):
    """Existing rows survive the ALTER and receive NULL user_id (non-destructive)."""
    db = tmp_path / "legacy_rows.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE price_alerts (id INTEGER PRIMARY KEY, payload TEXT)")
        conn.execute("INSERT INTO price_alerts(id, payload) VALUES (1, 'legacy')")
    with sqlite3.connect(db) as conn:
        _apply_multitenant_migration(conn)
    with sqlite3.connect(db) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM price_alerts WHERE id = 1").fetchone()
        assert row["payload"] == "legacy"
        assert row["user_id"] is None
