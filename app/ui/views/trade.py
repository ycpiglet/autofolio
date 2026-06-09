"""매매 / 주문 — 데모(mock) / 라이브(Mock 브로커 + SQLite)."""
from __future__ import annotations

import streamlit as st

from app.ui.components import ui
from app.ui.mock import data


def render() -> None:
    st.header("🧾 매매 / 주문")
    if st.session_state.get("data_source") == "backend":
        st.caption("🟢 라이브 (Mock 브로커 + SQLite, 증권 키 불필요) — 실제 주문은 발생하지 않습니다.")
        _live()
    else:
        st.caption("⚠️ 데모: 실제 주문은 발생하지 않습니다 (mock).")
        _demo()


def _live() -> None:
    from app.ui import backend

    cond_tab, run_tab, log_tab = st.tabs(["목표가 조건", "엔진 실행 / 결과", "주문로그"])

    with cond_tab:
        opts = backend.symbol_options()
        if not opts:
            ui.empty_state("화이트리스트가 비어있습니다")
        else:
            c1, c2, c3 = st.columns(3)
            label = c1.selectbox("종목", list(opts.keys()), key="lv_sym")
            sym = opts[label]
            cur = backend.price(sym)
            c1.metric("현재가 (mock)", f"{cur:,.0f}")
            side = c2.radio("방향", ["BUY", "SELL"], horizontal=True, key="lv_side")
            tp = c2.number_input("목표가", min_value=0.0, value=float(round(cur * 0.99)), step=100.0, key="lv_tp")
            qty = c3.number_input("수량", min_value=1, value=1, key="lv_qty")
            auto = c3.checkbox("자동주문 ON", value=False, key="lv_auto")
            if st.button("조건 저장", type="primary", key="lv_save"):
                cid = backend.add_condition(
                    symbol=sym, side=side, target_price=float(tp), quantity=int(qty),
                    order_type="LIMIT", auto_enabled=auto,
                )
                st.success(f"조건 저장 완료 (id={cid})")

        st.divider()
        st.caption("등록된 조건")
        st.dataframe(backend.list_conditions(), hide_index=True, width="stretch")

    with run_tab:
        if st.button("⚙️ 엔진 1회 실행 (mock)", key="lv_run"):
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
