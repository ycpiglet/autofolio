"""로컬 암호화 보관함 (Fernet).

연동 자격증명·토큰·사용자 해시를 기기에 **암호화**해서 저장한다.
키파일과 데이터는 .autofolio/ 아래(gitignore됨)에 둔다.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from cryptography.fernet import Fernet

from app.common.fileperms import restrict_to_user

logger = logging.getLogger(__name__)

_DIR = Path(os.getenv("AUTOFOLIO_HOME", ".autofolio"))
_KEY = _DIR / "vault.key"
_DATA = _DIR / "vault.enc"

# Env var holding a urlsafe-base64 Fernet key. When set, the key is NEVER written
# to disk — this is the production path. See scripts/rotate_vault_key.py for
# rotation (decrypt-with-old → re-encrypt-with-new).
_ENV_KEY_NAME = "AUTOFOLIO_VAULT_KEY"

# Emit the dev-fallback warning at most once per process to avoid log spam.
_warned_colocated = False


def _key_bytes() -> bytes:
    """Return the Fernet key bytes, sourced by priority.

    1. ``AUTOFOLIO_VAULT_KEY`` env var (production path — key never on disk).
       If the env var is SET but malformed a clear ``ValueError`` is raised
       immediately so misconfiguration is never silently hidden.
    2. Co-located ``.autofolio/vault.key`` file (DEV fallback). Generated if
       absent and a LOUD one-time warning is emitted; this preserves the exact
       historical local/test behaviour when the env var is unset, so existing
       ``vault.enc`` data stays decryptable byte-identically.
    """
    env_key = os.environ.get(_ENV_KEY_NAME)
    if env_key:
        key = env_key.encode("ascii") if isinstance(env_key, str) else env_key
        try:
            Fernet(key)  # validate format — raises ValueError on malformed key
        except Exception as exc:
            raise ValueError(
                f"Environment variable {_ENV_KEY_NAME!r} is set but contains an "
                f"invalid Fernet key (expected 32 URL-safe base64 bytes). "
                f"Details: {exc}"
            ) from exc
        return key

    global _warned_colocated
    _DIR.mkdir(parents=True, exist_ok=True)
    if not _KEY.exists():
        _KEY.write_bytes(Fernet.generate_key())
        restrict_to_user(_KEY)
    if not _warned_colocated:
        logger.warning(
            "vault key is co-located on disk at %s — set %s for production "
            "(the key is then never written to disk).",
            _KEY,
            _ENV_KEY_NAME,
        )
        _warned_colocated = True
    return _KEY.read_bytes()


def _fernet() -> Fernet:
    return Fernet(_key_bytes())


def encrypt_bytes(data: bytes) -> bytes:
    """Encrypt arbitrary bytes with the vault Fernet key.

    Shared so other on-disk secret caches (e.g. the KIS token cache) can reuse
    the same key-sourcing precedence (AUTOFOLIO_VAULT_KEY → co-located file).
    """
    return _fernet().encrypt(data)


def decrypt_bytes(token: bytes) -> bytes:
    """Decrypt bytes produced by :func:`encrypt_bytes`. Raises on bad token."""
    return _fernet().decrypt(token)


def load() -> dict:
    # Validate key eagerly so a malformed AUTOFOLIO_VAULT_KEY is always loud,
    # even when no vault data file exists yet.  _key_bytes() raises ValueError
    # for bad env keys; the co-located-file path never raises here.
    key = _key_bytes()  # may raise ValueError for malformed env key
    if not _DATA.exists():
        return {}
    try:
        return json.loads(Fernet(key).decrypt(_DATA.read_bytes()).decode("utf-8"))
    except ValueError:
        raise  # re-raise: malformed key slipped through — do not hide
    except Exception:  # noqa: BLE001 — corrupted / wrong-key ciphertext → treat as empty
        return {}


def save(data: dict) -> None:
    _DIR.mkdir(parents=True, exist_ok=True)
    token = _fernet().encrypt(json.dumps(data, ensure_ascii=False).encode("utf-8"))
    _DATA.write_bytes(token)
