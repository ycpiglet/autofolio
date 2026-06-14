"""Tests for home view proposal approve/reject buttons — TASK-055.

Isolation rules:
- AppTest embedded scripts only (no sys.modules swap).
- monkeypatch via patch.object inside the embedded script.
- TZ-independent (no real timestamps).
"""
from __future__ import annotations


def _base_patches() -> str:
    """Common patch block for home view tests (injected into embedded scripts)."""
    return """
import pandas as pd
import streamlit as st
from unittest.mock import patch, MagicMock

from app.ui import backend
from app.ui.mock import data as mock_data
from app.ui.views import home

_proposals = pd.DataFrame([
    {"id": "P-101", "종목": "TIGER 미국S&P500", "방향": "매수", "목표가": 18_900,
     "수량": 20, "에이전트": "kr-etf-specialist", "확신도": "중", "근거": "분할매수"},
    {"id": "P-102", "종목": "삼성전자", "방향": "매수", "목표가": 72_000,
     "수량": 10, "에이전트": "kr-equity-specialist", "확신도": "상", "근거": "업황"},
])

_one_holding = pd.DataFrame([{
    "종목": "KODEX 200", "티커": "069500", "자산군": "ETF", "지역": "KR",
    "수량": 1, "평단": 100_000, "현재가": 101_000, "평가금액": 101_000,
    "평가손익": 1_000, "손익률": 1.0, "예상연배당": 0, "배당수익률": 0.0, "비중": 100.0,
}])
"""


def test_approve_button_is_not_noop(tmp_path):
    """Clicking 승인 must call backend.add_condition (backend mode) — not silently drop."""
    from streamlit.testing.v1 import AppTest

    script = tmp_path / "approve_test.py"
    script.write_text(
        _base_patches()
        + """
import streamlit as st

st.session_state["data_source"] = "backend"

add_condition_calls = []

def fake_add_condition(**kwargs):
    add_condition_calls.append(kwargs)
    return 99  # fake condition id

with (
    patch.object(mock_data, "proposals", lambda: _proposals),
    patch.object(backend, "holdings_df", lambda **kw: _one_holding),
    patch.object(backend, "kpis", lambda: {
        "총자산": 1_000_000, "일손익률": 0.0,
        "누적손익률": 0.0, "현금비중": 10.0, "평가손익": 0,
    }),
    patch.object(backend, "asset_curve", lambda: __import__("pandas").DataFrame({"자산": [1_000_000]})),
    patch.object(backend, "recent_fills", lambda **kw: __import__("pandas").DataFrame(
        columns=["시각", "종목", "방향", "수량", "체결가"]
    )),
    patch.object(backend, "watchlist", lambda: __import__("pandas").DataFrame(
        columns=["symbol", "name", "price"]
    )),
    patch.object(backend, "market_indices_df", lambda: __import__("pandas").DataFrame(
        columns=["name", "code", "price", "change", "change_rate"]
    )),
    patch.object(backend, "add_condition", fake_add_condition),
):
    home.render()

# Store the call count in session_state so AppTest can read it
st.session_state["_add_condition_calls"] = len(add_condition_calls)
""",
        encoding="utf-8",
    )

    at = AppTest.from_file(str(script)).run(timeout=20)
    assert not at.exception, f"render crashed: {at.exception}"

    # Find the first approve button (key ap_P-101)
    approve_buttons = [b for b in at.button if b.key and b.key.startswith("ap_")]
    assert approve_buttons, "No approve buttons rendered"

    # Click the first approve button — CURRENT BEHAVIOR: noop (test should FAIL before fix)
    at2 = at.button(key="ap_P-101").click().run(timeout=20)
    assert not at2.exception

    # After fix: expect success message
    success_msgs = [s.value for s in at2.success]
    assert success_msgs, (
        "Approve button click produced no st.success — still a no-op. "
        "Expected at least one success message after clicking 승인."
    )

    # Also verify add_condition was actually called (not just the fallback branch)
    try:
        calls_made = at2.session_state["_add_condition_calls"]
    except KeyError:
        calls_made = 0
    assert calls_made >= 1, (
        f"backend.add_condition was never called — got {calls_made} calls. "
        "Approve handler hit the exception-fallback branch instead of the real path."
    )


