"""TASK-066: Repository edge-case tests.

Covers:
- Empty-DB queries return [] / None (not crash)
- FK violation: execution_log with orphan order_log_id raises IntegrityError
- order_log with null condition_id is permitted (ON DELETE SET NULL)
- today_order_amount() on empty DB returns 0.0 (not crash)
- today_realized_pnl() on empty DB returns 0.0 (not crash)
- Duplicate whitelist insert (UPSERT) does not crash; row is updated
- atomic_claim_condition on non-existent ID returns False (not crash)
- get_condition on non-existent ID returns None (not crash)

FK enforcement note: SQLite FK enforcement is per-connection (PRAGMA foreign_keys=ON).
get_connection() already sets this on every connection (app/database/sqlite_db.py:11).
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from app.database.repositories import Repository, WhitelistSymbol
from app.database.sqlite_db import initialize_database, get_connection


def _make_repo(tmp_path: Path):
    db = tmp_path / "test.db"
    initialize_database(db)
    return Repository(db), db


def _seed_whitelist(repo: Repository, symbol: str = "005930") -> None:
    repo.add_whitelist_symbol(
        WhitelistSymbol(symbol=symbol, name="test_name", market="KRX", role="TEST")
    )


def _insert_condition(repo: Repository, symbol: str = "005930") -> int:
    _seed_whitelist(repo, symbol)
    return repo.add_trade_condition(
        symbol=symbol,
        side="BUY",
        target_price=70_000.0,
        quantity=1,
    )


def _insert_order_log(repo: Repository, condition_id=None) -> int:
    return repo.create_order_log(
        condition_id=condition_id,
        symbol="005930",
        side="BUY",
        order_type="LIMIT",
        order_price=70_000.0,
        current_price=70_000.0,
        quantity=1,
        kis_order_id="ORD-001",
        order_status="FILLED",
    )


class TestEmptyDbQueries:
    def test_list_active_conditions_empty_db_returns_empty_list(self, tmp_path):
        repo, _ = _make_repo(tmp_path)
        assert repo.list_active_conditions() == []

    def test_list_conditions_empty_db_returns_empty_list(self, tmp_path):
        repo, _ = _make_repo(tmp_path)
        assert repo.list_conditions() == []

    def test_list_order_logs_empty_db_returns_empty_list(self, tmp_path):
        repo, _ = _make_repo(tmp_path)
        assert repo.list_order_logs() == []

    def test_list_whitelist_symbols_empty_db_returns_empty_list(self, tmp_path):
        repo, _ = _make_repo(tmp_path)
        assert repo.list_whitelist_symbols() == []

    def test_get_whitelist_symbol_missing_returns_none(self, tmp_path):
        repo, _ = _make_repo(tmp_path)
        assert repo.get_whitelist_symbol("DOES_NOT_EXIST") is None

    def test_get_condition_missing_returns_none(self, tmp_path):
        repo, _ = _make_repo(tmp_path)
        assert repo.get_condition(99999) is None

    def test_get_system_state_missing_key_returns_default(self, tmp_path):
        repo, _ = _make_repo(tmp_path)
        assert repo.get_system_state("nonexistent_key", "default_value") == "default_value"

    def test_get_system_state_missing_key_no_default_returns_none(self, tmp_path):
        repo, _ = _make_repo(tmp_path)
        assert repo.get_system_state("nonexistent_key") is None

    def test_today_order_amount_empty_db_returns_zero(self, tmp_path):
        repo, _ = _make_repo(tmp_path)
        assert repo.today_order_amount() == 0.0

    def test_today_realized_pnl_empty_db_returns_zero(self, tmp_path):
        repo, _ = _make_repo(tmp_path)
        assert repo.today_realized_pnl() == 0.0

    def test_total_realized_pnl_empty_db_returns_zero(self, tmp_path):
        repo, _ = _make_repo(tmp_path)
        assert repo.total_realized_pnl() == 0.0

    def test_total_buy_cost_basis_empty_db_returns_zero(self, tmp_path):
        repo, _ = _make_repo(tmp_path)
        assert repo.total_buy_cost_basis() == 0.0

    def test_list_active_alerts_empty_db_returns_empty_list(self, tmp_path):
        repo, _ = _make_repo(tmp_path)
        assert repo.list_active_alerts() == []

    def test_list_journal_entries_empty_db_returns_empty_list(self, tmp_path):
        repo, _ = _make_repo(tmp_path)
        assert repo.list_journal_entries() == []


class TestForeignKeyViolation:
    def test_execution_log_with_orphan_order_log_id_raises(self, tmp_path):
        """Inserting execution_log with a non-existent order_log_id raises IntegrityError.

        PRAGMA foreign_keys=ON is set in get_connection() — enforcement is active.
        """
        repo, _ = _make_repo(tmp_path)
        orphan_order_log_id = 99999  # does not exist
        with pytest.raises(sqlite3.IntegrityError):
            repo.create_execution_log(
                order_log_id=orphan_order_log_id,
                symbol="005930",
                filled_price=70_000.0,
                filled_quantity=1,
                raw_status="FILLED",
            )

    def test_fk_is_enforced_per_connection(self, tmp_path):
        """Each connection from get_connection() must have FK enforcement ON."""
        db = tmp_path / "fk_check.db"
        initialize_database(db)
        with get_connection(db) as conn:
            row = conn.execute("PRAGMA foreign_keys").fetchone()
            assert row[0] == 1, "PRAGMA foreign_keys must be 1 (ON) on every connection"

    def test_order_log_with_null_condition_id_is_allowed(self, tmp_path):
        """order_log condition_id = NULL is permitted (ON DELETE SET NULL FK)."""
        repo, _ = _make_repo(tmp_path)
        log_id = repo.create_order_log(
            condition_id=None,
            symbol="005930",
            side="BUY",
            order_type="LIMIT",
            order_price=70_000.0,
            current_price=70_000.0,
            quantity=1,
            kis_order_id="ORD-NULL",
            order_status="FILLED",
        )
        assert log_id > 0


class TestDuplicateInserts:
    def test_duplicate_whitelist_symbol_upserts_without_error(self, tmp_path):
        """Inserting same symbol twice (UPSERT) does not raise; row is updated."""
        repo, _ = _make_repo(tmp_path)
        repo.add_whitelist_symbol(
            WhitelistSymbol(symbol="005930", name="Samsung1", market="KRX", role="CORE")
        )
        repo.add_whitelist_symbol(
            WhitelistSymbol(symbol="005930", name="Samsung2", market="KRX", role="CORE_V2")
        )
        result = repo.get_whitelist_symbol("005930")
        assert result is not None
        assert result["name"] == "Samsung2"
        assert result["role"] == "CORE_V2"

    def test_duplicate_system_state_upserts_without_error(self, tmp_path):
        """set_system_state on an existing key does UPSERT (no duplicate error)."""
        repo, _ = _make_repo(tmp_path)
        repo.set_system_state("test_key", "value1")
        repo.set_system_state("test_key", "value2")
        assert repo.get_system_state("test_key") == "value2"

    def test_atomic_claim_on_nonexistent_id_returns_false(self, tmp_path):
        """atomic_claim_condition on a non-existent condition_id returns False (not crash)."""
        repo, _ = _make_repo(tmp_path)
        result = repo.atomic_claim_condition(99999)
        assert result is False

    def test_create_execution_log_with_valid_order_log_id_succeeds(self, tmp_path):
        """Execution log with a valid (seeded) order_log_id FK succeeds and returns int."""
        repo, _ = _make_repo(tmp_path)
        cid = _insert_condition(repo)
        order_log_id = _insert_order_log(repo, condition_id=cid)
        exec_log_id = repo.create_execution_log(
            order_log_id=order_log_id,
            symbol="005930",
            filled_price=70_000.0,
            filled_quantity=1,
            raw_status="FILLED",
        )
        assert isinstance(exec_log_id, int)
        assert exec_log_id > 0