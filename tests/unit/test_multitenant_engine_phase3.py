"""Multitenant Phase 3: per-user engine pool/lock + per-user engine state.

Flag-OFF (default): byte-identical to the pre-Phase-3 global path.
Flag-ON: per-user engine_state isolation CLOSES the Phase 2 consequence gap —
user A's circuit-breaker trip disables ONLY user A's auto_trading; user B still
trades (asserted end-to-end through SafetyChecker).

Use ``monkeypatch.delenv("AUTOFOLIO_MULTI_TENANT_ENABLED", raising=False)`` for
the OFF path and ``monkeypatch.setenv(..., "1")`` for the ON path.
"""
from __future__ import annotations

from datetime import datetime

import pytest

from app.brokers.mock.mock_client import MockBrokerClient
from app.database.repositories import Repository, WhitelistSymbol
from app.database.sqlite_db import initialize_database
from app.engine.live_trading_engine import LiveTradingEngine
from app.risk.safety_checker import SafetyChecker


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cond(symbol="005930", qty=1):
    return {
        "id": 1, "symbol": symbol, "side": "BUY", "quantity": qty,
        "status": "ACTIVE", "cooldown_until": None, "order_type": "LIMIT",
    }


def _make_env(tmp_path, db_name="p3.db"):
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
    return repo, checker


def _patch_window(monkeypatch):
    import app.risk.safety_checker as sc_mod
    monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
    monkeypatch.setattr(sc_mod, "is_krx_holiday", lambda d: False)


def _insert_loss_cycle(repo, user_id, symbol="005930", buy_price=75_000.0, sell_price=60_000.0, qty=1):
    """Insert a BUY+SELL cycle where sell_price < buy_price → realized loss."""
    buy_cid = repo.add_trade_condition(
        symbol=symbol, side="BUY", target_price=buy_price, quantity=qty, user_id=user_id
    )
    buy_order_id = repo.create_order_log(
        condition_id=buy_cid, symbol=symbol, side="BUY", order_type="LIMIT",
        order_price=buy_price, current_price=buy_price, quantity=qty,
        kis_order_id=None, order_status="FILLED", user_id=user_id,
    )
    repo.create_execution_log(
        order_log_id=buy_order_id, symbol=symbol,
        filled_price=buy_price, filled_quantity=qty, user_id=user_id,
    )
    sell_cid = repo.add_trade_condition(
        symbol=symbol, side="SELL", target_price=sell_price, quantity=qty, user_id=user_id
    )
    sell_order_id = repo.create_order_log(
        condition_id=sell_cid, symbol=symbol, side="SELL", order_type="LIMIT",
        order_price=sell_price, current_price=sell_price, quantity=qty,
        kis_order_id=None, order_status="FILLED", user_id=user_id,
    )
    repo.create_execution_log(
        order_log_id=sell_order_id, symbol=symbol,
        filled_price=sell_price, filled_quantity=qty, user_id=user_id,
    )


# ---------------------------------------------------------------------------
# Flag default + repository engine_state semantics
# ---------------------------------------------------------------------------

def test_flag_off_is_default(monkeypatch):
    from app.services.flags import multi_tenant_enabled
    monkeypatch.delenv("AUTOFOLIO_MULTI_TENANT_ENABLED", raising=False)
    assert multi_tenant_enabled() is False


def test_engine_state_flag_off_is_system_state(tmp_path, monkeypatch):
    """Flag OFF: get/set_engine_state delegate verbatim to get/set_system_state."""
    monkeypatch.delenv("AUTOFOLIO_MULTI_TENANT_ENABLED", raising=False)
    db = tmp_path / "off.db"
    initialize_database(db)
    repo = Repository(db)
    repo.set_engine_state("auto_trading_enabled", "true")
    assert repo.get_system_state("auto_trading_enabled") == "true"
    assert repo.get_engine_state("auto_trading_enabled") == "true"


def test_engine_state_flag_off_ignores_user_id(tmp_path, monkeypatch):
    """Flag OFF: user_id is ignored → writes/reads the GLOBAL row."""
    monkeypatch.delenv("AUTOFOLIO_MULTI_TENANT_ENABLED", raising=False)
    db = tmp_path / "off2.db"
    initialize_database(db)
    repo = Repository(db)
    repo.set_system_state("auto_trading_enabled", "true")
    # user_id supplied but flag OFF → still writes GLOBAL
    repo.set_engine_state("auto_trading_enabled", "false", user_id="user_a")
    assert repo.get_system_state("auto_trading_enabled") == "false"
    assert repo.get_engine_state("auto_trading_enabled", user_id="user_a") == "false"


def test_engine_state_per_user_falls_back_to_global(tmp_path, monkeypatch):
    """Flag ON: a user with no per-user row inherits the GLOBAL value."""
    monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
    db = tmp_path / "on.db"
    initialize_database(db)
    repo = Repository(db)
    repo.set_system_state("auto_trading_enabled", "true")
    assert repo.get_engine_state("auto_trading_enabled", "false", user_id="user_a") == "true"


