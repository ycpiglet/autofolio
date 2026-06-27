"""Multitenant Phase 4 — E2E cross-user isolation integration test.

Drives TWO users A and B through the FULL stack simultaneously in a single
real (temp) SQLite DB with AUTOFOLIO_MULTI_TENANT_ENABLED=1. Asserts actual
DB rows, not mocks. Covers all isolation layers required by INIT-MULTITENANT-ENGINE.

Layers tested:
  1. Conditions — list_active_conditions scoping
  2. Order/execution logs — list_order_logs scoping
  3. Aggregates — today_order_amount, today_realized_pnl, total_buy_cost_basis per-user
  4. Engine run — run_once(user_id=A) only processes A's conditions
  5. Safety/circuit-breaker — daily-loss trip AND consecutive-failures each disable only A
  6. Engine state / kill-switch — per-user; A's state does NOT leak to B
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from app.brokers.mock.mock_client import MockBrokerClient
from app.database.repositories import Repository, WhitelistSymbol
from app.database.sqlite_db import initialize_database
from app.engine.live_trading_engine import LiveTradingEngine
from app.risk.safety_checker import SafetyChecker


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _setup_db(tmp_path: Path, db_name: str = "iso_e2e.db") -> tuple[Path, Repository]:
    """Create and seed a fresh temp DB. Returns (db_path, repo)."""
    db = tmp_path / db_name
    initialize_database(db)
    repo = Repository(db)
    repo.add_whitelist_symbol(
        WhitelistSymbol(symbol="005930", name="삼성전자", market="KRX", role="LARGE_CAP_TEST")
    )
    # GLOBAL defaults: both users inherit these unless overridden per-user
    repo.set_system_state("auto_trading_enabled", "true")
    repo.set_system_state("kill_switch_active", "false")
    repo.set_system_state("global_mode", "L2")
    return db, repo


def _patch_trading_env(monkeypatch) -> None:
    """Bypass time-of-day and holiday guards so tests run at any time."""
    import app.risk.safety_checker as sc_mod
    monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)
    monkeypatch.setattr(sc_mod, "is_krx_holiday", lambda d: False)


def _seed_pnl_cycle(
    repo: Repository,
    user_id: str,
    buy_price: float = 75_000.0,
    sell_price: float = 60_000.0,
    qty: int = 1,
) -> None:
    """Insert a BUY+SELL execution cycle where realized PnL = (sell_price - buy_price) * qty
    (positive when sell > buy, negative when sell < buy)."""
    buy_cid = repo.add_trade_condition(
        symbol="005930", side="BUY", target_price=buy_price, quantity=qty, user_id=user_id
    )
    buy_oid = repo.create_order_log(
        condition_id=buy_cid, symbol="005930", side="BUY", order_type="LIMIT",
        order_price=buy_price, current_price=buy_price, quantity=qty,
        kis_order_id=None, order_status="FILLED", user_id=user_id,
    )
    repo.create_execution_log(
        order_log_id=buy_oid, symbol="005930",
        filled_price=buy_price, filled_quantity=qty, user_id=user_id,
    )
    sell_cid = repo.add_trade_condition(
        symbol="005930", side="SELL", target_price=sell_price, quantity=qty, user_id=user_id
    )
    sell_oid = repo.create_order_log(
        condition_id=sell_cid, symbol="005930", side="SELL", order_type="LIMIT",
        order_price=sell_price, current_price=sell_price, quantity=qty,
        kis_order_id=None, order_status="FILLED", user_id=user_id,
    )
    repo.create_execution_log(
        order_log_id=sell_oid, symbol="005930",
        filled_price=sell_price, filled_quantity=qty, user_id=user_id,
    )


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def iso_env(tmp_path, monkeypatch):
    """Full isolation environment with flag ON, two users A and B."""
    monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
    monkeypatch.setenv("AUTOFOLIO_AUTO_EXEC_ENABLED", "1")
    _patch_trading_env(monkeypatch)
    db, repo = _setup_db(tmp_path)
    broker = MockBrokerClient(prices={"005930": 69_800.0})
    engine = LiveTradingEngine(broker=broker, repo=repo)
    checker = SafetyChecker(repo)
    return repo, broker, engine, checker


# ---------------------------------------------------------------------------
# Layer 1: Conditions isolation
# ---------------------------------------------------------------------------

def test_layer1_conditions_scoped_per_user(iso_env):
    """list_active_conditions(user_id=A) returns only A's rows, not B's."""
    repo, *_ = iso_env
    cid_a = repo.add_trade_condition(
        symbol="005930", side="BUY", target_price=70_000, quantity=1,
        order_type="LIMIT", user_id="user_a",
    )
    cid_b = repo.add_trade_condition(
        symbol="005930", side="BUY", target_price=70_000, quantity=1,
        order_type="LIMIT", user_id="user_b",
    )

    conds_a = repo.list_active_conditions(user_id="user_a")
    conds_b = repo.list_active_conditions(user_id="user_b")

    ids_a = {c["id"] for c in conds_a}
    ids_b = {c["id"] for c in conds_b}
    assert cid_a in ids_a, "user_a's condition must appear in user_a's list"
    assert cid_b not in ids_a, "user_b's condition must NOT appear in user_a's list"
    assert cid_b in ids_b, "user_b's condition must appear in user_b's list"
    assert cid_a not in ids_b, "user_a's condition must NOT appear in user_b's list"


def test_layer1_conditions_add_with_user_id_stores_user_id(iso_env):
    """Conditions created with user_id have that user_id stored in the DB row."""
    repo, *_ = iso_env
    cid = repo.add_trade_condition(
        symbol="005930", side="BUY", target_price=70_000, quantity=1,
        order_type="LIMIT", user_id="user_a",
    )
    row = repo.get_condition(cid)
    assert row["user_id"] == "user_a"


# ---------------------------------------------------------------------------
# Layer 2: Order / execution logs isolation
# ---------------------------------------------------------------------------

def test_layer2_order_logs_scoped_per_user(iso_env):
    """list_order_logs(user_id=A) returns only A's order rows, not B's."""
    repo, *_ = iso_env
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
    ids_a = {r["id"] for r in logs_a}
    ids_b = {r["id"] for r in logs_b}

    assert oid_a in ids_a, "user_a order must appear in user_a's logs"
    assert oid_b not in ids_a, "user_b order must NOT appear in user_a's logs"
    assert oid_b in ids_b, "user_b order must appear in user_b's logs"
    assert oid_a not in ids_b, "user_a order must NOT appear in user_b's logs"


def test_layer2_execution_logs_scoped_per_user(iso_env):
    """Execution logs created with user_id are stored with that user_id."""
    repo, *_ = iso_env
    cid_a = repo.add_trade_condition(
        symbol="005930", side="BUY", target_price=70_000, quantity=1, user_id="user_a"
    )
    oid_a = repo.create_order_log(
        condition_id=cid_a, symbol="005930", side="BUY", order_type="LIMIT",
        order_price=70_000, current_price=69_800, quantity=1,
        kis_order_id="A-001", order_status="FILLED", user_id="user_a",
    )
    eid_a = repo.create_execution_log(
        order_log_id=oid_a, symbol="005930",
        filled_price=70_000.0, filled_quantity=1, user_id="user_a",
    )
    from app.database.sqlite_db import get_connection
    with get_connection(repo.db_path) as conn:
        row = conn.execute("SELECT user_id FROM execution_logs WHERE id = ?", (eid_a,)).fetchone()
    assert row["user_id"] == "user_a"


# ---------------------------------------------------------------------------
# Layer 3: Aggregate isolation
# ---------------------------------------------------------------------------

def test_layer3_today_order_amount_per_user(iso_env):
    """today_order_amount(user_id=A) does NOT include user_b's orders."""
    repo, *_ = iso_env
    cid_a = repo.add_trade_condition(
        symbol="005930", side="BUY", target_price=70_000, quantity=2, user_id="user_a"
    )
    cid_b = repo.add_trade_condition(
        symbol="005930", side="BUY", target_price=70_000, quantity=5, user_id="user_b"
    )
    repo.create_order_log(
        condition_id=cid_a, symbol="005930", side="BUY", order_type="LIMIT",
        order_price=70_000, current_price=70_000, quantity=2,
        kis_order_id="A-001", order_status="FILLED", user_id="user_a",
    )
    repo.create_order_log(
        condition_id=cid_b, symbol="005930", side="BUY", order_type="LIMIT",
        order_price=70_000, current_price=70_000, quantity=5,
        kis_order_id="B-001", order_status="FILLED", user_id="user_b",
    )

    amt_a = repo.today_order_amount(user_id="user_a")
    amt_b = repo.today_order_amount(user_id="user_b")

    assert amt_a == pytest.approx(70_000 * 2, rel=1e-6), f"user_a amount: {amt_a}"
    assert amt_b == pytest.approx(70_000 * 5, rel=1e-6), f"user_b amount: {amt_b}"
    assert amt_a != amt_b, "Amounts must differ because users have different orders"


