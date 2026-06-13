"""매매 / 주문 — 데모(mock) / 라이브(Mock 브로커 + SQLite)."""
from __future__ import annotations

import streamlit as st

from app.ui.components import ui
from app.ui.mock import data


def render() -> None:
    st.header("🧾 매매 / 주문")
    if st.session_state.get("data_source") == "backend":
        from app.ui import backend as _be
        env = _be.env()
        if env == "paper":
            st.caption("🟡 모의투자(paper) — KIS 모의투자 계좌로 실제 주문이 전송됩니다.")
        elif env == "prod":
            st.caption("🔴 실전투자(prod) — 실제 자금으로 주문이 집행됩니다. 주의하세요.")
        else:
            st.caption("🟢 라이브 (Mock 브로커 + SQLite) — 실제 주문은 발생하지 않습니다.")
        _live()
    else:
        st.caption("⚠️ 데모: 실제 주문은 발생하지 않습니다 (mock).")
        _demo()


def _live() -> None:
    from app.ui import backend

    cond_tab, run_tab, log_tab, kis_tab, check_tab = st.tabs(["목표가 조건", "엔진 실행 / 결과", "주문로그(SQLite)", "KIS 주문내역", "📋 장전 체크리스트"])

    with cond_tab:
        opts = backend.symbol_options()
        if not opts:
            ui.empty_state("화이트리스트가 비어있습니다")
        else:
            c1, c2, c3 = st.columns(3)
            label = c1.selectbox("종목", list(opts.keys()), key="lv_sym")
            sym = opts[label]
            cur = backend.price(sym)
            c1.metric("현재가", f"{cur:,.0f}")
            side = c2.radio("방향", ["BUY", "SELL"], horizontal=True, key="lv_side")
            default_tp = float(round(cur * 1.01)) if side == "BUY" else float(round(cur * 0.99))
            tp = c2.number_input(
                "목표가 (BUY: 현재가 이상이면 즉시 실행)",
                min_value=0.0, value=default_tp, step=500.0, key="lv_tp",
            )
            qty = c3.number_input("수량", min_value=1, value=1, key="lv_qty")
            auto = c3.checkbox("자동주문 ON", value=False, key="lv_auto")
            compliance_check = st.toggle("Compliance 검토 후 저장", value=True, key="lv_compliance")
            disclosure_gate = backend.disclosure_gate_state(sym)
            if st.button("공시 게이트 확인", key="lv_disclosure_check"):
                disclosure_gate = backend.refresh_disclosure_gate(sym, days=1)
            if disclosure_gate.get("blocked"):
                st.error(f"공시 게이트 차단: {disclosure_gate.get('reason', '')}")

            # --- Compliance ack state ---
            # Stale ack: clear when symbol or side changes to avoid carry-over.
            _ack_context = f"{sym}:{side}"
            if st.session_state.get("_trade_ack_context") != _ack_context:
                st.session_state.pop("trade_ack_checked", None)
                st.session_state.pop("_trade_ack_pending_message", None)
                st.session_state["_trade_ack_context"] = _ack_context

            # Render pending-ack UI OUTSIDE the button block so the widget
            # survives reruns (Streamlit deletes widget-keyed state when the
            # widget is not rendered; a plain session-state key persists).
            if st.session_state.get("_trade_ack_pending_message"):
                _msg = st.session_state["_trade_ack_pending_message"]
                st.warning(f"⚠️ Compliance 주의사항\n{_msg[:300]}")
                with st.expander("전체 의견"):
                    st.markdown(_msg)
                ack_val = st.checkbox(
                    "위 주의사항을 확인했으며 계속 진행합니다",
                    key="lv_comply_ack_widget",
                )
                # Mirror into persistent key that survives reruns.
                st.session_state["trade_ack_checked"] = ack_val
                st.info("체크박스를 선택한 뒤 '조건 저장'을 다시 클릭하세요.")

            if st.button(
                "조건 저장",
                type="primary",
                key="lv_save",
                disabled=bool(disclosure_gate.get("blocked")),
            ):
                from app.services.trading import save_condition_with_gates

                if compliance_check:
                    with st.spinner("Compliance Officer 검토 중…"):
                        result = save_condition_with_gates(
                            sym, side, tp, qty, auto,
                            compliance_check=True,
                            caution_acknowledged=st.session_state.get("trade_ack_checked", False),
                        )
                else:
                    result = save_condition_with_gates(
                        sym, side, tp, qty, auto,
                        compliance_check=False,
                    )

                if result.status == "blocked_disclosure":
                    st.error(f"❌ {result.message}")
                    st.stop()
                elif result.status == "rejected":
                    st.error(f"❌ Compliance Officer 거부\n{result.message[:400]}")
                    st.stop()
                elif result.status == "needs_acknowledgement":
                    # Store the CAUTION message in a persistent session key so
                    # the warning + checkbox render on the NEXT run (outside the
                    # button block), where Streamlit will not clean up the widget.
                    st.session_state["_trade_ack_pending_message"] = result.message
                    st.session_state.pop("trade_ack_checked", None)
                    st.rerun()
                elif result.status == "saved":
                    # Clear ack state on successful save.
                    st.session_state.pop("trade_ack_checked", None)
                    st.session_state.pop("_trade_ack_pending_message", None)
                    if result.compliance == "passed":
                        st.success("✅ Compliance 검토 통과")
                    elif result.compliance == "caution_acked":
                        st.warning(f"⚠️ Compliance 주의사항\n{result.message[:300]}")
                        with st.expander("전체 의견"):
                            st.markdown(result.message)
                    st.success(f"조건 저장 완료 (id={result.condition_id})")
                else:
                    st.error(f"알 수 없는 상태: {result.status}")

            _order_book_panel(backend, sym, side, int(qty))

        st.divider()
        st.caption("등록된 조건")
        st.dataframe(backend.list_conditions(), hide_index=True, width="stretch")

    with run_tab:
        from app.ui import backend as _be_run
        _env_label = {"paper": "모의투자", "prod": "실전"}.get(_be_run.env(), "mock")
        if st.button(f"⚙️ 엔진 1회 실행 ({_env_label})", key="lv_run"):
            msgs = backend.run_engine_once()
            if msgs:
                for m in msgs:
                    st.write("•", m)
            else:
                st.info("활성 조건이 없습니다. 먼저 조건을 등록하세요.")
        st.caption("실행 결과는 '주문로그' 탭에서 확인.")

    with log_tab:
        st.caption("🟢 라이브 — 실제 주문로그")
        try:
            df = backend.list_order_logs(limit=100)
            if df.empty:
                st.info("아직 주문로그가 없습니다. 엔진을 실행해 보세요.")
            else:
                st.dataframe(df, hide_index=True, width="stretch")
        except Exception as exc:  # noqa: BLE001 — UI 폴백
            st.warning(f"주문로그 조회 실패: {exc}")

    with kis_tab:
        st.caption("KIS 서버에서 오늘 주문내역을 직접 조회합니다 (스크립트로 넣은 주문 포함).")
        if st.button("🔄 새로고침", key="kis_refresh"):
            st.rerun()
        try:
            df = backend.kis_today_orders()
            if df.empty:
                st.info("오늘 주문내역이 없거나 mock 환경입니다.")
            else:
                st.dataframe(df, hide_index=True, width="stretch")
        except Exception as exc:  # noqa: BLE001
            st.warning(f"KIS 주문내역 조회 실패: {exc}")

    with check_tab:
        _pre_trade_checklist(backend)


