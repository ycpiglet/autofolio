"""매매 / 주문 — 데모(mock) / 라이브(Mock 브로커 + SQLite)."""
from __future__ import annotations

from datetime import datetime

import streamlit as st

from app.ui.components import ui
from app.ui.mock import data
from app.ui import theme


def render() -> None:
    st.header("🧾 매매 / 주문")
    if st.session_state.get("data_source") == "backend":
        from app.ui import backend as _be
        _render_guard_header(_be)
        _live()
    else:
        st.caption("⚠️ 데모: 실제 주문은 발생하지 않습니다 (mock).")
        _demo()


def _render_guard_header(backend) -> None:
    """주문 전 의사결정용 상단 상태를 텍스트 기반으로 먼저 노출한다."""
    state = _collect_trade_gate_state(backend)
    with st.container(border=True):
        st.subheader("🧪 Trade 실행 안전성 (우선 확인)")

        c1, c2, c3, c4 = st.columns([2.2, 1.8, 1.2, 1.2])
        c1.markdown(f"**환경(Environment):** {state['env_label']}")
        c1.markdown(f"**출처(Source):** {state['source']}")
        c2.markdown(f"**모드(Mode):** {state['mode']}")
        c2.markdown(f"**자동매매:** {'ON' if state['auto_enabled'] else 'OFF'}")
        c3.markdown(f"**킬스위치:** {'ACTIVE' if state['kill_active'] else 'CLEAR'}")
        c4.markdown(f"**서킷브레이커:** {'TRIGGERED' if state['circuit_triggered'] else 'CLEAR'}")

        st.markdown(f"**대상 수량 게이트:**")
        st.caption(
            "화이트리스트 "
            f"{state['whitelist_count']} / "
            f"활성 조건 {state['active_conditions']} / "
            f"실행 가능 조건 {state['executable_conditions']}개"
        )

        limit_lines = []
        if state["max_order_amount"] is not None:
            limit_lines.append(f"최대 주문금액 {state['max_order_amount']:,.0f}원")
        if state["max_daily_amount"] is not None:
            limit_lines.append(f"일일예산 {state['max_daily_amount']:,.0f}원")
        if state["today_order_amount"] is not None:
            limit_lines.append(f"오늘 주문금액 {state['today_order_amount']:,.0f}원")
        if limit_lines:
            st.caption(" | ".join(limit_lines))

        if not state["all_ok"]:
            st.error("❌ 실행 조건 미충족 — 아래 체크리스트 사유로 인해 주문/실행을 차단합니다.")
        else:
            st.success("✅ 실행 조건 충족 — 주문/실행이 노출됩니다.")


