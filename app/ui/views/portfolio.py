"""포트폴리오."""
from __future__ import annotations

import streamlit as st

from app.ui import theme
from app.ui.components import ui
from app.ui.mock import data


def _holdings_df():
    """보유 종목 표 — data_source=='backend' 면 실 KIS 잔고, 아니면 데모(mock).

    라이브 조회 실패 시 데모로 안전 폴백한다(화면이 죽지 않도록).
    """
    if st.session_state.get("data_source") == "backend":
        try:
            from app.ui import backend

            return backend.holdings_df()
        except Exception as exc:  # noqa: BLE001 — UI 폴백
            st.warning(f"라이브 잔고 조회 실패 — 데모 데이터로 대체합니다: {exc}")
    return data.holdings_df()


def render() -> None:
    ui.page_header("💼 포트폴리오")

    df = _holdings_df()
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
        if st.session_state.get("data_source") == "backend":
            # 라이브: holdings_df에서 직접 자산군 비중 집계
            alloc = df.groupby("자산군")["비중"].sum()
            st.bar_chart(alloc, height=260)
        else:
            st.bar_chart(data.allocation_df().set_index("자산군")["비중"], height=260)
    with right:
        st.subheader("목표 대비 (리밸런싱 갭)")
        if st.session_state.get("data_source") == "backend":
            try:
                from app.ui import backend
                st.dataframe(backend.allocation_gap(), hide_index=True, width="stretch")
            except Exception:  # noqa: BLE001
                st.dataframe(data.allocation_gap(), hide_index=True, width="stretch")
        else:
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