def _price_text(value) -> str:
    if value in (None, ""):
        return "-"
    try:
        return f"{float(value):,.0f}"
    except (TypeError, ValueError):
        return "-"


def _order_book_panel(backend, symbol: str, side: str, quantity: int) -> None:
    st.subheader("호가창")
    try:
        snapshot = backend.order_book_snapshot(symbol)
        df = backend.order_book_levels_df(snapshot)
    except Exception as exc:  # noqa: BLE001
        st.warning(f"호가 조회 실패: {exc}")
        return
    if df.empty:
        st.info("호가 데이터가 없습니다.")
        return

    best = df.iloc[0]
    spread = None
    if best["ask_price"] and best["bid_price"]:
        spread = float(best["ask_price"]) - float(best["bid_price"])
    c1, c2, c3 = st.columns(3)
    c1.metric("현재가", _price_text(snapshot.get("current_price")))
    c2.metric("예상체결가", _price_text(snapshot.get("expected_price")))
    c3.metric("스프레드", _price_text(spread))

    from app.brokers.kis.kis_client import estimate_order_book_slippage

    estimate = estimate_order_book_slippage(
        snapshot.get("levels") or [],
        side,
        int(quantity),
        snapshot.get("current_price"),
    )
    e1, e2, e3, e4 = st.columns(4)
    e1.metric("예상평균가", _price_text(estimate.get("average_price")))
    e2.metric("충족수량", f"{estimate.get('filled_quantity', 0):,}")
    e3.metric("미충족수량", f"{estimate.get('unfilled_quantity', 0):,}")
    slippage = estimate.get("slippage_per_share")
    slippage_rate = estimate.get("slippage_rate")
    e4.metric(
        "슬리피지",
        "-" if slippage is None else f"{slippage:,.1f}",
        None if slippage_rate is None else f"{slippage_rate:.2f}%",
    )

    display = df.rename(
        columns={
            "level": "단계",
            "ask_price": "매도호가",
            "ask_quantity": "매도잔량",
            "bid_price": "매수호가",
            "bid_quantity": "매수잔량",
        }
    )
    st.dataframe(display, hide_index=True, width="stretch")


