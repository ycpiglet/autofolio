"""Unit tests for OrderFlow._fallback_to_market and _wait_for_fill.

Focuses on the KIS-realistic case where place_order returns PENDING (not FILLED)
for market orders, verifying that the engine correctly polls via _wait_for_fill
rather than falling through to the old 'Market fallback failed' branch.
"""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

import pytest

from app.brokers.base import OrderResult
from app.brokers.mock.mock_client import MockBrokerClient
from app.common.enums import ConditionStatus, OrderStatus
from app.database.repositories import Repository, WhitelistSymbol
from app.database.sqlite_db import initialize_database
from app.engine.order_flow import OrderFlow
from app.risk.safety_checker import SafetyChecker


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_env(tmpdir: Path):
    """Initialise a test DB and return (repo, flow) with trading window patched open."""
    db_path = tmpdir / "test.db"
    initialize_database(db_path)

    repo = Repository(db_path)
    repo.set_system_state("auto_trading_enabled", "true")
    repo.set_system_state("kill_switch_active", "false")
    repo.add_whitelist_symbol(
        WhitelistSymbol(symbol="005930", name="삼성전자", market="KRX", role="LARGE_CAP_TEST")
    )

    broker = MockBrokerClient(prices={"005930": 70000.0}, fill_limit_orders=False)
    safety = SafetyChecker(repo)
    flow = OrderFlow(broker=broker, repo=repo, safety_checker=safety, order_timeout_sec=0)
    return repo, flow, broker


def _add_condition(repo: Repository, *, allow_market_fallback: bool = True) -> dict:
    cid = repo.add_trade_condition(
        symbol="005930",
        side="BUY",
        target_price=70000,
        quantity=1,
        order_type="LIMIT",
        allow_market_fallback=allow_market_fallback,
        auto_enabled=True,
    )
    return repo.get_condition(cid)


# ---------------------------------------------------------------------------
# 1. Market fallback — broker returns PENDING then FILLED on poll
# ---------------------------------------------------------------------------

def test_market_fallback_pending_then_filled(monkeypatch):
    """_fallback_to_market: place_order returns PENDING; poll returns FILLED.

    This is the realistic KIS paper/prod path.  The engine must call
    _wait_for_fill and ultimately report executed=True.
    """
    with TemporaryDirectory() as tmpdir:
        repo, flow, broker = _make_env(Path(tmpdir))
        condition = _add_condition(repo)

        import app.risk.safety_checker as sc_mod
        monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)

        # Override broker so market place_order returns PENDING
        pending_result = OrderResult(
            broker_order_id="MOCK-MKT-001",
            status=OrderStatus.PENDING,
            message="KIS order accepted: 주문접수",
        )
        filled_result = OrderResult(
            broker_order_id="MOCK-MKT-001",
            status=OrderStatus.FILLED,
            filled_price=70000.0,
            filled_quantity=1,
            message="Order filled.",
        )

        call_count = {"place": 0}

        original_place = broker.place_order

        def mock_place(request):
            call_count["place"] += 1
            if request.order_type.value == "MARKET":
                return pending_result
            return original_place(request)

        broker.place_order = mock_place  # type: ignore[method-assign]
        broker._orders["MOCK-MKT-001"] = filled_result

        result = flow.process_condition_once(condition)

        assert result.executed, f"Expected executed=True, got: {result.message}"
        assert "poll" in result.message.lower() or "filled" in result.message.lower()

        logs = repo.list_order_logs()
        market_log = next(l for l in logs if l["fallback_to_market"] == 1)
        assert market_log["order_status"] == OrderStatus.FILLED.value


# ---------------------------------------------------------------------------
# 2. Market fallback — broker returns PENDING then still PENDING after timeout
# ---------------------------------------------------------------------------

def test_market_fallback_pending_stays_pending(monkeypatch):
    """_wait_for_fill: order stays PENDING after poll — returns executed=False
    with informative message; condition is NOT marked ERROR (still open).
    """
    with TemporaryDirectory() as tmpdir:
        repo, flow, broker = _make_env(Path(tmpdir))
        condition = _add_condition(repo)

        import app.risk.safety_checker as sc_mod
        monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)

        pending_result = OrderResult(
            broker_order_id="MOCK-MKT-002",
            status=OrderStatus.PENDING,
            message="KIS order accepted",
        )

        original_place = broker.place_order

        def mock_place(request):
            if request.order_type.value == "MARKET":
                return pending_result
            return original_place(request)

        broker.place_order = mock_place  # type: ignore[method-assign]
        # get_order_status will also return PENDING (default from MockBrokerClient
        # when the order is stored as PENDING)
        broker._orders["MOCK-MKT-002"] = pending_result

        result = flow.process_condition_once(condition)

        assert not result.executed
        assert "pending" in result.message.lower()

        logs = repo.list_order_logs()
        market_log = next(l for l in logs if l["fallback_to_market"] == 1)
        assert market_log["order_status"] == OrderStatus.PENDING.value


