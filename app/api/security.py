"""Session cookie security — itsdangerous signed-cookie sessions.

Key lives in .autofolio/api_session.key (hex-encoded 32 random bytes).
Generated automatically on first run; never committed to git.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

_KEY_DIR = Path(os.getenv("AUTOFOLIO_HOME", ".autofolio"))
_KEY_FILE = _KEY_DIR / "api_session.key"
_COOKIE_NAME = "af_session"
_MAX_AGE = 86_400 * 7  # 7 days in seconds
_SALT = "autofolio-session"
_SECRET: str | None = None


def _load_or_create_key() -> str:
    """Return the hex secret key, generating and persisting it if absent.

    Cached at module level after first load to avoid per-request file reads.
    """
    global _SECRET
    if _SECRET is not None:
        return _SECRET
    _KEY_DIR.mkdir(parents=True, exist_ok=True)
    if not _KEY_FILE.exists():
        secret = os.urandom(32).hex()
        _KEY_FILE.write_text(secret, encoding="utf-8")
        try:
            os.chmod(_KEY_FILE, 0o600)
        except OSError:
            pass
        _SECRET = secret
        return _SECRET
    _SECRET = _KEY_FILE.read_text(encoding="utf-8").strip()
    return _SECRET


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(_load_or_create_key(), salt=_SALT)


def encode_session(data: dict[str, Any]) -> str:
    """Encode a session dict into a signed cookie value."""
    return _serializer().dumps(data)


def decode_session(cookie_value: str) -> dict[str, Any] | None:
    """Decode and verify a signed cookie value.

    Returns the session dict on success, or None if invalid / expired.
    """
    try:
        return _serializer().loads(cookie_value, max_age=_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None


COOKIE_NAME = _COOKIE_NAME
_SECURE = os.environ.get("AUTOFOLIO_ENV") == "production"
COOKIE_KWARGS: dict[str, Any] = {
    "httponly": True,
    "samesite": "lax",
    "secure": _SECURE,  # False for localhost; True when AUTOFOLIO_ENV=production
}

# ── Compliance acknowledgement tokens ────────────────────────────────────────

_ACK_SALT = "autofolio-ack-token"
_ACK_MAX_AGE = 300  # 5 minutes
_OAUTH_STATE_SALT = "autofolio-oauth-state"
_OAUTH_STATE_MAX_AGE = 600  # 10 minutes
OAUTH_STATE_COOKIE = "af_oauth_state"


def encode_ack_token(payload: dict) -> str:
    """Sign a compliance-acknowledgement payload (short-lived, 5 min)."""
    return URLSafeTimedSerializer(_load_or_create_key(), salt=_ACK_SALT).dumps(payload)


def decode_ack_token(token: str) -> dict | None:
    """Verify and decode an ack_token. Returns None if expired/tampered."""
    try:
        return URLSafeTimedSerializer(
            _load_or_create_key(), salt=_ACK_SALT
        ).loads(token, max_age=_ACK_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None


def encode_oauth_state(payload: dict) -> str:
    """Sign an OAuth state payload for the short-lived state cookie."""
    return URLSafeTimedSerializer(_load_or_create_key(), salt=_OAUTH_STATE_SALT).dumps(payload)


def decode_oauth_state(token: str) -> dict | None:
    """Verify an OAuth state cookie. Returns None if expired/tampered."""
    try:
        return URLSafeTimedSerializer(
            _load_or_create_key(), salt=_OAUTH_STATE_SALT
        ).loads(token, max_age=_OAUTH_STATE_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None
