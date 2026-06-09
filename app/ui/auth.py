"""로그인 — 로컬 ID/PW(해시) + Google OIDC(st.login) + 게스트.

로컬 계정: 처음 보는 ID면 그 비밀번호로 **자동 가입**, 이후엔 로그인.
비밀번호는 PBKDF2(sha256, 200k)로 해시해서 암호화 보관함에 저장한다(평문 저장 없음).
"""
from __future__ import annotations

import hashlib
import hmac
import os

import streamlit as st

from app.ui import vault


def _hash(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000).hex()


def _users() -> dict:
    return vault.load().get("users", {})


def _save_users(users: dict) -> None:
    data = vault.load()
    data["users"] = users
    vault.save(data)


def login_or_register(username: str, password: str) -> tuple[bool, str]:
    """존재하면 검증, 없으면 가입. (성공여부, 메시지)."""
    username = (username or "").strip()
    if not username or not password:
        return False, "ID와 비밀번호를 입력하세요."
    users = _users()
    if username in users:
        rec = users[username]
        if hmac.compare_digest(_hash(password, bytes.fromhex(rec["salt"])), rec["hash"]):
            return True, "로그인되었습니다."
        return False, "비밀번호가 일치하지 않습니다."
    salt = os.urandom(16)
    users[username] = {"salt": salt.hex(), "hash": _hash(password, salt)}
    _save_users(users)
    return True, "계정을 만들고 로그인했습니다."


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
