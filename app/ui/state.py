"""세션 상태 — 로그인·운영모드·킬스위치 (P1.0a, mock)."""
from __future__ import annotations

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


def logout() -> None:
    for key in ("authed", "user", "demo"):
        st.session_state[key] = DEFAULTS[key]


def activate_kill() -> None:
    st.session_state.kill_switch = True
    st.session_state.auto_enabled = False


def release_kill() -> None:
    st.session_state.kill_switch = False
