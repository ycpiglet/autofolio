"""Paper-mode scenario matrix for engine/risk/UI behavior.

These tests use an isolated temporary DB and MockBrokerClient. They validate the
same control surfaces used by paper trading without placing live KIS orders.
"""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from app.brokers.base import OrderResult
from app.brokers.mock.mock_client import MockBrokerClient
from app.common.enums import ConditionStatus, OrderStatus
from app.database.repositories import Repository, WhitelistSymbol
from app.database.sqlite_db import get_connection, initialize_database
from app.engine.live_trading_engine import LiveTradingEngine


def _make_env(
    monkeypatch,
    *,
    symbol: str = "005930",
    price: float = 70_000.0,
    fill_limit_orders: bool = True,
    whitelisted: bool = True,
    auto_enabled: bool = True,
    kill_switch: bool = False,
    global_mode: str = "L2",
) -> tuple[Repository, MockBrokerClient, LiveTradingEngine]:
    tmp = TemporaryDirectory()
    db_path = Path(tmp.name) / "scenario.db"
    initialize_database(db_path)

    repo = Repository(db_path)
    repo._tmpdir = tmp  # keep TemporaryDirectory alive for the test lifetime
    repo.set_system_state("auto_trading_enabled", "true" if auto_enabled else "false")
    repo.set_system_state("kill_switch_active", "true" if kill_switch else "false")
    repo.set_system_state("global_mode", global_mode)
    if whitelisted:
        repo.add_whitelist_symbol(
            WhitelistSymbol(symbol=symbol, name=symbol, market="KRX", role="LARGE_CAP_TEST")
        )

    import app.risk.safety_checker as safety_checker_module

    monkeypatch.setattr(
        safety_checker_module,
        "is_within_trading_window",
        lambda *args, **kwargs: True,
    )

    broker = MockBrokerClient(prices={symbol: price}, fill_limit_orders=fill_limit_orders)
    engine = LiveTradingEngine(broker=broker, repo=repo)
    engine.order_flow.order_timeout_sec = 0
    return repo, broker, engine


def _run_scenario(
    monkeypatch,
    *,
    symbol: str = "005930",
    price: float = 70_000.0,
    side: str = "BUY",
    target_price: float = 70_000.0,
    quantity: int = 1,
    order_type: str = "LIMIT",
    allow_market_fallback: bool = False,
    fill_limit_orders: bool = True,
    whitelisted: bool = True,
    auto_enabled: bool = True,
    kill_switch: bool = False,
    global_mode: str = "L2",
) -> tuple[Repository, MockBrokerClient, list[str], int]:
    repo, broker, engine = _make_env(
        monkeypatch,
        symbol=symbol,
        price=price,
        fill_limit_orders=fill_limit_orders,
        whitelisted=whitelisted,
        auto_enabled=auto_enabled,
        kill_switch=kill_switch,
        global_mode=global_mode,
    )
    condition_id = repo.add_trade_condition(
        symbol=symbol,
        side=side,
        target_price=target_price,
        quantity=quantity,
        order_type=order_type,
        allow_market_fallback=allow_market_fallback,
        auto_enabled=True,
        created_by="SCENARIO-MATRIX",
    )
    messages = engine.run_once()
    return repo, broker, messages, condition_id


def _set_order_log_local_today(repo: Repository, order_log_id: int) -> None:
    """Make synthetic prior orders align with KST-local daily limit checks."""
    with get_connection(repo.db_path) as conn:
        conn.execute(
            "UPDATE order_logs SET created_at = datetime('now', 'localtime') WHERE id = ?",
            (order_log_id,),
        )


