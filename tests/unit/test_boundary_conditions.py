"""TASK-066: Boundary condition tests for safety-critical limit logic.

Tests exactly-at and just-over boundaries for:
- daily order amount (today_order_amount + order_amount vs max_daily_amount)
- per-order amount limit (max_order_amount)
- circuit-breaker daily-loss threshold (loss_pct exactly at vs just over)

TZ-robust: all paths gated by trading window are monkeypatched.
Tests must pass on a UTC machine.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from app.database.repositories import Repository, WhitelistSymbol
from app.database.sqlite_db import initialize_database
from app.risk.safety_checker import SafetyChecker


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def db(tmp_path: Path) -> Path:
    db_path = tmp_path / "test.db"
    initialize_database(db_path)
    return db_path


@pytest.fixture
def env(db: Path):
    """Repo + SafetyChecker with auto-trading enabled and symbol whitelisted."""
    repo = Repository(db)
    repo.add_whitelist_symbol(
        WhitelistSymbol(symbol="005930", name="삼성전자", market="KRX", role="LARGE_CAP_TEST")
    )
    repo.set_system_state("auto_trading_enabled", "true")
    repo.set_system_state("kill_switch_active", "false")
    checker = SafetyChecker(repo)
    return repo, checker


def _cond(symbol: str = "005930", qty: int = 1) -> dict:
    return {
        "id": 1,
        "symbol": symbol,
        "side": "BUY",
        "quantity": qty,
        "status": "ACTIVE",
        "cooldown_until": None,
        "order_type": "LIMIT",
    }


def _patch_window():
    """Context manager: make trading window always open (TZ-robust)."""
    import app.risk.safety_checker as sc_mod
    return patch.object(sc_mod, "is_within_trading_window", return_value=True)


def _patch_holiday(is_holiday: bool = False):
    """Context manager: control KRX holiday gate."""
    import app.risk.safety_checker as sc_mod
    return patch.object(sc_mod, "is_krx_holiday", return_value=is_holiday)


# ---------------------------------------------------------------------------
# Category 1: daily order amount boundary
# ---------------------------------------------------------------------------

class TestDailyOrderAmountBoundary:
    """Tests the today_amount + order_amount <= max_daily_amount gate."""

    def test_order_exactly_at_daily_limit_is_allowed(self, env: tuple, monkeypatch):
        """When today's cumulative amount equals max_daily_amount exactly, allow."""
        repo, checker = env
        limit = repo.get_global_risk_limit()
        max_daily = float(limit["max_daily_amount"])  # default 300_000

        # price * qty = exactly max_daily, today_order_amount = 0
        price = max_daily  # qty = 1
        qty = 1

        import app.risk.safety_checker as sc_mod
        monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
        monkeypatch.setattr(sc_mod, "is_krx_holiday", lambda d: False)

        # price*qty = max_daily; today_amount = 0 → 0 + max_daily <= max_daily → allowed
        r = checker.check(condition=_cond(qty=qty), current_price=price, now=datetime.now())
        # This may be blocked by max_order_amount gate first (price=300000 > 100000 default)
        # but qty=1 triggers the one-share exception → should be allowed
        assert r.allowed, f"Expected allowed at daily limit boundary, got: {r.reason}"

    def test_order_one_over_daily_limit_is_blocked(self, env: tuple, monkeypatch):
        """When today's prior spend + this order > max_daily_amount by 1 KRW, block."""
        repo, checker = env
        limit = repo.get_global_risk_limit()
        max_daily = float(limit["max_daily_amount"])  # 300_000

        import app.risk.safety_checker as sc_mod
        monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
        monkeypatch.setattr(sc_mod, "is_krx_holiday", lambda d: False)

        # Insert an order log that burns up (max_daily - 1) of the daily budget
        prior_spend = max_daily - 1.0
        repo.create_order_log(
            condition_id=None,
            symbol="005930",
            side="BUY",
            order_type="LIMIT",
            order_price=prior_spend,
            current_price=prior_spend,
            quantity=1,
            kis_order_id=None,
            order_status="FILLED",
        )
        # today_order_amount() sums price*qty of FILLED orders today = prior_spend
        # Adding 2 KRW at price=2 qty=1 → prior_spend + 2 > max_daily → blocked
        r = checker.check(condition=_cond(qty=1), current_price=2.0, now=datetime.now())
        assert not r.allowed
        assert "daily" in r.reason.lower() or "limit" in r.reason.lower() or "exceeded" in r.reason.lower()

    def test_fresh_db_order_within_daily_limit_allowed(self, env: tuple, monkeypatch):
        """Fresh DB: a small order well under daily limit is allowed."""
        repo, checker = env
        import app.risk.safety_checker as sc_mod
        monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
        monkeypatch.setattr(sc_mod, "is_krx_holiday", lambda d: False)

        # price=1000 * qty=1 = 1000 << 300_000 daily limit
        r = checker.check(condition=_cond(qty=1), current_price=1_000.0, now=datetime.now())
        assert r.allowed, f"Small order should be allowed on fresh DB: {r.reason}"


