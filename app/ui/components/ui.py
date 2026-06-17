"""공용 UI 컴포넌트 (P1.0a/0b)."""
from __future__ import annotations

import streamlit as st

from app.ui import state, theme


def _circuit_breaker_info() -> dict | None:
    """서킷브레이커 상태를 조회한다. 백엔드 연결 실패 시 None 반환."""
    try:
        from app.services import backend  # 로컬 import — demo 모드에서도 조용히 실패
        return backend.circuit_breaker_status()
    except Exception:
        return None


@st.dialog("⚠️ 킬스위치")
def _confirm_kill() -> None:
    st.write("**모든 자동매매를 즉시 중단**합니다. 진행할까요?")
    c1, c2 = st.columns(2)
    if c1.button("중단 실행", type="primary", width="stretch"):
        state.activate_kill()
        st.rerun()
    if c2.button("취소", width="stretch"):
        st.rerun()


def top_bar() -> None:
    """상단 상태바: 모드 배지 · 자동 ON/OFF · 새로고침 · 킬스위치."""
    mode = st.session_state.mode
    auto = st.session_state.auto_enabled
    kill = st.session_state.kill_switch

    c1, c2, c3, c4, c5 = st.columns([4, 2, 2, 1, 2])
    with c1:
        st.markdown(f"### {theme.APP_ICON} {theme.APP_NAME}")
        if st.session_state.get("data_source") == "backend":
            st.caption("📡 라이브 데이터 — KIS paper · SQLite")
        elif st.session_state.get("demo"):
            st.caption("🧪 데모 모드 — mock 데이터")
    with c2:
        st.markdown(f"**모드** :blue[{mode}] · {theme.MODE_LABELS[mode]}")
    with c3:
        st.markdown("**자동매매** " + (":red[ON]" if auto else ":gray[OFF]"))
    with c4:
        if st.button("🔄", help="데이터 새로고침", width="stretch"):
            st.cache_data.clear()
            st.rerun()

    open_kill = False
    with c5:
        if kill:
            if st.button("🔓 KILL 해제", width="stretch"):
                state.release_kill()
                st.rerun()
        else:
            open_kill = st.button("🔴 KILL", type="primary", width="stretch")

    if kill:
        st.error("🔴 킬스위치 활성 — 자동매매 강제 OFF")

    # Circuit breaker warning (only shown in backend/live mode)
    if not st.session_state.get("demo"):
        cb = _circuit_breaker_info()
        if cb and cb.get("triggered"):
            parts = []
            if cb["consecutive_failures"] >= 3:
                parts.append(f"연속 실패 {cb['consecutive_failures']}회")
            if cb["today_pnl"] < 0:
                parts.append(f"당일손실 {cb['today_pnl']:,.0f}원")
            detail = " · ".join(parts) if parts else ""
            st.warning(
                f"⚠️ 서킷브레이커 발동 — 자동매매 일시 중단"
                + (f" ({detail})" if detail else ""),
                icon="🟠",
            )

    st.divider()

    if open_kill:
        _confirm_kill()


def kpi_cards(items) -> None:
    cols = st.columns(len(items))
    for col, (label, value, delta) in zip(cols, items):
        col.metric(label, value, delta)


def badge(status: str) -> str:
    colors = {
        "연결": "green", "연동": "green", "활성": "green",
        "미연결": "gray", "미연동": "gray", "OFF": "gray",
        "주의": "orange", "경고": "red", "위험": "red",
    }
    return f":{colors.get(status, 'gray')}[●] {status}"


def page_header(title: str, subtitle: str | None = None) -> None:
    st.header(title)
    if subtitle:
        st.caption(subtitle)


def empty_state(msg: str, hint: str | None = None) -> None:
    with st.container(border=True):
        st.markdown(f"#### 🪹 {msg}")
        if hint:
            st.caption(hint)
