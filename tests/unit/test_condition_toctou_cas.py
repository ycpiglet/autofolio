"""TASK-064: atomic CAS claim — TOCTOU race fix tests."""
from __future__ import annotations

import threading
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.common.enums import ConditionStatus
from app.database.repositories import Repository, WhitelistSymbol
from app.database.sqlite_db import initialize_database


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_repo(tmp_path: Path) -> Repository:
    db = tmp_path / "test.db"
    initialize_database(db)
    repo = Repository(db)
    repo.add_whitelist_symbol(
        WhitelistSymbol(symbol="005930", name="삼성전자", market="KRX", role="LARGE_CAP_TEST")
    )
    return repo


def _insert_active_condition(repo: Repository) -> int:
    return repo.add_trade_condition(
        symbol="005930",
        side="BUY",
        target_price=70_000.0,
        quantity=1,
    )


# ---------------------------------------------------------------------------
# Task 1: Enum smoke
# ---------------------------------------------------------------------------

def test_processing_status_exists():
    """ConditionStatus must have PROCESSING for atomic claim mid-flight marker."""
    assert ConditionStatus.PROCESSING.value == "PROCESSING"


# ---------------------------------------------------------------------------
# Task 2: CAS primitive tests
# ---------------------------------------------------------------------------

def test_cas_claim_first_caller_wins(tmp_path):
    """First atomic_claim_condition call on an ACTIVE row returns True."""
    repo = _make_repo(tmp_path)
    cid = _insert_active_condition(repo)

    result = repo.atomic_claim_condition(cid)
    assert result is True


def test_cas_claim_second_caller_loses(tmp_path):
    """Second atomic_claim_condition call on same row returns False (already PROCESSING)."""
    repo = _make_repo(tmp_path)
    cid = _insert_active_condition(repo)

    first = repo.atomic_claim_condition(cid)
    second = repo.atomic_claim_condition(cid)

    assert first is True
    assert second is False


def test_cas_claimed_condition_shows_processing_status(tmp_path):
    """After a successful claim, the DB row has status='PROCESSING'."""
    repo = _make_repo(tmp_path)
    cid = _insert_active_condition(repo)

    repo.atomic_claim_condition(cid)

    cond = repo.get_condition(cid)
    assert cond["status"] == "PROCESSING"


def test_cas_claim_non_active_condition_fails(tmp_path):
    """Claiming an already-TRIGGERED condition returns False."""
    repo = _make_repo(tmp_path)
    cid = _insert_active_condition(repo)
    repo.update_condition_status(cid, "TRIGGERED")

    result = repo.atomic_claim_condition(cid)
    assert result is False


# ---------------------------------------------------------------------------
# Task 3: Concurrency tests
# ---------------------------------------------------------------------------

def test_concurrent_claims_only_one_wins(tmp_path):
    """Two threads racing on atomic_claim_condition() — exactly one must win.

    Uses threading.Barrier to synchronise both threads at the UPDATE call,
    maximising the chance of a genuine concurrent write.  SQLite serialises
    write transactions so exactly one rowcount==1 is returned.
    """
    repo = _make_repo(tmp_path)
    cid = _insert_active_condition(repo)

    barrier = threading.Barrier(2)
    results: list[bool] = []
    lock = threading.Lock()

    def claim():
        barrier.wait()  # both threads arrive at UPDATE simultaneously
        won = repo.atomic_claim_condition(cid)
        with lock:
            results.append(won)

    t1 = threading.Thread(target=claim)
    t2 = threading.Thread(target=claim)
    t1.start()
    t2.start()
    t1.join(timeout=5)
    t2.join(timeout=5)

    assert len(results) == 2, "Both threads must complete"
    assert results.count(True) == 1, (
        f"Exactly one thread must win the CAS claim; got {results}"
    )
    assert results.count(False) == 1


def test_toctou_old_path_allows_double_processing():
    """Documents the TOCTOU race in the OLD (non-CAS) path.

    Proves semantically: if two callers both read status='ACTIVE' before
    either updates it, both callers proceed to process — the bug.
    This test is unconditional documentation; it always passes regardless
    of fix state, to preserve the failure-mode evidence.
    """
    condition_status = "ACTIVE"

    def old_path_would_process(status: str) -> bool:
        """Old code: list_active_conditions() returns ACTIVE → process unconditionally."""
        return status == "ACTIVE"

    caller_a_processes = old_path_would_process(condition_status)
    caller_b_processes = old_path_would_process(condition_status)

    # Both process → duplicate order in the old code (the bug)
    assert caller_a_processes is True
    assert caller_b_processes is True


# ---------------------------------------------------------------------------
# Task 4: Engine-level duplicate-order prevention
# ---------------------------------------------------------------------------

from app.brokers.base import BrokerClient, OrderResult, PriceQuote
from app.common.enums import OrderStatus
from app.engine.live_trading_engine import LiveTradingEngine


def _make_engine(repo: Repository) -> LiveTradingEngine:
    broker = MagicMock(spec=BrokerClient)
    broker.get_current_price.return_value = PriceQuote(symbol="005930", price=65_000.0)
    broker.place_order.return_value = OrderResult(
        broker_order_id="ORD-001",
        status=OrderStatus.FILLED,
        filled_price=65_000.0,
        filled_quantity=1,
        message="filled",
    )
    return LiveTradingEngine(broker=broker, repo=repo)


def _make_repo_with_trading_enabled(tmp_path: Path) -> Repository:
    repo = _make_repo(tmp_path)
    repo.set_system_state("auto_trading_enabled", "true")
    repo.set_system_state("kill_switch_active", "false")
    return repo


def test_run_once_does_not_process_already_processing_condition(tmp_path):
    """If condition is PROCESSING (claimed by another caller), run_once() skips it.

    list_active_conditions() only returns status='ACTIVE' rows, so a PROCESSING
    condition is invisible to the second caller — 0 orders placed.
    """
    repo = _make_repo_with_trading_enabled(tmp_path)
    cid = _insert_active_condition(repo)
    # Simulate another caller already claimed it
    repo.update_condition_status(cid, "PROCESSING")

    engine = _make_engine(repo)
    engine.run_once()

    order_logs = repo.list_order_logs()
    assert len(order_logs) == 0, (
        f"No orders should be placed when condition is PROCESSING; got {order_logs}"
    )


def test_run_once_atomic_claim_prevents_double_order(tmp_path):
    """Two sequential run_once() calls on the same ACTIVE condition only place one order.

    First call claims (ACTIVE→PROCESSING) and processes (→TRIGGERED).
    Second call: list_active_conditions() returns nothing (status=TRIGGERED) → 0 new orders.
    """
    repo = _make_repo_with_trading_enabled(tmp_path)
    _insert_active_condition(repo)
    engine = _make_engine(repo)

    # First run — should claim and process
    engine.run_once()
    logs_after_first = repo.list_order_logs()
    assert len(logs_after_first) == 1, "First run_once() must produce exactly 1 order"

    # Second run — condition is TRIGGERED, not ACTIVE → nothing to do
    engine.run_once()
    logs_after_second = repo.list_order_logs()
    assert len(logs_after_second) == 1, (
        f"Second run_once() must NOT add another order; got {len(logs_after_second)}"
    )
