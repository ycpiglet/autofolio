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


def test_initialize_database_on_legacy_db_does_not_crash(tmp_path):
    """initialize_database must succeed on a pre-multitenant DB (regression).

    Reproduces the ordering bug where user_id indexes lived in schema.sql and
    ran (via executescript) BEFORE the migration added the columns: on an
    existing DB, CREATE TABLE IF NOT EXISTS is skipped, so the index DDL hit
    'no such column: user_id' and crashed init. The indexes now live in the
    migration, created after the columns are added.
    """
    db = tmp_path / "legacy_init.db"
    # Build a pre-multitenant trade_conditions table: no user_id, no user_id index.
    with sqlite3.connect(db) as conn:
        conn.execute(
            """CREATE TABLE trade_conditions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                target_price REAL NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                order_type TEXT NOT NULL DEFAULT 'LIMIT',
                allow_market_fallback INTEGER NOT NULL DEFAULT 0,
                auto_enabled INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                cooldown_until TEXT,
                created_by TEXT NOT NULL DEFAULT 'USER',
                rationale TEXT,
                risk_note TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )"""
        )

    # Must NOT raise — and must end up with the user_id column + index.
    initialize_database(db)

    with get_connection(db) as conn:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(trade_conditions)")]
        assert "user_id" in cols
        idx = [r[1] for r in conn.execute("PRAGMA index_list(trade_conditions)")]
        assert "idx_trade_conditions_user_id" in idx


def test_migration_does_not_mask_genuine_errors(tmp_path):
    """A non-duplicate OperationalError (e.g. 'no such table') must NOT be swallowed.

    Guards against the catch being too broad: if the target table is missing,
    the migration must surface the error rather than silently no-op and leave
    the columns absent.
    """
    db = tmp_path / "no_tables.db"
    with sqlite3.connect(db) as conn:
        # No tables created — the first ALTER hits "no such table".
        with pytest.raises(sqlite3.OperationalError, match="no such table"):
            _apply_multitenant_migration(conn)


def test_migration_preserves_existing_rows_with_null_user_id(tmp_path):
    """Existing rows survive the ALTER and receive NULL user_id (non-destructive)."""
    db = tmp_path / "legacy_rows.db"
    # A realistic pre-migration DB has ALL 7 tables, just without user_id.
    with sqlite3.connect(db) as conn:
        for table, _column, _type in _MULTITENANT_COLUMNS:
            conn.execute(f"CREATE TABLE {table} (id INTEGER PRIMARY KEY, payload TEXT)")
        conn.execute("INSERT INTO price_alerts(id, payload) VALUES (1, 'legacy')")
    with sqlite3.connect(db) as conn:
        _apply_multitenant_migration(conn)
    with sqlite3.connect(db) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM price_alerts WHERE id = 1").fetchone()
        assert row["payload"] == "legacy"
        assert row["user_id"] is None


# ---- Helpers ----

def _seed_whitelist(repo_obj, symbol="005930"):
    repo_obj.add_whitelist_symbol(
        WhitelistSymbol(symbol=symbol, name="테스트", market="KRX", role="TEST")
    )


def _insert_filled_sell(repo_obj, user_id, symbol="005930", price=75_000.0, qty=1):
    """Insert a complete BUY+SELL cycle for realized PnL testing."""
    # BUY order
    buy_cid = repo_obj.add_trade_condition(
        symbol=symbol, side="BUY", target_price=price,
        quantity=qty, user_id=user_id,
    )
    buy_order_id = repo_obj.create_order_log(
        condition_id=buy_cid, symbol=symbol, side="BUY",
        order_type="LIMIT", order_price=price, current_price=price,
        quantity=qty, kis_order_id=None, order_status="FILLED",
        user_id=user_id,
    )
    repo_obj.create_execution_log(
        order_log_id=buy_order_id, symbol=symbol,
        filled_price=price, filled_quantity=qty,
        user_id=user_id,
    )
    # SELL order
    sell_cid = repo_obj.add_trade_condition(
        symbol=symbol, side="SELL", target_price=price + 1000,
        quantity=qty, user_id=user_id,
    )
    sell_order_id = repo_obj.create_order_log(
        condition_id=sell_cid, symbol=symbol, side="SELL",
        order_type="LIMIT", order_price=price + 1000, current_price=price + 1000,
        quantity=qty, kis_order_id=None, order_status="FILLED",
        user_id=user_id,
    )
    repo_obj.create_execution_log(
        order_log_id=sell_order_id, symbol=symbol,
        filled_price=price + 1000, filled_quantity=qty,
        user_id=user_id,
    )
    return buy_order_id, sell_order_id


# ---- Flag-ON scoping tests ----

