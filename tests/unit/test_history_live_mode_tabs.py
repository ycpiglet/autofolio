"""TASK-058: 라이브 모드 내역 화면 PnL/배당 탭 렌더 검증.

TDD: 현재 코드에서는 FAIL (조기 return), 수정 후 PASS.
"""
from __future__ import annotations

import pandas as pd


def _make_script(tmp_path) -> str:
    """라이브 모드 history.render() 임베디드 앱 스크립트 경로."""
    script = tmp_path / "history_live_tabs_app.py"
    script.write_text(
        """
import streamlit as st
import pandas as pd

st.session_state["data_source"] = "backend"

from app.ui.views import history
history.render()
""",
        encoding="utf-8",
    )
    return str(script)


def test_live_mode_renders_pnl_and_dividend_tabs(monkeypatch, tmp_path):
    """라이브 모드에서 일·월 손익 및 배당 섹션 서브헤더가 모두 렌더링돼야 한다.

    수정 전: 조기 return으로 탭 미렌더 → 서브헤더 없음 → FAIL.
    수정 후: 탭 전부 렌더링 → 서브헤더 존재 → PASS.
    """
    from streamlit.testing.v1 import AppTest

    from app.ui import backend

    # --- stub live backend functions ---
    monkeypatch.setattr(backend, "list_order_logs", lambda: pd.DataFrame())
    monkeypatch.setattr(backend, "kis_order_history", lambda s, e: pd.DataFrame())
    # daily_pnl_series: 빈 DataFrame (live PnL 소스 없음 — 빈 상태 표시)
    monkeypatch.setattr(
        backend,
        "daily_pnl_series",
        lambda: pd.DataFrame(columns=["date", "pnl"]),
    )

    script = _make_script(tmp_path)
    at = AppTest.from_file(script).run(timeout=15)

    assert not at.exception, f"렌더 예외: {at.exception}"

    # PnL 서브헤더가 있어야 한다 (일·월 손익 섹션)
    subheader_values = [item.value for item in at.subheader]
    assert any("손익" in v for v in subheader_values), (
        f"일·월 손익 서브헤더가 없음 — 조기 return으로 탭 미렌더. "
        f"실제 서브헤더: {subheader_values}"
    )

    # 배당 서브헤더가 있어야 한다
    assert any("배당" in v for v in subheader_values), (
        f"배당 서브헤더가 없음 — 조기 return으로 탭 미렌더. "
        f"실제 서브헤더: {subheader_values}"
    )


def test_live_mode_renders_all_three_tab_sections(monkeypatch, tmp_path):
    """라이브 모드에서 체결내역·일월손익·배당 탭 3개가 모두 렌더링돼야 한다."""
    from streamlit.testing.v1 import AppTest

    from app.ui import backend

    monkeypatch.setattr(backend, "list_order_logs", lambda: pd.DataFrame())
    monkeypatch.setattr(backend, "kis_order_history", lambda s, e: pd.DataFrame())
    monkeypatch.setattr(
        backend,
        "daily_pnl_series",
        lambda: pd.DataFrame(columns=["date", "pnl"]),
    )

    script = _make_script(tmp_path)
    at = AppTest.from_file(script).run(timeout=15)

    assert not at.exception, f"렌더 예외: {at.exception}"

    # KIS 주문내역 서브헤더 (기존 live 섹션 — 항상 있어야 함)
    subheader_values = [item.value for item in at.subheader]
    assert any("KIS" in v for v in subheader_values), (
        f"KIS 주문내역 서브헤더 없음: {subheader_values}"
    )

    # PnL 탭 + 배당 탭도 있어야 한다
    assert any("손익" in v for v in subheader_values), (
        f"손익 서브헤더 없음: {subheader_values}"
    )
    assert any("배당" in v for v in subheader_values), (
        f"배당 서브헤더 없음: {subheader_values}"
    )
