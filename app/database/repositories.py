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

    def atomic_claim_condition(self, condition_id: int) -> bool:
        """Atomic Compare-And-Swap: ACTIVE → PROCESSING.

        Returns True only if this caller claimed the condition (rowcount == 1).
        Returns False if another caller already claimed or the condition is not ACTIVE.
        SQLite serialises write transactions so exactly one concurrent caller wins.
        """
        with get_connection(self.db_path) as conn:
            cur = conn.execute(
                """
                UPDATE trade_conditions
                SET status = 'PROCESSING', updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND status = 'ACTIVE'
                """,
                (condition_id,),
            )
            return cur.rowcount == 1

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
                    '''
                    SELECT
                        ol.*,
                        ex.filled_price,
                        ex.filled_quantity,
                        ex.filled_at
                    FROM order_logs ol
                    LEFT JOIN (
                        SELECT
                            order_log_id,
                            CASE
                                WHEN SUM(COALESCE(filled_quantity, 0)) > 0
                                THEN SUM(COALESCE(filled_price, 0) * COALESCE(filled_quantity, 0))
                                     / SUM(COALESCE(filled_quantity, 0))
                                ELSE MAX(filled_price)
                            END AS filled_price,
                            SUM(COALESCE(filled_quantity, 0)) AS filled_quantity,
                            MAX(filled_at) AS filled_at
                        FROM execution_logs
                        GROUP BY order_log_id
                    ) ex ON ex.order_log_id = ol.id
                    ORDER BY ol.id DESC LIMIT ?
                    ''',
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

    def update_global_risk_limit(
        self,
        *,
        max_order_amount: float | None = None,
        max_daily_amount: float | None = None,
    ) -> None:
        fields, params = [], []
        if max_order_amount is not None:
            fields.append("max_order_amount = ?")
            params.append(max_order_amount)
        if max_daily_amount is not None:
            fields.append("max_daily_amount = ?")
            params.append(max_daily_amount)
        if not fields:
            return
        params.append("GLOBAL")
        with get_connection(self.db_path) as conn:
            conn.execute(
                f"UPDATE risk_limits SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE scope = ?",
                params,
            )

    def today_order_amount(self) -> float:
        with get_connection(self.db_path) as conn:
            row = conn.execute(
                '''
                SELECT COALESCE(SUM(COALESCE(order_price, current_price, 0) * quantity), 0) AS amount
                FROM order_logs
                WHERE DATE(created_at, '+9 hours') = DATE('now', '+9 hours')
                  AND order_status IN ('REQUESTED', 'FILLED', 'PENDING')
                '''
            ).fetchone()
            return float(row["amount"] or 0.0)

    def today_realized_pnl(self) -> float:
        """오늘 체결된 실현 현금흐름 합계.

        SELL: 양수(현금 유입), BUY: 음수(현금 유출).
        execution_logs 와 order_logs 를 조인해 당일 체결 행만 집계한다.
        체결 내역이 없으면 0.0 을 반환한다.
        """
        with get_connection(self.db_path) as conn:
            row = conn.execute(
                '''
                SELECT COALESCE(
                    SUM(
                        CASE WHEN ol.side = 'SELL'
                             THEN el.filled_price * el.filled_quantity
                             ELSE -el.filled_price * el.filled_quantity
                        END
                    ), 0
                ) AS net_pnl
                FROM execution_logs el
                JOIN order_logs ol ON el.order_log_id = ol.id
                WHERE DATE(el.filled_at) = DATE('now')
                '''
            ).fetchone()
            return float(row["net_pnl"] or 0.0)

    def increment_consecutive_failures(self) -> None:
        """연속 주문 실패 카운터를 1 증가시킨다."""
        current = self.get_system_state("consecutive_order_failures", "0")
        try:
            count = int(current)
        except (ValueError, TypeError):
            count = 0
        self.set_system_state("consecutive_order_failures", str(count + 1))

    def reset_consecutive_failures(self) -> None:
        """연속 주문 실패 카운터를 0으로 초기화한다."""
        self.set_system_state("consecutive_order_failures", "0")
    # ---- price alerts ----
    def add_price_alert(self, symbol: str, target_price: float, direction: str) -> int:
        with get_connection(self.db_path) as conn:
            cur = conn.execute(
                'INSERT INTO price_alerts(symbol, target_price, direction) VALUES(?,?,?)',
                (symbol, target_price, direction.upper()),
            )
            return cur.lastrowid

    def list_active_alerts(self) -> list:
        with get_connection(self.db_path) as conn:
            return [dict(r) for r in conn.execute(
                'SELECT * FROM price_alerts WHERE active=1 ORDER BY id'
            ).fetchall()]

    def trigger_alert(self, alert_id: int) -> None:
        with get_connection(self.db_path) as conn:
            conn.execute(
                "UPDATE price_alerts SET active=0, triggered_at=CURRENT_TIMESTAMP WHERE id=?",
                (alert_id,),
            )
    # ---- trade journal ----
    def add_journal_entry(
        self, symbol: str, side: str, *,
        order_log_id: int | None = None,
        entry_reason: str = "",
        exit_reason: str = "",
        grade: str | None = None,
        lesson: str = "",
        plan_followed: bool = True,
        emotion_flag: bool = False,
    ) -> int:
        with get_connection(self.db_path) as conn:
            cur = conn.execute(
                """INSERT INTO trade_journal
                    (order_log_id, symbol, side, entry_reason, exit_reason,
                     grade, lesson, plan_followed, emotion_flag)
                    VALUES(?,?,?,?,?,?,?,?,?)""",
                (order_log_id, symbol, side, entry_reason, exit_reason,
                 grade, lesson, int(plan_followed), int(emotion_flag)),
            )
            return cur.lastrowid

    def list_journal_entries(self, limit: int = 100) -> list:
        with get_connection(self.db_path) as conn:
            return [dict(r) for r in conn.execute(
                "SELECT * FROM trade_journal ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()]