@pytest.fixture
def mt_repo(tmp_path, monkeypatch):
    """Repo fixture with AUTOFOLIO_MULTI_TENANT_ENABLED=1."""
    monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
    db = tmp_path / "mt_test.db"
    initialize_database(db)
    return Repository(db), db


def test_flagoff_is_default(tmp_path, monkeypatch):
    """With no env var set, multi_tenant_enabled() returns False."""
    from app.services.flags import multi_tenant_enabled
    monkeypatch.delenv("AUTOFOLIO_MULTI_TENANT_ENABLED", raising=False)
    assert multi_tenant_enabled() is False


class TestConditionScoping:
    def test_list_conditions_scoped_to_user(self, mt_repo, monkeypatch):
        monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
        repo, _ = mt_repo
        _seed_whitelist(repo)
        repo.add_trade_condition(
            symbol="005930", side="BUY", target_price=70_000, quantity=1, user_id="user_a"
        )
        repo.add_trade_condition(
            symbol="005930", side="SELL", target_price=75_000, quantity=1, user_id="user_b"
        )
        rows_a = repo.list_conditions(user_id="user_a")
        rows_b = repo.list_conditions(user_id="user_b")
        assert len(rows_a) == 1 and rows_a[0]["side"] == "BUY"
        assert len(rows_b) == 1 and rows_b[0]["side"] == "SELL"

    def test_list_active_conditions_scoped(self, mt_repo, monkeypatch):
        monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
        repo, _ = mt_repo
        _seed_whitelist(repo)
        repo.add_trade_condition(
            symbol="005930", side="BUY", target_price=70_000, quantity=1, user_id="user_a"
        )
        repo.add_trade_condition(
            symbol="005930", side="SELL", target_price=75_000, quantity=1, user_id="user_b"
        )
        active_a = repo.list_active_conditions(user_id="user_a")
        assert len(active_a) == 1
        assert active_a[0]["side"] == "BUY"

    def test_null_user_id_row_not_returned_in_scoped_query(self, mt_repo, monkeypatch):
        """Legacy row with NULL user_id must NOT be returned to a scoped query."""
        monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
        repo, _ = mt_repo
        _seed_whitelist(repo)
        # Insert without user_id → NULL user_id
        repo.add_trade_condition(
            symbol="005930", side="BUY", target_price=70_000, quantity=1
        )
        # Scoped query for user_a should not return the legacy row
        rows = repo.list_conditions(user_id="user_a")
        assert rows == []


class TestOrderLogScoping:
    def test_list_order_logs_scoped(self, mt_repo, monkeypatch):
        monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
        repo, _ = mt_repo
        _seed_whitelist(repo)
        cid_a = repo.add_trade_condition(
            symbol="005930", side="BUY", target_price=70_000, quantity=1, user_id="user_a"
        )
        cid_b = repo.add_trade_condition(
            symbol="005930", side="BUY", target_price=70_000, quantity=1, user_id="user_b"
        )
        repo.create_order_log(
            condition_id=cid_a, symbol="005930", side="BUY",
            order_type="LIMIT", order_price=70_000, current_price=70_000,
            quantity=1, kis_order_id="A001", order_status="FILLED",
            user_id="user_a",
        )
        repo.create_order_log(
            condition_id=cid_b, symbol="005930", side="BUY",
            order_type="LIMIT", order_price=70_000, current_price=70_000,
            quantity=1, kis_order_id="B001", order_status="FILLED",
            user_id="user_b",
        )
        logs_a = repo.list_order_logs(user_id="user_a")
        assert len(logs_a) == 1 and logs_a[0]["kis_order_id"] == "A001"


