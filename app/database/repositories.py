from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.database.sqlite_db import get_connection


@dataclass(frozen=True)
class WhitelistSymbol:
    symbol: str
    name: str
    market: str
    role: str
    enabled: bool = True


class Repository:
    def __init__(self, db_path=None):
        self.db_path = db_path

    def add_whitelist_symbol(self, item: WhitelistSymbol) -> None:
        with get_connection(self.db_path) as conn:
            conn.execute(
                '''
                INSERT INTO whitelist_symbols(symbol, name, market, role, enabled)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(symbol) DO UPDATE SET
                    name = excluded.name,
                    market = excluded.market,
                    role = excluded.role,
                    enabled = excluded.enabled,
                    updated_at = CURRENT_TIMESTAMP
                ''',
                (item.symbol, item.name, item.market, item.role, int(item.enabled)),
            )

    def list_whitelist_symbols(self, enabled_only: bool = False) -> list[dict[str, Any]]:
        sql = "SELECT * FROM whitelist_symbols"
        params: list[Any] = []
        if enabled_only:
            sql += " WHERE enabled = 1"
        sql += " ORDER BY symbol"
        with get_connection(self.db_path) as conn:
            return [dict(row) for row in conn.execute(sql, params).fetchall()]

    def get_whitelist_symbol(self, symbol: str) -> dict[str, Any] | None:
        with get_connection(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM whitelist_symbols WHERE symbol = ? AND enabled = 1",
                (symbol,),
            ).fetchone()
            return dict(row) if row else None

    def add_trade_condition(
        self,
        *,
        symbol: str,
        side: str,
        target_price: float,
        quantity: int,
        order_type: str = "LIMIT",
        allow_market_fallback: bool = False,
        auto_enabled: bool = False,
        created_by: str = "USER",
        rationale: str | None = None,
        risk_note: str | None = None,
    ) -> int:
        with get_connection(self.db_path) as conn:
            cur = conn.execute(
                '''
                INSERT INTO trade_conditions(
                    symbol, side, target_price, quantity, order_type,
                    allow_market_fallback, auto_enabled, created_by,
                    rationale, risk_note
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    symbol,
                    side,
                    target_price,
                    quantity,
                    order_type,
                    int(allow_market_fallback),
                    int(auto_enabled),
                    created_by,
                    rationale,
                    risk_note,
                ),
            )
            return int(cur.lastrowid)

    def list_active_conditions(self) -> list[dict[str, Any]]:
        with get_connection(self.db_path) as conn:
            return [
                dict(row)
                for row in conn.execute(
                    '''
                    SELECT * FROM trade_conditions
                    WHERE status = 'ACTIVE'
                    ORDER BY id
                    '''
                ).fetchall()
            ]

    def list_conditions(self) -> list[dict[str, Any]]:
        with get_connection(self.db_path) as conn:
            return [
                dict(row)
                for row in conn.execute(
                    "SELECT * FROM trade_conditions ORDER BY id DESC"
                ).fetchall()
            ]

    def get_condition(self, condition_id: int) -> dict[str, Any] | None:
        with get_connection(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM trade_conditions WHERE id = ?",
                (condition_id,),
            ).fetchone()
            return dict(row) if row else None

    def update_condition_status(self, condition_id: int, status: str) -> None:
        with get_connection(self.db_path) as conn:
            conn.execute(
                '''
                UPDATE trade_conditions
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                ''',
                (status, condition_id),
            )

    def set_condition_cooldown(self, condition_id: int, cooldown_until: datetime) -> None:
        with get_connection(self.db_path) as conn:
            conn.execute(
                '''
                UPDATE trade_conditions
                SET cooldown_until = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                ''',
                (cooldown_until.isoformat(timespec="seconds"), condition_id),
            )

    def create_order_log(
        self,
        *,
        condition_id: int | None,
        symbol: str,
        side: str,
        order_type: str,
        order_price: float | None,
        current_price: float | None,
        quantity: int,
        kis_order_id: str | None,
        order_status: str,
        fallback_to_market: bool = False,
        error_message: str | None = None,
    ) -> int:
        with get_connection(self.db_path) as conn:
            cur = conn.execute(
                '''
                INSERT INTO order_logs(
                    condition_id, symbol, side, order_type, order_price,
                    current_price, quantity, kis_order_id, order_status,
                    fallback_to_market, error_message
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    condition_id,
                    symbol,
                    side,
                    order_type,
                    order_price,
                    current_price,
                    quantity,
                    kis_order_id,
                    order_status,
                    int(fallback_to_market),
                    error_message,
                ),
            )
            return int(cur.lastrowid)

    def update_order_status(self, order_log_id: int, status: str, error_message: str | None = None) -> None:
        with get_connection(self.db_path) as conn:
            conn.execute(
                '''
                UPDATE order_logs
                SET order_status = ?, error_message = COALESCE(?, error_message)
                WHERE id = ?
                ''',
                (status, error_message, order_log_id),
            )

    def create_execution_log(
        self,
        *,
        order_log_id: int,
        symbol: str,
        filled_price: float | None,
        filled_quantity: int | None,
        raw_status: str | None = None,
    ) -> int:
        with get_connection(self.db_path) as conn:
            cur = conn.execute(
                '''
                INSERT INTO execution_logs(
                    order_log_id, symbol, filled_price, filled_quantity, raw_status
                )
                VALUES (?, ?, ?, ?, ?)
                ''',
                (order_log_id, symbol, filled_price, filled_quantity, raw_status),
            )
            return int(cur.lastrowid)

    def list_order_logs(self, limit: int = 100) -> list[dict[str, Any]]:
        with get_connection(self.db_path) as conn:
            return [
                dict(row)
                for row in conn.execute(
                    "SELECT * FROM order_logs ORDER BY id DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            ]

    def get_system_state(self, key: str, default: str | None = None) -> str | None:
        with get_connection(self.db_path) as conn:
            row = conn.execute(
                "SELECT value FROM system_state WHERE key = ?",
                (key,),
            ).fetchone()
            return str(row["value"]) if row else default

    def set_system_state(self, key: str, value: str) -> None:
        with get_connection(self.db_path) as conn:
            conn.execute(
                '''
                INSERT INTO system_state(key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = CURRENT_TIMESTAMP
                ''',
                (key, value),
            )

    def get_global_risk_limit(self) -> dict[str, Any]:
        with get_connection(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM risk_limits WHERE scope = 'GLOBAL' LIMIT 1"
            ).fetchone()
            if not row:
                raise RuntimeError("Global risk limit is not initialized.")
            return dict(row)

    def today_order_amount(self) -> float:
        with get_connection(self.db_path) as conn:
            row = conn.execute(
                '''
                SELECT COALESCE(SUM(COALESCE(order_price, current_price, 0) * quantity), 0) AS amount
                FROM order_logs
                WHERE DATE(created_at) = DATE('now', 'localtime')
                  AND order_status IN ('REQUESTED', 'FILLED', 'PENDING')
                '''
            ).fetchone()
            return float(row["amount"] or 0.0)