# ---------------------------------------------------------------------------
# Category 2: per-order amount boundary (max_order_amount)
# ---------------------------------------------------------------------------

class TestOrderAmountBoundary:
    """Tests the order_amount <= max_order_amount gate."""

    def test_order_exactly_at_max_order_amount_is_allowed(self, env: tuple, monkeypatch):
        """price * qty == max_order_amount → allowed (not over the limit)."""
        repo, checker = env
        limit = repo.get_global_risk_limit()
        max_order = float(limit["max_order_amount"])  # default 100_000

        import app.risk.safety_checker as sc_mod
        monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
        monkeypatch.setattr(sc_mod, "is_krx_holiday", lambda d: False)

        # price * 2 = max_order → 2 qty, price = max_order / 2
        qty = 2
        price = max_order / qty  # = 50_000

        r = checker.check(condition=_cond(qty=qty), current_price=price, now=datetime.now())
        assert r.allowed, f"Order exactly at max_order_amount should be allowed: {r.reason}"

    def test_order_one_above_max_order_amount_with_qty2_is_blocked(self, env: tuple, monkeypatch):
        """price * 2 = max_order_amount + 2 → blocked (no one-share exception for qty=2)."""
        repo, checker = env
        limit = repo.get_global_risk_limit()
        max_order = float(limit["max_order_amount"])  # 100_000

        import app.risk.safety_checker as sc_mod
        monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
        monkeypatch.setattr(sc_mod, "is_krx_holiday", lambda d: False)

        # price * 2 = max_order + 2 → just over
        qty = 2
        price = (max_order + 2) / qty  # = 50_001

        r = checker.check(condition=_cond(qty=qty), current_price=price, now=datetime.now())
        assert not r.allowed
        assert "amount" in r.reason.lower() or "max" in r.reason.lower() or "exceeds" in r.reason.lower()

    def test_one_share_exception_bypasses_order_amount_limit(self, env: tuple, monkeypatch):
        """qty=1 with price >> max_order_amount → allowed via one-share exception."""
        repo, checker = env
        limit = repo.get_global_risk_limit()
        max_order = float(limit["max_order_amount"])  # 100_000

        import app.risk.safety_checker as sc_mod
        monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
        monkeypatch.setattr(sc_mod, "is_krx_holiday", lambda d: False)

        # price = 10x the limit; qty=1 triggers the exception
        price = max_order * 10

        r = checker.check(condition=_cond(qty=1), current_price=price, now=datetime.now())
        # One-share exception allows this — provided daily limit is also OK (fresh DB)
        # Fresh DB: today_amount = 0 → 0 + price = 1_000_000 > 300_000 daily → blocked by DAILY not ORDER
        # The important thing: we confirm the ORDER block message (not one-share) vs DAILY block
        # Since daily limit is 300_000 and order is 1_000_000, this will be blocked by DAILY
        # Let's set a higher daily limit
        repo.update_global_risk_limit(max_daily_amount=max_order * 20)
        r = checker.check(condition=_cond(qty=1), current_price=price, now=datetime.now())
        assert r.allowed, (
            f"One-share exception should allow high-priced single-share order: {r.reason}"
        )


# ---------------------------------------------------------------------------
# Category 3: circuit-breaker daily-loss threshold boundary
# ---------------------------------------------------------------------------

