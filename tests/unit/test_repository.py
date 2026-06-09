"""Repository 핵심 메서드 단위 테스트."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from app.database.repositories import Repository, WhitelistSymbol
from app.database.sqlite_db import initialize_database


@pytest.fixture
def repo():
    with TemporaryDirectory() as tmpdir:
        db = Path(tmpdir) / "test.db"
        initialize_database(db)
        yield Repository(db)


# ---- whitelist ----
def test_add_and_list_whitelist(repo):
    repo.add_whitelist_symbol(WhitelistSymbol("005930", "삼성전자", "KRX", "LARGE_CAP_TEST"))
    rows = repo.list_whitelist_symbols()
    assert len(rows) == 1 and rows[0]["symbol"] == "005930"


def test_get_whitelist_symbol(repo):
    repo.add_whitelist_symbol(WhitelistSymbol("069500", "KODEX 200", "KRX", "ETF_TEST"))
    row = repo.get_whitelist_symbol("069500")
    assert row is not None and row["name"] == "KODEX 200"


def test_get_missing_whitelist_symbol_returns_none(repo):
    assert repo.get_whitelist_symbol("999999") is None


# ---- system_state ----
def test_set_and_get_system_state(repo):
    repo.set_system_state("auto_trading_enabled", "true")
    assert repo.get_system_state("auto_trading_enabled") == "true"


def test_get_missing_state_returns_default(repo):
    assert repo.get_system_state("no_such_key", "fallback") == "fallback"


# ---- risk limits ----
def test_get_global_risk_limit(repo):
    limits = repo.get_global_risk_limit()
    assert "max_order_amount" in limits
    assert float(limits["max_order_amount"]) > 0


def test_update_global_risk_limit(repo):
    repo.update_global_risk_limit(max_order_amount=50_000.0, max_daily_amount=150_000.0)
    limits = repo.get_global_risk_limit()
    assert float(limits["max_order_amount"]) == 50_000.0
    assert float(limits["max_daily_amount"]) == 150_000.0


# ---- trade conditions ----
def test_add_and_list_conditions(repo):
    repo.add_whitelist_symbol(WhitelistSymbol("005930", "삼성전자", "KRX", "LARGE_CAP_TEST"))
    cid = repo.add_trade_condition(
        symbol="005930", side="BUY", target_price=70000,
        quantity=1, order_type="LIMIT", auto_enabled=True,
    )
    assert cid is not None
    conds = repo.list_conditions()
    assert any(c["id"] == cid for c in conds)


def test_list_active_conditions_filters_status(repo):
    repo.add_whitelist_symbol(WhitelistSymbol("005930", "삼성전자", "KRX", "LARGE_CAP_TEST"))
    cid = repo.add_trade_condition(
        symbol="005930", side="BUY", target_price=70000, quantity=1,
        order_type="LIMIT", auto_enabled=True,
    )
    active = repo.list_active_conditions()
    assert any(c["id"] == cid for c in active)
    repo.update_condition_status(cid, "TRIGGERED")
    active2 = repo.list_active_conditions()
    assert not any(c["id"] == cid for c in active2)


# ---- today_order_amount ----
def test_today_order_amount_zero_initially(repo):
    assert repo.today_order_amount() == 0.0