@pytest.mark.parametrize(
    ("name", "kwargs", "expected"),
    [
        (
            "buy_limit_triggered_fills",
            {"price": 69_800.0, "side": "BUY", "target_price": 70_000.0},
            {"executed": True, "statuses": [OrderStatus.FILLED.value], "condition": ConditionStatus.TRIGGERED.value},
        ),
        (
            "buy_limit_not_triggered_no_order",
            {"price": 70_500.0, "side": "BUY", "target_price": 70_000.0},
            {"executed": False, "statuses": [], "condition": ConditionStatus.ACTIVE.value},
        ),
        (
            "sell_limit_triggered_fills",
            {"price": 72_000.0, "side": "SELL", "target_price": 70_000.0},
            {"executed": True, "statuses": [OrderStatus.FILLED.value], "condition": ConditionStatus.TRIGGERED.value},
        ),
        (
            "kill_switch_blocks",
            {"price": 69_800.0, "kill_switch": True},
            {"executed": False, "statuses": [], "condition": ConditionStatus.ACTIVE.value, "message": "Kill switch"},
        ),
        (
            "auto_disabled_blocks",
            {"price": 69_800.0, "auto_enabled": False},
            {"executed": False, "statuses": [], "condition": ConditionStatus.ACTIVE.value, "message": "Auto trading is disabled"},
        ),
        (
            "global_l1_blocks",
            {"price": 69_800.0, "global_mode": "L1"},
            {"executed": False, "statuses": [], "condition": ConditionStatus.ACTIVE.value, "message": "Autonomy level L1"},
        ),
        (
            "not_whitelisted_blocks",
            {"price": 69_800.0, "whitelisted": False},
            {"executed": False, "statuses": [], "condition": ConditionStatus.ACTIVE.value, "message": "not enabled in whitelist"},
        ),
        (
            "pending_limit_cancels_without_fallback",
            {"price": 69_800.0, "fill_limit_orders": False},
            {"executed": False, "statuses": [OrderStatus.CANCELED.value], "condition": ConditionStatus.TRIGGERED.value},
        ),
        (
            "pending_limit_market_fallback_fills",
            {"price": 69_800.0, "fill_limit_orders": False, "allow_market_fallback": True},
            {"executed": True, "statuses": [OrderStatus.FILLED.value, OrderStatus.CANCELED.value], "condition": ConditionStatus.TRIGGERED.value},
        ),
    ],
)
def test_engine_scenario_matrix(monkeypatch, name, kwargs, expected):
    repo, _, messages, condition_id = _run_scenario(monkeypatch, **kwargs)

    logs = [
        row for row in repo.list_order_logs(limit=10)
        if row["condition_id"] == condition_id
    ]
    statuses = [row["order_status"] for row in logs]
    condition = repo.get_condition(condition_id)

    assert statuses == expected["statuses"], name
    assert condition["status"] == expected["condition"], name
    if expected["executed"]:
        assert any("filled" in msg.lower() for msg in messages), name
    if expected.get("message"):
        assert any(expected["message"].lower() in msg.lower() for msg in messages), name


def test_symbol_l1_overrides_global_l2(monkeypatch):
    repo, _, engine = _make_env(monkeypatch, price=69_800.0, global_mode="L2")
    repo.set_system_state("symbol_mode_005930", "L1")
    cid = repo.add_trade_condition(
        symbol="005930",
        side="BUY",
        target_price=70_000.0,
        quantity=1,
        order_type="LIMIT",
        auto_enabled=True,
    )

    messages = engine.run_once()

    assert repo.list_order_logs() == []
    assert repo.get_condition(cid)["status"] == ConditionStatus.ACTIVE.value
    assert any("Autonomy level L1".lower() in msg.lower() for msg in messages)


def test_max_order_amount_blocks_non_exception_quantity(monkeypatch):
    repo, _, engine = _make_env(monkeypatch, price=70_000.0)
    repo.update_global_risk_limit(max_order_amount=100_000.0)
    cid = repo.add_trade_condition(
        symbol="005930",
        side="BUY",
        target_price=80_000.0,
        quantity=2,
        order_type="LIMIT",
        auto_enabled=True,
    )

    messages = engine.run_once()

    assert repo.list_order_logs() == []
    assert repo.get_condition(cid)["status"] == ConditionStatus.ACTIVE.value
    assert any("exceeds max order amount" in msg for msg in messages)


def test_daily_order_amount_limit_blocks_new_order(monkeypatch):
    repo, _, engine = _make_env(monkeypatch, price=70_000.0)
    repo.update_global_risk_limit(max_daily_amount=300_000.0)
    previous_order_id = repo.create_order_log(
        condition_id=None,
        symbol="005930",
        side="BUY",
        order_type="MARKET",
        order_price=None,
        current_price=250_000.0,
        quantity=1,
        kis_order_id="PREVIOUS",
        order_status=OrderStatus.FILLED.value,
    )
    _set_order_log_local_today(repo, previous_order_id)
    cid = repo.add_trade_condition(
        symbol="005930",
        side="BUY",
        target_price=80_000.0,
        quantity=1,
        order_type="LIMIT",
        auto_enabled=True,
    )

    messages = engine.run_once()

    assert [row for row in repo.list_order_logs() if row["condition_id"] == cid] == []
    assert any("Daily order amount limit exceeded" in msg for msg in messages)


