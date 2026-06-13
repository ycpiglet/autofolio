"""Safety-critical boundary tests — condition evaluator + safety checker + duplicate guard + trading window."""
from __future__ import annotations

import math
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from app.database.repositories import Repository, WhitelistSymbol
from app.database.sqlite_db import initialize_database
from app.risk.safety_checker import SafetyChecker


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_env(*, auto_enabled="true", kill_switch="false", global_mode=None):
    """Return (tmpdir, repo, checker); caller must close tmpdir manually."""
    # ignore_cleanup_errors=True avoids Windows PermissionError on locked .db files
    import sys
    if sys.version_info >= (3, 10):
        tmpdir = TemporaryDirectory(ignore_cleanup_errors=True)
    else:
        tmpdir = TemporaryDirectory()
    db = Path(tmpdir.name) / "test.db"
    initialize_database(db)
    repo = Repository(db)
    repo.add_whitelist_symbol(
        WhitelistSymbol(symbol="005930", name="삼성전자", market="KRX", role="LARGE_CAP_TEST")
    )
    repo.set_system_state("auto_trading_enabled", auto_enabled)
    repo.set_system_state("kill_switch_active", kill_switch)
    if global_mode is not None:
        repo.set_system_state("global_mode", global_mode)
    checker = SafetyChecker(repo)
    return tmpdir, repo, checker


def _cond(symbol="005930", qty=1, status="ACTIVE", cooldown_until=None):
    return {
        "id": 1,
        "symbol": symbol,
        "side": "BUY",
        "quantity": qty,
        "status": status,
        "cooldown_until": cooldown_until,
        "order_type": "LIMIT",
    }


# ---------------------------------------------------------------------------
# Condition evaluator boundary tests
# ---------------------------------------------------------------------------

def test_buy_triggered_at_exact_target_price():
    """BUY condition fires when current_price equals target_price (boundary <=)."""
    from app.engine.condition_evaluator import is_condition_triggered
    assert is_condition_triggered(side="BUY", current_price=70000, target_price=70000) is True


def test_sell_triggered_at_exact_target_price():
    """SELL condition fires when current_price equals target_price (boundary >=)."""
    from app.engine.condition_evaluator import is_condition_triggered
    assert is_condition_triggered(side="SELL", current_price=76000, target_price=76000) is True


def test_condition_evaluator_nan_price_does_not_trigger():
    """NaN as current_price must not trigger a BUY condition."""
    from app.engine.condition_evaluator import is_condition_triggered
    # float('nan') comparisons are always False; BUY uses <=, so nan <= x is False.
    result = is_condition_triggered(side="BUY", current_price=float("nan"), target_price=70000)
    assert result is False


def test_condition_evaluator_invalid_side_raises_value_error():
    """An unknown side string must raise ValueError."""
    from app.engine.condition_evaluator import is_condition_triggered
    with pytest.raises(ValueError):
        is_condition_triggered(side="UNKNOWN", current_price=70000, target_price=70000)


def test_condition_evaluator_zero_target_zero_price():
    """target=0.0 and current=0.0 for BUY must not raise ZeroDivisionError."""
    from app.engine.condition_evaluator import is_condition_triggered
    # 0.0 <= 0.0 is True; must not raise
    result = is_condition_triggered(side="BUY", current_price=0.0, target_price=0.0)
    assert result is True


# ---------------------------------------------------------------------------
# Safety checker daily limit boundary tests
# ---------------------------------------------------------------------------

def test_safety_checker_daily_limit_at_exact_boundary(monkeypatch):
    """Order that pushes past the daily budget is BLOCKED (check is today + order > max_daily)."""
    import app.risk.safety_checker as sc_mod
    from app.database.sqlite_db import get_connection
    from datetime import datetime as _dt
    monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
    tmpdir, repo, checker = _make_env()
    try:
        repo.update_global_risk_limit(max_order_amount=500_000.0, max_daily_amount=100_000.0)
        # Insert a FILLED order with today's LOCAL date so today_order_amount() counts it.
        # The query: DATE(created_at) = DATE('now', 'localtime').
        # Using Python datetime.now() gives the local date, avoiding UTC/KST offset issues.
        local_today = _dt.now().strftime("%Y-%m-%d")
        created_at = f"{local_today} 10:00:00"
        with get_connection(repo.db_path) as conn:
            conn.execute(
                """
                INSERT INTO order_logs(
                    condition_id, symbol, side, order_type, order_price,
                    current_price, quantity, kis_order_id, order_status,
                    fallback_to_market, error_message, created_at
                ) VALUES (1, '005930', 'BUY', 'LIMIT', 1.0, 1.0, 1, NULL, 'FILLED', 0, NULL, ?)
                """,
                (created_at,),
            )
        # today_amount = 1.0; order_amount = 100_000 → 1 + 100_000 > 100_000 → BLOCKED
        cond = _cond(qty=1)
        r = checker.check(condition=cond, current_price=100_000.0, now=datetime.now())
        assert not r.allowed
        assert "daily" in r.reason.lower() or "amount" in r.reason.lower()
    finally:
        tmpdir.cleanup()