def test_engine_state_per_user_write_isolated(tmp_path, monkeypatch):
    """Flag ON: a per-user write touches ONLY that user — not GLOBAL, not others."""
    monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
    db = tmp_path / "on2.db"
    initialize_database(db)
    repo = Repository(db)
    repo.set_system_state("auto_trading_enabled", "true")  # GLOBAL default
    repo.set_engine_state("auto_trading_enabled", "false", user_id="user_a")
    assert repo.get_engine_state("auto_trading_enabled", "false", user_id="user_a") == "false"
    assert repo.get_engine_state("auto_trading_enabled", "false", user_id="user_b") == "true"
    assert repo.get_system_state("auto_trading_enabled") == "true"


# ---------------------------------------------------------------------------
# SafetyChecker — per-user engine state (the Phase 2 gap closure)
# ---------------------------------------------------------------------------

def test_safety_check_flag_off_user_id_ignored(tmp_path, monkeypatch):
    """Flag OFF: passing user_id to check() gives the same result as omitting it."""
    monkeypatch.delenv("AUTOFOLIO_MULTI_TENANT_ENABLED", raising=False)
    repo, checker = _make_env(tmp_path)
    _patch_window(monkeypatch)
    r1 = checker.check(condition=_cond(), current_price=70_000, now=datetime.now(), user_id="u")
    r2 = checker.check(condition=_cond(), current_price=70_000, now=datetime.now())
    assert r1.allowed == r2.allowed is True


def test_circuit_breaker_consequence_is_per_user__B_trades_after_A_trips(tmp_path, monkeypatch):
    """THE Phase 3 gap closure.

    user_a's daily-loss circuit breaker TRIPS and disables auto_trading. Because
    the consequence is now PER-USER, the GLOBAL flag is untouched and user_b can
    STILL trade. This is exactly what Phase 2 could not do (its consequence was a
    global write that disabled everyone).
    """
    monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
    repo, checker = _make_env(tmp_path)
    _patch_window(monkeypatch)

    _insert_loss_cycle(repo, "user_a", buy_price=75_000.0, sell_price=60_000.0, qty=1)

    # user_a trips → writes PER-USER auto_trading=false
    r_a = checker.check(condition=_cond(), current_price=70_000, now=datetime.now(), user_id="user_a")
    assert not r_a.allowed
    assert "circuit breaker" in r_a.reason.lower()

    # The consequence is per-user: GLOBAL auto_trading is untouched.
    assert repo.get_system_state("auto_trading_enabled") == "true"
    # user_a's per-user disable STICKS on re-check.
    r_a2 = checker.check(condition=_cond(), current_price=70_000, now=datetime.now(), user_id="user_a")
    assert not r_a2.allowed
    assert "disabled" in r_a2.reason.lower()

    # GAP CLOSED: user_b (no loss) can STILL trade after user_a tripped.
    r_b = checker.check(condition=_cond(), current_price=70_000, now=datetime.now(), user_id="user_b")
    assert r_b.allowed, f"user_b should still trade after user_a trip, got: {r_b.reason}"


def test_per_user_kill_switch_does_not_leak(tmp_path, monkeypatch):
    """Flag ON: a per-user kill-switch blocks only that user; others fall back to
    the GLOBAL (inactive) value and keep trading."""
    monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
    repo, checker = _make_env(tmp_path)
    _patch_window(monkeypatch)

    repo.set_engine_state("kill_switch_active", "true", user_id="user_a")
    r_a = checker.check(condition=_cond(), current_price=70_000, now=datetime.now(), user_id="user_a")
    assert not r_a.allowed
    assert "kill switch" in r_a.reason.lower()

    r_b = checker.check(condition=_cond(), current_price=70_000, now=datetime.now(), user_id="user_b")
    assert r_b.allowed, f"user_b must be unaffected by user_a kill switch, got: {r_b.reason}"
    # GLOBAL kill switch untouched.
    assert repo.get_system_state("kill_switch_active") == "false"


# ---------------------------------------------------------------------------
# Per-user engine context pool (backend)
# ---------------------------------------------------------------------------

def test_ctx_for_user_distinct_engines(tmp_path, monkeypatch):
    """Flag ON: each user gets their OWN engine instance; same user is cached;
    repo/broker are shared with the singleton context."""
    monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
    db = tmp_path / "ctx.db"
    initialize_database(db)
    repo = Repository(db)
    broker = MockBrokerClient(prices={"005930": 70_000.0})
    base_engine = LiveTradingEngine(broker=broker, repo=repo)
    agent = object()

    import app.services.backend as backend
    monkeypatch.setattr(backend, "_ctx", lambda: (repo, broker, base_engine, agent))
    with backend._user_ctx_lock:
        backend._user_ctx.clear()
    try:
        ctx_a = backend._ctx_for_user("user_a")
        ctx_b = backend._ctx_for_user("user_b")
        ctx_a2 = backend._ctx_for_user("user_a")
        assert ctx_a[2] is ctx_a2[2]          # cached per user
        assert ctx_a[2] is not ctx_b[2]       # isolated across users
        assert ctx_a[2] is not base_engine    # per-user engine, not the singleton's
        assert ctx_a[0] is repo and ctx_a[1] is broker  # shares repo/broker
    finally:
        with backend._user_ctx_lock:
            backend._user_ctx.clear()


