"""순수 인증 코어 — 로컬 ID/PW(해시) 로그인·가입.

Streamlit 의존이 없는 순수 함수만 포함한다.
OIDC(Google st.login/st.user) 관련 함수는 app/ui/auth.py 에 남는다.

app.ui.auth 의 SPLIT 이다 (Phase 0 마이그레이션). shim: app/ui/auth.py.
"""
from __future__ import annotations

import hashlib
import hmac
import os

from app.ui import vault

__all__ = ["login_or_register"]


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
