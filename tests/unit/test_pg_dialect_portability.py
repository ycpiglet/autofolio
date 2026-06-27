"""SQLite-side guardrail tests for the Postgres dialect-portability changes.

These assert that the portable SQL forms introduced for cross-engine
compatibility (KST-day window computed in Python, ``WHERE <bool>`` instead of
``= 1``, ``SET active = FALSE``, and the backend-aware ON CONFLICT upserts)
produce results IDENTICAL to the original SQLite-only SQL. Postgres itself is
verified separately by the controller's live round-trip; here we only protect
the default SQLite path from any regression.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from app.database import repositories
from app.database.repositories import Repository, WhitelistSymbol, _kst_today_utc_bounds
from app.database.sqlite_db import get_connection, initialize_database

_KST = timezone(timedelta(hours=9))
_FMT = "%Y-%m-%d %H:%M:%S"


@pytest.fixture
def repo():
    with TemporaryDirectory() as tmpdir:
        db = Path(tmpdir) / "dialect.db"
        initialize_database(db)
        yield Repository(db)


def _kst_midnight_utc() -> datetime:
    """UTC instant of the current KST calendar day's 00:00 (mirrors the repo)."""
    now_kst = datetime.now(timezone.utc).astimezone(_KST)
    midnight = now_kst.replace(hour=0, minute=0, second=0, microsecond=0)
    return midnight.astimezone(timezone.utc)


def _fmt(dt: datetime) -> str:
    return dt.strftime(_FMT)


def _set_created_at(repo: Repository, order_id: int, value: str) -> None:
    with get_connection(repo.db_path) as conn:
        conn.execute(
            "UPDATE order_logs SET created_at = ? WHERE id = ?", (value, order_id)
        )


def _set_filled_at(repo: Repository, exec_order_id: int, value: str) -> None:
    with get_connection(repo.db_path) as conn:
        conn.execute(
            "UPDATE execution_logs SET filled_at = ? WHERE order_log_id = ?",
            (value, exec_order_id),
        )


def _new_order(repo: Repository, *, price: float, qty: int, kid: str) -> int:
    return repo.create_order_log(
        condition_id=None,
        symbol="005930",
        side="BUY",
        order_type="LIMIT",
        order_price=price,
        current_price=price,
        quantity=qty,
        kis_order_id=kid,
        order_status="FILLED",
    )


# ---------------------------------------------------------------------------
# _kst_today_utc_bounds — Python KST-day boundary helper
# ---------------------------------------------------------------------------
def test_kst_bounds_sqlite_form_is_text_with_exact_format():
    """On the default (SQLite) backend the bounds are 'YYYY-MM-DD HH:MM:SS' text."""
    lo, hi = _kst_today_utc_bounds()
    assert isinstance(lo, str) and isinstance(hi, str)
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", lo)
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", hi)


def test_kst_bounds_span_exactly_one_day_and_start_is_kst_midnight():
    lo, hi = _kst_today_utc_bounds()
    lo_dt = datetime.strptime(lo, _FMT)
    hi_dt = datetime.strptime(hi, _FMT)
    assert hi_dt - lo_dt == timedelta(days=1)
    # lo is the UTC instant of KST midnight → convert back to KST → 00:00:00.
    lo_kst = lo_dt.replace(tzinfo=timezone.utc).astimezone(_KST)
    assert (lo_kst.hour, lo_kst.minute, lo_kst.second) == (0, 0, 0)


# ---------------------------------------------------------------------------
# KST-day window — today_order_amount
# ---------------------------------------------------------------------------
def test_today_order_amount_kst_boundary_includes_0030_excludes_2330(repo):
    """Row at KST today 00:30 counts; row at KST yesterday 23:30 does not."""
    start = _kst_midnight_utc()
    today_0030 = _fmt(start + timedelta(minutes=30))       # 00:30 KST today
    yesterday_2330 = _fmt(start - timedelta(minutes=30))   # 23:30 KST yesterday

    oid_today = _new_order(repo, price=100.0, qty=2, kid="TODAY")     # 200
    oid_yest = _new_order(repo, price=500.0, qty=2, kid="YEST")       # 1000 (excluded)
    _set_created_at(repo, oid_today, today_0030)
    _set_created_at(repo, oid_yest, yesterday_2330)

    assert repo.today_order_amount() == pytest.approx(200.0)


def test_today_order_amount_matches_legacy_date_filter(repo):
    """The portable window returns the SAME rows the old DATE('+9 hours') filter did."""
    start = _kst_midnight_utc()
    samples = {
        "T0030": (start + timedelta(minutes=30), 100.0),        # in
        "TNOON": (start + timedelta(hours=12), 200.0),          # in
        "Y2330": (start - timedelta(minutes=30), 400.0),        # out (prev KST day)
        "M0030": (start + timedelta(days=1, minutes=30), 800.0),  # out (next KST day)
    }
    for kid, (ts, price) in samples.items():
        oid = _new_order(repo, price=price, qty=1, kid=kid)
        _set_created_at(repo, oid, _fmt(ts))

    legacy_sql = """
        SELECT COALESCE(SUM(COALESCE(order_price, current_price, 0) * quantity), 0) AS amount
        FROM order_logs
        WHERE DATE(created_at, '+9 hours') = DATE('now', '+9 hours')
          AND order_status IN ('REQUESTED', 'FILLED', 'PENDING')
    """
    with get_connection(repo.db_path) as conn:
        legacy = float(conn.execute(legacy_sql).fetchone()["amount"] or 0.0)

    assert repo.today_order_amount() == pytest.approx(legacy)
    assert repo.today_order_amount() == pytest.approx(300.0)  # T0030 + TNOON


