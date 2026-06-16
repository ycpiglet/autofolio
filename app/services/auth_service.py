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

__all__ = ["login_or_register", "change_password", "MIN_PASSWORD_LEN"]

#: Minimum length for a (new) password. Kept conservative for a local vault.
MIN_PASSWORD_LEN = 8


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


def change_password(
    username: str, old_password: str, new_password: str
) -> tuple[bool, str]:
    """Change a local account's password. (성공여부, 메시지).

    Verifies ``old_password`` against the stored PBKDF2 hash (constant-time),
    validates ``new_password`` (non-empty, length, must differ from old), then
    stores a fresh salt + hash. Passwords are never logged.
    """
    username = (username or "").strip()
    old_password = old_password or ""
    new_password = new_password or ""

    if not username:
        return False, "계정을 찾을 수 없습니다."

    users = _users()
    rec = users.get(username)
    if rec is None:
        # Do not reveal whether the account exists beyond what the session implies.
        return False, "계정을 찾을 수 없습니다."

    # Verify the current password (constant-time comparison).
    current_hash = _hash(old_password, bytes.fromhex(rec["salt"]))
    if not hmac.compare_digest(current_hash, rec["hash"]):
        return False, "현재 비밀번호가 일치하지 않습니다."

    # Validate the new password.
    if not new_password:
        return False, "새 비밀번호를 입력하세요."
    if len(new_password) < MIN_PASSWORD_LEN:
        return False, f"새 비밀번호는 최소 {MIN_PASSWORD_LEN}자 이상이어야 합니다."
    if new_password == old_password:
        return False, "새 비밀번호는 현재 비밀번호와 달라야 합니다."

    # Store a fresh salt + hash.
    salt = os.urandom(16)
    users[username] = {"salt": salt.hex(), "hash": _hash(new_password, salt)}
    _save_users(users)
    return True, "비밀번호가 변경되었습니다."