def test_layer3_realized_pnl_per_user(iso_env):
    """today_realized_pnl(user_id=A) only reflects A's executions."""
    repo, *_ = iso_env
    # A: profitable cycle (buy 60k, sell 70k)
    _seed_pnl_cycle(repo, "user_a", buy_price=60_000.0, sell_price=70_000.0, qty=1)
    # B: loss cycle (buy 75k, sell 60k) — should not affect A's PnL
    _seed_pnl_cycle(repo, "user_b", buy_price=75_000.0, sell_price=60_000.0, qty=1)

    pnl_a = repo.today_realized_pnl(user_id="user_a")
    pnl_b = repo.today_realized_pnl(user_id="user_b")

    # Exact values: PnL = (sell - buy) * qty
    # user_a: (70_000 - 60_000) * 1 = +10_000
    # user_b: (60_000 - 75_000) * 1 = -15_000
    assert pnl_a == pytest.approx(10_000, rel=1e-6), (
        f"user_a expected profit +10_000 (buy 60k→sell 70k×1), got: {pnl_a}"
    )
    assert pnl_b == pytest.approx(-15_000, rel=1e-6), (
        f"user_b expected loss -15_000 (buy 75k→sell 60k×1), got: {pnl_b}"
    )


def test_layer3_cost_basis_per_user(iso_env):
    """total_buy_cost_basis(user_id=A) only counts A's BUY fills."""
    repo, *_ = iso_env
    cid_a = repo.add_trade_condition(
        symbol="005930", side="BUY", target_price=70_000, quantity=2, user_id="user_a"
    )
    cid_b = repo.add_trade_condition(
        symbol="005930", side="BUY", target_price=70_000, quantity=10, user_id="user_b"
    )
    oid_a = repo.create_order_log(
        condition_id=cid_a, symbol="005930", side="BUY", order_type="LIMIT",
        order_price=70_000, current_price=70_000, quantity=2,
        kis_order_id="A-001", order_status="FILLED", user_id="user_a",
    )
    oid_b = repo.create_order_log(
        condition_id=cid_b, symbol="005930", side="BUY", order_type="LIMIT",
        order_price=70_000, current_price=70_000, quantity=10,
        kis_order_id="B-001", order_status="FILLED", user_id="user_b",
    )
    repo.create_execution_log(
        order_log_id=oid_a, symbol="005930",
        filled_price=70_000.0, filled_quantity=2, user_id="user_a",
    )
    repo.create_execution_log(
        order_log_id=oid_b, symbol="005930",
        filled_price=70_000.0, filled_quantity=10, user_id="user_b",
    )

    basis_a = repo.total_buy_cost_basis(user_id="user_a")
    basis_b = repo.total_buy_cost_basis(user_id="user_b")

    assert basis_a == pytest.approx(70_000 * 2, rel=1e-6), f"user_a basis: {basis_a}"
    assert basis_b == pytest.approx(70_000 * 10, rel=1e-6), f"user_b basis: {basis_b}"


