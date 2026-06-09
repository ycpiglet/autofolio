"""연동 보관함 — 증권 다계좌 / 알림채널 (vault에 암호화 영속).

민감정보(_app_secret 등)는 vault 안에 암호화 저장하고, 표시용 함수는 제외하고 돌려준다.
"""
from __future__ import annotations

from app.ui import vault

_DEFAULT_CHANNELS = [
    {"채널": "Telegram", "status": "미연결", "detail": ""},
    {"채널": "KakaoTalk(나에게)", "status": "미연결", "detail": ""},
    {"채널": "Notion", "status": "미연결", "detail": ""},
    {"채널": "Discord", "status": "미연결", "detail": ""},
    {"채널": "Email", "status": "미연결", "detail": ""},
]


def _persist(conn: dict) -> None:
    data = vault.load()
    data["connections"] = conn
    vault.save(data)


def get() -> dict:
    conn = vault.load().get("connections")
    if not conn:
        conn = {"brokers": [], "channels": [dict(c) for c in _DEFAULT_CHANNELS]}
        _persist(conn)
    conn.setdefault("brokers", [])
    conn.setdefault("channels", [dict(c) for c in _DEFAULT_CHANNELS])
    return conn


def brokers_public() -> list[dict]:
    return [
        {k: v for k, v in b.items() if not k.startswith("_")}
        for b in get().get("brokers", [])
    ]


def add_broker(alias: str, securities: str, app_key: str, app_secret: str,
               account_no: str, env: str) -> None:
    conn = get()
    brokers = conn.setdefault("brokers", [])
    brokers.append(
        {
            "별칭": alias or "내 계좌",
            "증권사": securities,
            "환경": env,
            "상태": "연동",
            "기본": len(brokers) == 0,
            "_app_key": app_key,
            "_app_secret": app_secret,
            "_account": account_no,
        }
    )
    _persist(conn)


def remove_broker(idx: int) -> None:
    conn = get()
    brokers = conn.get("brokers", [])
    if 0 <= idx < len(brokers):
        was_default = brokers[idx].get("기본")
        brokers.pop(idx)
        if was_default and brokers:
            brokers[0]["기본"] = True
        _persist(conn)


def set_default_broker(idx: int) -> None:
    conn = get()
    for i, b in enumerate(conn.get("brokers", [])):
        b["기본"] = (i == idx)
    _persist(conn)


def connect_channel(name: str, detail: str) -> None:
    conn = get()
    for c in conn.get("channels", []):
        if c["채널"] == name:
            c["status"] = "연결"
            c["detail"] = detail
    _persist(conn)


def disconnect_channel(name: str) -> None:
    conn = get()
    for c in conn.get("channels", []):
        if c["채널"] == name:
            c["status"] = "미연결"
            c["detail"] = ""
    _persist(conn)
