"""Risk acknowledgement persistence and live-trading readiness checks."""
from __future__ import annotations

import json
from typing import Any

from app.database.sqlite_db import get_connection


LIVE_TRADING_ACK_KIND = "live_trading_risk_v1"
LIVE_TRADING_ACK_VERSION = "live-trading-risk-v1"

_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS user_acknowledgements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    kind TEXT NOT NULL,
    document_slug TEXT NOT NULL,
    document_version TEXT NOT NULL,
    acknowledgement_text TEXT NOT NULL,
    method TEXT NOT NULL DEFAULT 'session_ack',
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_user_ack_user_kind_created
ON user_acknowledgements(username, kind, created_at);
"""


def record_acknowledgement(
    *,
    username: str,
    kind: str,
    document_slug: str,
    document_version: str,
    acknowledgement_text: str,
    method: str = "session_ack",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    _ensure_tables()
    _validate_acknowledgement(kind, acknowledgement_text)
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO user_acknowledgements(
                username, kind, document_slug, document_version,
                acknowledgement_text, method, metadata_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                kind,
                document_slug,
                document_version,
                acknowledgement_text,
                method,
                json.dumps(metadata or {}, ensure_ascii=False, sort_keys=True),
            ),
        )
        ack_id = int(cur.lastrowid)
        row = conn.execute(
            "SELECT * FROM user_acknowledgements WHERE id = ?",
            (ack_id,),
        ).fetchone()
    return _row_to_ack(dict(row))


def latest_acknowledgement(username: str, kind: str) -> dict[str, Any] | None:
    _ensure_tables()
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT * FROM user_acknowledgements
            WHERE username = ? AND kind = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (username, kind),
        ).fetchone()
    return _row_to_ack(dict(row)) if row else None


def live_trading_ack_completed(username: str) -> bool:
    ack = latest_acknowledgement(username, LIVE_TRADING_ACK_KIND)
    return bool(ack and ack.get("document_version") == LIVE_TRADING_ACK_VERSION)


def acknowledgement_status(username: str) -> dict[str, Any]:
    ack = latest_acknowledgement(username, LIVE_TRADING_ACK_KIND)
    return {
        "username": username,
        "live_trading_acknowledged": bool(
            ack and ack.get("document_version") == LIVE_TRADING_ACK_VERSION
        ),
        "live_trading_acknowledged_at": ack.get("created_at") if ack else None,
        "latest_live_trading_ack_id": ack.get("id") if ack else None,
        "totp_recommended": True,
        "totp_enabled": False,
        "message": (
            "실전 거래 위험 고지가 기록되었습니다."
            if ack
            else "실전 거래 전 위험 고지 확인이 필요합니다."
        ),
    }


def _ensure_tables() -> None:
    with get_connection() as conn:
        conn.executescript(_TABLE_SQL)


def _validate_acknowledgement(kind: str, text: str) -> None:
    cleaned = (text or "").strip()
    if len(cleaned) < 20:
        raise ValueError("acknowledgement_text is too short")
    if kind == LIVE_TRADING_ACK_KIND:
        required = ("손실", "책임")
        missing = [word for word in required if word not in cleaned]
        if missing:
            raise ValueError("live-trading acknowledgement must mention loss and responsibility")


def _row_to_ack(row: dict[str, Any]) -> dict[str, Any]:
    metadata_raw = row.get("metadata_json") or "{}"
    try:
        metadata = json.loads(metadata_raw)
    except json.JSONDecodeError:
        metadata = {}
    return {
        "id": int(row["id"]),
        "username": row["username"],
        "kind": row["kind"],
        "document_slug": row["document_slug"],
        "document_version": row["document_version"],
        "acknowledgement_text": row["acknowledgement_text"],
        "method": row["method"],
        "metadata": metadata if isinstance(metadata, dict) else {},
        "created_at": row["created_at"],
    }