class TestCircuitBreakerLossBoundary:
    """Tests the circuit breaker daily-loss threshold gate.

    The SafetyChecker computes:
      loss_pct = abs(today_pnl) / reference * 100.0
    and trips when loss_pct >= threshold_pct (default 3.0).

    reference = max_daily_amount (default 300_000).
    threshold_pct = 3.0 → trip when abs(pnl) >= 9_000 KRW.
    """

    def _seed_pnl_scenario(self, repo: Repository, buy_price: float, sell_price: float, qty: int = 1) -> None:
        """Insert a BUY fill then a SELL fill to produce a realized PnL record."""
        # BUY order log + execution
        buy_log_id = repo.create_order_log(
            condition_id=None,
            symbol="005930",
            side="BUY",
            order_type="LIMIT",
            order_price=buy_price,
            current_price=buy_price,
            quantity=qty,
            kis_order_id=None,
            order_status="FILLED",
        )
        repo.create_execution_log(
            order_log_id=buy_log_id,
            symbol="005930",
            filled_price=buy_price,
            filled_quantity=qty,
            raw_status="FILLED",
        )
        # SELL order log + execution (today)
        sell_log_id = repo.create_order_log(
            condition_id=None,
            symbol="005930",
            side="SELL",
            order_type="LIMIT",
            order_price=sell_price,
            current_price=sell_price,
            quantity=qty,
            kis_order_id=None,
            order_status="FILLED",
        )
        repo.create_execution_log(
            order_log_id=sell_log_id,
            symbol="005930",
            filled_price=sell_price,
            filled_quantity=qty,
            raw_status="FILLED",
        )

    def test_circuit_breaker_exactly_at_threshold_trips(self, env: tuple, monkeypatch):
        """When loss_pct == threshold_pct, circuit breaker must trip (>= comparison)."""
        repo, checker = env
        import app.risk.safety_checker as sc_mod
        monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
        monkeypatch.setattr(sc_mod, "is_krx_holiday", lambda d: False)

        # reference = max_daily_amount = 300_000; threshold = 3.0%
        # required loss = 300_000 * 3.0 / 100 = 9_000
        limit = repo.get_global_risk_limit()
        reference = float(limit["max_daily_amount"])
        threshold_pct = float(repo.get_system_state("circuit_breaker_threshold_pct", "3.0"))
        required_loss = reference * threshold_pct / 100.0  # 9_000

        buy_price = 100_000.0
        sell_price = buy_price - required_loss  # exactly 9_000 loss

        self._seed_pnl_scenario(repo, buy_price=buy_price, sell_price=sell_price, qty=1)

        r = checker.check(condition=_cond(qty=1), current_price=1_000.0, now=datetime.now())
        assert not r.allowed
        assert "circuit" in r.reason.lower() or "loss" in r.reason.lower() or "threshold" in r.reason.lower()

    def test_circuit_breaker_just_below_threshold_does_not_trip(self, env: tuple, monkeypatch):
        """When loss_pct < threshold_pct (by 1 KRW), circuit breaker must NOT trip."""
        repo, checker = env
        import app.risk.safety_checker as sc_mod
        monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
        monkeypatch.setattr(sc_mod, "is_krx_holiday", lambda d: False)

        limit = repo.get_global_risk_limit()
        reference = float(limit["max_daily_amount"])
        threshold_pct = float(repo.get_system_state("circuit_breaker_threshold_pct", "3.0"))
        required_loss = reference * threshold_pct / 100.0  # 9_000

        buy_price = 100_000.0
        sell_price = buy_price - (required_loss - 1)  # loss = 8_999 → below threshold

        self._seed_pnl_scenario(repo, buy_price=buy_price, sell_price=sell_price, qty=1)

        r = checker.check(condition=_cond(qty=1), current_price=1_000.0, now=datetime.now())
        # Circuit breaker should NOT trip; allowed on other grounds
        if not r.allowed:
            # Any other rejection reason is fine; only circuit-breaker reason is wrong
            assert "circuit" not in r.reason.lower() and "loss" not in r.reason.lower(), (
                f"Circuit breaker should NOT trip at loss below threshold, but got: {r.reason}"
            )

    def test_consecutive_failures_at_3_trips_circuit_breaker(self, env: tuple, monkeypatch):
        """When consecutive_order_failures == 3, circuit breaker blocks and disables auto-trading."""
        repo, checker = env
        import app.risk.safety_checker as sc_mod
        monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
        monkeypatch.setattr(sc_mod, "is_krx_holiday", lambda d: False)

        repo.set_system_state("consecutive_order_failures", "3")

        r = checker.check(condition=_cond(qty=1), current_price=1_000.0, now=datetime.now())
        assert not r.allowed
        assert "circuit" in r.reason.lower() or "consecutive" in r.reason.lower() or "3" in r.reason

        # Also verify auto_trading_enabled was flipped to false
        assert repo.get_system_state("auto_trading_enabled") == "false"

    def test_consecutive_failures_at_2_does_not_trip(self, env: tuple, monkeypatch):
        """When consecutive_order_failures == 2, circuit breaker does NOT trip."""
        repo, checker = env
        import app.risk.safety_checker as sc_mod
        monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
        monkeypatch.setattr(sc_mod, "is_krx_holiday", lambda d: False)

        repo.set_system_state("consecutive_order_failures", "2")

        r = checker.check(condition=_cond(qty=1), current_price=1_000.0, now=datetime.now())
        # Should be allowed (failures < 3)
        if not r.allowed:
            assert "consecutive" not in r.reason.lower() and "circuit" not in r.reason.lower(), (
                f"With only 2 failures, circuit breaker should NOT trip: {r.reason}"
            )
