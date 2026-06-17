"""app/services/alerts — 가격 알림·공시 게이트 상태 조회·갱신.

app/services/backend 구현을 도메인별로 재-익스포트한다.
내부 상수(_DISCLOSURE_BLOCK_PREFIX, _DISCLOSURE_REASON_PREFIX)와
헬퍼(_send_disclosure_notification)도 포함한다.
"""
from __future__ import annotations

from app.services.backend import (  # noqa: F401
    _DISCLOSURE_BLOCK_PREFIX,
    _DISCLOSURE_REASON_PREFIX,
    _send_disclosure_notification,
    add_price_alert,
    disclosure_gate_state,
    refresh_disclosure_gate,
)

__all__ = [
    "_DISCLOSURE_BLOCK_PREFIX",
    "_DISCLOSURE_REASON_PREFIX",
    "_send_disclosure_notification",
    "add_price_alert",
    "disclosure_gate_state",
    "refresh_disclosure_gate",
]
