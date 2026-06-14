"""세션 상태 — 로그인·운영모드·킬스위치 (P1.0a, mock)."""
from __future__ import annotations

import copy

import streamlit as st

DEFAULTS: dict = {
    "authed": False,
    "user": None,          # {"name": str, "provider": str}
    "demo": False,
    "mode": "L1",          # 전역 기본 자율성 레벨
    "auto_enabled": False,
    "kill_switch": False,
    "pnl_kr_colors": True,
    "symbol_modes": {},     # {티커: "L0".."L4"} 종목별 자율성
    "data_source": "demo",  # "demo"(mock) | "backend"(Mock 브로커 + SQLite)
}


def init_state() -> None:
    for key, value in DEFAULTS.items():
        st.session_state.setdefault(key, value)


def login(provider: str, name: str, demo: bool = False) -> None:
    st.session_state.authed = True
    st.session_state.user = {"name": name, "provider": provider}
    st.session_state.demo = demo


# Extra session-scoped keys not in DEFAULTS that must be cleared on logout
_EXTRA_SESSION_KEYS: tuple[str, ...] = (
    "trade_ack_checked",
    "_trade_ack_pending_message",
    "_trade_ack_context",
)


def logout() -> None:
    """완전 세션 초기화 — DEFAULTS 전체 키 순회 + 추가 세션 키 제거.

    보안: 이전 사용자의 kill_switch·auto_enabled·mode·symbol_modes·data_source·
    ack 상태가 다음 로그인으로 누출되지 않도록 보장한다.
    """
    for key, value in DEFAULTS.items():
        st.session_state[key] = copy.copy(value)
    for key in _EXTRA_SESSION_KEYS:
        st.session_state.pop(key, None)


def activate_kill() -> None:
    st.session_state.kill_switch = True
    st.session_state.auto_enabled = False


def release_kill() -> None:
    st.session_state.kill_switch = False