def test_reject_button_is_not_noop(tmp_path):
    """Clicking 거부 must dismiss the proposal with feedback (demo or backend mode)."""
    from streamlit.testing.v1 import AppTest

    script = tmp_path / "reject_test.py"
    script.write_text(
        _base_patches()
        + """
import streamlit as st

# Demo mode (no backend) — reject should still give feedback
st.session_state["data_source"] = "demo"

with (
    patch.object(mock_data, "proposals", lambda: _proposals),
    patch.object(mock_data, "holdings_df", lambda: _one_holding),
    patch.object(mock_data, "kpis", lambda: {
        "총자산": 1_000_000, "일손익률": 0.0,
        "누적손익률": 0.0, "현금비중": 10.0, "평가손익": 0,
    }),
    patch.object(mock_data, "asset_curve", lambda *a, **kw: __import__("pandas").DataFrame(
        {"자산": [1_000_000]}
    )),
    patch.object(mock_data, "recent_fills", lambda: __import__("pandas").DataFrame(
        columns=["시각", "종목", "방향", "수량", "체결가"]
    )),
    patch.object(mock_data, "watchlist", lambda: __import__("pandas").DataFrame(
        columns=["종목", "현재가", "등락률"]
    )),
):
    home.render()
""",
        encoding="utf-8",
    )

    at = AppTest.from_file(str(script)).run(timeout=20)
    assert not at.exception, f"render crashed: {at.exception}"

    reject_buttons = [b for b in at.button if b.key and b.key.startswith("rj_")]
    assert reject_buttons, "No reject buttons rendered"

    at2 = at.button(key="rj_P-101").click().run(timeout=20)
    assert not at2.exception

    # After fix: expect info or success message
    feedback_msgs = [s.value for s in at2.info] + [s.value for s in at2.success]
    assert feedback_msgs, (
        "Reject button click produced no st.info or st.success — still a no-op. "
        "Expected at least one feedback message after clicking 거부."
    )


def test_handled_proposal_removed_from_pending(tmp_path):
    """After approve, the proposal should disappear from the pending list on re-render."""
    from streamlit.testing.v1 import AppTest

    script = tmp_path / "remove_test.py"
    script.write_text(
        _base_patches()
        + """
import streamlit as st

st.session_state["data_source"] = "demo"
# Pre-seed: P-101 already handled
st.session_state.setdefault("handled_proposals", set()).add("P-101")

with (
    patch.object(mock_data, "proposals", lambda: _proposals),
    patch.object(mock_data, "holdings_df", lambda: _one_holding),
    patch.object(mock_data, "kpis", lambda: {
        "총자산": 1_000_000, "일손익률": 0.0,
        "누적손익률": 0.0, "현금비중": 10.0, "평가손익": 0,
    }),
    patch.object(mock_data, "asset_curve", lambda *a, **kw: __import__("pandas").DataFrame(
        {"자산": [1_000_000]}
    )),
    patch.object(mock_data, "recent_fills", lambda: __import__("pandas").DataFrame(
        columns=["시각", "종목", "방향", "수량", "체결가"]
    )),
    patch.object(mock_data, "watchlist", lambda: __import__("pandas").DataFrame(
        columns=["종목", "현재가", "등락률"]
    )),
):
    home.render()
""",
        encoding="utf-8",
    )

    at = AppTest.from_file(str(script)).run(timeout=20)
    assert not at.exception, f"render crashed: {at.exception}"

    # P-101 should NOT have buttons (it's handled); P-102 still should
    button_keys = [b.key for b in at.button if b.key and b.key.startswith(("ap_", "rj_"))]
    assert "ap_P-101" not in button_keys, (
        "Handled proposal P-101 still shows approve button — not filtered."
    )
    assert "ap_P-102" in button_keys, "Unhandled proposal P-102 must still appear"
