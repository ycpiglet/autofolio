from __future__ import annotations

from datetime import datetime, time

import pytest

from scripts import kis_minimal_order_smoke as smoke


class _Quote:
    def __init__(self, price: float) -> None:
        self.price = price


class _Position:
    def __init__(self, symbol: str, quantity: int) -> None:
        self.symbol = symbol
        self.quantity = quantity


class _ReadOnlyClient:
    def get_current_price(self, symbol: str) -> _Quote:
        return _Quote(400.0)

    def get_order_book(self, symbol: str) -> dict:
        return {"levels": [{} for _ in range(10)]}

    def get_buying_power(self, symbol: str, price: float) -> dict:
        return {"max_quantity": 100, "available_cash": 100_000.0}


def test_regular_session_guard_accepts_expected_kst_date():
    now = datetime(2026, 6, 19, 9, 1, tzinfo=smoke.KST)

    ok, reason = smoke._is_regular_session(
        now,
        start=time(9, 0),
        end=time(15, 20),
        expected_date=now.date(),
    )

    assert ok is True
    assert "pass" in reason


def test_regular_session_guard_blocks_wrong_expected_date():
    now = datetime(2026, 6, 19, 9, 1, tzinfo=smoke.KST)

    ok, reason = smoke._is_regular_session(
        now,
        start=time(9, 0),
        end=time(15, 20),
        expected_date=datetime(2026, 6, 18, tzinfo=smoke.KST).date(),
    )

    assert ok is False
    assert "expected" in reason


def test_choose_candidate_caps_quantity_and_notional():
    selected, checked = smoke._choose_candidate(
        _ReadOnlyClient(),
        symbol="004870",
        requested_qty=50,
        max_qty=5,
        max_notional=5_000,
        min_orderbook_levels=5,
    )

    assert selected["symbol"] == "004870"
    assert selected["planned_qty"] == 5
    assert selected["notional_estimate"] == 2_000
    assert checked[0]["buying_power_ok"] is True


def test_candidate_symbol_must_be_whitelisted():
    with pytest.raises(ValueError):
        smoke._candidate_list("999999")


def test_prod_confirmation_requires_execute_and_flag():
    parser = smoke.build_parser("prod")

    dry_run = parser.parse_args(["--env", "prod"])
    execute_without_flag = parser.parse_args(["--env", "prod", "--execute"])
    execute_with_flag = parser.parse_args(
        ["--env", "prod", "--execute", "--i-understand-this-places-real-orders"]
    )

    assert smoke._prod_confirmation_ok(dry_run) is False
    assert smoke._prod_confirmation_ok(execute_without_flag) is False
    assert smoke._prod_confirmation_ok(execute_with_flag) is True


def test_locked_entrypoint_rejects_env_override():
    assert smoke.main(["--env", "prod"], default_env="paper", locked_env=True) == 2


def test_write_local_result_only_promotes_passing_executed_paper(tmp_path, monkeypatch):
    latest = tmp_path / "latest_paper.json"
    monkeypatch.setattr(smoke, "RUN_DIR", tmp_path)
    monkeypatch.setattr(smoke, "LATEST_PAPER_PATH", latest)

    blocked = {
        "env": "paper",
        "started_at": "2026-06-19T09:01:00+09:00",
        "execute": False,
        "overall_status": "blocked",
    }
    passed = {
        "env": "paper",
        "started_at": "2026-06-19T09:02:00+09:00",
        "execute": True,
        "overall_status": "pass",
    }

    smoke._write_local_result(blocked, env="paper")
    assert latest.exists() is False

    smoke._write_local_result(passed, env="paper")
    assert latest.exists() is True
