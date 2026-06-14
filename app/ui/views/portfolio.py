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

            return backend.holdings_df(include_dividends=False)
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
    total_market_value = float(df["평가금액"].sum())
    total_cost = float((df["평단"] * df["수량"]).sum())
    total_pnl = int(df["평가손익"].sum())
    total_return_pct = total_pnl / total_cost * 100 if total_cost else 0.0
    annual_dividend = int(df["예상연배당"].sum()) if "예상연배당" in df.columns else 0
    dividend_yield = annual_dividend / total_market_value * 100 if total_market_value else 0.0
    c0, c1, c2, c3, c4 = st.columns(5)
    c0.metric("평가금액 합", theme.fmt_won(total_market_value))
    c1.metric("총 매입금액", theme.fmt_won(total_cost))
    c2.markdown("**평가손익**\n\n" + theme.pnl_md(total_pnl, theme.fmt_won(total_pnl), kr))
    c3.metric("총수익률", f"{total_return_pct:+.2f}%")
    c4.metric("보유 종목", len(df))

    st.subheader("보유 현황")
    display_columns = [
        "종목", "티커", "자산군", "수량", "평단", "현재가",
        "평가금액", "평가손익", "손익률", "비중",
    ]
    display = df[[col for col in display_columns if col in df.columns]].copy()
    if "평가금액" in display.columns:
        display = display.sort_values("평가금액", ascending=False)
    st.dataframe(
        display,
        hide_index=True,
        width="stretch",
        height=min(560, 72 + max(len(display), 1) * 36),
        column_config={
            "수량": st.column_config.NumberColumn(format="%d"),
            "평단": st.column_config.NumberColumn(format="%.0f"),
            "현재가": st.column_config.NumberColumn(format="%.0f"),
            "평가금액": st.column_config.NumberColumn(format="₩%d"),
            "평가손익": st.column_config.NumberColumn(format="₩%d"),
            "손익률": st.column_config.NumberColumn(format="%.1f%%"),
            "비중": st.column_config.NumberColumn(format="%.1f%%"),
        },
    )

    d0, d1 = st.columns(2)
    d0.metric("예상 연배당", theme.fmt_won(annual_dividend))
    d1.metric("배당수익률", f"{dividend_yield:.2f}%")

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
            except Exception as exc:  # noqa: BLE001
                st.warning(f"라이브 갭 조회 실패 — 데모 데이터로 대체합니다: {exc}")
                st.dataframe(data.allocation_gap(), hide_index=True, width="stretch")
        else:
            st.dataframe(data.allocation_gap(), hide_index=True, width="stretch")