def _live() -> None:
    from app.ui import backend

    cond_tab, run_tab, log_tab, kis_tab, check_tab = st.tabs(
        ["목표가 조건", "엔진 실행 / 결과", "주문로그(SQLite)", "KIS 주문내역", "📋 장전 체크리스트"]
    )
    gate_state = _collect_trade_gate_state(backend)

    with cond_tab:
        if not gate_state["all_ok"]:
            st.caption("🔒 체크리스트 미통과: 조건 저장/주문 실행은 차단됩니다.")
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
            est_notional = float(tp) * int(qty)
            st.caption(
                f"주문 intent 요약 · "
                f"Environment: {gate_state['env_label']} · "
                f"Source: {gate_state['source']} · "
                f"Symbol: {sym} · Side: {side} · Qty: {int(qty)} · "
                f"Notional: {est_notional:,.0f}원"
            )
            st.caption(f"감사 사유(기본): symbol={sym}, side={side}, qty={int(qty)}, tp={float(tp):,.0f}")
            compliance_check = st.toggle("Compliance 검토 후 저장", value=True, key="lv_compliance")
            if st.button("조건 저장", type="primary", key="lv_save", disabled=not gate_state["all_ok"]):
                if compliance_check:
                    # T-26: compliance-officer 사전 검토
                    with st.spinner("Compliance Officer 검토 중…"):
                        from app.ui import agents_runtime as ar
                        verdict_text = ar.ask(
                            "compliance-officer",
                            f"다음 매매 조건을 법규·세금·거래소 규정 관점에서 검토해주세요: "
                            f"{sym} {side} {int(qty)}주 @ {int(tp):,}원 (지정가)",
                        )
                    # 간단 판정: REJECT 포함 시 차단, CAUTION 시 경고
                    verdict_lower = verdict_text.lower()
                    if "reject" in verdict_lower or "거부" in verdict_lower:
                        st.error(f"❌ Compliance Officer 거부\n{verdict_text[:400]}")
                        st.stop()
                    elif "caution" in verdict_lower or "주의" in verdict_lower:
                        st.warning(f"⚠️ Compliance 주의사항\n{verdict_text[:300]}")
                        with st.expander("전체 의견"):
                            st.markdown(verdict_text)
                        if not st.checkbox("위 주의사항을 확인했으며 계속 진행합니다", key="lv_comply_ack"):
                            st.info("체크박스를 선택해야 조건이 저장됩니다.")
                            st.stop()
                    else:
                        st.success("✅ Compliance 검토 통과")

                cid = backend.add_condition(
                    symbol=sym, side=side, target_price=float(tp), quantity=int(qty),
                    order_type="LIMIT", auto_enabled=auto,
                )
                st.success(f"조건 저장 완료 (id={cid})")

        st.divider()
        st.caption("등록된 조건")
        st.dataframe(backend.list_conditions(), hide_index=True, width="stretch")

    with run_tab:
        from app.ui import backend as _be_run
        _env_label = theme.env_label(_be_run.env())
        if st.button(
            f"⚙️ 엔진 1회 실행 ({_env_label})",
            key="lv_run",
            disabled=not gate_state["all_ok"],
        ):
            msgs = backend.run_engine_once()
            if msgs:
                for m in msgs:
                    st.write("•", m)
            else:
                st.info("활성 조건이 없습니다. 먼저 조건을 등록하세요.")
        if not gate_state["all_ok"]:
            st.error("체크리스트 미통과 — 엔진 실행이 비활성화됩니다.")
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
                st.dataframe(df, hide_index=True, use_container_width=True)
        except Exception as exc:  # noqa: BLE001
            st.warning(f"KIS 주문내역 조회 실패: {exc}")

    with check_tab:
        _pre_trade_checklist(backend, gate_state["checks"])


