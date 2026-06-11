"""공용 UI 컴포넌트 (P1.0a/0b)."""
from __future__ import annotations

import streamlit as st

from app.ui import state, theme


STATUS_TONES = {
    "연결": "success",
    "연동": "success",
    "활성": "success",
    "정상": "success",
    "ON": "success",
    "ON ": "success",
    "CLEAR": "success",
    "주의": "warning",
    "대기": "warning",
    "경고": "warning",
    "OFF": "neutral",
    "미연결": "neutral",
    "미연동": "neutral",
    "BLOCK": "danger",
    "위험": "danger",
    "킬스위치": "danger",
    "kill": "danger",
    "ACTIVE": "danger",
    "TRIGGERED": "danger",
}

TONE_MARKERS = {
    "success": "[OK]",
    "warning": "[CHECK]",
    "danger": "[BLOCK]",
    "neutral": "[OFF]",
}

TONE_COLORS = {
    "success": "green",
    "warning": "orange",
    "danger": "red",
    "neutral": "gray",
}


def _normalize_env_for_summary(env: str | None) -> str:
    key = (env or "").strip().lower()
    if key == "demo":
        return "mock"
    if key == "backend":
        return "paper"
    return key


def _circuit_breaker_info() -> dict | None:
    """서킷브레이커 상태를 조회한다. 백엔드 연결 실패 시 None 반환."""
    try:
        from app.ui import backend  # 로컬 import — demo 모드에서도 조용히 실패
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
    """상단 상태바: Safety Rail 형태 운영 상태 배지 · 새로고침 · 킬스위치."""
    env = _normalize_env_for_summary(st.session_state.get("data_source"))
    mode = st.session_state.mode
    auto = st.session_state.auto_enabled
    kill = st.session_state.kill_switch
    cb = _circuit_breaker_info()
    summary = build_safety_summary(
        env=env,
        mode=mode,
        auto=auto,
        kill=kill,
        circuit_breaker=bool(cb.get("triggered")) if cb else False,
    )

    c1, c2, c3, c4, c5 = st.columns([4, 2, 2, 1, 2])
    with c1:
        st.markdown(f"### {theme.APP_ICON} {theme.APP_NAME}")
        st.caption(f"환경: {summary['env']}")
    with c2:
        st.markdown(f"**모드** {mode} · {theme.MODE_LABELS.get(mode, '미지정')}")
    with c3:
        st.markdown(f"**자동매매** {status_badge('ON' if auto else 'OFF')}")
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

    st.caption(
        f"✅ 환경 {summary['env']} / "
        f"자동매매 {summary['auto']} / "
        f"킬스위치 {summary['kill']} / "
        f"서킷브레이커 {summary['circuit_breaker']}"
    )

    if not st.session_state.get("demo") and summary["circuit_breaker"] == "TRIGGERED":
        parts = []
        if cb and cb.get("consecutive_failures") is not None:
            parts.append(f"연속 실패 {cb['consecutive_failures']}회")
        if cb and cb.get("today_pnl", 0) < 0:
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
    return status_badge(status)


def status_tone(status: str) -> str:
    """텍스트 상태를 상태 톤(success/warning/danger/neutral)으로 정규화한다."""
    return STATUS_TONES.get(status, "neutral")


def status_badge(status: str) -> str:
    """색상뿐 아니라 마커 텍스트를 함께 출력하는 status badge."""
    tone = status_tone(status)
    marker = TONE_MARKERS[tone]
    color = TONE_COLORS[tone]
    return f":{color}[{marker}] {status}"


def build_safety_summary(
    env: str | None,
    mode: str | None,
    auto: bool,
    kill: bool,
    circuit_breaker: bool,
) -> dict[str, str]:
    """안전 rail 표시를 위한 요약 딕셔너리를 생성한다."""
    norm_env = _normalize_env_for_summary(env)
    mode_text = mode or "L1"
    return {
        "env": theme.env_label(norm_env),
        "mode": mode_text,
        "auto": "ON" if auto else "OFF",
        "kill": "ACTIVE" if kill else "CLEAR",
        "circuit_breaker": "TRIGGERED" if circuit_breaker else "CLEAR",
    }


def console_row(timestamp: str, source: str, message: str) -> str:
    """콘솔형 표면에서 시간, 출처, 메시지를 색상 의존 없이 표시한다."""
    return f"`{timestamp}` **{source}** - {message}"


def page_header(title: str, subtitle: str | None = None) -> None:
    st.header(title)
    if subtitle:
        st.caption(subtitle)


def empty_state(msg: str, hint: str | None = None) -> None:
    with st.container(border=True):
        st.markdown(f"#### 🪹 {msg}")
        if hint:
            st.caption(hint)