# ---------------------------------------------------------------------------
# KST-day window — today_realized_pnl (filled_at)
# ---------------------------------------------------------------------------
def test_today_realized_pnl_kst_boundary_on_filled_at(repo):
    start = _kst_midnight_utc()
    today_0030 = _fmt(start + timedelta(minutes=30))
    yesterday_2330 = _fmt(start - timedelta(minutes=30))

    # Cost basis: one BUY @ 70_000 (no date filter on the avg-cost CTE).
    buy = _new_order(repo, price=70000.0, qty=1, kid="B1")
    repo.create_execution_log(order_log_id=buy, symbol="005930", filled_price=70000.0, filled_quantity=1)

    # SELL today (filled_at 00:30 KST) → realized (75_000-70_000)*1 = 5_000 counted.
    sell_today = repo.create_order_log(
        condition_id=None, symbol="005930", side="SELL", order_type="LIMIT",
        order_price=75000.0, current_price=75000.0, quantity=1,
        kis_order_id="S_TODAY", order_status="FILLED",
    )
    repo.create_execution_log(order_log_id=sell_today, symbol="005930", filled_price=75000.0, filled_quantity=1)
    _set_filled_at(repo, sell_today, today_0030)

    # SELL yesterday (filled_at 23:30 KST) → would be +10_000 but EXCLUDED.
    sell_yest = repo.create_order_log(
        condition_id=None, symbol="005930", side="SELL", order_type="LIMIT",
        order_price=80000.0, current_price=80000.0, quantity=1,
        kis_order_id="S_YEST", order_status="FILLED",
    )
    repo.create_execution_log(order_log_id=sell_yest, symbol="005930", filled_price=80000.0, filled_quantity=1)
    _set_filled_at(repo, sell_yest, yesterday_2330)

    assert repo.today_realized_pnl() == pytest.approx(5000.0)


# ---------------------------------------------------------------------------
# boolean compares — WHERE enabled / WHERE active / SET active = FALSE
# ---------------------------------------------------------------------------
def test_whitelist_enabled_filter(repo):
    repo.add_whitelist_symbol(WhitelistSymbol("005930", "삼성전자", "KRX", "LARGE_CAP", enabled=True))
    repo.add_whitelist_symbol(WhitelistSymbol("000660", "SK하이닉스", "KRX", "LARGE_CAP", enabled=False))

    all_rows = {r["symbol"] for r in repo.list_whitelist_symbols()}
    enabled_rows = {r["symbol"] for r in repo.list_whitelist_symbols(enabled_only=True)}

    assert all_rows == {"005930", "000660"}
    assert enabled_rows == {"005930"}
    assert repo.get_whitelist_symbol("005930") is not None
    # get_whitelist_symbol filters on `enabled` → a disabled symbol reads as None.
    assert repo.get_whitelist_symbol("000660") is None


def test_price_alert_active_filter_and_trigger(repo):
    aid = repo.add_price_alert("005930", 80000.0, "above")
    assert [a["id"] for a in repo.list_active_alerts()] == [aid]

    repo.trigger_alert(aid)  # SET active = FALSE
    assert repo.list_active_alerts() == []
    with get_connection(repo.db_path) as conn:
        row = conn.execute("SELECT active, triggered_at FROM price_alerts WHERE id = ?", (aid,)).fetchone()
    assert row["active"] == 0
    assert row["triggered_at"] is not None


# ---------------------------------------------------------------------------
# ON CONFLICT upserts — whitelist (symbol) and system_state (key)
# ---------------------------------------------------------------------------
def test_whitelist_on_conflict_symbol_upsert(repo):
    repo.add_whitelist_symbol(WhitelistSymbol("005930", "old name", "KRX", "ROLE_A", enabled=True))
    repo.add_whitelist_symbol(WhitelistSymbol("005930", "new name", "NASDAQ", "ROLE_B", enabled=False))

    rows = repo.list_whitelist_symbols()
    assert len(rows) == 1
    assert rows[0]["name"] == "new name"
    assert rows[0]["market"] == "NASDAQ"
    assert rows[0]["role"] == "ROLE_B"
    assert rows[0]["enabled"] == 0


def test_system_state_on_conflict_key_upsert(repo):
    repo.set_system_state("kill_switch_active", "true")
    assert repo.get_system_state("kill_switch_active") == "true"

    repo.set_system_state("kill_switch_active", "false")
    assert repo.get_system_state("kill_switch_active") == "false"

    with get_connection(repo.db_path) as conn:
        count = conn.execute(
            "SELECT COUNT(*) AS c FROM system_state WHERE key = ?",
            ("kill_switch_active",),
        ).fetchone()["c"]
    assert count == 1  # upsert, not duplicate insert


def test_default_backend_is_sqlite_for_these_tests():
    """Sanity: the suite runs on the SQLite path (PG branches are not taken)."""
    assert repositories._active_backend_is_postgres() is False
