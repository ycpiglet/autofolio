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

        st.divider()
        st.subheader("KIS 날짜별 주문내역")
        import datetime
        col1, col2 = st.columns(2)
        start = col1.date_input("시작일", value=datetime.date.today() - datetime.timedelta(days=30), key="hist_start")
        end = col2.date_input("종료일", value=datetime.date.today(), key="hist_end")
        if st.button("🔍 조회", key="hist_search"):
            try:
                df_hist = backend.kis_order_history(start.strftime("%Y%m%d"), end.strftime("%Y%m%d"))
                if df_hist.empty:
                    st.info("조회 결과가 없습니다.")
                else:
                    st.dataframe(df_hist, hide_index=True, use_container_width=True)
            except Exception as exc:
                st.warning(f"조회 실패: {exc}")

        # --- 일·월 손익 섹션 (라이브) ---
        st.divider()
        st.subheader("일·월 손익")
        try:
            pnl_df = backend.daily_pnl_series()
        except Exception:
            pnl_df = None
        if pnl_df is None or pnl_df.empty:
            ui.empty_state(
                "손익 데이터 없음",
                "체결 내역이 쌓이면 일별 실현손익이 표시됩니다.",
            )
        else:
            st.bar_chart(pnl_df.set_index("date")["pnl"], height=260)
            st.caption("체결 내역 기반 일별 실현손익 (수수료·세금 미반영).")

        # --- 배당 섹션 (라이브) ---
        st.divider()
        st.subheader("배당")
        ui.empty_state(
            "배당 내역 없음",
            "KIS 배당 내역 조회 기능은 준비 중입니다.",
        )
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
