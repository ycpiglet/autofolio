"""로컬 암호화 보관함 (Fernet).

연동 자격증명·토큰·사용자 해시를 기기에 **암호화**해서 저장한다.
키파일과 데이터는 .autofolio/ 아래(gitignore됨)에 둔다.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from cryptography.fernet import Fernet

_DIR = Path(os.getenv("AUTOFOLIO_HOME", ".autofolio"))
_KEY = _DIR / "vault.key"
_DATA = _DIR / "vault.enc"


def _fernet() -> Fernet:
    _DIR.mkdir(parents=True, exist_ok=True)
    if not _KEY.exists():
        _KEY.write_bytes(Fernet.generate_key())
        try:
            os.chmod(_KEY, 0o600)
        except OSError:
            pass
    return Fernet(_KEY.read_bytes())


def load() -> dict:
    if not _DATA.exists():
        return {}
    try:
        return json.loads(_fernet().decrypt(_DATA.read_bytes()).decode("utf-8"))
    except Exception:
        return {}


def save(data: dict) -> None:
    _DIR.mkdir(parents=True, exist_ok=True)
    token = _fernet().encrypt(json.dumps(data, ensure_ascii=False).encode("utf-8"))
    _DATA.write_bytes(token)
