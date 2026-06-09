"""Unit tests for C11 circuit breaker logic.

Covers:
  - Repository.today_realized_pnl()
  - Repository.increment_consecutive_failures() / reset_consecutive_failures()
  - SafetyChecker: consecutive failure trip
  - SafetyChecker: daily-loss trip
  - OrderFlow: failure increments counter, fill resets it
"""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

import pytest

from app.brokers.mock.mock_client import MockBrokerClient
from app.common.enums import OrderStatus
from app.database.repositories import Repository, WhitelistSymbol
from app.database.sqlite_db import initialize_database
from app.engine.order_flow import OrderFlow
from app.risk.safety_checker import SafetyChecker


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def db(tmp_path):
    """Initialized SQLite DB in a temp directory."""
    db_path = tmp_path / "test_cb.db"
    initialize_database(db_path)
    return db_path


@pytest.fixture()
def repo(db):
    r = Repository(db)
    r.set_system_state("auto_trading_enabled", "true")
    r.set_system_state("kill_switch_active", "false")
    r.add_whitelist_symbol(
        WhitelistSymbol(symbol="005930", name="삼성전자", market="KRX", role="LARGE_CAP_TEST")
    )
    return r


# ---------------------------------------------------------------------------
# C11-B: Repository methods
# ---------------------------------------------------------------------------

class TestTodayRealizedPnl:
    def test_returns_zero_when_no_executions(self, repo):
        assert repo.today_realized_pnl() == 0.0

    def test_sell_positive_buy_negative(self, repo):
        """SELL 체결 → 양수, BUY 체결 → 음수."""
        # Insert a BUY order log and execution
        buy_log_id = repo.create_order_log(
            condition_id=None,
            symbol="005930",
            side="BUY",
            order_type="LIMIT",
            order_price=70000.0,
            current_price=70000.0,
            quantity=1,
            kis_order_id="B1",
            order_status="FILLED",
        )
        repo.create_execution_log(
            order_log_id=buy_log_id,
            symbol="005930",
            filled_price=70000.0,
            filled_quantity=1,
        )

        pnl = repo.today_realized_pnl()
        assert pnl == pytest.approx(-70000.0)

        # Add a SELL execution
        sell_log_id = repo.create_order_log(
            condition_id=None,
            symbol="005930",
            side="SELL",
            order_type="LIMIT",
            order_price=75000.0,
            current_price=75000.0,
            quantity=1,
            kis_order_id="S1",
            order_status="FILLED",
        )
        repo.create_execution_log(
            order_log_id=sell_log_id,
            symbol="005930",
            filled_price=75000.0,
            filled_quantity=1,
        )

        pnl = repo.today_realized_pnl()
        assert pnl == pytest.approx(-70000.0 + 75000.0)


class TestConsecutiveFailures:
    def test_initial_value_is_zero(self, repo):
        assert repo.get_system_state("consecutive_order_failures", "0") == "0"

    def test_increment(self, repo):
        repo.increment_consecutive_failures()
        assert repo.get_system_state("consecutive_order_failures") == "1"
        repo.increment_consecutive_failures()
        assert repo.get_system_state("consecutive_order_failures") == "2"

    def test_reset(self, repo):
        repo.increment_consecutive_failures()
        repo.increment_consecutive_failures()
        repo.reset_consecutive_failures()
        assert repo.get_system_state("consecutive_order_failures") == "0"


# ---------------------------------------------------------------------------
# C11-A: SafetyChecker circuit breaker
# ---------------------------------------------------------------------------

def _make_condition(repo):
    cid = repo.add_trade_condition(
        symbol="005930",
        side="BUY",
        target_price=70000.0,
        quantity=1,
        order_type="LIMIT",
        auto_enabled=True,
    )
    return repo.get_condition(cid)


