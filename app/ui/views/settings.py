"""설정 · 연동 — SSO / 채널 / 증권 다계좌 / 운영모드 / 리스크 (P1.0c 실연동)."""
from __future__ import annotations

import streamlit as st

from app.ui import auth, store, theme
from app.ui.components import ui
from app.ui.mock import data
from app.ui.services import connectors


def render() -> None:
    ui.page_header("⚙️ 설정 · 연동", "운영 모드, 리스크, 연동 상태를 분리해 관리")
    mode_tab, risk_tab, broker_tab, ch_tab, sso_tab = st.tabs(
        ["운영모드", "리스크", "증권계좌", "알림채널", "계정(SSO)"]
    )
    with mode_tab:
        _modes()
    with risk_tab:
        _risk()
    with broker_tab:
        _brokers()
    with ch_tab:
        _channels()
    with sso_tab:
        _sso()


def _sso() -> None:
    user = st.session_state.user or {}
    st.write(f"로그인: **{user.get('name', '?')}** · {user.get('provider', '')}")
    if auth.oidc_configured():
        st.success("Google OIDC 설정됨 — 로그인 화면에서 1클릭 로그인됩니다.")
    else:
        st.info("Google OIDC 미설정. `.streamlit/secrets.toml`에 `[auth]` 추가 시 활성화 (secrets.toml.example 참고).")
    st.caption("Kakao/Naver는 streamlit-oauth 컴포넌트로 확장 예정.")


def _channels() -> None:
    for c in store.get()["channels"]:
        col1, col2, col3 = st.columns([2, 3, 2])
        col1.write(f"**{c['채널']}**")
        col2.markdown(ui.badge(c["status"]) + (f" · {c['detail']}" if c["detail"] else ""))
        if c["status"] == "연결":
            if col3.button("해제", key=f"chx_{c['채널']}", width="stretch"):
                store.disconnect_channel(c["채널"])
                st.rerun()
        else:
            with col3.popover("연결"):
                _channel_form(c["채널"])


def _channel_form(name: str) -> None:
    if name == "Telegram":
        token = st.text_input("봇 토큰", type="password", key=f"tg_{name}")
        st.text_input("Chat ID", key=f"tgc_{name}")
        if st.button("연결 테스트", key=f"tgb_{name}"):
            ok, msg = connectors.test_telegram(token)
            if ok:
                store.connect_channel(name, "봇 연결됨")
                st.rerun()
            st.warning(msg)
        if st.button("토큰 저장(검증 생략)", key=f"tgs_{name}"):
            store.connect_channel(name, "저장됨")
            st.rerun()
    else:
        detail = st.text_input("연결 정보(토큰/주소)", key=f"gen_{name}")
        if st.button("연결", key=f"genb_{name}"):
            store.connect_channel(name, detail or "저장됨")
            st.rerun()


def _brokers() -> None:
    st.subheader("연동 계좌")
    st.caption("Secret 값은 입력 시에만 사용하고 목록에는 표시하지 않습니다.")
    brokers = store.brokers_public()
    if not brokers:
        ui.empty_state("연동된 증권계좌가 없습니다", "아래 '계좌 추가'로 첫 계좌를 연결하세요.")
    else:
        for i, b in enumerate(brokers):
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 2, 2])
                star = "기본 · " if b.get("기본") else ""
                c1.write(f"**{star}{b['별칭']}** · {b['증권사']}")
                c2.markdown(ui.badge(b["상태"]) + f" · {b['환경']}")
                if not b.get("기본"):
                    if c3.button("기본 설정", key=f"bd_{i}", width="stretch"):
                        store.set_default_broker(i)
                        st.rerun()
                with st.expander("위험 작업"):
                    st.caption("계좌 연결 삭제는 되돌릴 수 없습니다.")
                    if st.button("계좌 연결 삭제", key=f"brm_{i}", width="stretch"):
                        store.remove_broker(i)
                        st.rerun()

    st.subheader("Secret 입력")
    with st.expander("계좌 추가"):
        alias = st.text_input("별칭", placeholder="내 KIS(실전)", key="b_alias")
        sec = st.selectbox("증권사", ["한국투자증권 (KIS)"], key="b_sec")
        app_key = st.text_input("App Key", type="password", key="b_key")
        app_secret = st.text_input("App Secret", type="password", key="b_secret")
        account = st.text_input("계좌번호", placeholder="00000000-00", type="password", key="b_acct")
        env = st.radio("환경", ["mock", "모의", "실전"], horizontal=True, key="b_env")
        if st.button("🔗 연동하기 (토큰 테스트)", type="primary", key="b_go"):
            if env == "mock":
                store.add_broker(alias, sec, app_key, app_secret, account, env)
                st.success("✅ 연동 완료 (mock 저장)")
                st.rerun()
            else:
                ok, msg = connectors.test_kis(app_key, app_secret, env)
                store.add_broker(alias, sec, app_key, app_secret, account, env)
                (st.success if ok else st.warning)(f"{'✅' if ok else '⚠️'} {msg} — 저장됨")
                st.rerun()