# ---------------------------------------------------------------------------
# Layer 4: Engine run scoping
# ---------------------------------------------------------------------------

def test_layer4_run_once_processes_only_target_user_conditions(iso_env):
    """run_once(user_id=user_a) processes only user_a's conditions; user_b untouched."""
    repo, broker, engine, _ = iso_env
    # Set per-user auto_trading_enabled (flag ON path)
    repo.set_engine_state("auto_trading_enabled", "true", user_id="user_a")
    repo.set_engine_state("auto_trading_enabled", "true", user_id="user_b")

    cid_a = repo.add_trade_condition(
        symbol="005930", side="BUY", target_price=70_000, quantity=1,
        order_type="LIMIT", auto_enabled=True, user_id="user_a",
    )
    cid_b = repo.add_trade_condition(
        symbol="005930", side="BUY", target_price=70_000, quantity=1,
        order_type="LIMIT", auto_enabled=True, user_id="user_b",
    )

    msgs = engine.run_once(user_id="user_a")
    assert len(msgs) >= 1, "Engine must have processed at least one condition"

    logs_a = repo.list_order_logs(user_id="user_a")
    logs_b = repo.list_order_logs(user_id="user_b")

    assert len(logs_a) >= 1, "user_a's condition should produce an order log"
    assert len(logs_b) == 0, "user_b's condition must NOT be processed by user_a's run"

    # user_b's condition must remain ACTIVE
    cond_b = repo.get_condition(cid_b)
    assert cond_b["status"] == "ACTIVE", f"user_b condition status: {cond_b['status']}"