class TestSafetyCheckerCircuitBreaker:
    def test_consecutive_failures_trips_at_3(self, repo):
        checker = SafetyChecker(repo)
        condition = _make_condition(repo)

        # 2 failures — still allowed
        repo.set_system_state("consecutive_order_failures", "2")
        with patch("app.risk.safety_checker.is_within_trading_window", return_value=True):
            result = checker.check(condition=condition, current_price=69900.0)
        assert result.allowed

        # 3 failures — tripped
        repo.set_system_state("consecutive_order_failures", "3")
        result = checker.check(condition=condition, current_price=69900.0)
        assert not result.allowed
        assert "consecutive" in result.reason.lower()
        # auto_trading_enabled must be disabled
        assert repo.get_system_state("auto_trading_enabled") == "false"

    def test_daily_loss_trips_when_loss_exceeds_threshold(self, repo, monkeypatch):
        """당일 실현 손실이 max_daily_amount 의 threshold_pct% 이상이면 트립."""
        import app.risk.safety_checker as sc_mod
        monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)

        checker = SafetyChecker(repo)
        condition = _make_condition(repo)

        # Set threshold to 3% and max_daily_amount to 1_000_000
        repo.set_system_state("circuit_breaker_threshold_pct", "3.0")
        repo.update_global_risk_limit(max_daily_amount=1_000_000.0)

        # Inject a BUY execution that causes -40_000 PnL (4% of 1M)
        log_id = repo.create_order_log(
            condition_id=None, symbol="005930", side="BUY",
            order_type="LIMIT", order_price=40000.0, current_price=40000.0,
            quantity=1, kis_order_id="X1", order_status="FILLED",
        )
        repo.create_execution_log(
            order_log_id=log_id, symbol="005930",
            filled_price=40000.0, filled_quantity=1,
        )

        result = checker.check(condition=condition, current_price=69900.0)
        assert not result.allowed
        assert "circuit breaker" in result.reason.lower()
        assert repo.get_system_state("auto_trading_enabled") == "false"

    def test_daily_loss_below_threshold_does_not_trip(self, repo):
        checker = SafetyChecker(repo)
        condition = _make_condition(repo)

        repo.set_system_state("circuit_breaker_threshold_pct", "3.0")
        repo.update_global_risk_limit(max_daily_amount=1_000_000.0)

        # 2% loss — below threshold
        log_id = repo.create_order_log(
            condition_id=None, symbol="005930", side="BUY",
            order_type="LIMIT", order_price=20000.0, current_price=20000.0,
            quantity=1, kis_order_id="X2", order_status="FILLED",
        )
        repo.create_execution_log(
            order_log_id=log_id, symbol="005930",
            filled_price=20000.0, filled_quantity=1,
        )

        with patch("app.risk.safety_checker.is_within_trading_window", return_value=True):
            result = checker.check(condition=condition, current_price=69900.0)
        assert result.allowed


# ---------------------------------------------------------------------------
# C11-C: OrderFlow wires failure tracking
# ---------------------------------------------------------------------------

class TestOrderFlowFailureTracking:
    def _flow(self, repo, broker):
        checker = SafetyChecker(repo)
        return OrderFlow(broker=broker, repo=repo, safety_checker=checker, order_timeout_sec=0)

    def test_failed_order_increments_counter(self, repo, monkeypatch):
        import app.risk.safety_checker as sc_mod
        monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)

        broker = MockBrokerClient(prices={"005930": 69900.0})
        # Force place_order to return FAILED
        from app.brokers.base import OrderResult
        broker.place_order = MagicMock(
            return_value=OrderResult(
                broker_order_id=None,
                status=OrderStatus.FAILED,
                filled_price=None,
                filled_quantity=None,
                message="Broker error",
            )
        )

        cid = repo.add_trade_condition(
            symbol="005930", side="BUY", target_price=70000.0, quantity=1,
            order_type="LIMIT", auto_enabled=True,
        )
        condition = repo.get_condition(cid)
        flow = self._flow(repo, broker)
        flow.process_condition_once(condition)

        assert repo.get_system_state("consecutive_order_failures") == "1"

    def test_filled_order_resets_counter(self, repo, monkeypatch):
        import app.risk.safety_checker as sc_mod
        monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)

        repo.set_system_state("consecutive_order_failures", "2")

        broker = MockBrokerClient(prices={"005930": 69900.0})
        cid = repo.add_trade_condition(
            symbol="005930", side="BUY", target_price=70000.0, quantity=1,
            order_type="LIMIT", auto_enabled=True,
        )
        condition = repo.get_condition(cid)
        flow = self._flow(repo, broker)
        result = flow.process_condition_once(condition)

        assert result.executed
        assert repo.get_system_state("consecutive_order_failures") == "0"
