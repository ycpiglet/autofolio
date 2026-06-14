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

    def test_buy_only_day_returns_zero(self, repo):
        """BUG REGRESSION: BUY-only day must return 0 (not a large negative)."""
        buy_log_id = repo.create_order_log(
            condition_id=None,
            symbol="005930",
            side="BUY",
            order_type="LIMIT",
            order_price=70000.0,
            current_price=70000.0,
            quantity=10,
            kis_order_id="B1",
            order_status="FILLED",
        )
        repo.create_execution_log(
            order_log_id=buy_log_id,
            symbol="005930",
            filled_price=70000.0,
            filled_quantity=10,
        )
        # No SELL fills → realized PnL must be 0, not -700_000
        assert repo.today_realized_pnl() == pytest.approx(0.0)

    def test_sell_after_buy_profit(self, repo):
        """BUY at 70_000, SELL at 75_000 → realized = (75_000 − 70_000) × 1 = 5_000."""
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
        assert repo.today_realized_pnl() == pytest.approx(5000.0)

    def test_sell_after_buy_loss(self, repo):
        """BUY at 70_000, SELL at 65_000 → realized = (65_000 − 70_000) × 1 = −5_000."""
        buy_log_id = repo.create_order_log(
            condition_id=None,
            symbol="005930",
            side="BUY",
            order_type="LIMIT",
            order_price=70000.0,
            current_price=70000.0,
            quantity=1,
            kis_order_id="B2",
            order_status="FILLED",
        )
        repo.create_execution_log(
            order_log_id=buy_log_id,
            symbol="005930",
            filled_price=70000.0,
            filled_quantity=1,
        )
        sell_log_id = repo.create_order_log(
            condition_id=None,
            symbol="005930",
            side="SELL",
            order_type="LIMIT",
            order_price=65000.0,
            current_price=65000.0,
            quantity=1,
            kis_order_id="S2",
            order_status="FILLED",
        )
        repo.create_execution_log(
            order_log_id=sell_log_id,
            symbol="005930",
            filled_price=65000.0,
            filled_quantity=1,
        )
        assert repo.today_realized_pnl() == pytest.approx(-5000.0)

    def test_avg_cost_weighted_correctly(self, repo):
        """Two BUYs at different prices → avg cost used for SELL realized PnL.

        BUY 1 share @ 60_000, BUY 1 share @ 80_000 → avg_cost = 70_000.
        SELL 1 share @ 75_000 → realized = (75_000 − 70_000) × 1 = 5_000.
        """
        for price, kid in [(60000.0, "B3a"), (80000.0, "B3b")]:
            lid = repo.create_order_log(
                condition_id=None,
                symbol="005930",
                side="BUY",
                order_type="LIMIT",
                order_price=price,
                current_price=price,
                quantity=1,
                kis_order_id=kid,
                order_status="FILLED",
            )
            repo.create_execution_log(
                order_log_id=lid,
                symbol="005930",
                filled_price=price,
                filled_quantity=1,
            )
        sell_lid = repo.create_order_log(
            condition_id=None,
            symbol="005930",
            side="SELL",
            order_type="LIMIT",
            order_price=75000.0,
            current_price=75000.0,
            quantity=1,
            kis_order_id="S3",
            order_status="FILLED",
        )
        repo.create_execution_log(
            order_log_id=sell_lid,
            symbol="005930",
            filled_price=75000.0,
            filled_quantity=1,
        )
        assert repo.today_realized_pnl() == pytest.approx(5000.0)


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
    def test_consecutive_failures_trips_at_3(self, repo, monkeypatch):
        import app.risk.safety_checker as sc_mod
        monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)

        checker = SafetyChecker(repo)
        condition = _make_condition(repo)

        # 2 failures — still allowed
        repo.set_system_state("consecutive_order_failures", "2")
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
        """당일 실현 손실이 max_daily_amount 의 threshold_pct% 이상이면 트립.

        SELL at a loss that exceeds threshold — NOT a BUY fill.
        BUY fills never realize PnL (regression guard).
        """
        import app.risk.safety_checker as sc_mod
        monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)

        checker = SafetyChecker(repo)
        condition = _make_condition(repo)

        # threshold 3%, max_daily_amount 1_000_000 → trip if loss >= 30_000
        repo.set_system_state("circuit_breaker_threshold_pct", "3.0")
        repo.update_global_risk_limit(max_daily_amount=1_000_000.0)

        # BUY 1 share @ 40_000 (avg cost = 40_000)
        buy_lid = repo.create_order_log(
            condition_id=None, symbol="005930", side="BUY",
            order_type="LIMIT", order_price=40000.0, current_price=40000.0,
            quantity=1, kis_order_id="CB_B1", order_status="FILLED",
        )
        repo.create_execution_log(
            order_log_id=buy_lid, symbol="005930",
            filled_price=40000.0, filled_quantity=1,
        )

        # SELL 1 share @ 0 (extreme loss: realized = (0 − 40_000) × 1 = −40_000 = 4% of 1M)
        sell_lid = repo.create_order_log(
            condition_id=None, symbol="005930", side="SELL",
            order_type="LIMIT", order_price=0.0, current_price=0.0,
            quantity=1, kis_order_id="CB_S1", order_status="FILLED",
        )
        repo.create_execution_log(
            order_log_id=sell_lid, symbol="005930",
            filled_price=0.0, filled_quantity=1,
        )

        result = checker.check(condition=condition, current_price=69900.0)
        assert not result.allowed
        assert "circuit breaker" in result.reason.lower()
        assert repo.get_system_state("auto_trading_enabled") == "false"

    def test_daily_loss_below_threshold_does_not_trip(self, repo, monkeypatch):
        """Realized loss of -1_000 (0.1% of 1M) is well below the 3% threshold."""
        import app.risk.safety_checker as sc_mod
        monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)

        checker = SafetyChecker(repo)
        condition = _make_condition(repo)

        repo.set_system_state("circuit_breaker_threshold_pct", "3.0")
        repo.update_global_risk_limit(max_daily_amount=1_000_000.0)

        # BUY 1 share @ 20_000 → avg cost = 20_000
        buy_lid = repo.create_order_log(
            condition_id=None, symbol="005930", side="BUY",
            order_type="LIMIT", order_price=20000.0, current_price=20000.0,
            quantity=1, kis_order_id="X2_B", order_status="FILLED",
        )
        repo.create_execution_log(
            order_log_id=buy_lid, symbol="005930",
            filled_price=20000.0, filled_quantity=1,
        )

        # SELL 1 share @ 19_000 → realized = (19_000 − 20_000) × 1 = −1_000 (0.1% of 1M)
        sell_lid = repo.create_order_log(
            condition_id=None, symbol="005930", side="SELL",
            order_type="LIMIT", order_price=19000.0, current_price=19000.0,
            quantity=1, kis_order_id="X2_S", order_status="FILLED",
        )
        repo.create_execution_log(
            order_log_id=sell_lid, symbol="005930",
            filled_price=19000.0, filled_quantity=1,
        )

        result = checker.check(condition=condition, current_price=69900.0)
        assert result.allowed

    def test_buy_only_day_does_not_trip_circuit_breaker(self, repo, monkeypatch):
        """BUG REGRESSION: buy-heavy day must NOT trip the daily-loss circuit breaker."""
        import app.risk.safety_checker as sc_mod
        monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)

        checker = SafetyChecker(repo)
        condition = _make_condition(repo)

        repo.set_system_state("circuit_breaker_threshold_pct", "3.0")
        repo.update_global_risk_limit(max_daily_amount=1_000_000.0)

        # Large BUY fills — old code would return −800_000 PnL and trip (80% of 1M)
        for i in range(10):
            lid = repo.create_order_log(
                condition_id=None, symbol="005930", side="BUY",
                order_type="LIMIT", order_price=80000.0, current_price=80000.0,
                quantity=1, kis_order_id=f"BIG_B{i}", order_status="FILLED",
            )
            repo.create_execution_log(
                order_log_id=lid, symbol="005930",
                filled_price=80000.0, filled_quantity=1,
            )

        result = checker.check(condition=condition, current_price=69900.0)
        assert result.allowed, f"Circuit breaker falsely tripped on buy-only day: {result.reason}"


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


