# Multitenant Phase 4 — Cross-User Isolation Tests + Flag-OFF Characterization

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Write two integration test files that prove the full multi-tenant stack (Phases 1-3) achieves cross-user isolation (flag ON) and is byte-identical to the single-owner system (flag OFF), plus a readiness doc listing what must land before the Owner flips the flag.

**Architecture:** Real (temp) SQLite DB through the repository layer; no mocks for DB. MockBrokerClient for broker. monkeypatch env vars for flag control. Two integration test files + one readiness doc.

**Tech Stack:** pytest, sqlite3 (via initialize_database), MockBrokerClient, LiveTradingEngine, SafetyChecker, Repository, app.services.flags.

## Global Constraints

- Test runner: `.venv\Scripts\python.exe -m pytest -q` (NOT `pytest tests/`)
- Baseline: 1743 passed / 0 failed — must end at 1743+ / 0 failed
- Flag env var: `AUTOFOLIO_MULTI_TENANT_ENABLED=1` for ON, `monkeypatch.delenv("AUTOFOLIO_MULTI_TENANT_ENABLED", raising=False)` for OFF
- Also need `AUTOFOLIO_AUTO_EXEC_ENABLED=1` for safety checker to pass auto_exec gate
- Branch: `feat/multitenant-phase4`
- No production code changes unless a test reveals a genuine isolation gap (then minimal fix + note it)
- Flag stays default OFF
- `python scripts/now.py` for timestamps
- Report to `.superpowers/sdd/multitenant-p4-report.md` (NOT git-added)
- Commit message: `test(multitenant): Phase 4 — cross-user 격리 e2e + flag-OFF characterization + flag-ON readiness`

---

### Task 1: E2E Cross-User Isolation Integration Test

**Files:**
- Create: `tests/integration/test_multitenant_isolation_e2e.py`

**Interfaces:**
- Consumes: `app.database.repositories.Repository`, `app.database.sqlite_db.initialize_database`, `app.database.repositories.WhitelistSymbol`, `app.brokers.mock.mock_client.MockBrokerClient`, `app.engine.live_trading_engine.LiveTradingEngine`, `app.risk.safety_checker.SafetyChecker`
- Produces: 12+ integration test functions covering 6 isolation layers

- [ ] **Step 1: Write the test file**

```python
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
from tempfile import TemporaryDirectory

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


def _seed_loss_cycle(
    repo: Repository,
    user_id: str,
    buy_price: float = 75_000.0,
    sell_price: float = 60_000.0,
    qty: int = 1,
) -> None:
    """Insert a BUY+SELL execution cycle where sell_price < buy_price → realized loss."""
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
    _seed_loss_cycle(repo, "user_a", buy_price=60_000.0, sell_price=70_000.0, qty=1)
    # B: loss cycle (buy 75k, sell 60k) — should not affect A's PnL
    _seed_loss_cycle(repo, "user_b", buy_price=75_000.0, sell_price=60_000.0, qty=1)

    pnl_a = repo.today_realized_pnl(user_id="user_a")
    pnl_b = repo.today_realized_pnl(user_id="user_b")

    assert pnl_a > 0, f"user_a should have profit, got: {pnl_a}"
    assert pnl_b < 0, f"user_b should have loss, got: {pnl_b}"


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
    _seed_loss_cycle(repo, "user_a", buy_price=75_000.0, sell_price=60_000.0, qty=1)

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
```

- [ ] **Step 2: Run only the new test file to verify it passes**

```
.venv\Scripts\python.exe -m pytest tests/integration/test_multitenant_isolation_e2e.py -v
```
Expected: All tests PASS. If any assertion fails, that is a genuine isolation gap — report it, do NOT weaken the assertion.

- [ ] **Step 3: Commit**

```
git add tests/integration/test_multitenant_isolation_e2e.py
```

---

### Task 2: Flag-OFF Characterization Test

**Files:**
- Create: `tests/integration/test_multitenant_flagoff_characterization.py`

**Interfaces:**
- Consumes: Same as Task 1
- Produces: 8+ test functions proving flag-OFF is byte-identical to the pre-multitenant single-owner system

- [ ] **Step 1: Write the characterization test file**

```python
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
```

- [ ] **Step 2: Run only the new test file to verify it passes**

```
.venv\Scripts\python.exe -m pytest tests/integration/test_multitenant_flagoff_characterization.py -v
```
Expected: All tests PASS.

- [ ] **Step 3: Commit (together with Task 1 file + Task 3 doc)**

```
git add tests/integration/test_multitenant_isolation_e2e.py tests/integration/test_multitenant_flagoff_characterization.py
```

---

### Task 3: Readiness Doc + Report

**Files:**
- Create: `agents/project/MULTITENANT-FLAG-ENABLE-READINESS.md`
- Create: `.superpowers/sdd/multitenant-p4-report.md` (NOT git-added)

- [ ] **Step 1: Get timestamp**

```
python scripts/now.py
```

- [ ] **Step 2: Write the readiness doc**

File: `agents/project/MULTITENANT-FLAG-ENABLE-READINESS.md`

Content must list the four prerequisite gating items (a-d from the task spec) before the Owner can set `AUTOFOLIO_MULTI_TENANT_ENABLED=1` in any shared/staging env.

- [ ] **Step 3: Run the full test suite to get final count**

```
.venv\Scripts\python.exe -m pytest -q
```
Expected: 1743+ passed / 0 failed

- [ ] **Step 4: Write the report to `.superpowers/sdd/multitenant-p4-report.md`**

Include: isolation assertions per layer, characterization assertions, full pytest -q result, any gap found, files changed. This file is NOT git-added.

- [ ] **Step 5: Git commit**

```
git add tests/integration/test_multitenant_isolation_e2e.py
git add tests/integration/test_multitenant_flagoff_characterization.py
git add agents/project/MULTITENANT-FLAG-ENABLE-READINESS.md
git commit -m "$(cat <<'EOF'
test(multitenant): Phase 4 — cross-user 격리 e2e + flag-OFF characterization + flag-ON readiness

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 6: Verify commit**

```
git log --oneline -3
```
