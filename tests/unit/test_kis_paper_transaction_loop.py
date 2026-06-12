from __future__ import annotations

import json

import pytest

from scripts import kis_paper_transaction_loop as loop


def test_build_cycle_plan_rotates_symbols() -> None:
    plans = loop.build_cycle_plan(4)

    assert [plan.fill_symbol for plan in plans] == ["069500", "005930", "000660", "069500"]
    assert plans[0].unfilled_symbols == ("005930", "000660")
    assert plans[1].unfilled_symbols == ("069500", "000660")


@pytest.mark.parametrize("cycles", [0, loop.MAX_CYCLES + 1])
def test_build_cycle_plan_rejects_unbounded_cycles(cycles: int) -> None:
    with pytest.raises(ValueError):
        loop.build_cycle_plan(cycles)


def test_command_for_plan_keeps_existing_soak_runner() -> None:
    plan = loop.CyclePlan(cycle=1, fill_symbol="069500", unfilled_symbols=("005930", "000660"))

    command = loop.command_for_plan(plan, qty=1, attempts=3, sleep_sec=0.1)

    assert "kis_paper_transaction_soak.py" in command[1]
    assert command[command.index("--fill-symbol") + 1] == "069500"
    assert command[command.index("--qty") + 1] == "1"
    assert command[command.index("--attempts") + 1] == "3"


def test_parse_json_stdout_reads_last_json_line() -> None:
    payload = {"ok": True, "records": []}

    assert loop.parse_json_stdout("noise\n" + json.dumps(payload)) == payload


def test_summarize_child_is_redacted_counts_only() -> None:
    output = {
        "ok": True,
        "fill_symbol": "069500",
        "post_open_like_count": 0,
        "records": [
            {"status": "FILLED"},
            {"status": "FILLED"},
            {"status": "CANCELED"},
        ],
        "after": {
            "order_log_rows": 18,
            "recent_fills_rows": 10,
            "kis_today_order_rows": 33,
        },
    }

    summary = loop.summarize_child(output)

    assert summary == {
        "ok": True,
        "fill_symbol": "069500",
        "filled_records": 2,
        "canceled_records": 1,
        "post_open_like_count": 0,
        "order_log_rows_after": 18,
        "recent_fills_after": 10,
        "kis_today_order_rows_after": 33,
    }
