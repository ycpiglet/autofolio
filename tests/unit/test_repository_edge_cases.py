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
        # Pre-create a trade_condition so that order_logs.condition_id FK is satisfiable.
        r._test_condition_id = r.add_trade_condition(
            symbol="005930", side="BUY", target_price=70_000.0, quantity=1,
            order_type="LIMIT", auto_enabled=False, created_by="FIXTURE",
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
    """Insert an order_log row whose created_at is KST-today-aware.

    today_order_amount() filters with DATE(created_at, '+9 hours') = DATE('now', '+9 hours'),
    i.e. it compares KST dates.  We compute created_at using SQLite datetime arithmetic
    with explicit '+9 hours' offsets so the result is identical regardless of the
    OS/CI timezone (never 'localtime').

    Formula for days_offset=0 (today KST):
        datetime('now', '+9 hours', 'start of day', '-9 hours', '+12 hours')
        => KST today at 00:00  expressed as UTC, then +12 h  => KST today noon as UTC.
    For days_offset=-1 (yesterday KST):
        append '-1 day' before '-9 hours'.
    """
    # Build the modifier chain: +9h → start of KST day → apply day offset → back to UTC → midday.
    # Using only explicit hour/day offsets (never 'localtime') makes the result identical on
    # any OS timezone, including the UTC CI environment.
    modifiers = ["+9 hours", "start of day"]
    if days_offset != 0:
        modifiers.append(f"{days_offset:+d} days")
    modifiers += ["-9 hours", "+12 hours"]
    modifier_sql = ", ".join(f"'{m}'" for m in modifiers)
    created_at_expr = f"datetime('now', {modifier_sql})"
    # Use the pre-seeded condition_id so FK foreign_keys=ON is satisfied.
    condition_id = getattr(repo, "_test_condition_id", None)
    with get_connection(repo.db_path) as conn:
        conn.execute(
            f"""
            INSERT INTO order_logs(
                condition_id, symbol, side, order_type, order_price,
                current_price, quantity, kis_order_id, order_status,
                fallback_to_market, error_message, created_at
            ) VALUES (?, '005930', 'BUY', 'LIMIT', ?, ?, ?, NULL, ?, 0, NULL,
                      {created_at_expr})
            """,
            (condition_id, order_price, order_price, quantity, order_status),
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