class TestAggregateScoping:
    def test_today_order_amount_scoped(self, mt_repo, monkeypatch):
        monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
        repo, _ = mt_repo
        _seed_whitelist(repo)
        cid_a = repo.add_trade_condition(
            symbol="005930", side="BUY", target_price=70_000, quantity=1, user_id="user_a"
        )
        cid_b = repo.add_trade_condition(
            symbol="005930", side="BUY", target_price=70_000, quantity=1, user_id="user_b"
        )
        repo.create_order_log(
            condition_id=cid_a, symbol="005930", side="BUY",
            order_type="LIMIT", order_price=70_000, current_price=70_000,
            quantity=2, kis_order_id=None, order_status="FILLED",
            user_id="user_a",
        )
        repo.create_order_log(
            condition_id=cid_b, symbol="005930", side="BUY",
            order_type="LIMIT", order_price=90_000, current_price=90_000,
            quantity=3, kis_order_id=None, order_status="FILLED",
            user_id="user_b",
        )
        amt_a = repo.today_order_amount(user_id="user_a")
        amt_b = repo.today_order_amount(user_id="user_b")
        assert amt_a == pytest.approx(140_000.0)  # 70000 * 2
        assert amt_b == pytest.approx(270_000.0)  # 90000 * 3

    def test_total_buy_cost_basis_scoped(self, mt_repo, monkeypatch):
        monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
        repo, _ = mt_repo
        _seed_whitelist(repo)
        cid_a = repo.add_trade_condition(
            symbol="005930", side="BUY", target_price=70_000, quantity=1, user_id="user_a"
        )
        order_a = repo.create_order_log(
            condition_id=cid_a, symbol="005930", side="BUY",
            order_type="LIMIT", order_price=70_000, current_price=70_000,
            quantity=1, kis_order_id=None, order_status="FILLED",
            user_id="user_a",
        )
        repo.create_execution_log(
            order_log_id=order_a, symbol="005930",
            filled_price=70_000, filled_quantity=1,
            user_id="user_a",
        )
        cid_b = repo.add_trade_condition(
            symbol="005930", side="BUY", target_price=80_000, quantity=1, user_id="user_b"
        )
        order_b = repo.create_order_log(
            condition_id=cid_b, symbol="005930", side="BUY",
            order_type="LIMIT", order_price=80_000, current_price=80_000,
            quantity=1, kis_order_id=None, order_status="FILLED",
            user_id="user_b",
        )
        repo.create_execution_log(
            order_log_id=order_b, symbol="005930",
            filled_price=80_000, filled_quantity=1,
            user_id="user_b",
        )
        assert repo.total_buy_cost_basis(user_id="user_a") == pytest.approx(70_000.0)
        assert repo.total_buy_cost_basis(user_id="user_b") == pytest.approx(80_000.0)

    def test_today_realized_pnl_scoped(self, mt_repo, monkeypatch):
        """Per-user realized PnL: both the avg_cost CTE and the outer SELL query
        must be scoped to the user.

        Both users trade the SAME symbol at DIFFERENT buy prices, so a CTE that
        failed to scope by user_id would blend their cost bases and produce a
        wrong number (not merely a wrong sum). Realized PnL per the helper is
        (sell_price - avg_buy_price) * qty = 1000 * qty when correctly scoped.
        """
        monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
        repo, _ = mt_repo
        _seed_whitelist(repo)
        _insert_filled_sell(repo, "user_a", symbol="005930", price=75_000.0, qty=1)
        _insert_filled_sell(repo, "user_b", symbol="005930", price=50_000.0, qty=3)
        # Correct scoping: A = (76000-75000)*1 = 1000 ; B = (51000-50000)*3 = 3000.
        assert repo.today_realized_pnl(user_id="user_a") == pytest.approx(1_000.0)
        assert repo.today_realized_pnl(user_id="user_b") == pytest.approx(3_000.0)

    def test_total_realized_pnl_scoped(self, mt_repo, monkeypatch):
        """total_realized_pnl (no date filter) must isolate per user, CTE included."""
        monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
        repo, _ = mt_repo
        _seed_whitelist(repo)
        _insert_filled_sell(repo, "user_a", symbol="005930", price=75_000.0, qty=1)
        _insert_filled_sell(repo, "user_b", symbol="005930", price=50_000.0, qty=3)
        assert repo.total_realized_pnl(user_id="user_a") == pytest.approx(1_000.0)
        assert repo.total_realized_pnl(user_id="user_b") == pytest.approx(3_000.0)

    def test_realized_pnl_excludes_null_user_id_legacy_rows(self, mt_repo, monkeypatch):
        """A scoped realized-PnL query must ignore legacy NULL-user_id fills."""
        monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
        repo, _ = mt_repo
        _seed_whitelist(repo)
        # Legacy cycle with NO user_id (NULL) — must be invisible to scoped query.
        _insert_filled_sell(repo, None, symbol="005930", price=10_000.0, qty=5)
        _insert_filled_sell(repo, "user_a", symbol="005930", price=75_000.0, qty=1)
        assert repo.total_realized_pnl(user_id="user_a") == pytest.approx(1_000.0)


class TestAlertScoping:
    def test_list_active_alerts_scoped(self, mt_repo, monkeypatch):
        monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
        repo, _ = mt_repo
        repo.add_price_alert("005930", 70_000, "ABOVE", user_id="user_a")
        repo.add_price_alert("000660", 80_000, "BELOW", user_id="user_b")
        alerts_a = repo.list_active_alerts(user_id="user_a")
        assert len(alerts_a) == 1 and alerts_a[0]["symbol"] == "005930"


class TestJournalScoping:
    def test_list_journal_entries_scoped(self, mt_repo, monkeypatch):
        monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
        repo, _ = mt_repo
        repo.add_journal_entry("005930", "BUY", entry_reason="value", user_id="user_a")
        repo.add_journal_entry("000660", "SELL", entry_reason="momentum", user_id="user_b")
        entries_a = repo.list_journal_entries(user_id="user_a")
        assert len(entries_a) == 1 and entries_a[0]["symbol"] == "005930"
