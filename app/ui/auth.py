"""로그인 — 로컬 ID/PW(해시) + Google OIDC(st.login) + 게스트.

로컬 계정: 처음 보는 ID면 그 비밀번호로 **자동 가입**, 이후엔 로그인.
비밀번호는 PBKDF2(sha256, 200k)로 해시해서 암호화 보관함에 저장한다(평문 저장 없음).

순수 로컬 인증 구현은 app/services/auth_service.py 에 있다 (Phase 0 SPLIT).
OIDC(st.login/st.user) 함수는 streamlit 의존이 있어 이 파일에 잔류한다.
"""
from __future__ import annotations

import streamlit as st

from app.services.auth_service import (  # noqa: F401
    login_or_register,
)


# --- Google OIDC (st.login) ---
def oidc_configured() -> bool:
    try:
        return "auth" in st.secrets
    except Exception:
        return False


def oidc_logged_in() -> bool:
    try:
        user = getattr(st, "user", None)
        return bool(user and user.is_logged_in)
    except Exception:
        return False


def oidc_email() -> str:
    try:
        return getattr(st.user, "email", None) or "Google 사용자"
    except Exception:
        return "Google 사용자"
