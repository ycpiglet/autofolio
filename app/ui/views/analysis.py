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
            try:
                import plotly.graph_objects as go
                labels = ["포트폴리오"] + attr["구분"].tolist()
                sources = [0] * len(attr)
                targets = list(range(1, len(attr) + 1))
                values = attr["기여(만원)"].abs().tolist()
                colors = ["#2ecc71" if v >= 0 else "#e74c3c" for v in attr["기여(만원)"].tolist()]
                fig = go.Figure(go.Sankey(
                    node=dict(label=labels, color=["#3498db"] + colors),
                    link=dict(source=sources, target=targets, value=values, color=colors),
                ))
                fig.update_layout(height=280, margin=dict(t=20, b=10, l=10, r=10))
                st.plotly_chart(fig, use_container_width=True)
            except ImportError:
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
        # ── 시나리오 분석 ──────────────────────────────────────────────
        st.subheader("시나리오 분석")
        if _live():
            st.caption("🟢 라이브 — 보유 포트폴리오 기반 시나리오 영향 계산")
            try:
                from app.ui import backend
                scen_df = backend.scenario_analysis()
                if scen_df.empty:
                    st.info("보유 종목이 없어 시나리오를 계산할 수 없습니다.")
                else:
                    for scenario_name in scen_df["시나리오"].unique():
                        sub = scen_df[scen_df["시나리오"] == scenario_name].copy()
                        totals_row = sub[sub["자산군"] == "합계"].iloc[0]
                        delta_pct = totals_row["변동률(%)"]
                        delta_won = totals_row["변동액(원)"]
                        sign = "+" if delta_pct >= 0 else ""
                        with st.expander(
                            f"**{scenario_name}** — 포트폴리오 예상 변동: {sign}{delta_pct:.2f}% "
                            f"({sign}{delta_won:,.0f}원)",
                            expanded=(scenario_name == "Base"),
                        ):
                            detail = sub[sub["자산군"] != "합계"].reset_index(drop=True)
                            # 숫자 포맷팅
                            display = detail[["자산군", "현재금액(원)", "변동률(%)", "변동액(원)", "시나리오후금액(원)"]].copy()
                            display["현재금액(원)"] = display["현재금액(원)"].apply(lambda x: f"{x:,.0f}")
                            display["변동액(원)"] = display["변동액(원)"].apply(
                                lambda x: f"+{x:,.0f}" if x >= 0 else f"{x:,.0f}"
                            )
                            display["시나리오후금액(원)"] = display["시나리오후금액(원)"].apply(lambda x: f"{x:,.0f}")
                            display["변동률(%)"] = display["변동률(%)"].apply(
                                lambda x: f"+{x:.1f}%" if x >= 0 else f"{x:.1f}%"
                            )
                            st.dataframe(display, hide_index=True, use_container_width=True)
                            c1, c2, c3 = st.columns(3)
                            c1.metric("총 변동액", f"{sign}{delta_won:,.0f}원")
                            c2.metric("총 변동률", f"{sign}{delta_pct:.2f}%")
                            c3.metric("시나리오 후 총자산", f"{totals_row['시나리오후금액(원)']:,.0f}원")
            except Exception as exc:  # noqa: BLE001
                st.warning(f"라이브 시나리오 계산 실패: {exc}")
                st.caption("⬇ 데모 시나리오")
                st.dataframe(mock_data.scenarios(), hide_index=True, use_container_width=True)
        else:
            st.caption("🧪 데모 (mock 데이터)")
            st.dataframe(mock_data.scenarios(), hide_index=True, use_container_width=True)

        st.divider()

        # ── What-if 계산기 ────────────────────────────────────────────
        st.subheader("What-if 계산기")
        if _live():
            st.caption("🟢 종목 비중을 변경했을 때의 포트폴리오 영향을 계산합니다.")
            with st.expander("⚙️ What-if 비중 시뮬레이터 열기", expanded=False):
                try:
                    from app.ui import backend
                    wl_df = backend.watchlist()
                    if wl_df.empty:
                        st.info("화이트리스트가 비어있습니다. 먼저 화이트리스트를 구성하세요.")
                    else:
                        symbol_list = wl_df["symbol"].tolist()
                        wi_col1, wi_col2 = st.columns(2)
                        wi_symbol = wi_col1.selectbox("종목 (ticker)", symbol_list, key="wi_symbol")
                        wi_weight = wi_col2.number_input(
                            "목표 비중 (%)", min_value=0.0, max_value=100.0,
                            value=10.0, step=0.5, format="%.1f", key="wi_weight"
                        )
                        if st.button("계산", key="wi_calc", type="primary"):
                            result = backend.whatif_weight_change(wi_symbol, wi_weight)
                            st.session_state["wi_result"] = result

                        r = st.session_state.get("wi_result")
                        if r and r.get("symbol") == wi_symbol:
                            st.markdown("---")
                            c1, c2, c3 = st.columns(3)
                            c1.metric("현재 비중", f"{r['current_weight']:.2f}%")
                            c2.metric("목표 비중", f"{r['new_weight']:.1f}%")
                            delta_sign = "+" if r["delta_shares"] >= 0 else ""
                            c3.metric(
                                "추가매수/매도 주수",
                                f"{delta_sign}{r['delta_shares']:,}주",
                                delta=f"{delta_sign}{r['delta_cost']:,.0f}원",
                            )
                            c4, c5 = st.columns(2)
                            c4.metric("예상 총자산 (거래 후)", f"{r['new_total_assets_estimated']:,.0f}원")
                            c5.metric(
                                "거래 비용 추정",
                                f"{abs(r['delta_cost']):,.0f}원",
                                delta=("매수" if r["delta_shares"] >= 0 else "매도"),
                            )
                            if r["risk_note"] and r["risk_note"] != "이상 없음.":
                                st.warning(f"⚠️ 리스크 노트: {r['risk_note']}")
                            else:
                                st.success(f"리스크 노트: {r['risk_note']}")
                except Exception as exc:  # noqa: BLE001
                    st.warning(f"What-if 계산기 로딩 실패: {exc}")
        else:
            with st.expander("⚙️ What-if 비중 시뮬레이터 (데모)", expanded=False):
                st.caption("🧪 데모 모드 — 실제 계산은 라이브 모드에서 가능합니다.")
                mock_symbols = [f"{r['종목']} ({r['티커']})" for _, r in mock_data.holdings_df().iterrows()]
                wi_demo_sym = st.selectbox("종목", mock_symbols, key="wi_demo_sym")
                wi_demo_w = st.number_input(
                    "목표 비중 (%)", min_value=0.0, max_value=100.0,
                    value=10.0, step=0.5, format="%.1f", key="wi_demo_w"
                )
                st.info("라이브 모드로 전환하면 실제 보유종목 기반 시뮬레이션이 가능합니다.")

        st.divider()


        st.divider()

        # ── T-32: VaR/MDD 몬테카를로 시뮬레이션 ─────────────────────────
        st.subheader("리스크 시뮬레이션 (VaR)")
        if _live():
            with st.expander("🎲 몬테카를로 VaR/MDD 추정", expanded=False):
                v_horizon = st.slider("시뮬레이션 기간 (거래일)", 5, 60, 10, key="var_h")
                v_n = st.select_slider("시뮬레이션 횟수", [1000, 3000, 5000, 10000], value=5000, key="var_n")
                if st.button("▶ 시뮬레이션 실행", key="var_run"):
                    try:
                        from app.ui import backend
                        from app.quant.risk_sim import simulate_portfolio_var
                        df = backend.holdings_df()
                        with st.spinner(f"{v_n:,}회 시뮬레이션 중…"):
                            result = simulate_portfolio_var(
                                df, horizon_days=v_horizon, n_simulations=v_n
                            )
                        st.session_state["var_result"] = result
                    except Exception as exc:  # noqa: BLE001
                        st.warning(f"시뮬레이션 실패: {exc}")

                var_res = st.session_state.get("var_result")
                if var_res and var_res.total_value > 0:
                    c1, c2, c3 = st.columns(3)
                    c1.metric("95% VaR", f"{var_res.var_95:,.0f}원",
                              help=f"{v_horizon}일 기간 중 5% 확률로 초과하는 손실")
                    c2.metric("99% VaR", f"{var_res.var_99:,.0f}원")
                    c3.metric("평균 MDD", f"-{var_res.max_drawdown_pct:.1f}%")
                    st.caption(f"포트폴리오: {var_res.total_value:,.0f}원 · {var_res.note}")
                    p = var_res.percentiles
                    st.markdown(
                        f"| 최하 1% | 5% | 10% | 25% | 중간 |"
                        f"
|---|---|---|---|---|"
                        f"
| {p.get(1,0):,.0f} | {p.get(5,0):,.0f} | {p.get(10,0):,.0f} | {p.get(25,0):,.0f} | {p.get(50,0):,.0f} |"
                    )
                    st.caption("⚠️ 과거 수익률 분포 기반 통계 추정. 실제 미래 손실을 보장하지 않습니다.")
        else:
            st.caption("🧪 데모 — VaR 시뮬레이션은 라이브 모드에서 사용 가능합니다.")
        # ── 리밸런싱 플랜 ─────────────────────────────────────────────
        st.subheader("리밸런싱 플랜")
        st.dataframe(_alloc_gap(), hide_index=True, use_container_width=True)
        st.caption("📐 몬테카를로·예측 시그널은 P3 + 퀀트팀(③) 구현 예정.")