def test_market_order_pending_then_filled_like_kis(monkeypatch):
    repo, broker, engine = _make_env(monkeypatch, price=70_000.0)
    pending = OrderResult("KIS-PENDING-1", OrderStatus.PENDING, message="KIS order accepted")
    filled = OrderResult(
        "KIS-PENDING-1",
        OrderStatus.FILLED,
        filled_price=70_000.0,
        filled_quantity=1,
        message="Order filled.",
    )

    def place_order(request):
        broker._orders[pending.broker_order_id] = filled
        return pending

    broker.place_order = place_order  # type: ignore[method-assign]
    cid = repo.add_trade_condition(
        symbol="005930",
        side="BUY",
        target_price=80_000.0,
        quantity=1,
        order_type="MARKET",
        auto_enabled=True,
    )

    messages = engine.run_once()

    logs = [row for row in repo.list_order_logs() if row["condition_id"] == cid]
    executions = repo.list_order_logs()
    assert logs[0]["order_status"] == OrderStatus.FILLED.value
    assert repo.get_condition(cid)["status"] == ConditionStatus.TRIGGERED.value
    assert any("Order filled" in msg or "filled" in msg.lower() for msg in messages)
    assert executions


def test_market_order_still_pending_marks_condition_error(monkeypatch):
    repo, broker, engine = _make_env(monkeypatch, price=70_000.0)
    pending = OrderResult("KIS-PENDING-2", OrderStatus.PENDING, message="KIS order accepted")

    def place_order(request):
        broker._orders[pending.broker_order_id] = pending
        return pending

    broker.place_order = place_order  # type: ignore[method-assign]
    cid = repo.add_trade_condition(
        symbol="005930",
        side="BUY",
        target_price=80_000.0,
        quantity=1,
        order_type="MARKET",
        auto_enabled=True,
    )

    messages = engine.run_once()

    logs = [row for row in repo.list_order_logs() if row["condition_id"] == cid]
    assert logs[0]["order_status"] == OrderStatus.PENDING.value
    assert repo.get_condition(cid)["status"] == ConditionStatus.ERROR.value
    assert any("still pending" in msg for msg in messages)


def test_three_failures_trip_circuit_breaker_on_next_run(monkeypatch):
    repo, broker, engine = _make_env(monkeypatch, price=69_800.0)

    def fail_order(request):
        return OrderResult("FAIL", OrderStatus.FAILED, message="forced failure")

    broker.place_order = fail_order  # type: ignore[method-assign]
    for idx in range(3):
        repo.add_trade_condition(
            symbol="005930",
            side="BUY",
            target_price=70_000.0 + idx,
            quantity=1,
            order_type="LIMIT",
            auto_enabled=True,
        )
        engine.run_once()

    repo.add_trade_condition(
        symbol="005930",
        side="BUY",
        target_price=70_000.0,
        quantity=1,
        order_type="LIMIT",
        auto_enabled=True,
    )
    messages = engine.run_once()

    assert repo.get_system_state("auto_trading_enabled") == "false"
    assert any("Circuit breaker" in msg for msg in messages)


def test_ui_backend_reflects_filled_scenario(monkeypatch):
    repo, broker, engine = _make_env(monkeypatch, symbol="069500", price=35_000.0)
    cid = repo.add_trade_condition(
        symbol="069500",
        side="BUY",
        target_price=36_000.0,
        quantity=2,
        order_type="LIMIT",
        auto_enabled=True,
    )
    engine.run_once()

    from app.ui import backend

    monkeypatch.setattr(backend, "_ctx", lambda: (repo, broker, engine, None))
    holdings = backend.holdings_df()
    fills = backend.recent_fills(limit=5)

    assert repo.get_condition(cid)["status"] == ConditionStatus.TRIGGERED.value
    assert holdings[holdings["티커"] == "069500"].iloc[0]["수량"] == 2
    assert "069500" in fills["종목"].tolist()
