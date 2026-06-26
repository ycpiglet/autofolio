"""순수 인증 코어 — 로컬 ID/PW(해시) 로그인.

Streamlit 의존이 없는 순수 함수만 포함한다.
OIDC(Google st.login/st.user) 관련 함수는 app/ui/auth.py 에 남는다.

app.ui.auth 의 SPLIT 이다 (Phase 0 마이그레이션). shim: app/ui/auth.py.
"""
from __future__ import annotations

import hashlib
import hmac
import os

from app.ui import vault
from app.services.flags import local_auto_register_enabled as _auto_register_enabled

__all__ = [
    "login_or_register",
    "change_password",
    "create_or_update_user",
    "verify_password",
    "role_for_user",
    "sso_role_for_email",
    "MIN_PASSWORD_LEN",
]

#: Minimum length for a (new) password. Kept conservative for a local vault.
MIN_PASSWORD_LEN = 8


def _hash(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000).hex()


def _password_matches(record: dict, password: str) -> bool:
    try:
        salt = bytes.fromhex(str(record["salt"]))
        expected_hash = str(record["hash"])
    except (KeyError, TypeError, ValueError):
        return False
    return hmac.compare_digest(_hash(password or "", salt), expected_hash)


def _users() -> dict:
    return vault.load().get("users", {})


def _save_users(users: dict) -> None:
    data = vault.load()
    data["users"] = users
    vault.save(data)


def _normalize_username(username: str) -> str:
    return " ".join((username or "").strip().split())


def login_or_register(username: str, password: str) -> tuple[bool, str]:
    """존재하면 검증, 없으면 기본 차단. (성공여부, 메시지).

    First-run auto-registration is an explicit local/dev opt-in only. The
    product membership model is approval-based, so unknown usernames fail
    closed unless AUTOFOLIO_LOCAL_AUTO_REGISTER=1 is set.
    """
    username = _normalize_username(username)
    if not username or not password:
        return False, "ID와 비밀번호를 입력하세요."
    users = _users()
    if username in users:
        rec = users[username]
        if _password_matches(rec, password):
            return True, "로그인되었습니다."
        return False, "비밀번호가 일치하지 않습니다."
    if not _auto_register_enabled():
        return False, "승인된 계정이 아닙니다. 가입 승인 또는 계정 활성화 후 로그인하세요."
    create_or_update_user(username, password, role="owner", source="local_auto_register")
    return True, "계정을 만들고 로그인했습니다."


def role_for_user(username: str) -> str:
    """Return the local account role, defaulting legacy records to owner."""
    username = _normalize_username(username)
    users = _users()
    rec = users.get(username)
    if not isinstance(rec, dict):
        return "owner"
    role = str(rec.get("role") or "owner").strip().lower()
    return role if role in {"owner", "member"} else "owner"


def sso_role_for_email(email: str | None) -> str | None:
    """3-way SSO role assignment: 'owner' | 'member' | None (deny).

    Resolution order:
    1. If the SSO email matches AUTOFOLIO_OWNER_EMAIL → 'owner'.
       Fail-closed: if AUTOFOLIO_OWNER_EMAIL is unset, no SSO email is owner.
    2. Elif the email maps to an approved local 'member' account → 'member'.
    3. Else → None (caller must deny / return 403).

    This prevents any allowlisted-but-unapproved email from silently receiving
    owner privileges (TASK-087 A3 security fix).
    """
    if not email:
        return None

    owner_email = (os.getenv("AUTOFOLIO_OWNER_EMAIL") or "").strip().lower()
    normalized = email.strip().lower()

    # 1. Owner identity check (explicit designation required)
    if owner_email and normalized == owner_email:
        return "owner"

    # 2. Approved member account lookup (username == SSO email, case-insensitive).
    # Vault keys are stored via _normalize_username() which does NOT lowercase, so
    # we must normalize both sides to avoid denying a legitimate member whose SSO
    # provider returns a differently-cased email (e.g. Member@Example.com vs
    # member@example.com stored at registration time).
    users = _users()
    normalized_email = _normalize_username(email.strip().lower())
    rec = next(
        (v for k, v in users.items() if _normalize_username(k).lower() == normalized_email),
        None,
    )
    if isinstance(rec, dict) and str(rec.get("role") or "").strip().lower() == "member":
        return "member"

    # 3. Deny — allowlisted but no matching account
    return None


def verify_password(username: str, password: str) -> tuple[bool, str]:
    """Verify a local account password without mutating account metadata."""
    username = _normalize_username(username)
    password = password or ""
    if not username:
        return False, "계정을 찾을 수 없습니다."
    rec = _users().get(username)
    if rec is None:
        return False, "계정을 찾을 수 없습니다."
    if not _password_matches(rec, password):
        return False, "현재 비밀번호가 일치하지 않습니다."
    return True, "비밀번호가 확인되었습니다."


def create_or_update_user(
    username: str,
    password: str,
    *,
    role: str = "owner",
    source: str = "membership_approval",
    membership_request_id: str | None = None,
) -> tuple[bool, str]:
    """Create or reset a local approved account without storing plaintext."""
    username = _normalize_username(username)
    password = password or ""
    role = (role or "owner").strip().lower()

    if not username:
        return False, "계정 ID를 입력하세요."
    if len(username) > 160:
        return False, "계정 ID가 너무 깁니다."
    if not password:
        return False, "임시 비밀번호를 입력하세요."
    if len(password) < MIN_PASSWORD_LEN:
        return False, f"임시 비밀번호는 최소 {MIN_PASSWORD_LEN}자 이상이어야 합니다."
    if role not in {"owner", "member"}:
        return False, "지원하지 않는 계정 권한입니다."

    users = _users()
    salt = os.urandom(16)
    users[username] = {
        "salt": salt.hex(),
        "hash": _hash(password, salt),
        "role": role,
        "source": source,
        "membership_request_id": membership_request_id,
    }
    _save_users(users)
    return True, "계정이 활성화되었습니다."


def change_password(
    username: str, old_password: str, new_password: str
) -> tuple[bool, str]:
    """Change a local account's password. (성공여부, 메시지).

    Verifies ``old_password`` against the stored PBKDF2 hash (constant-time),
    validates ``new_password`` (non-empty, length, must differ from old), then
    stores a fresh salt + hash. Passwords are never logged.
    """
    username = _normalize_username(username)
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
    if not _password_matches(rec, old_password):
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
    updated = dict(rec)
    updated.update({"salt": salt.hex(), "hash": _hash(new_password, salt)})
    users[username] = updated
    _save_users(users)
    return True, "비밀번호가 변경되었습니다."
