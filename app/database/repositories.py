from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from typing import Any
from uuid import uuid4

from app.database.sqlite_db import get_connection
from app.services import flags


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
        user_id: str | None = None,
    ) -> int:
        with get_connection(self.db_path) as conn:
            if flags.multi_tenant_enabled() and user_id is not None:
                cur = conn.execute(
                    '''
                    INSERT INTO trade_conditions(
                        user_id, symbol, side, target_price, quantity, order_type,
                        allow_market_fallback, auto_enabled, created_by,
                        rationale, risk_note
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        user_id,
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
            else:
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

    def list_active_conditions(self, *, user_id: str | None = None) -> list[dict[str, Any]]:
        if flags.multi_tenant_enabled() and user_id is not None:
            sql = "SELECT * FROM trade_conditions WHERE status = 'ACTIVE' AND user_id = ? ORDER BY id"
            params: list[Any] = [user_id]
        else:
            sql = "SELECT * FROM trade_conditions WHERE status = 'ACTIVE' ORDER BY id"
            params = []
        with get_connection(self.db_path) as conn:
            return [dict(row) for row in conn.execute(sql, params).fetchall()]

    def list_conditions(self, *, user_id: str | None = None) -> list[dict[str, Any]]:
        if flags.multi_tenant_enabled() and user_id is not None:
            sql = "SELECT * FROM trade_conditions WHERE user_id = ? ORDER BY id DESC"
            params: list[Any] = [user_id]
        else:
            sql = "SELECT * FROM trade_conditions ORDER BY id DESC"
            params = []
        with get_connection(self.db_path) as conn:
            return [dict(row) for row in conn.execute(sql, params).fetchall()]

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
        user_id: str | None = None,
    ) -> int:
        with get_connection(self.db_path) as conn:
            if flags.multi_tenant_enabled() and user_id is not None:
                cur = conn.execute(
                    '''
                    INSERT INTO order_logs(
                        user_id, condition_id, symbol, side, order_type, order_price,
                        current_price, quantity, kis_order_id, order_status,
                        fallback_to_market, error_message
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        user_id,
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
            else:
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
        user_id: str | None = None,
    ) -> int:
        with get_connection(self.db_path) as conn:
            if flags.multi_tenant_enabled() and user_id is not None:
                cur = conn.execute(
                    '''
                    INSERT INTO execution_logs(
                        user_id, order_log_id, symbol, filled_price, filled_quantity, raw_status
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''',
                    (user_id, order_log_id, symbol, filled_price, filled_quantity, raw_status),
                )
            else:
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

    def list_order_logs(self, limit: int = 100, *, user_id: str | None = None) -> list[dict[str, Any]]:
        scope = flags.multi_tenant_enabled() and user_id is not None
        if scope:
            sql = '''
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
                WHERE ol.user_id = ?
                ORDER BY ol.id DESC LIMIT ?
            '''
            params: list[Any] = [user_id, limit]
        else:
            sql = '''
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
            '''
            params = [limit]
        with get_connection(self.db_path) as conn:
            return [dict(row) for row in conn.execute(sql, params).fetchall()]

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

    def today_order_amount(self, *, user_id: str | None = None) -> float:
        if flags.multi_tenant_enabled() and user_id is not None:
            sql = '''
                SELECT COALESCE(SUM(COALESCE(order_price, current_price, 0) * quantity), 0) AS amount
                FROM order_logs
                WHERE DATE(created_at, '+9 hours') = DATE('now', '+9 hours')
                  AND order_status IN ('REQUESTED', 'FILLED', 'PENDING')
                  AND user_id = ?
            '''
            params: list[Any] = [user_id]
        else:
            sql = '''
                SELECT COALESCE(SUM(COALESCE(order_price, current_price, 0) * quantity), 0) AS amount
                FROM order_logs
                WHERE DATE(created_at, '+9 hours') = DATE('now', '+9 hours')
                  AND order_status IN ('REQUESTED', 'FILLED', 'PENDING')
            '''
            params = []
        with get_connection(self.db_path) as conn:
            row = conn.execute(sql, params).fetchone()
            return float(row["amount"] or 0.0)

    def today_realized_pnl(self, *, user_id: str | None = None) -> float:
        """오늘 SELL 체결 기준 실현 손익 합계.

        실현 손익 = Σ (매도체결가 − 종목별 평균매입가) × 매도수량
        - SELL 체결만 집계 (BUY 체결은 실현 손익 없음 → 0).
        - 평균매입가: execution_logs 전체 BUY 체결의 가중평균 (포지션 테이블 없음).
        - KST 당일 필터: DATE(filled_at, '+9 hours') = DATE('now', '+9 hours').
        - 체결 내역 없으면 0.0 반환.

        Cost basis: 전체 기간 BUY 체결 가중평균 (average cost basis).
        SELL 체결이 없으면 realized PnL = 0 (매수만인 날 서킷브레이커 오발동 방지).
        """
        if flags.multi_tenant_enabled() and user_id is not None:
            sql = '''
                WITH avg_cost AS (
                    SELECT
                        el.symbol,
                        SUM(el.filled_price * el.filled_quantity) /
                            SUM(el.filled_quantity) AS avg_buy_price
                    FROM execution_logs el
                    JOIN order_logs ol ON el.order_log_id = ol.id
                    WHERE ol.side = 'BUY'
                      AND el.filled_quantity > 0
                      AND ol.user_id = ?
                    GROUP BY el.symbol
                )
                SELECT COALESCE(
                    SUM(
                        (el.filled_price - COALESCE(ac.avg_buy_price, el.filled_price))
                        * el.filled_quantity
                    ), 0
                ) AS realized_pnl
                FROM execution_logs el
                JOIN order_logs ol ON el.order_log_id = ol.id
                LEFT JOIN avg_cost ac ON ac.symbol = el.symbol
                WHERE ol.side = 'SELL'
                  AND el.filled_quantity > 0
                  AND DATE(el.filled_at, '+9 hours') = DATE('now', '+9 hours')
                  AND ol.user_id = ?
            '''
            params: list[Any] = [user_id, user_id]
        else:
            sql = '''
                WITH avg_cost AS (
                    -- 종목별 전체 기간 BUY 체결 가중평균 매입가
                    SELECT
                        el.symbol,
                        SUM(el.filled_price * el.filled_quantity) /
                            SUM(el.filled_quantity) AS avg_buy_price
                    FROM execution_logs el
                    JOIN order_logs ol ON el.order_log_id = ol.id
                    WHERE ol.side = 'BUY'
                      AND el.filled_quantity > 0
                    GROUP BY el.symbol
                )
                SELECT COALESCE(
                    SUM(
                        (el.filled_price - COALESCE(ac.avg_buy_price, el.filled_price))
                        * el.filled_quantity
                    ), 0
                ) AS realized_pnl
                FROM execution_logs el
                JOIN order_logs ol ON el.order_log_id = ol.id
                LEFT JOIN avg_cost ac ON ac.symbol = el.symbol
                WHERE ol.side = 'SELL'
                  AND el.filled_quantity > 0
                  AND DATE(el.filled_at, '+9 hours') = DATE('now', '+9 hours')
            '''
            params = []
        with get_connection(self.db_path) as conn:
            row = conn.execute(sql, params).fetchone()
            return float(row["realized_pnl"] or 0.0)

    def total_realized_pnl(self, *, user_id: str | None = None) -> float:
        """전체 기간 SELL 체결 기준 실현 손익 합계 (누적손익률 분자 사용).

        실현 손익 = Σ (매도체결가 − 종목별 평균매입가) × 매도수량
        평균매입가: 전체 기간 BUY 체결 가중평균 (avg cost basis).
        체결 내역 없으면 0.0 반환.
        today_realized_pnl()과 동일한 로직이나 날짜 필터 없음.
        """
        if flags.multi_tenant_enabled() and user_id is not None:
            sql = '''
                WITH avg_cost AS (
                    SELECT
                        el.symbol,
                        SUM(el.filled_price * el.filled_quantity) /
                            SUM(el.filled_quantity) AS avg_buy_price
                    FROM execution_logs el
                    JOIN order_logs ol ON el.order_log_id = ol.id
                    WHERE ol.side = 'BUY'
                      AND el.filled_quantity > 0
                      AND ol.user_id = ?
                    GROUP BY el.symbol
                )
                SELECT COALESCE(
                    SUM(
                        (el.filled_price - COALESCE(ac.avg_buy_price, el.filled_price))
                        * el.filled_quantity
                    ), 0
                ) AS realized_pnl
                FROM execution_logs el
                JOIN order_logs ol ON el.order_log_id = ol.id
                LEFT JOIN avg_cost ac ON ac.symbol = el.symbol
                WHERE ol.side = 'SELL'
                  AND el.filled_quantity > 0
                  AND ol.user_id = ?
            '''
            params: list[Any] = [user_id, user_id]
        else:
            sql = '''
                WITH avg_cost AS (
                    SELECT
                        el.symbol,
                        SUM(el.filled_price * el.filled_quantity) /
                            SUM(el.filled_quantity) AS avg_buy_price
                    FROM execution_logs el
                    JOIN order_logs ol ON el.order_log_id = ol.id
                    WHERE ol.side = 'BUY'
                      AND el.filled_quantity > 0
                    GROUP BY el.symbol
                )
                SELECT COALESCE(
                    SUM(
                        (el.filled_price - COALESCE(ac.avg_buy_price, el.filled_price))
                        * el.filled_quantity
                    ), 0
                ) AS realized_pnl
                FROM execution_logs el
                JOIN order_logs ol ON el.order_log_id = ol.id
                LEFT JOIN avg_cost ac ON ac.symbol = el.symbol
                WHERE ol.side = 'SELL'
                  AND el.filled_quantity > 0
            '''
            params = []
        with get_connection(self.db_path) as conn:
            row = conn.execute(sql, params).fetchone()
            return float(row["realized_pnl"] or 0.0)

    def total_buy_cost_basis(self, *, user_id: str | None = None) -> float:
        """전체 기간 BUY 체결 원가 합계 (누적손익률 분모 사용).

        투자 원금 = Σ (매수체결가 × 매수수량) for all BUY fills ever.
        체결 내역 없으면 0.0 반환.
        """
        if flags.multi_tenant_enabled() and user_id is not None:
            sql = '''
                SELECT COALESCE(
                    SUM(el.filled_price * el.filled_quantity), 0
                ) AS total_cost
                FROM execution_logs el
                JOIN order_logs ol ON el.order_log_id = ol.id
                WHERE ol.side = 'BUY'
                  AND el.filled_quantity > 0
                  AND ol.user_id = ?
            '''
            params: list[Any] = [user_id]
        else:
            sql = '''
                SELECT COALESCE(
                    SUM(el.filled_price * el.filled_quantity), 0
                ) AS total_cost
                FROM execution_logs el
                JOIN order_logs ol ON el.order_log_id = ol.id
                WHERE ol.side = 'BUY'
                  AND el.filled_quantity > 0
            '''
            params = []
        with get_connection(self.db_path) as conn:
            row = conn.execute(sql, params).fetchone()
            return float(row["total_cost"] or 0.0)

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

    def _load_json_state(self, key: str, default: Any) -> Any:
        raw = self.get_system_state(key)
        if raw is None:
            return default
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return default

    def _save_json_state(self, key: str, value: Any) -> None:
        self.set_system_state(key, json.dumps(value, ensure_ascii=False, sort_keys=True))

    @staticmethod
    def _dedupe_symbols(symbols: list[str]) -> list[str]:
        result: list[str] = []
        seen: set[str] = set()
        for symbol in symbols:
            normalized = str(symbol).strip().upper()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            result.append(normalized)
        return result

    def list_portfolio_groups(self) -> list[dict[str, Any]]:
        groups = self._load_json_state("portfolio_groups", [])
        if not isinstance(groups, list):
            return []
        return sorted(groups, key=lambda row: (row.get("sort_order", 0), row.get("name", "")))

    def create_portfolio_group(
        self,
        *,
        name: str,
        symbols: list[str],
        description: str | None = None,
        color: str = "#3182F6",
        sort_order: int = 0,
    ) -> dict[str, Any]:
        groups = self.list_portfolio_groups()
        now = datetime.utcnow().isoformat(timespec="seconds")
        group = {
            "group_id": f"pg_{uuid4().hex[:12]}",
            "name": name.strip(),
            "description": description or "",
            "color": color,
            "sort_order": int(sort_order),
            "symbols": self._dedupe_symbols(symbols),
            "created_at": now,
            "updated_at": now,
        }
        groups.append(group)
        self._save_json_state("portfolio_groups", groups)
        return group

    def update_portfolio_group(
        self,
        group_id: str,
        *,
        name: str | None = None,
        symbols: list[str] | None = None,
        description: str | None = None,
        color: str | None = None,
        sort_order: int | None = None,
    ) -> dict[str, Any] | None:
        groups = self.list_portfolio_groups()
        updated: dict[str, Any] | None = None
        for group in groups:
            if group.get("group_id") != group_id:
                continue
            if name is not None:
                group["name"] = name.strip()
            if symbols is not None:
                group["symbols"] = self._dedupe_symbols(symbols)
            if description is not None:
                group["description"] = description
            if color is not None:
                group["color"] = color
            if sort_order is not None:
                group["sort_order"] = int(sort_order)
            group["updated_at"] = datetime.utcnow().isoformat(timespec="seconds")
            updated = group
            break
        if updated is None:
            return None
        self._save_json_state("portfolio_groups", groups)
        return updated

    def delete_portfolio_group(self, group_id: str) -> bool:
        groups = self.list_portfolio_groups()
        next_groups = [group for group in groups if group.get("group_id") != group_id]
        if len(next_groups) == len(groups):
            return False
        self._save_json_state("portfolio_groups", next_groups)
        return True

    def list_portfolio_symbol_aliases(self) -> list[dict[str, Any]]:
        aliases = self._load_json_state("portfolio_symbol_aliases", {})
        if not isinstance(aliases, dict):
            return []
        return sorted(aliases.values(), key=lambda row: row.get("symbol", ""))

    def upsert_portfolio_symbol_alias(
        self,
        *,
        symbol: str,
        name: str,
        asset_class: str | None = None,
        region: str | None = None,
        sector: str | None = None,
        strategy: str | None = None,
        risk_bucket: str | None = None,
    ) -> dict[str, Any]:
        aliases = self._load_json_state("portfolio_symbol_aliases", {})
        if not isinstance(aliases, dict):
            aliases = {}
        normalized = symbol.strip().upper()
        row = {
            "symbol": normalized,
            "name": name.strip(),
            "asset_class": asset_class,
            "region": region,
            "sector": sector,
            "strategy": strategy,
            "risk_bucket": risk_bucket,
            "updated_at": datetime.utcnow().isoformat(timespec="seconds"),
        }
        aliases[normalized] = row
        self._save_json_state("portfolio_symbol_aliases", aliases)
        return row
    # ---- price alerts ----
    def add_price_alert(self, symbol: str, target_price: float, direction: str, *, user_id: str | None = None) -> int:
        with get_connection(self.db_path) as conn:
            if flags.multi_tenant_enabled() and user_id is not None:
                cur = conn.execute(
                    'INSERT INTO price_alerts(user_id, symbol, target_price, direction) VALUES(?,?,?,?)',
                    (user_id, symbol, target_price, direction.upper()),
                )
            else:
                cur = conn.execute(
                    'INSERT INTO price_alerts(symbol, target_price, direction) VALUES(?,?,?)',
                    (symbol, target_price, direction.upper()),
                )
            return cur.lastrowid

    def list_active_alerts(self, *, user_id: str | None = None) -> list:
        if flags.multi_tenant_enabled() and user_id is not None:
            sql = 'SELECT * FROM price_alerts WHERE active=1 AND user_id=? ORDER BY id'
            params: list[Any] = [user_id]
        else:
            sql = 'SELECT * FROM price_alerts WHERE active=1 ORDER BY id'
            params = []
        with get_connection(self.db_path) as conn:
            return [dict(r) for r in conn.execute(sql, params).fetchall()]

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
        user_id: str | None = None,
    ) -> int:
        with get_connection(self.db_path) as conn:
            if flags.multi_tenant_enabled() and user_id is not None:
                cur = conn.execute(
                    """INSERT INTO trade_journal
                        (user_id, order_log_id, symbol, side, entry_reason, exit_reason,
                         grade, lesson, plan_followed, emotion_flag)
                        VALUES(?,?,?,?,?,?,?,?,?,?)""",
                    (user_id, order_log_id, symbol, side, entry_reason, exit_reason,
                     grade, lesson, int(plan_followed), int(emotion_flag)),
                )
            else:
                cur = conn.execute(
                    """INSERT INTO trade_journal
                        (order_log_id, symbol, side, entry_reason, exit_reason,
                         grade, lesson, plan_followed, emotion_flag)
                        VALUES(?,?,?,?,?,?,?,?,?)""",
                    (order_log_id, symbol, side, entry_reason, exit_reason,
                     grade, lesson, int(plan_followed), int(emotion_flag)),
                )
            return cur.lastrowid

    def list_journal_entries(self, limit: int = 100, *, user_id: str | None = None) -> list:
        if flags.multi_tenant_enabled() and user_id is not None:
            sql = "SELECT * FROM trade_journal WHERE user_id=? ORDER BY created_at DESC LIMIT ?"
            params: list[Any] = [user_id, limit]
        else:
            sql = "SELECT * FROM trade_journal ORDER BY created_at DESC LIMIT ?"
            params = [limit]
        with get_connection(self.db_path) as conn:
            return [dict(r) for r in conn.execute(sql, params).fetchall()]
