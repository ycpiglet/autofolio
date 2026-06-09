"""내역 · 손익 — 데모(mock) / 라이브(SQLite 주문로그)."""
from __future__ import annotations

import streamlit as st

from app.ui.components import ui
from app.ui.mock import data


def render() -> None:
    st.header("📒 내역 · 손익")

    if st.session_state.get("data_source") == "backend":
        from app.ui import backend

        st.caption("🟢 라이브 — 실제 주문로그(SQLite)")
        logs = backend.list_order_logs()
        if logs.empty:
            ui.empty_state(
                "주문 로그가 없습니다",
                "매매 화면에서 조건을 등록하고 '엔진 1회 실행'을 눌러보세요.",
            )
        else:
            st.dataframe(logs, hide_index=True, width="stretch")
        return

    fills_tab, pnl_tab, div_tab = st.tabs(["체결내역", "일·월 손익", "배당"])
    with fills_tab:
        df = data.history_df()
        st.dataframe(df, hide_index=True, width="stretch")
        st.download_button(
            "내보내기 (CSV)",
            df.to_csv(index=False).encode("utf-8-sig"),
            file_name="autofolio_history.csv",
            mime="text/csv",
        )
    with pnl_tab:
        st.bar_chart(data.pnl_daily().set_index("날짜")["손익"], height=260)
        st.caption("수수료·세금 반영 후 실현손익 (mock).")
    with div_tab:
        st.dataframe(data.dividends(), hide_index=True, width="stretch")