def test_layer4_run_once_order_log_tagged_with_correct_user_id(iso_env):
    """run_once(user_id=user_a) tags the produced order_log with user_id=user_a."""
    repo, broker, engine, _ = iso_env
    repo.set_engine_state("auto_trading_enabled", "true", user_id="user_a")

    repo.add_trade_condition(
        symbol="005930", side="BUY", target_price=70_000, quantity=1,
        order_type="LIMIT", auto_enabled=True, user_id="user_a",
    )
    engine.run_once(user_id="user_a")

    logs_a = repo.list_order_logs(user_id="user_a")
    assert len(logs_a) >= 1
    for log in logs_a:
        assert log["user_id"] == "user_a", f"Order log must have user_id='user_a', got: {log['user_id']}"


# ---------------------------------------------------------------------------
# Layer 5: Safety / circuit-breaker isolation
# ---------------------------------------------------------------------------

def test_layer5_daily_loss_cb_trips_only_user_a(iso_env):
    """A's daily-loss circuit breaker disables ONLY A's auto_trading; B still trades."""
    repo, _, _, checker = iso_env
    # Seed user_a with a loss >= 3% of max_daily_amount (300k). Loss = 15k > 9k (3%).
    _seed_pnl_cycle(repo, "user_a", buy_price=75_000.0, sell_price=60_000.0, qty=1)

    r_a = checker.check(
        condition={
            "id": 1, "symbol": "005930", "side": "BUY", "quantity": 1,
            "status": "ACTIVE", "cooldown_until": None, "order_type": "LIMIT",
        },
        current_price=69_800,
        now=datetime.now(),
        user_id="user_a",
    )
    assert not r_a.allowed, f"user_a should be blocked by CB, got: {r_a.reason}"
    assert "circuit breaker" in r_a.reason.lower() or "disabled" in r_a.reason.lower()

    # GLOBAL auto_trading must be untouched
    assert repo.get_system_state("auto_trading_enabled") == "true"

    # Per-user disable must have been persisted for user_a (not just in-memory)
    assert repo.get_engine_state("auto_trading_enabled", user_id="user_a") == "false", (
        "user_a per-user auto_trading_enabled must be persisted as 'false' after CB trip"
    )
    # user_b has no per-user row → must fall back to GLOBAL "true" (no leak from user_a)
    assert repo.get_engine_state("auto_trading_enabled", user_id="user_b") == "true", (
        "user_b must still see GLOBAL 'true'; user_a CB must not leak to user_b"
    )

    # user_b has no losses and must still be allowed
    r_b = checker.check(
        condition={
            "id": 2, "symbol": "005930", "side": "BUY", "quantity": 1,
            "status": "ACTIVE", "cooldown_until": None, "order_type": "LIMIT",
        },
        current_price=69_800,
        now=datetime.now(),
        user_id="user_b",
    )
    assert r_b.allowed, f"user_b should still trade after user_a CB trip, got: {r_b.reason}"


