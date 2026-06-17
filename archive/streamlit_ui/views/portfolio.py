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
            from app.services import backend

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
                from app.services import backend
                st.dataframe(backend.allocation_gap(), hide_index=True, width="stretch")
            except Exception as exc:  # noqa: BLE001
                st.warning(f"라이브 갭 조회 실패 — 데모 데이터로 대체합니다: {exc}")
                st.dataframe(data.allocation_gap(), hide_index=True, width="stretch")
        else:
            st.dataframe(data.allocation_gap(), hide_index=True, width="stretch")

    # ── 성과 리포트 (읽기전용 / TASK-040) ─────────────────────────
    with st.expander("📊 성과 리포트 (읽기전용)", expanded=False):
        _render_perf_report(df)


def _render_perf_report(holdings_df: "pd.DataFrame") -> None:
    """포트폴리오 성과/귀속/tax-lot 읽기전용 리포트 섹션.

    순수 UI 렌더러 — 주문/리밸런싱 실행 없음.
    데이터 없는 섹션은 솔직하게 '데이터 없음' 표시.
    """
    from app.services.perf_report import build_portfolio_report

    # --- 데이터 수집 (backend 또는 mock) ---
    if st.session_state.get("data_source") == "backend":
        try:
            from app.services import backend
            pnl_series = backend.daily_pnl_series()
            kpis_data = backend.kpis()
            repo, *_ = backend._ctx()
            realized_pnl = repo.total_realized_pnl()
        except Exception as exc:  # noqa: BLE001
            st.warning(f"성과 데이터 라이브 조회 실패 — 데모 데이터로 대체합니다: {exc}")
            from app.ui.mock import data as mock_data
            pnl_series = mock_data.pnl_daily().rename(columns={"날짜": "date", "손익": "pnl"})
            kpis_data = mock_data.kpis()
            realized_pnl = 0.0
    else:
        from app.ui.mock import data as mock_data
        pnl_series = mock_data.pnl_daily().rename(columns={"날짜": "date", "손익": "pnl"})
        kpis_data = mock_data.kpis()
        realized_pnl = 0.0

    report = build_portfolio_report(
        holdings=holdings_df,
        pnl_series=pnl_series,
        kpis=kpis_data,
        realized_pnl=realized_pnl,
    )

    # ── 1. 실현/미실현 P&L 요약 ───────────────────────────────────
    st.subheader("실현/미실현 손익")
    c1, c2, c3 = st.columns(3)
    c1.metric("실현 손익", f"₩{report.realized_pnl:,.0f}")
    c2.metric("미실현 평가손익", f"₩{report.unrealized_pnl:,.0f}")
    c3.metric("합계", f"₩{report.realized_pnl + report.unrealized_pnl:,.0f}")

    # ── 2. 현금흐름·수수료·턴오버 (데이터 없음 명시) ──────────────
    st.subheader("현금흐름 / 수수료 / 턴오버")
    st.info(report.cashflow_note)
    st.info(report.fee_slippage_note)
    st.info(report.turnover_note)

    # ── 3. Attribution (자산군별 기여) ────────────────────────────
    st.subheader("귀속 분석 (Attribution)")
    st.caption(report.attribution_note)
    if not report.attribution_df.empty:
        st.dataframe(report.attribution_df, hide_index=True, width="stretch")
        st.bar_chart(report.attribution_df.set_index("구분")["기여(만원)"], height=200)
    else:
        st.write("데이터 없음 — 보유 종목이 없습니다.")

    # ── 4. Tax-lot placeholder ────────────────────────────────────
    st.subheader("Tax-Lot 보기 (참고용 Placeholder)")
    st.warning(report.tax_lot_disclaimer)
    if not report.tax_lot_df.empty:
        st.dataframe(
            report.tax_lot_df,
            hide_index=True,
            width="stretch",
            column_config={
                "수량": st.column_config.NumberColumn(format="%d"),
                "평단": st.column_config.NumberColumn(format="%.0f"),
                "현재가": st.column_config.NumberColumn(format="%.0f"),
                "평가손익": st.column_config.NumberColumn(format="₩%d"),
                "손익률": st.column_config.NumberColumn(format="%.1f%%"),
            },
        )
    else:
        st.write("보유 종목 없음.")