def test_run_engine_once_flag_off_uses_singleton(tmp_path, monkeypatch):
    """Flag OFF: run_engine_once() never creates a per-user context."""
    monkeypatch.delenv("AUTOFOLIO_MULTI_TENANT_ENABLED", raising=False)
    db = tmp_path / "off_run.db"
    initialize_database(db)
    repo = Repository(db)
    broker = MockBrokerClient(prices={"005930": 70_000.0})
    engine = LiveTradingEngine(broker=broker, repo=repo)

    import app.services.backend as backend
    monkeypatch.setattr(backend, "_ctx", lambda: (repo, broker, engine, object()))
    with backend._user_ctx_lock:
        backend._user_ctx.clear()
    backend.run_engine_once()  # no user_id
    assert backend._user_ctx == {}, "Flag OFF must not populate the per-user pool"


# ---------------------------------------------------------------------------
# Per-user run lock (engine router)
# ---------------------------------------------------------------------------

def test_run_lock_for_distinct_users_independent():
    import app.api.routers.engine as engine_mod
    with engine_mod._user_run_locks_lock:
        engine_mod._user_run_locks.clear()
    try:
        lock_a = engine_mod._run_lock_for("user_a")
        lock_b = engine_mod._run_lock_for("user_b")
        assert lock_a is engine_mod._run_lock_for("user_a")  # cached
        assert lock_a is not lock_b                          # independent
        # user_a holding its lock must NOT block user_b's lock.
        assert lock_a.acquire(blocking=False)
        try:
            assert lock_b.acquire(blocking=False), "user_b lock must be independent of user_a"
            lock_b.release()
        finally:
            lock_a.release()
    finally:
        with engine_mod._user_run_locks_lock:
            engine_mod._user_run_locks.clear()


# ---------------------------------------------------------------------------
# Engine run path — per-user condition scoping
# ---------------------------------------------------------------------------

def test_engine_run_once_scopes_conditions_per_user(tmp_path, monkeypatch):
    """Flag ON: engine.run_once(user_id=user_a) processes ONLY user_a's conditions;
    user_b's condition is never claimed and produces no order log."""
    monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
    monkeypatch.setenv("AUTOFOLIO_AUTO_EXEC_ENABLED", "1")
    repo, _ = _make_env(tmp_path, db_name="run_scope.db")
    _patch_window(monkeypatch)
    broker = MockBrokerClient(prices={"005930": 69_800.0})
    engine = LiveTradingEngine(broker=broker, repo=repo)

    repo.add_trade_condition(
        symbol="005930", side="BUY", target_price=70_000, quantity=1,
        order_type="LIMIT", auto_enabled=True, user_id="user_a",
    )
    cid_b = repo.add_trade_condition(
        symbol="005930", side="BUY", target_price=70_000, quantity=1,
        order_type="LIMIT", auto_enabled=True, user_id="user_b",
    )

    engine.run_once(user_id="user_a")

    logs_a = repo.list_order_logs(user_id="user_a")
    logs_b = repo.list_order_logs(user_id="user_b")
    assert len(logs_a) >= 1, "user_a's condition should have been processed"
    assert len(logs_b) == 0, "user_b's condition must NOT be touched by user_a's run"
    # user_b's condition remains ACTIVE (never claimed).
    assert repo.get_condition(cid_b)["status"] == "ACTIVE"


def test_engine_run_once_flag_off_iterates_globally(tmp_path, monkeypatch):
    """Flag OFF: run_once() iterates ALL active conditions exactly as before."""
    monkeypatch.delenv("AUTOFOLIO_MULTI_TENANT_ENABLED", raising=False)
    monkeypatch.setenv("AUTOFOLIO_AUTO_EXEC_ENABLED", "1")
    repo, _ = _make_env(tmp_path, db_name="run_global.db")
    _patch_window(monkeypatch)
    broker = MockBrokerClient(prices={"005930": 69_800.0})
    engine = LiveTradingEngine(broker=broker, repo=repo)

    repo.add_trade_condition(
        symbol="005930", side="BUY", target_price=70_000, quantity=1,
        order_type="LIMIT", auto_enabled=True,
    )
    msgs = engine.run_once()  # no user_id → global iteration
    assert len(msgs) >= 1
    logs = repo.list_order_logs()
    assert len(logs) >= 1