# ---------------------------------------------------------------------------
# 3. Market fallback — broker returns PENDING then CANCELED on poll
# ---------------------------------------------------------------------------

def test_market_fallback_pending_then_canceled(monkeypatch):
    """_wait_for_fill: poll returns CANCELED — executed=False and condition ERROR."""
    with TemporaryDirectory() as tmpdir:
        repo, flow, broker = _make_env(Path(tmpdir))
        condition = _add_condition(repo)

        import app.risk.safety_checker as sc_mod
        monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)

        pending_result = OrderResult(
            broker_order_id="MOCK-MKT-003",
            status=OrderStatus.PENDING,
            message="KIS order accepted",
        )
        canceled_result = OrderResult(
            broker_order_id="MOCK-MKT-003",
            status=OrderStatus.CANCELED,
            message="Order canceled.",
        )

        original_place = broker.place_order

        def mock_place(request):
            if request.order_type.value == "MARKET":
                return pending_result
            return original_place(request)

        broker.place_order = mock_place  # type: ignore[method-assign]
        broker._orders["MOCK-MKT-003"] = canceled_result

        result = flow.process_condition_once(condition)

        assert not result.executed
        assert "cancel" in result.message.lower()

        logs = repo.list_order_logs()
        market_log = next(l for l in logs if l["fallback_to_market"] == 1)
        assert market_log["order_status"] == OrderStatus.CANCELED.value

        cond_after = repo.get_condition(condition["id"])
        assert cond_after["status"] == ConditionStatus.ERROR.value


# ---------------------------------------------------------------------------
# 4. Market fallback — broker returns PENDING then FAILED on poll
# ---------------------------------------------------------------------------

def test_market_fallback_pending_then_failed(monkeypatch):
    """_wait_for_fill: poll returns FAILED — executed=False and condition ERROR."""
    with TemporaryDirectory() as tmpdir:
        repo, flow, broker = _make_env(Path(tmpdir))
        condition = _add_condition(repo)

        import app.risk.safety_checker as sc_mod
        monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)

        pending_result = OrderResult(
            broker_order_id="MOCK-MKT-004",
            status=OrderStatus.PENDING,
            message="KIS order accepted",
        )
        failed_result = OrderResult(
            broker_order_id="MOCK-MKT-004",
            status=OrderStatus.FAILED,
            message="Broker internal error.",
        )

        original_place = broker.place_order

        def mock_place(request):
            if request.order_type.value == "MARKET":
                return pending_result
            return original_place(request)

        broker.place_order = mock_place  # type: ignore[method-assign]
        broker._orders["MOCK-MKT-004"] = failed_result

        result = flow.process_condition_once(condition)

        assert not result.executed
        assert "fail" in result.message.lower()

        logs = repo.list_order_logs()
        market_log = next(l for l in logs if l["fallback_to_market"] == 1)
        assert market_log["order_status"] == OrderStatus.FAILED.value

        cond_after = repo.get_condition(condition["id"])
        assert cond_after["status"] == ConditionStatus.ERROR.value


# ---------------------------------------------------------------------------
# 5. Market fallback — broker returns FILLED immediately (mock path, unchanged)
# ---------------------------------------------------------------------------

def test_market_fallback_immediate_fill(monkeypatch):
    """_fallback_to_market: place_order returns FILLED immediately (MockBrokerClient
    default for market orders).  No polling needed; executed=True.
    """
    with TemporaryDirectory() as tmpdir:
        repo, flow, broker = _make_env(Path(tmpdir))
        # For this test let market orders fill immediately
        condition = _add_condition(repo)

        import app.risk.safety_checker as sc_mod
        monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)

        # MockBrokerClient fills market orders immediately by default
        # (fill_limit_orders=False only affects limit orders)
        result = flow.process_condition_once(condition)

        assert result.executed
        logs = repo.list_order_logs()
        market_log = next(l for l in logs if l["fallback_to_market"] == 1)
        assert market_log["order_status"] == OrderStatus.FILLED.value
