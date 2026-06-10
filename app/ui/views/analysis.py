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


def _backtest_section() -> None:
    """백테스트 UI — SMA 크로스오버 실행 섹션."""
    import datetime as dt
    from app.ui import backend

    wl = backend.list_whitelist()
    if wl.empty:
        st.caption("화이트리스트가 비어있습니다.")
        return

    symbols = wl["symbol"].tolist()
    c1, c2, c3, c4 = st.columns(4)
    sym = c1.selectbox("종목", symbols, key="bt_sym")
    fast = c2.number_input("빠른 SMA", min_value=2, max_value=50, value=5, key="bt_fast")
    slow = c3.number_input("느린 SMA", min_value=5, max_value=200, value=20, key="bt_slow")
    days = c4.number_input("기간(일)", min_value=30, max_value=365, value=90, key="bt_days")

    if st.button("▶ 백테스트 실행", key="bt_run"):
        end = dt.date.today()
        start = end - dt.timedelta(days=int(days))
        with st.spinner("데이터 로딩 및 백테스트 실행 중…"):
            try:
                from app.quant.data_loader import fetch_and_cache
                fetched = fetch_and_cache(sym, start, end)
                from app.quant.backtest import run_sma_crossover
                result = run_sma_crossover(sym, start, end, fast=int(fast), slow=int(slow))
                st.session_state["bt_result"] = result
                if fetched:
                    st.caption(f"📥 {fetched}일치 시세 캐시 갱신")
            except Exception as exc:  # noqa: BLE001
                st.warning(f"백테스트 실패: {exc}")

    r = st.session_state.get("bt_result")
    if r and r.symbol == sym:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("총 수익률", f"{r.total_return_pct:+.1f}%")
        c2.metric("거래 횟수", f"{r.trade_count}회")
        c3.metric("승률", f"{r.win_rate_pct:.1f}%")
        c4.metric("최대낙폭", f"-{r.max_drawdown_pct:.1f}%")
        if r.equity_curve:
            import pandas as pd
            df = pd.DataFrame(r.equity_curve).set_index("date")
            st.line_chart(df["equity"], height=200)
        st.caption("⚠️ 이 백테스트는 참고용입니다. 과거 성과가 미래를 보장하지 않습니다.")


def render() -> None:
    st.header("📊 분석")

    past_tab, journal_tab, future_tab = st.tabs(["과거 (회고·기여·백테스트)", "📓 거래 저널", "미래 (시나리오·예측)"])

    with past_tab:
        if _live():
            st.caption("🟢 라이브 — 보유종목 기반 손익 기여 / 주문로그 회고")
        else:
            st.caption("🧪 데모 (mock 데이터)")

        st.subheader("백테스트")
        if _live():
            _backtest_section()
        else:
            st.line_chart(mock_data.backtest_curve(), height=240)

        st.subheader("손익 기여 (Attribution)")
        attr = _attribution()
        if not attr.empty:
            st.bar_chart(attr.set_index("구분")["기여(만원)"], height=240)
        else:
            st.caption("체결 내역이 없습니다.")

        # PnL 캘린더 히트맵
        st.subheader("일별 손익 캘린더")
        if _live():
            try:
                from app.ui import backend
                pnl_df = backend.daily_pnl_series()
                if not pnl_df.empty:
                    pnl_df["pnl_만원"] = (pnl_df["pnl"] / 10_000).round(1)
                    st.bar_chart(pnl_df.set_index("date")["pnl_만원"], height=180)
                else:
                    st.caption("체결 내역이 없습니다.")
            except Exception:  # noqa: BLE001
                st.bar_chart(mock_data.pnl_daily().set_index("날짜")["손익"], height=180)
        else:
            st.bar_chart(mock_data.pnl_daily().set_index("날짜")["손익"], height=180)

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

    with journal_tab:
        st.subheader("📓 거래 저널")
        if _live():
            try:
                from app.ui import backend
                df = backend.list_journal_entries()
                if df.empty:
                    st.info("저널 항목이 없습니다. 아래 폼으로 첫 항목을 추가하세요.")
                else:
                    st.dataframe(df, hide_index=True, width="stretch")
            except Exception as exc:  # noqa: BLE001
                st.warning(f"저널 로딩 실패: {exc}")
        else:
            st.caption("🧪 데모 — 저널은 라이브 모드(backend)에서 사용 가능합니다.")

        with st.expander("➕ 저널 항목 추가"):
            c1, c2 = st.columns(2)
            j_sym = c1.text_input("종목코드", placeholder="005930", key="j_sym")
            j_side = c2.radio("구분", ["BUY", "SELL"], horizontal=True, key="j_side")
            j_entry = st.text_area("진입 이유", key="j_entry", height=80)
            j_exit = st.text_area("청산 이유 (선택)", key="j_exit", height=60)
            c3, c4 = st.columns(2)
            j_grade = c3.selectbox("등급", ["", "A", "B", "C", "D", "F"], key="j_grade")
            j_lesson = c4.text_input("교훈 (한 줄)", key="j_lesson")
            j_plan = st.checkbox("계획대로 실행했나요?", value=True, key="j_plan")
            j_emotion = st.checkbox("감정적 요소가 있었나요?", value=False, key="j_emo")
            if st.button("💾 저널 저장", type="primary", key="j_save") and j_sym:
                try:
                    from app.ui import backend
                    jid = backend.add_journal_entry(
                        symbol=j_sym.strip().upper(), side=j_side,
                        entry_reason=j_entry, exit_reason=j_exit,
                        grade=j_grade or None, lesson=j_lesson,
                        plan_followed=j_plan, emotion_flag=j_emotion,
                    )
                    st.success(f"저장 완료 (id={jid})")
                except Exception as exc:  # noqa: BLE001
                    st.error(f"저장 실패: {exc}")

    with future_tab:
        st.subheader("시나리오")
        st.dataframe(mock_data.scenarios(), hide_index=True, width="stretch")
        st.subheader("리밸런싱 플랜")
        st.dataframe(_alloc_gap(), hide_index=True, width="stretch")
        st.caption("📐 몬테카를로·예측 시그널은 P3 + 퀀트팀(③) 구현 예정.")
