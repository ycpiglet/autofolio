#!/usr/bin/env python3
"""Buy and hold a small KIS paper basket for UI holdings verification.

This is intentionally paper-only. Unlike the transaction soak, it does not sell
the filled shares back; the point is to make the paper holdings screen visibly
change so UI sync can be verified against persistent positions.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import asdict, dataclass
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

from app.brokers.base import OrderRequest  # noqa: E402
from app.brokers.kis.kis_client import KisClient  # noqa: E402
from app.common.enums import OrderStatus, OrderType, Side  # noqa: E402
from app.config.settings import resolve_settings  # noqa: E402
from app.database.repositories import Repository  # noqa: E402
from scripts.kis_paper_transaction_soak import _guard_paper, _poll_status, _record_order  # noqa: E402

DEFAULT_SYMBOLS = (
    "035420",  # NAVER
    "035720",  # Kakao
    "005380",  # Hyundai Motor
    "068270",  # Celltrion
    "105560",  # KB Financial
    "055550",  # Shinhan Financial
    "102110",  # TIGER 200 ETF
    "114260",  # KODEX bond ETF
)


@dataclass(frozen=True)
class BasketRecord:
    symbol: str
    requested_quantity: int
    status: str
    filled_quantity: int
    order_log_id: int | None = None
    execution_log_id: int | None = None
    error: str | None = None


def _safe_error(error: Exception) -> str:
    return f"{type(error).__name__}: {str(error)[:240]}"


def _buy_one(
    client: KisClient,
    repo: Repository,
    *,
    symbol: str,
    qty: int,
    attempts: int,
    sleep_sec: float,
) -> BasketRecord:
    current = client.get_current_price(symbol).price
    req = OrderRequest(symbol=symbol, side=Side.BUY, order_type=OrderType.MARKET, quantity=qty)
    placed = client.place_order(req)
    observed = _poll_status(client, placed.broker_order_id, attempts=attempts, sleep_sec=sleep_sec)
    recorded = _record_order(
        repo,
        request=req,
        placed=placed,
        observed=observed,
        expected=OrderStatus.FILLED.value,
        current_price=current,
        note="paper hold basket market buy",
    )
    return BasketRecord(
        symbol=symbol,
        requested_quantity=qty,
        status=recorded.status,
        filled_quantity=recorded.filled_quantity,
        order_log_id=recorded.order_log_id,
        execution_log_id=recorded.execution_log_id,
    )


def _ui_holdings_summary() -> dict[str, Any]:
    from app.services import backend

    holdings = backend.holdings_df()
    symbols = sorted(str(value) for value in holdings.get("티커", [])) if not holdings.empty else []
    return {
        "holdings_rows": int(len(holdings)),
        "holding_symbols": symbols,
        "recent_fills_rows": int(len(backend.recent_fills(limit=50))),
        "order_log_rows": int(len(backend.list_order_logs(limit=100))),
        "kis_today_order_rows": int(len(backend.kis_today_orders())),
    }


def _open_like_count(client: KisClient) -> int:
    rows = client.get_today_orders()
    return sum(
        1
        for row in rows
        if str(row.get("status") or "").upper() in {"PENDING", "NEW", "PARTIAL"}
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Buy and hold a KIS paper basket")
    parser.add_argument("--symbols", nargs="*", default=list(DEFAULT_SYMBOLS))
    parser.add_argument("--qty", type=int, default=1)
    parser.add_argument("--attempts", type=int, default=10)
    parser.add_argument("--sleep", type=float, default=1.0)
    parser.add_argument("--pause-between", type=float, default=0.4)
    parser.add_argument("--min-filled", type=int, default=5)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.qty != 1:
        raise SystemExit("paper hold basket keeps qty fixed at 1")
    settings = resolve_settings("paper")
    _guard_paper(settings)
    client = KisClient(settings)
    repo = Repository(settings.db_path)
    before = _ui_holdings_summary()

    records: list[BasketRecord] = []
    seen: set[str] = set()
    for symbol in args.symbols:
        code = str(symbol).strip()
        if not code or code in seen:
            continue
        seen.add(code)
        try:
            records.append(
                _buy_one(
                    client,
                    repo,
                    symbol=code,
                    qty=args.qty,
                    attempts=args.attempts,
                    sleep_sec=args.sleep,
                )
            )
        except Exception as exc:  # noqa: BLE001 - emit redacted per-symbol diagnostics.
            records.append(
                BasketRecord(
                    symbol=code,
                    requested_quantity=args.qty,
                    status="ERROR",
                    filled_quantity=0,
                    error=_safe_error(exc),
                )
            )
        time.sleep(max(args.pause_between, 0.0))

    after = _ui_holdings_summary()
    open_like = _open_like_count(client)
    filled_symbols = [record.symbol for record in records if record.status == OrderStatus.FILLED.value]
    output = {
        "ok": len(filled_symbols) >= args.min_filled and open_like == 0,
        "env": settings.kis_env,
        "paper_endpoint": "openapivts" in settings.kis_base_url,
        "requested_symbols": list(seen),
        "filled_symbols": filled_symbols,
        "records": [asdict(record) for record in records],
        "before": before,
        "after": after,
        "post_open_like_count": open_like,
        "checks": {
            "paper_only": settings.kis_env == "paper" and "openapivts" in settings.kis_base_url,
            "min_filled": len(filled_symbols) >= args.min_filled,
            "holdings_increased_or_visible": after["holdings_rows"] >= before["holdings_rows"],
            "no_open_like": open_like == 0,
        },
    }
    print(json.dumps(output, ensure_ascii=False))
    return 0 if output["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
