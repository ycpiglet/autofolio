"""Multitenant Phase 1: schema migration + repository scoping tests."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from app.database.repositories import Repository, WhitelistSymbol
from app.database.sqlite_db import initialize_database, get_connection


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