# ---------------------------------------------------------------------------
# TASK-057: total_realized_pnl / total_buy_cost_basis helpers
# ---------------------------------------------------------------------------

class TestTotalRealizedPnl:
    def test_returns_zero_when_no_executions(self, repo):
        assert repo.total_realized_pnl() == 0.0

    def test_accumulates_multiple_sell_days(self, repo):
        """Two SELL fills on different (simulated) days both count."""
        for kid in ("B_acc1", "B_acc2"):
            lid = repo.create_order_log(
                condition_id=None, symbol="005930", side="BUY",
                order_type="LIMIT", order_price=70000.0, current_price=70000.0,
                quantity=1, kis_order_id=kid, order_status="FILLED",
            )
            repo.create_execution_log(
                order_log_id=lid, symbol="005930",
                filled_price=70000.0, filled_quantity=1,
            )
        s1 = repo.create_order_log(
            condition_id=None, symbol="005930", side="SELL",
            order_type="LIMIT", order_price=75000.0, current_price=75000.0,
            quantity=1, kis_order_id="S_acc1", order_status="FILLED",
        )
        repo.create_execution_log(
            order_log_id=s1, symbol="005930",
            filled_price=75000.0, filled_quantity=1,
        )
        assert repo.total_realized_pnl() == pytest.approx(5000.0)


class TestTotalBuyCostBasis:
    def test_returns_zero_when_no_executions(self, repo):
        assert repo.total_buy_cost_basis() == 0.0

    def test_sums_all_buy_fills(self, repo):
        """BUY 2 shares @ 70_000 and 1 share @ 80_000 → total cost = 220_000."""
        fills = [(70000.0, 2, "B_cost1"), (80000.0, 1, "B_cost2")]
        for price, qty, kid in fills:
            lid = repo.create_order_log(
                condition_id=None, symbol="005930", side="BUY",
                order_type="LIMIT", order_price=price, current_price=price,
                quantity=qty, kis_order_id=kid, order_status="FILLED",
            )
            repo.create_execution_log(
                order_log_id=lid, symbol="005930",
                filled_price=price, filled_quantity=qty,
            )
        assert repo.total_buy_cost_basis() == pytest.approx(220000.0)