def _modes() -> None:
    live = st.session_state.get("data_source") == "backend"

    st.subheader("자동화 수준")
    with st.container(border=True):
        summary = ui.build_safety_summary(
            env=st.session_state.get("data_source", "demo"),
            mode=st.session_state.get("mode", "L1"),
            auto=bool(st.session_state.get("auto_enabled", False)),
            kill=bool(st.session_state.get("kill_switch", False)),
            circuit_breaker=False,
        )
        st.caption(
            f"환경 {summary['env']} · 모드 {summary['mode']} · "
            f"자동매매 {summary['auto']} · 킬스위치 {summary['kill']}"
        )

    st.select_slider(
        "전역 기본 자율성",
        options=theme.MODES,
        format_func=lambda m: f"{m} · {theme.MODE_LABELS[m]}",
        key="mode",
    )

    confirmed = True
    if st.session_state.mode in ("L3", "L4") and not st.session_state.auto_enabled:
        st.warning("자동 실행 모드(L3+) — 예산·주문한도·서킷브레이커가 적용됩니다.")
        confirmed = st.checkbox("위험을 이해했고 자동매매를 활성화합니다", key="auto_confirm")

    prev_auto = st.session_state.get("auto_enabled", False)
    st.toggle(
        "자동매매 활성",
        key="auto_enabled",
        disabled=st.session_state.kill_switch
        or (st.session_state.mode in ("L3", "L4") and not confirmed),
    )

    # 라이브 모드: auto_enabled 토글 변경 → DB 즉시 동기화
    if live and st.session_state.auto_enabled != prev_auto:
        try:
            from app.ui import backend
            backend.set_flag("auto_trading_enabled", st.session_state.auto_enabled)
            st.toast(f"자동매매 {'ON' if st.session_state.auto_enabled else 'OFF'} — DB 저장됨")
        except Exception as exc:  # noqa: BLE001
            st.warning(f"DB 동기화 실패: {exc}")

    if live:
        # DB 실제 상태 표시
        try:
            from app.ui import backend
            db_auto = backend.get_flag("auto_trading_enabled")
            db_kill = backend.get_flag("kill_switch_active")
            st.caption(
                f"DB 상태: 자동매매={'ON' if db_auto else 'OFF'} · "
                f"킬스위치={'활성' if db_kill else '해제'} 🟢 라이브"
            )
        except Exception:  # noqa: BLE001
            pass
    else:
        st.caption("킬스위치 활성 시 자동매매는 강제 OFF.")

    st.toggle("손익 색: 상승=빨강 / 하락=파랑 (한국식)", key="pnl_kr_colors")

    st.divider()
    st.markdown("**종목별 자율성**")
    if live:
        try:
            from app.ui import backend
            wl = backend.list_whitelist()
            if not wl.empty:
                wl = wl[["symbol", "name"]].rename(columns={"symbol": "티커", "name": "종목"})
                wl["모드"] = [st.session_state.symbol_modes.get(t, st.session_state.mode) for t in wl["티커"]]
                edited = st.data_editor(wl, hide_index=True, width="stretch", key="symmode_editor_live",
                    disabled=["종목", "티커"],
                    column_config={"모드": st.column_config.SelectboxColumn(options=theme.MODES)})
                for _, r in edited.iterrows():
                    st.session_state.symbol_modes[r["티커"]] = r["모드"]
            else:
                st.caption("화이트리스트가 비어있습니다.")
        except Exception as exc:  # noqa: BLE001
            st.caption(f"종목별 모드 로딩 실패: {exc}")
    else:
        df = data.holdings_df()[["종목", "티커"]].copy()
        df["모드"] = [st.session_state.symbol_modes.get(t, st.session_state.mode) for t in df["티커"]]
        edited = st.data_editor(df, hide_index=True, width="stretch", key="symmode_editor",
            disabled=["종목", "티커"],
            column_config={"모드": st.column_config.SelectboxColumn(options=theme.MODES)})
        for _, r in edited.iterrows():
            st.session_state.symbol_modes[r["티커"]] = r["모드"]


def _risk() -> None:
    live = st.session_state.get("data_source") == "backend"

    st.subheader("리스크 한도")
    c1, c2 = st.columns(2)
    daily = c1.number_input("일일 예산 (₩)", min_value=0, value=300_000, step=50_000, key="risk_daily")
    order_limit = c1.number_input("건당 주문 한도 (₩)", min_value=0, value=100_000, step=10_000, key="risk_order")
    c2.number_input("종목당 비중 상한 (%)", min_value=1, max_value=100, value=15, key="risk_sym")
    c2.number_input("서킷브레이커 일손실 (%)", min_value=1, max_value=50, value=3, key="risk_cb")
    st.text_input("자동매매 거래시간", value="09:10 ~ 15:20", key="risk_window")

    if live and st.button("💾 리스크 한도 저장", type="primary", key="risk_save"):
        try:
            from app.ui import backend
            backend.set_risk_limits(
                max_order_amount=float(order_limit),
                max_daily_amount=float(daily),
            )
            st.success("✅ 리스크 한도 DB 저장됨")
        except Exception as exc:  # noqa: BLE001
            st.error(f"저장 실패: {exc}")