def _pre_trade_checklist(backend) -> None:
    """장전 체크리스트 — 매매 전 통과 관문."""
    st.subheader("📋 장전 체크리스트")
    st.caption("매매 실행 전 아래 항목을 확인하세요.")

    try:
        cb = backend.circuit_breaker_status()
        auto = backend.get_flag("auto_trading_enabled")
        kill = backend.get_flag("kill_switch_active")
        wl = backend.list_whitelist()
        wl_count = 0 if wl is None or wl.empty else len(wl)
        conds = backend.list_conditions()
        active_conds = 0
        if not conds.empty and "status" in conds.columns:
            active_conds = int((conds["status"] == "ACTIVE").sum())
    except Exception as exc:  # noqa: BLE001
        st.warning(f"상태 조회 실패: {exc}")
        return

    def row(label: str, ok: bool, detail: str = "") -> None:
        icon = "✅" if ok else "❌"
        st.markdown(f"{icon} **{label}**" + (f" — {detail}" if detail else ""))

    row("킬스위치 해제", not kill, "활성 중" if kill else "")
    row("자동매매 활성", auto, "OFF" if not auto else "ON")
    row("서킷브레이커 미발동", not cb.get("triggered", False),
        f"발동: {cb.get('consecutive_failures', 0)}연속실패" if cb.get("triggered") else "")
    row("화이트리스트 종목", wl_count > 0, f"{wl_count}종목")
    row("활성 조건", active_conds > 0, f"{active_conds}개 조건")

    st.divider()
    all_ok = (not kill) and auto and (not cb.get("triggered")) and wl_count > 0
    if all_ok:
        st.success("✅ 모든 게이트 통과 — 매매 준비 완료")
    else:
        st.error("❌ 일부 게이트 미통과 — 위 항목을 확인하세요")


def _demo() -> None:
    order_tab, cond_tab, open_tab = st.tabs(["주문", "목표가 조건(자동매매)", "미체결"])

    with order_tab:
        c1, c2 = st.columns(2)
        with c1:
            st.selectbox("종목", data.symbol_options())
            st.radio("구분", ["매수", "매도"], horizontal=True)
            st.radio("유형", ["지정가", "시장가"], horizontal=True)
        with c2:
            st.number_input("수량", min_value=1, value=10, step=1)
            st.number_input("가격", min_value=0, value=74_300, step=100)
            st.button("주문 (모드·게이트 통과 필요)", type="primary", width="stretch")
            st.caption("게이트: 화이트리스트 ✅ · 거래시간 ✅ · 주문한도 ✅ · 쿨다운 ✅")

    with cond_tab:
        c1, c2, c3 = st.columns(3)
        c1.selectbox("종목", data.symbol_options(), key="cond_sym")
        c1.radio("방향", ["매수", "매도"], horizontal=True, key="cond_side")
        c2.number_input("목표가", min_value=0, value=72_000, step=100, key="cond_price")
        c2.number_input("수량", min_value=1, value=10, key="cond_qty")
        c3.selectbox("자율성", ["L1 자문", "L2 반자동", "L3 감독형 자동"], key="cond_mode")
        c3.button("조건 등록 (데모)", width="stretch")
        st.divider()
        st.caption("🧪 데모 — 등록된 목표가 조건 (mock)")
        st.dataframe(
            data.open_orders().assign(자동="ON")[["종목", "방향", "지정가", "수량", "자동"]],
            hide_index=True,
            width="stretch",
        )

    with open_tab:
        st.caption("🧪 데모")
        st.dataframe(data.open_orders(), hide_index=True, width="stretch")
        st.caption("미체결 주문은 정책상 일정 시간 후 자동 취소(엔진).")
