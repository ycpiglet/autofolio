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


def _kpis() -> dict:
    if st.session_state.get("data_source") == "backend":
        try:
            from app.ui import backend

            return backend.kpis()
        except Exception:  # noqa: BLE001
            return data.kpis()
    return data.kpis()


def _allocation_gap():
    if st.session_state.get("data_source") == "backend":
        try:
            from app.ui import backend

            return backend.allocation_gap()
        except Exception:  # noqa: BLE001
            return data.allocation_gap()
    return data.allocation_gap()


def _allocation_series(df):
    if st.session_state.get("data_source") == "backend":
        return df.groupby("자산군")["비중"].sum()
    return data.allocation_df().set_index("자산군")["비중"]


def render() -> None:
    ui.page_header("💼 포트폴리오", "보유 종목, 비중, 리스크를 먼저 확인합니다.")

    df = _holdings_df()
    if df.empty:
        ui.empty_state("보유 종목이 없습니다", "매매 화면에서 첫 주문을 넣어보세요.")
        return

    kr = st.session_state.get("pnl_kr_colors", True)
    total_pnl = int(df["평가손익"].sum())
    kpis = _kpis()

    st.subheader("보유 종목")
    display_cols = ["종목", "티커", "자산군", "지역", "수량", "평단", "현재가", "평가금액", "평가손익", "손익률", "비중"]
    st.dataframe(
        df[display_cols],
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

    c0, c1, c2, c3 = st.columns(4)
    c0.metric("평가금액 합", theme.fmt_won(df["평가금액"].sum()))
    c1.markdown("**평가손익**\n\n" + theme.pnl_md(total_pnl, theme.fmt_won(total_pnl), kr))
    c2.metric("보유 종목", len(df))
    c3.metric("현금비중", f'{kpis.get("현금비중", 0.0):.1f}%')

    left, right = st.columns([2, 3])
    with left:
        st.subheader("자산배분")
        st.bar_chart(_allocation_series(df), height=260)
    with right:
        st.subheader("목표 대비")
        st.dataframe(_allocation_gap(), hide_index=True, width="stretch")

    st.subheader("리스크 메모")
    largest = df.sort_values("비중", ascending=False).iloc[0]
    concentration = float(largest["비중"])
    cash_ratio = float(kpis.get("현금비중", 0.0))
    if concentration >= 30:
        st.warning(
            f"단일 보유 집중: {largest['종목']} {concentration:.1f}% — 리밸런싱 필요 여부를 점검하세요."
        )
    else:
        st.info(f"최대 보유: {largest['종목']} {concentration:.1f}%")
    st.caption(f"현금비중 {cash_ratio:.1f}% · 총 {len(df)}개 포지션 · 손익 색상은 한국식 기준입니다.")
