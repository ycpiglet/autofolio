"""분석 — 과거 / 미래."""
from __future__ import annotations

import streamlit as st

from app.ui.components import ui
from app.ui.mock import data as mock_data


def _live() -> bool:
    return st.session_state.get("data_source") == "backend"


def _attribution():
    if _live():
        try:
            from app.ui import backend
            df = backend.attribution_df()
            if not df.empty:
                return df
        except Exception:  # noqa: BLE001
            pass
    return mock_data.attribution()


def _retro():
    if _live():
        try:
            from app.ui import backend
            return backend.retro_metrics()
        except Exception:  # noqa: BLE001
            pass
    return mock_data.retro_metrics()


def _alloc_gap():
    if _live():
        try:
            from app.ui import backend
            return backend.allocation_gap()
        except Exception:  # noqa: BLE001
            pass
    return mock_data.allocation_gap()


def render() -> None:
    st.header("📊 분석")

    past_tab, future_tab = st.tabs(["과거 (회고·기여·백테스트)", "미래 (시나리오·예측)"])

    with past_tab:
        if _live():
            st.caption("🟢 라이브 — 보유종목 기반 손익 기여 / 주문로그 회고")
        else:
            st.caption("🧪 데모 (mock 데이터)")

        st.subheader("백테스트 (예시 전략 vs KOSPI)")
        if _live():
            st.info("📐 백테스트 엔진은 퀀트팀(③) 구현 예정. 실거래 이력이 쌓이면 자동 활성화됩니다.")
        else:
            st.line_chart(mock_data.backtest_curve(), height=240)

        st.subheader("손익 기여 (Attribution)")
        attr = _attribution()
        if not attr.empty:
            st.bar_chart(attr.set_index("구분")["기여(만원)"], height=240)
        else:
            st.caption("체결 내역이 없습니다.")

        st.subheader("회고 요약")
        m = _retro()
        ui.kpi_cards(
            [
                ("승률", f'{m["승률"]}%', None),
                ("평균 R", f'{m["평균R"]}', None),
                ("최대낙폭", f'{m["MDD"]}%', None),
                ("규율점수", f'{m["규율"]}/100', None),
            ]
        )

    with future_tab:
        st.subheader("시나리오")
        st.dataframe(mock_data.scenarios(), hide_index=True, width="stretch")
        st.subheader("리밸런싱 플랜")
        st.dataframe(_alloc_gap(), hide_index=True, width="stretch")
        st.caption("📐 몬테카를로·예측 시그널은 P3 + 퀀트팀(③) 구현 예정.")
