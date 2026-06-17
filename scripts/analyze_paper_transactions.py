#!/usr/bin/env python3
"""Redacted paper transaction analysis for reuse after market-hour soaks."""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")
os.environ["KIS_ENV"] = "paper"

from app.brokers.kis.kis_client import KisClient  # noqa: E402
from app.config.settings import resolve_settings  # noqa: E402
from app.database.repositories import Repository  # noqa: E402
from app.database.sqlite_db import get_connection  # noqa: E402


def _count(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    return dict(Counter(str(row.get(key) or "unknown") for row in rows))


def summarize_db(repo: Repository, limit: int) -> dict[str, Any]:
    orders = repo.list_order_logs(limit=limit)
    with get_connection(repo.db_path) as conn:
        executions = [
            dict(row)
            for row in conn.execute(
                """
                SELECT el.symbol, ol.side, el.filled_quantity, el.filled_price, el.filled_at
                FROM execution_logs el
                JOIN order_logs ol ON ol.id = el.order_log_id
                ORDER BY el.id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        ]
    filled_quantity_by_symbol: Counter[str] = Counter()
    cashflow_by_side: Counter[str] = Counter()
    for row in executions:
        symbol = str(row.get("symbol") or "unknown")
        qty = int(row.get("filled_quantity") or 0)
        price = float(row.get("filled_price") or 0.0)
        side = str(row.get("side") or "unknown")
        filled_quantity_by_symbol[symbol] += qty
        cashflow_by_side[side] += int(round(qty * price))
    return {
        "order_rows": len(orders),
        "execution_rows": len(executions),
        "orders_by_status": _count(orders, "order_status"),
        "orders_by_symbol": _count(orders, "symbol"),
        "orders_by_side": _count(orders, "side"),
        "orders_by_type": _count(orders, "order_type"),
        "filled_quantity_by_symbol": dict(filled_quantity_by_symbol),
        "notional_by_side_rounded": dict(cashflow_by_side),
    }


def _safe_error(error: Exception) -> str:
    return f"{type(error).__name__}: {str(error)[:240]}"


def _get_today_orders_with_retry(
    client: KisClient,
    *,
    retries: int,
    retry_sleep: float,
) -> tuple[list[dict[str, Any]], list[str]]:
    warnings: list[str] = []
    attempts = max(retries, 0) + 1
    for attempt in range(1, attempts + 1):
        try:
            return client.get_today_orders(suppress_errors=False), warnings
        except Exception as exc:  # noqa: BLE001 - keep live KIS diagnostics redacted.
            warnings.append(f"attempt {attempt}/{attempts}: {_safe_error(exc)}")
            if attempt < attempts:
                time.sleep(max(retry_sleep, 0.0))
    return [], warnings


def summarize_kis(
    client: KisClient,
    *,
    retries: int = 2,
    retry_sleep: float = 1.0,
) -> dict[str, Any]:
    rows, warnings = _get_today_orders_with_retry(
        client,
        retries=retries,
        retry_sleep=retry_sleep,
    )
    available = bool(rows) or not warnings
    open_like = [
        row
        for row in rows
        if str(row.get("status") or "").upper() in {"PENDING", "NEW", "PARTIAL"}
    ]
    filled_rows = [
        row
        for row in rows
        if int(str(row.get("tot_ccld_qty") or "0").replace(",", "") or 0) > 0
    ]
    return {
        "available": available,
        "today_order_rows": len(rows),
        "open_like_count": len(open_like),
        "filled_row_count": len(filled_rows),
        "rows_by_symbol": _count(rows, "pdno"),
        "rows_by_side_code": _count(rows, "sll_buy_dvsn_cd"),
        "canceled_rows": sum(1 for row in rows if str(row.get("cncl_yn") or "").upper() == "Y"),
        "warnings": warnings,
    }


def summarize_ui() -> dict[str, Any]:
    from app.services import backend

    return {
        "holdings_rows": int(len(backend.holdings_df())),
        "recent_fills_rows": int(len(backend.recent_fills(limit=20))),
        "order_log_rows": int(len(backend.list_order_logs(limit=50))),
        "kis_today_orders_rows": int(len(backend.kis_today_orders())),
    }


def build_summary(
    limit: int = 200,
    include_kis: bool = True,
    *,
    kis_retries: int = 2,
    kis_retry_sleep: float = 1.0,
) -> dict[str, Any]:
    settings = resolve_settings("paper")
    repo = Repository(settings.db_path)
    summary: dict[str, Any] = {
        "env": settings.kis_env,
        "paper_endpoint": "openapivts" in settings.kis_base_url,
        "db": summarize_db(repo, limit),
        "ui": summarize_ui(),
    }
    if include_kis:
        summary["kis"] = summarize_kis(
            KisClient(settings),
            retries=kis_retries,
            retry_sleep=kis_retry_sleep,
        )
    kis_available = summary.get("kis", {}).get("available") if include_kis else None
    summary["checks"] = {
        "paper_only": summary["env"] == "paper" and summary["paper_endpoint"],
        "ui_reads_order_logs": summary["ui"]["order_log_rows"] >= summary["db"]["order_rows"],
        "ui_reads_recent_fills": summary["ui"]["recent_fills_rows"] <= summary["db"]["execution_rows"],
        "kis_available": kis_available,
        "no_open_like": (
            summary.get("kis", {}).get("open_like_count", 0) == 0
            if include_kis and kis_available
            else None
        ),
    }
    return summary


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze paper transaction soak state")
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument("--no-kis", action="store_true", help="Skip live KIS today-orders read")
    parser.add_argument("--kis-retries", type=int, default=2)
    parser.add_argument("--kis-retry-sleep", type=float, default=1.0)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    summary = build_summary(
        limit=args.limit,
        include_kis=not args.no_kis,
        kis_retries=args.kis_retries,
        kis_retry_sleep=args.kis_retry_sleep,
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    checks = summary.get("checks", {})
    required = [
        checks.get("paper_only") is True,
        checks.get("ui_reads_order_logs") is True,
        checks.get("ui_reads_recent_fills") is True,
        checks.get("kis_available") in (True, None),
        checks.get("no_open_like") in (True, None),
    ]
    return 0 if all(required) else 1


if __name__ == "__main__":
    raise SystemExit(main())
