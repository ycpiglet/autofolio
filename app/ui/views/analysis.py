"""분석 — 과거 / 미래."""
from __future__ import annotations

import streamlit as st

from app.ui.components import ui
from app.ui.mock import data


def render() -> None:
    st.header("📊 분석")

    past_tab, future_tab = st.tabs(["과거 (회고·기여·백테스트)", "미래 (시나리오·예측)"])

    with past_tab:
        st.subheader("백테스트 (예시 전략 vs KOSPI)")
        st.line_chart(data.backtest_curve(), height=240)

        st.subheader("손익 기여 (Attribution)")
        st.bar_chart(data.attribution().set_index("구분")["기여(만원)"], height=240)

        st.subheader("회고 요약")
        m = data.retro_metrics()
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
        st.dataframe(data.scenarios(), hide_index=True, width="stretch")
        st.subheader("리밸런싱 플랜")
        st.dataframe(data.allocation_gap(), hide_index=True, width="stretch")
        st.caption("📐 몬테카를로·예측 시그널은 P3 + 퀀트팀(③) 구현 예정.")
