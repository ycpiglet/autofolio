from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from app.brokers.base import PriceQuote
from app.brokers.mock.mock_client import MockBrokerClient
from app.common.enums import ConditionStatus
from app.database.repositories import Repository, WhitelistSymbol
from app.database.sqlite_db import initialize_database
from app.engine.live_trading_engine import LiveTradingEngine
from app.risk.safety_checker import SafetyChecker


def _env(monkeypatch, *, symbol: str = "005930", role: str = "LARGE_CAP_TEST", market: str = "KRX"):
    tmp = TemporaryDirectory()
    db_path = Path(tmp.name) / "r3.db"
    initialize_database(db_path)
    repo = Repository(db_path)
    repo._tmpdir = tmp
    repo.add_whitelist_symbol(WhitelistSymbol(symbol=symbol, name=symbol, market=market, role=role))
    repo.set_system_state("auto_trading_enabled", "true")
    repo.set_system_state("kill_switch_active", "false")
    repo.set_system_state("global_mode", "L3")
    import app.risk.safety_checker as sc_mod

    monkeypatch.setattr(sc_mod, "is_krx_holiday", lambda d: False)
    return repo, SafetyChecker(repo)


def _cond(**updates):
    condition = {
        "id": 1,
        "symbol": "005930",
        "side": "BUY",
        "quantity": 1,
        "status": "ACTIVE",
        "cooldown_until": None,
        "order_type": "LIMIT",
    }
    condition.update(updates)
    return condition


def test_halt_vi_and_disclosure_state_block_orders(monkeypatch):
    repo, checker = _env(monkeypatch)
    import app.risk.safety_checker as sc_mod

    monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
    for key, expected in [
        ("market_halt_005930", "halt"),
        ("vi_active_005930", "volatility"),
        ("disclosure_block_005930", "disclosure"),
    ]:
        repo.set_system_state(key, "true")
        result = checker.check(condition=_cond(), current_price=70_000, now=datetime.now())
        assert not result.allowed
        assert expected in result.reason.lower()
        repo.set_system_state(key, "false")


def test_after_hours_session_uses_dedicated_window(monkeypatch):
    _repo, checker = _env(monkeypatch)
    result = checker.check(
        condition=_cond(order_session="AFTER_CLOSE_SINGLE"),
        current_price=70_000,
        now=datetime(2026, 6, 17, 15, 45),
    )
    assert result.allowed, result.reason

    blocked = checker.check(
        condition=_cond(order_session="AFTER_CLOSE_SINGLE"),
        current_price=70_000,
        now=datetime(2026, 6, 17, 15, 20),
    )
    assert not blocked.allowed
    assert "after_close_single" in blocked.reason


def test_credit_and_short_sell_require_l3(monkeypatch):
    repo, checker = _env(monkeypatch)
    import app.risk.safety_checker as sc_mod

    monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
    repo.set_system_state("global_mode", "L2")
    result = checker.check(
        condition=_cond(side="SELL", sell_type="05"),
        current_price=70_000,
        now=datetime.now(),
    )
    assert not result.allowed
    assert "credit/short" in result.reason.lower()

    repo.set_system_state("global_mode", "L3")
    allowed = checker.check(
        condition=_cond(side="SELL", sell_type="05"),
        current_price=70_000,
        now=datetime.now(),
    )
    assert allowed.allowed, allowed.reason


def test_derivatives_are_mock_disabled_by_default(monkeypatch):
    repo, checker = _env(monkeypatch, symbol="101V6000", role="FUTURES_TEST")
    import app.risk.safety_checker as sc_mod

    monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
    condition = _cond(symbol="101V6000", product_type="FUTURES")
    blocked = checker.check(condition=condition, current_price=350.0, now=datetime.now())
    assert not blocked.allowed
    assert "mock-only" in blocked.reason

    repo.set_system_state("derivatives_mock_enabled", "true")
    allowed = checker.check(condition=condition, current_price=350.0, now=datetime.now())
    assert allowed.allowed, allowed.reason


def test_alternative_product_unit_and_price_limit_policy(monkeypatch):
    _repo, checker = _env(monkeypatch, symbol="KR-BOND-1", role="BOND_DIRECT")
    import app.risk.safety_checker as sc_mod

    monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
    invalid_unit = checker.check(
        condition=_cond(symbol="KR-BOND-1", product_type="BOND", quantity=3),
        current_price=10_000.0,
        now=datetime.now(),
    )
    assert not invalid_unit.allowed
    assert "multiple of 10" in invalid_unit.reason

    price_limit = checker.check(
        condition=_cond(symbol="KR-BOND-1", product_type="BOND", quantity=10, reference_price=10_000.0),
        current_price=14_000.0,
        now=datetime.now(),
    )
    assert not price_limit.allowed
    assert "exceeds limit" in price_limit.reason


def test_stale_or_invalid_market_data_blocks_before_order(monkeypatch):
    tmp = TemporaryDirectory()
    db_path = Path(tmp.name) / "dq.db"
    initialize_database(db_path)
    repo = Repository(db_path)
    repo._tmpdir = tmp
    repo.add_whitelist_symbol(WhitelistSymbol(symbol="005930", name="삼성전자", market="KRX", role="LARGE_CAP_TEST"))
    repo.set_system_state("auto_trading_enabled", "true")
    repo.set_system_state("kill_switch_active", "false")
    repo.set_system_state("global_mode", "L3")
    import app.risk.safety_checker as sc_mod

    monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
    monkeypatch.setattr(sc_mod, "is_krx_holiday", lambda d: False)

    class StaleBroker(MockBrokerClient):
        def get_current_price(self, symbol: str) -> PriceQuote:
            return PriceQuote(
                symbol=symbol,
                price=70_000.0,
                as_of=datetime.now() - timedelta(hours=1),
                source="test-stale",
            )

    engine = LiveTradingEngine(broker=StaleBroker(prices={"005930": 70_000.0}), repo=repo)
    cid = repo.add_trade_condition(
        symbol="005930",
        side="BUY",
        target_price=80_000.0,
        quantity=1,
        order_type="LIMIT",
        auto_enabled=True,
    )

    messages = engine.run_once()

    assert repo.list_order_logs() == []
    assert repo.get_condition(cid)["status"] == ConditionStatus.ACTIVE.value
    assert any("market data rejected" in message.lower() for message in messages)
