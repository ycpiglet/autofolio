"""Multitenant Phase 4 — Flag-OFF characterization test.

With AUTOFOLIO_MULTI_TENANT_ENABLED unset (default OFF), proves that the
tenant-aware code paths behave EXACTLY as the single-owner system:

  - Passing a user_id while flag OFF is IGNORED (unscoped / global queries run)
  - list_active_conditions(user_id=X) == list_active_conditions() (same rows)
  - engine_state reads/writes go to the GLOBAL system_state key
  - run_once(user_id=X) iterates ALL active conditions globally
  - safety gate uses global PnL / limits / counters regardless of user_id
  - consecutive failures counter: global, not per-user

This is the gate that proves flipping the flag is the ONLY behavior change.
Any regression here means a code path silently diverged from the flag-OFF
invariant and must be fixed before the flag can be turned ON.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from app.brokers.mock.mock_client import MockBrokerClient
from app.database.repositories import Repository, WhitelistSymbol
from app.database.sqlite_db import initialize_database, get_connection
from app.engine.live_trading_engine import LiveTradingEngine
from app.risk.safety_checker import SafetyChecker


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _setup(tmp_path: Path, db_name: str = "flagoff.db") -> tuple[Repository, SafetyChecker, LiveTradingEngine]:
    db = tmp_path / db_name
    initialize_database(db)
    repo = Repository(db)
    repo.add_whitelist_symbol(
        WhitelistSymbol(symbol="005930", name="삼성전자", market="KRX", role="LARGE_CAP_TEST")
    )
    repo.set_system_state("auto_trading_enabled", "true")
    repo.set_system_state("kill_switch_active", "false")
    repo.set_system_state("global_mode", "L2")
    checker = SafetyChecker(repo)
    broker = MockBrokerClient(prices={"005930": 69_800.0})
    engine = LiveTradingEngine(broker=broker, repo=repo)
    return repo, checker, engine


def _patch_window(monkeypatch) -> None:
    import app.risk.safety_checker as sc_mod
    monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
    monkeypatch.setattr(sc_mod, "is_krx_holiday", lambda d: False)


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def off_env(tmp_path, monkeypatch):
    """Flag-OFF environment. user_id is ignored everywhere."""
    monkeypatch.delenv("AUTOFOLIO_MULTI_TENANT_ENABLED", raising=False)
    monkeypatch.setenv("AUTOFOLIO_AUTO_EXEC_ENABLED", "1")
    _patch_window(monkeypatch)
    repo, checker, engine = _setup(tmp_path)
    return repo, checker, engine


# ---------------------------------------------------------------------------
# Characterization: conditions are unscoped when flag OFF
# ---------------------------------------------------------------------------

def test_flagoff_list_conditions_ignores_user_id(off_env):
    """Flag OFF: list_active_conditions(user_id=X) returns ALL active conditions."""
    repo, *_ = off_env

    # Add conditions with different user_ids (column exists but flag OFF ignores it)
    cid_a = repo.add_trade_condition(
        symbol="005930", side="BUY", target_price=70_000, quantity=1,
        order_type="LIMIT", user_id="user_a",
    )
    cid_b = repo.add_trade_condition(
        symbol="005930", side="BUY", target_price=70_000, quantity=1,
        order_type="LIMIT", user_id="user_b",
    )

    # Flag OFF: user_id is ignored → all conditions returned regardless of user_id arg
    scoped_a = repo.list_active_conditions(user_id="user_a")
    scoped_b = repo.list_active_conditions(user_id="user_b")
    unscoped = repo.list_active_conditions()

    ids_scoped_a = {c["id"] for c in scoped_a}
    ids_scoped_b = {c["id"] for c in scoped_b}
    ids_unscoped = {c["id"] for c in unscoped}

    # All three calls return the same rows
    assert ids_scoped_a == ids_unscoped, "Flag OFF: user_id arg must be ignored"
    assert ids_scoped_b == ids_unscoped, "Flag OFF: user_id arg must be ignored"
    assert cid_a in ids_unscoped and cid_b in ids_unscoped


def test_flagoff_list_order_logs_ignores_user_id(off_env):
    """Flag OFF: list_order_logs(user_id=X) returns ALL order logs."""
    repo, *_ = off_env
    cid_a = repo.add_trade_condition(
        symbol="005930", side="BUY", target_price=70_000, quantity=1, user_id="user_a"
    )
    cid_b = repo.add_trade_condition(
        symbol="005930", side="BUY", target_price=70_000, quantity=1, user_id="user_b"
    )
    oid_a = repo.create_order_log(
        condition_id=cid_a, symbol="005930", side="BUY", order_type="LIMIT",
        order_price=70_000, current_price=69_800, quantity=1,
        kis_order_id="A-001", order_status="FILLED", user_id="user_a",
    )
    oid_b = repo.create_order_log(
        condition_id=cid_b, symbol="005930", side="BUY", order_type="LIMIT",
        order_price=70_000, current_price=69_800, quantity=1,
        kis_order_id="B-001", order_status="FILLED", user_id="user_b",
    )

    logs_a = repo.list_order_logs(user_id="user_a")
    logs_b = repo.list_order_logs(user_id="user_b")
    logs_all = repo.list_order_logs()

    ids_a = {r["id"] for r in logs_a}
    ids_b = {r["id"] for r in logs_b}
    ids_all = {r["id"] for r in logs_all}

    assert ids_a == ids_all, "Flag OFF: user_id in list_order_logs must be ignored"
    assert ids_b == ids_all, "Flag OFF: user_id in list_order_logs must be ignored"
    assert oid_a in ids_all and oid_b in ids_all


# ---------------------------------------------------------------------------
# Characterization: engine_state goes to GLOBAL system_state key
# ---------------------------------------------------------------------------

def test_flagoff_engine_state_writes_global_key(off_env):
    """Flag OFF: set_engine_state with user_id writes to the GLOBAL system_state key."""
    repo, *_ = off_env
    # Both calls (with and without user_id) must write the same global key
    repo.set_engine_state("auto_trading_enabled", "false", user_id="user_x")
    assert repo.get_system_state("auto_trading_enabled") == "false"

    # And reads back from the global key
    assert repo.get_engine_state("auto_trading_enabled", user_id="user_x") == "false"


def test_flagoff_engine_state_read_returns_global_value(off_env):
    """Flag OFF: get_engine_state ignores user_id and reads the GLOBAL row."""
    repo, *_ = off_env
    repo.set_system_state("auto_trading_enabled", "true")
    # user_id supplied but flag OFF → reads GLOBAL key
    assert repo.get_engine_state("auto_trading_enabled", user_id="user_a") == "true"
    assert repo.get_engine_state("auto_trading_enabled", user_id="user_b") == "true"
    assert repo.get_engine_state("auto_trading_enabled") == "true"


# ---------------------------------------------------------------------------
# Characterization: aggregates are global
# ---------------------------------------------------------------------------

def test_flagoff_today_order_amount_is_global(off_env):
    """Flag OFF: today_order_amount(user_id=X) == today_order_amount() — global sum."""
    repo, *_ = off_env
    cid_a = repo.add_trade_condition(
        symbol="005930", side="BUY", target_price=70_000, quantity=2, user_id="user_a"
    )
    cid_b = repo.add_trade_condition(
        symbol="005930", side="BUY", target_price=70_000, quantity=3, user_id="user_b"
    )
    repo.create_order_log(
        condition_id=cid_a, symbol="005930", side="BUY", order_type="LIMIT",
        order_price=70_000, current_price=70_000, quantity=2,
        kis_order_id="A-001", order_status="FILLED", user_id="user_a",
    )
    repo.create_order_log(
        condition_id=cid_b, symbol="005930", side="BUY", order_type="LIMIT",
        order_price=70_000, current_price=70_000, quantity=3,
        kis_order_id="B-001", order_status="FILLED", user_id="user_b",
    )

    amt_global = repo.today_order_amount()
    amt_a_scoped = repo.today_order_amount(user_id="user_a")
    amt_b_scoped = repo.today_order_amount(user_id="user_b")

    # All three must be the same global sum
    expected = 70_000 * (2 + 3)
    assert amt_global == pytest.approx(expected, rel=1e-6)
    assert amt_a_scoped == pytest.approx(expected, rel=1e-6), \
        "Flag OFF: user_id arg to today_order_amount must be ignored"
    assert amt_b_scoped == pytest.approx(expected, rel=1e-6), \
        "Flag OFF: user_id arg to today_order_amount must be ignored"


# ---------------------------------------------------------------------------
# Characterization: consecutive failures counter is global
# ---------------------------------------------------------------------------

def test_flagoff_consecutive_failures_counter_is_global(off_env):
    """Flag OFF: increment/get_consecutive_failures ignores user_id (global counter)."""
    repo, *_ = off_env
    repo.increment_consecutive_failures(user_id="user_a")
    repo.increment_consecutive_failures(user_id="user_b")
    repo.increment_consecutive_failures()

    global_count = repo.get_consecutive_failures()
    count_a = repo.get_consecutive_failures(user_id="user_a")
    count_b = repo.get_consecutive_failures(user_id="user_b")

    # All three should return the same global count (3)
    assert global_count == 3
    assert count_a == global_count, "Flag OFF: user_id must not create per-user counter"
    assert count_b == global_count, "Flag OFF: user_id must not create per-user counter"

    # The global system_state key is the single source of truth
    raw = repo.get_system_state("consecutive_order_failures", "0")
    assert int(raw) == 3


def test_flagoff_reset_consecutive_failures_is_global(off_env):
    """Flag OFF: reset_consecutive_failures with user_id resets the GLOBAL counter."""
    repo, *_ = off_env
    for _ in range(3):
        repo.increment_consecutive_failures()
    assert repo.get_consecutive_failures() == 3

    repo.reset_consecutive_failures(user_id="user_a")  # user_id ignored, flag OFF
    assert repo.get_consecutive_failures() == 0
    assert repo.get_system_state("consecutive_order_failures") == "0"


# ---------------------------------------------------------------------------
# Characterization: engine run is global
# ---------------------------------------------------------------------------

def test_flagoff_run_once_processes_all_conditions_globally(off_env):
    """Flag OFF: run_once(user_id=X) processes ALL conditions (global iteration)."""
    repo, _, engine = off_env
    # Add conditions with different user_ids — flag OFF means the engine iterates ALL
    repo.add_trade_condition(
        symbol="005930", side="BUY", target_price=70_000, quantity=1,
        order_type="LIMIT", auto_enabled=True, user_id="user_a",
    )
    repo.add_trade_condition(
        symbol="005930", side="BUY", target_price=70_000, quantity=1,
        order_type="LIMIT", auto_enabled=True, user_id="user_b",
    )

    msgs = engine.run_once(user_id="user_a")  # user_id is ignored when flag OFF
    # Both conditions should be processed (globally scoped)
    assert len(msgs) >= 2, f"Expected both conditions processed globally, got: {msgs}"
    logs = repo.list_order_logs()
    assert len(logs) >= 2, "Both conditions should have generated order logs"


# ---------------------------------------------------------------------------
# Characterization: safety gate uses global PnL
# ---------------------------------------------------------------------------

def test_flagoff_safety_checker_user_id_is_ignored(off_env):
    """Flag OFF: check(user_id=X) and check() give the same result."""
    repo, checker, _ = off_env
    cond = {
        "id": 1, "symbol": "005930", "side": "BUY", "quantity": 1,
        "status": "ACTIVE", "cooldown_until": None, "order_type": "LIMIT",
    }
    r_with_uid = checker.check(condition=cond, current_price=69_800, now=datetime.now(), user_id="user_a")
    r_no_uid = checker.check(condition=cond, current_price=69_800, now=datetime.now())
    assert r_with_uid.allowed == r_no_uid.allowed
