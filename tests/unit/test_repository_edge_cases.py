"""Repository boundary and persistence edge-case tests."""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from app.database.repositories import Repository, WhitelistSymbol
from app.database.sqlite_db import get_connection, initialize_database


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def repo():
    with TemporaryDirectory() as tmpdir:
        db = Path(tmpdir) / "test.db"
        initialize_database(db)
        r = Repository(db)
        r.add_whitelist_symbol(
            WhitelistSymbol(symbol="005930", name="삼성전자", market="KRX", role="LARGE_CAP_TEST")
        )
        yield r


def _insert_order_log(
    repo: Repository,
    *,
    order_status: str,
    order_price: float,
    quantity: int,
    days_offset: int = 0,
) -> None:
    """Insert an order_log row with created_at set to the local date + days_offset.

    today_order_amount() filters with DATE(created_at) = DATE('now', 'localtime').
    CURRENT_TIMESTAMP stores UTC, which on a UTC+9 machine before 09:00 KST falls
    on the previous UTC date — so the filter misses those rows.
    This helper sets created_at to the local date string directly so tests are
    timezone-safe on any host.
    """
    from datetime import datetime as _dt, timedelta as _td
    local_now = _dt.now()
    target_day = (local_now + _td(days=days_offset)).strftime("%Y-%m-%d")
    created_at = f"{target_day} 10:00:00"  # Use a stable mid-day time
    with get_connection(repo.db_path) as conn:
        conn.execute(
            """
            INSERT INTO order_logs(
                condition_id, symbol, side, order_type, order_price,
                current_price, quantity, kis_order_id, order_status,
                fallback_to_market, error_message, created_at
            ) VALUES (1, '005930', 'BUY', 'LIMIT', ?, ?, ?, NULL, ?, 0, NULL, ?)
            """,
            (order_price, order_price, quantity, order_status, created_at),
        )


# ---------------------------------------------------------------------------
# today_order_amount — status filtering
# ---------------------------------------------------------------------------

def test_today_order_amount_only_counts_active_statuses(repo):
    """FILLED is counted; CANCELED and FAILED are excluded from today_order_amount."""
    _insert_order_log(repo, order_status="FILLED",   order_price=10_000.0, quantity=2)
    _insert_order_log(repo, order_status="CANCELED", order_price=10_000.0, quantity=5)
    _insert_order_log(repo, order_status="FAILED",   order_price=10_000.0, quantity=3)

    amount = repo.today_order_amount()
    # Only the FILLED order: 10_000 * 2 = 20_000
    assert amount == pytest.approx(20_000.0)


def test_today_order_amount_ignores_previous_days(repo):
    """Orders with yesterday's local timestamp are not counted in today's amount."""
    _insert_order_log(repo, order_status="FILLED", order_price=10_000.0, quantity=10,
                      days_offset=-1)
    amount = repo.today_order_amount()
    assert amount == pytest.approx(0.0)


def test_today_order_amount_includes_pending_and_requested(repo):
    """PENDING and REQUESTED orders are counted in today_order_amount."""
    _insert_order_log(repo, order_status="PENDING",   order_price=5_000.0, quantity=3)
    _insert_order_log(repo, order_status="REQUESTED", order_price=5_000.0, quantity=2)

    amount = repo.today_order_amount()
    # 5_000 * 3 + 5_000 * 2 = 25_000
    assert amount == pytest.approx(25_000.0)


# ---------------------------------------------------------------------------
# add_trade_condition — duplicate symbol+side
# ---------------------------------------------------------------------------

def test_add_condition_duplicate_symbol_side_both_exist(repo):
    """Two conditions with identical symbol and side can both exist (no uniqueness constraint)."""
    cid1 = repo.add_trade_condition(
        symbol="005930", side="BUY", target_price=70_000.0, quantity=1,
        order_type="LIMIT", auto_enabled=True,
    )
    cid2 = repo.add_trade_condition(
        symbol="005930", side="BUY", target_price=68_000.0, quantity=2,
        order_type="LIMIT", auto_enabled=False,
    )
    assert cid1 != cid2
    all_conds = repo.list_conditions()
    ids = {c["id"] for c in all_conds}
    assert cid1 in ids
    assert cid2 in ids


# ---------------------------------------------------------------------------
# list_active_conditions — status exclusions
# ---------------------------------------------------------------------------

def test_list_active_conditions_excludes_triggered_and_completed(repo):
    """TRIGGERED and COMPLETED conditions are not returned by list_active_conditions."""
    cid1 = repo.add_trade_condition(
        symbol="005930", side="BUY", target_price=70_000.0, quantity=1,
        order_type="LIMIT", auto_enabled=True,
    )
    cid2 = repo.add_trade_condition(
        symbol="005930", side="SELL", target_price=75_000.0, quantity=1,
        order_type="LIMIT", auto_enabled=True,
    )
    repo.update_condition_status(cid1, "TRIGGERED")
    repo.update_condition_status(cid2, "DISABLED")

    active = repo.list_active_conditions()
    active_ids = {c["id"] for c in active}
    assert cid1 not in active_ids
    assert cid2 not in active_ids


# ---------------------------------------------------------------------------
# increment_consecutive_failures — atomicity / sequential correctness
# ---------------------------------------------------------------------------

def test_increment_consecutive_failures_atomic(repo):
    """Calling increment_consecutive_failures twice yields a counter of 2."""
    repo.increment_consecutive_failures()
    repo.increment_consecutive_failures()
    value = repo.get_system_state("consecutive_order_failures", "0")
    assert int(value) == 2
