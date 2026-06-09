"""포트폴리오."""
from __future__ import annotations

import streamlit as st

from app.ui import theme
from app.ui.components import ui
from app.ui.mock import data


def render() -> None:
    ui.page_header("💼 포트폴리오")

    df = data.holdings_df()
    if df.empty:
        ui.empty_state("보유 종목이 없습니다", "매매 화면에서 첫 주문을 넣어보세요.")
        return

    kr = st.session_state.get("pnl_kr_colors", True)
    total_pnl = int(df["평가손익"].sum())
    c0, c1, c2 = st.columns(3)
    c0.metric("평가금액 합", theme.fmt_won(df["평가금액"].sum()))
    c1.markdown("**평가손익**\n\n" + theme.pnl_md(total_pnl, theme.fmt_won(total_pnl), kr))
    c2.metric("보유 종목", len(df))

    left, right = st.columns([2, 3])
    with left:
        st.subheader("자산배분")
        st.bar_chart(data.allocation_df().set_index("자산군")["비중"], height=260)
    with right:
        st.subheader("목표 대비 (리밸런싱 갭)")
        st.dataframe(data.allocation_gap(), hide_index=True, width="stretch")

    st.subheader("보유 종목")
    st.dataframe(
        df,
        hide_index=True,
        width="stretch",
        column_config={
            "평단": st.column_config.NumberColumn(format="%.0f"),
            "현재가": st.column_config.NumberColumn(format="%.0f"),
            "평가금액": st.column_config.NumberColumn(format="₩%d"),
            "평가손익": st.column_config.NumberColumn(format="₩%d"),
            "손익률": st.column_config.NumberColumn(format="%.1f%%"),
            "비중": st.column_config.NumberColumn(format="%.1f%%"),
        },
    )