def test_layer5_consecutive_failures_cb_trips_only_user_a(iso_env):
    """3 consecutive failures for user_a disable ONLY user_a; user_b unaffected."""
    repo, _, _, checker = iso_env

    for _ in range(3):
        repo.increment_consecutive_failures(user_id="user_a")

    r_a = checker.check(
        condition={
            "id": 1, "symbol": "005930", "side": "BUY", "quantity": 1,
            "status": "ACTIVE", "cooldown_until": None, "order_type": "LIMIT",
        },
        current_price=69_800,
        now=datetime.now(),
        user_id="user_a",
    )
    assert not r_a.allowed
    assert "consecutive" in r_a.reason.lower()

    # GLOBAL counter must be 0 (per-user counter was used, not global)
    assert repo.get_system_state("consecutive_order_failures", "0") == "0"

    r_b = checker.check(
        condition={
            "id": 2, "symbol": "005930", "side": "BUY", "quantity": 1,
            "status": "ACTIVE", "cooldown_until": None, "order_type": "LIMIT",
        },
        current_price=69_800,
        now=datetime.now(),
        user_id="user_b",
    )
    assert r_b.allowed, f"user_b must be unaffected by user_a consecutive-failure CB: {r_b.reason}"
    assert repo.get_consecutive_failures(user_id="user_b") == 0


# ---------------------------------------------------------------------------
# Layer 6: Engine state / kill-switch isolation
# ---------------------------------------------------------------------------

def test_layer6_engine_state_per_user_write_does_not_leak(iso_env):
    """set_engine_state for user_a does NOT affect user_b or the GLOBAL row."""
    repo, *_ = iso_env

    # Write a per-user kill-switch for user_a only
    repo.set_engine_state("kill_switch_active", "true", user_id="user_a")

    assert repo.get_engine_state("kill_switch_active", user_id="user_a") == "true"
    # user_b falls back to GLOBAL (="false")
    assert repo.get_engine_state("kill_switch_active", user_id="user_b") == "false"
    # GLOBAL row unchanged
    assert repo.get_system_state("kill_switch_active") == "false"


def test_layer6_per_user_kill_switch_blocks_only_that_user(iso_env):
    """SafetyChecker: per-user kill switch blocks user_a but not user_b."""
    repo, _, _, checker = iso_env

    repo.set_engine_state("kill_switch_active", "true", user_id="user_a")
    cond = {
        "id": 1, "symbol": "005930", "side": "BUY", "quantity": 1,
        "status": "ACTIVE", "cooldown_until": None, "order_type": "LIMIT",
    }

    r_a = checker.check(condition=cond, current_price=69_800, now=datetime.now(), user_id="user_a")
    assert not r_a.allowed
    assert "kill switch" in r_a.reason.lower()

    r_b = checker.check(condition=cond, current_price=69_800, now=datetime.now(), user_id="user_b")
    assert r_b.allowed, f"user_b must not be blocked by user_a kill switch: {r_b.reason}"


def test_layer6_global_fallback_only_when_no_per_user_state(iso_env):
    """Per-user reads fall back to GLOBAL only when no per-user row exists."""
    repo, *_ = iso_env

    # No per-user row for auto_trading_enabled: should fall back to GLOBAL "true"
    global_val = repo.get_engine_state("auto_trading_enabled", "MISSING", user_id="user_new")
    assert global_val == "true", f"Expected GLOBAL fallback 'true', got: {global_val}"

    # Set per-user override
    repo.set_engine_state("auto_trading_enabled", "false", user_id="user_new")
    per_user_val = repo.get_engine_state("auto_trading_enabled", "MISSING", user_id="user_new")
    assert per_user_val == "false", f"Per-user override should read 'false', got: {per_user_val}"

    # Another new user still sees the GLOBAL fallback
    other_val = repo.get_engine_state("auto_trading_enabled", "MISSING", user_id="user_other")
    assert other_val == "true", f"Unrelated user should see GLOBAL 'true', got: {other_val}"