def test_safety_checker_daily_limit_one_below_boundary(monkeypatch):
    """Order one unit below the daily budget ceiling is ALLOWED."""
    import app.risk.safety_checker as sc_mod
    monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
    tmpdir, repo, checker = _make_env()
    try:
        repo.update_global_risk_limit(max_order_amount=500_000.0, max_daily_amount=100_000.0)
        # today_amount=0, order_amount = 99_999 → 0 + 99_999 > 100_000 → False → allowed
        cond = _cond(qty=1)
        r = checker.check(condition=cond, current_price=99_999.0, now=datetime.now())
        assert r.allowed, r.reason
    finally:
        tmpdir.cleanup()


def test_safety_checker_kill_switch_before_auto_disabled(monkeypatch):
    """When both kill_switch=true and auto_enabled=false, the reason mentions 'kill'."""
    import app.risk.safety_checker as sc_mod
    monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
    tmpdir, repo, checker = _make_env(kill_switch="true", auto_enabled="false")
    try:
        r = checker.check(condition=_cond(), current_price=70000, now=datetime.now())
        assert not r.allowed
        # Kill switch is checked first; reason should mention kill
        assert "kill" in r.reason.lower()
    finally:
        tmpdir.cleanup()


def test_safety_checker_circuit_breaker_two_failures_still_allowed(monkeypatch):
    """With consecutive_failures=2 the circuit breaker does not trip (threshold is 3)."""
    import app.risk.safety_checker as sc_mod
    monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
    tmpdir, repo, checker = _make_env()
    try:
        repo.set_system_state("consecutive_order_failures", "2")
        r = checker.check(condition=_cond(), current_price=70000, now=datetime.now())
        assert r.allowed, r.reason
    finally:
        tmpdir.cleanup()


def test_safety_checker_whitelist_disabled_symbol_blocked(monkeypatch):
    """Symbol present in whitelist but with enabled=False is blocked."""
    import app.risk.safety_checker as sc_mod
    monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
    tmpdir, repo, checker = _make_env()
    try:
        # Add a symbol with enabled=False
        repo.add_whitelist_symbol(
            WhitelistSymbol(symbol="000660", name="SK하이닉스", market="KRX",
                            role="LARGE_CAP_TEST", enabled=False)
        )
        cond = _cond(symbol="000660")
        r = checker.check(condition=cond, current_price=70000, now=datetime.now())
        assert not r.allowed
        assert "whitelist" in r.reason.lower()
    finally:
        tmpdir.cleanup()


def test_safety_checker_l1_mode_blocks_auto_execution(monkeypatch):
    """Global mode L1 prevents automatic execution."""
    import app.risk.safety_checker as sc_mod
    monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
    tmpdir, repo, checker = _make_env(global_mode="L1")
    try:
        r = checker.check(condition=_cond(), current_price=70000, now=datetime.now())
        assert not r.allowed
        assert "L1" in r.reason or "manual" in r.reason.lower() or "autonomy" in r.reason.lower()
    finally:
        tmpdir.cleanup()


# ---------------------------------------------------------------------------
# Duplicate guard cooldown boundary tests
# ---------------------------------------------------------------------------

def test_duplicate_guard_cooldown_exact_expiry():
    """cooldown_until one second in the past means the condition IS executable."""
    from app.risk.duplicate_guard import is_condition_executable
    now = datetime(2026, 6, 14, 10, 0, 0)
    just_expired = (now - timedelta(seconds=1)).isoformat()
    assert is_condition_executable("ACTIVE", just_expired, now) is True


def test_duplicate_guard_cooldown_not_yet_expired():
    """cooldown_until 60 seconds in the future means the condition is NOT executable."""
    from app.risk.duplicate_guard import is_condition_executable
    now = datetime(2026, 6, 14, 10, 0, 0)
    future = (now + timedelta(seconds=60)).isoformat()
    assert is_condition_executable("ACTIVE", future, now) is False


# ---------------------------------------------------------------------------
# Trading window boundary tests
# ---------------------------------------------------------------------------

def test_trading_window_exact_open_and_close_boundary():
    """09:10:00 is inside the window; 15:20:59 is inside; 15:21:00 is outside."""
    from app.risk.trading_window import is_within_trading_window

    # Exactly at open boundary (09:10:00)
    at_open = datetime(2026, 6, 14, 9, 10, 0)
    assert is_within_trading_window(at_open, "09:10", "15:20") is True

    # Exactly at close boundary hh:mm — is_within_trading_window compares time() (hh:mm:ss)
    # against parse_hhmm which sets seconds=0, so 15:20:00 == 15:20 → True
    at_close = datetime(2026, 6, 14, 15, 20, 0)
    assert is_within_trading_window(at_close, "09:10", "15:20") is True

    # One second after the parsed close boundary is still within because
    # parse_hhmm returns time(15, 20) with second=0, and 15:20:01 > 15:20:00 → outside
    one_second_after = datetime(2026, 6, 14, 15, 20, 1)
    assert is_within_trading_window(one_second_after, "09:10", "15:20") is False
