from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.brokers.mock.mock_client import MockBrokerClient
from app.common.enums import ConditionStatus, OrderStatus
from app.database.repositories import Repository, WhitelistSymbol
from app.database.sqlite_db import initialize_database
from app.engine.live_trading_engine import LiveTradingEngine


def _make_env(tmp_path: Path, monkeypatch, broker: MockBrokerClient):
    db_path = tmp_path / "portfolio-reality.db"
    initialize_database(db_path)
    repo = Repository(db_path)
    repo.set_system_state("auto_trading_enabled", "true")
    repo.set_system_state("kill_switch_active", "false")
    repo.set_system_state("global_mode", "L2")
    repo.add_whitelist_symbol(WhitelistSymbol("005930", "삼성전자", "KRX", "LARGE_CAP_TEST"))

    import app.risk.safety_checker as safety_checker_module

    monkeypatch.setattr(safety_checker_module, "is_within_trading_window", lambda *a, **kw: True)
    engine = LiveTradingEngine(broker=broker, repo=repo)
    engine.order_flow.order_timeout_sec = 0
    return repo, engine


def _add_market_buy(repo: Repository, quantity: int = 1) -> int:
    return repo.add_trade_condition(
        symbol="005930",
        side="BUY",
        target_price=100_000.0,
        quantity=quantity,
        order_type="MARKET",
        auto_enabled=True,
        created_by="PORTFOLIO-REALITY-TEST",
    )


def test_engine_records_cash_shortage_as_failed_no_execution(tmp_path, monkeypatch):
    broker = MockBrokerClient(prices={"005930": 70_000.0}, cash_balance=50_000.0)
    repo, engine = _make_env(tmp_path, monkeypatch, broker)
    condition_id = _add_market_buy(repo)

    messages = engine.run_once()

    logs = [row for row in repo.list_order_logs() if row["condition_id"] == condition_id]
    assert logs[0]["order_status"] == OrderStatus.FAILED.value
    assert logs[0]["filled_price"] is None
    assert repo.get_condition(condition_id)["status"] == ConditionStatus.ERROR.value
    assert broker.get_positions() == []
    assert any("insufficient cash" in message for message in messages)


def test_engine_records_concentration_rejection_as_failed_no_execution(tmp_path, monkeypatch):
    broker = MockBrokerClient(
        prices={"005930": 70_000.0},
        cash_balance=100_000.0,
        max_position_weight=0.50,
    )
    repo, engine = _make_env(tmp_path, monkeypatch, broker)
    condition_id = _add_market_buy(repo)

    messages = engine.run_once()

    logs = [row for row in repo.list_order_logs() if row["condition_id"] == condition_id]
    assert logs[0]["order_status"] == OrderStatus.FAILED.value
    assert logs[0]["filled_quantity"] is None
    assert repo.get_condition(condition_id)["status"] == ConditionStatus.ERROR.value
    assert broker.get_positions() == []
    assert any("concentration" in message for message in messages)


def test_recent_fills_uses_execution_price_for_market_orders(tmp_path, monkeypatch):
    broker = MockBrokerClient(
        prices={"005930": 10_000.0},
        cash_balance=100_000.0,
        fee_rate=0.001,
        slippage_bps=50,
    )
    repo, engine = _make_env(tmp_path, monkeypatch, broker)
    condition_id = _add_market_buy(repo, quantity=2)
    engine.run_once()

    from app.services import backend

    monkeypatch.setattr(backend, "_ctx", lambda: (repo, broker, engine, None))
    fills = backend.recent_fills(limit=5)
    kpis = backend.kpis()

    assert repo.get_condition(condition_id)["status"] == ConditionStatus.TRIGGERED.value
    assert fills.iloc[0]["체결가"] == 10_050.0
    assert fills.iloc[0]["수량"] == 2
    assert round(kpis["총자산"], 1) == round(
        backend.holdings_df(include_dividends=False)["평가금액"].sum() + broker.get_cash_balance(),
        1,
    )


def test_recent_fills_falls_back_to_order_price_for_legacy_frames(monkeypatch):
    from app.services import backend

    logs = pd.DataFrame(
        [
            {
                "id": 1,
                "symbol": "005930",
                "side": "BUY",
                "quantity": 1,
                "order_price": 70_000.0,
                "order_status": "FILLED",
                "created_at": "2026-06-12 09:10:00",
            }
        ]
    )
    monkeypatch.setattr(backend, "list_order_logs", lambda limit=200: logs)

    fills = backend.recent_fills()

    assert fills.iloc[0]["체결가"] == 70_000.0
    assert fills.iloc[0]["수량"] == 1