def _collect_trade_gate_state(backend) -> dict:
    """거래 페이지에서 필요한 게이트 상태를 모아 텍스트 사유까지 구성."""
    checks: list[tuple[str, bool, str]] = []

    try:
        env = backend.env()
        env_label = theme.env_label(env)
        source = st.session_state.get("data_source", "backend")
        mode = st.session_state.get("mode", "L1")
        auto_enabled = bool(backend.get_flag("auto_trading_enabled"))
        kill_db = bool(backend.get_flag("kill_switch_active"))
        kill_session = bool(st.session_state.get("kill_switch", False))
        kill_active = bool(kill_db or kill_session)
        cb = backend.circuit_breaker_status()
        circuit_triggered = bool(cb.get("triggered", False))
        whitelist_rows = _rows(backend.list_whitelist())
        wl_active = len([r for r in whitelist_rows if _enabled(r.get("enabled", True))])
        cond_df = backend.list_conditions()
        active_conds = 0
        executable_conds = 0
        if cond_df is not None and not cond_df.empty:
            cond_rows = cond_df.to_dict("records")
            active_rows = [r for r in cond_rows if str(r.get("status") or "").upper() == "ACTIVE"]
            active_conds = len(active_rows)
            now = datetime.now()
            for row in cond_rows:
                executable, reason = _is_condition_executable(row, now)
                if executable:
                    executable_conds += 1
                else:
                    checks.append((f"조건 차단: {row.get('symbol','?')} {row.get('side','?')}", False, reason))

        today_order_amount = _safe_float(backend.today_order_amount())
        limits = _safe_limits(backend)
        max_order_amount = limits.get("max_order_amount")
        max_daily_amount = limits.get("max_daily_amount")

        all_ok = (not kill_active) and auto_enabled and (not circuit_triggered) and (wl_active > 0) and (today_order_amount is not None)
        if not kill_active:
            checks.append(("킬스위치", True, "해제 상태"))
        else:
            checks.append(("킬스위치", False, "킬스위치 활성"))
        checks.append(("자동매매", auto_enabled, "ON" if auto_enabled else "OFF"))
        checks.append(("서킷브레이커", not circuit_triggered, "미발동" if not circuit_triggered else "발동"))
        checks.append(("화이트리스트", wl_active > 0, f"{wl_active}개 종목 활성"))
        checks.append(("활성 조건", active_conds > 0, f"{active_conds}개 / 실행 가능 {executable_conds}개"))

        if max_order_amount is not None and max_daily_amount is not None:
            checks.append(("주문 한도", today_order_amount <= max_daily_amount, "한도 이내"))

        all_ok = all(flag for flag, _, _ in [
            (not kill_active, "", ""),
            (auto_enabled, "", ""),
            (not circuit_triggered, "", ""),
        ]) and (wl_active > 0)
    except Exception as exc:  # noqa: BLE001
        st.warning(f"거래 게이트 상태 조회 실패: {exc}")
        return {
            "env_label": theme.env_label("unknown"),
            "source": st.session_state.get("data_source", "backend"),
            "mode": st.session_state.get("mode", "L1"),
            "auto_enabled": False,
            "kill_active": True,
            "circuit_triggered": True,
            "whitelist_count": 0,
            "active_conditions": 0,
            "executable_conditions": 0,
            "today_order_amount": None,
            "max_order_amount": None,
            "max_daily_amount": None,
            "checks": [("상태 조회", False, "DB 조회 실패")],
            "all_ok": False,
        }

    return {
        "env_label": env_label,
        "source": "backend" if source == "backend" else "demo",
        "mode": mode,
        "auto_enabled": auto_enabled,
        "kill_active": kill_active,
        "circuit_triggered": circuit_triggered,
        "whitelist_count": wl_active,
        "active_conditions": active_conds,
        "executable_conditions": executable_conds,
        "today_order_amount": today_order_amount,
        "max_order_amount": max_order_amount,
        "max_daily_amount": max_daily_amount,
        "checks": checks,
        "all_ok": all_ok,
    }


def _safe_float(value):
    try:
        return float(value)
    except Exception:  # noqa: BLE001
        return None


def _safe_limits(backend) -> dict:
    try:
        limits = backend.get_global_risk_limit()
        return {
            "max_order_amount": _safe_float(limits.get("max_order_amount")),
            "max_daily_amount": _safe_float(limits.get("max_daily_amount")),
        }
    except Exception:
        return {"max_order_amount": None, "max_daily_amount": None}


def _rows(value) -> list[dict]:
    if value is None:
        return []
    if hasattr(value, "to_dict"):
        return value.to_dict("records")
    return [dict(row) for row in value]


def _enabled(value) -> bool:
    if isinstance(value, str):
        return value.strip().lower() not in {"0", "false", "off", "no", "disabled"}
    return bool(value)


def _is_condition_executable(condition: dict, now: datetime) -> tuple[bool, str]:
    """조건 활성/쿨다운 조건을 판단해 실행 가능/차단 이유를 텍스트로 반환."""
    if str(condition.get("status", "")).upper() != "ACTIVE":
        return False, "상태가 ACTIVE가 아님"
    cooldown_until = condition.get("cooldown_until")
    if cooldown_until:
        try:
            until = datetime.fromisoformat(str(cooldown_until))
            if now < until:
                return False, f"쿨다운 중 ({until:%m-%d %H:%M})"
        except Exception:  # noqa: BLE001
            return False, "쿨다운 시간 파싱 실패"
    return True, "실행 가능"


def _pre_trade_checklist(backend, checks: list[tuple[str, bool, str]]) -> None:
    """장전 체크리스트 — 매매 전 통과 관문."""
    st.subheader("📋 장전 체크리스트")
    st.caption("매매 실행 전 아래 항목을 확인하세요.")

    def row(label: str, ok: bool, detail: str = "") -> None:
        icon = "✅" if ok else "❌"
        st.markdown(f"{icon} **{label}**" + (f" — {detail}" if detail else ""))

    for label, ok, detail in checks:
        row(label, bool(ok), detail)

    st.divider()
    all_ok = all(ok for _, ok, _ in checks)
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
