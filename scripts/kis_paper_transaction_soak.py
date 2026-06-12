#!/usr/bin/env python3
"""KIS paper transaction soak with UI/backend sync verification.

This script is intentionally paper-only. It creates a tiny transaction set:

- market BUY then market SELL for one liquid symbol, to exercise filled orders;
- below-market LIMIT BUY then cancel for one or more symbols, to exercise
  pending/canceled orders;
- SQLite order/execution log writes for UI sync verification.

No prod trading path is allowed.
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

from app.brokers.base import OrderRequest, OrderResult  # noqa: E402
from app.brokers.kis.kis_client import KisClient  # noqa: E402
from app.common.enums import OrderStatus, OrderType, Side  # noqa: E402
from app.config.settings import resolve_settings  # noqa: E402
from app.database.repositories import Repository  # noqa: E402


@dataclass
class RecordedOrder:
    symbol: str
    side: str
    order_type: str
    expected: str
    status: str
    filled_quantity: int
    order_log_id: int
    execution_log_id: int | None = None
    broker_order_id_tail: str | None = None
    note: str = ""


def _tick_size(price: float) -> int:
    if price < 2_000:
        return 1
    if price < 5_000:
        return 5
    if price < 20_000:
        return 10
    if price < 50_000:
        return 50
    if price < 200_000:
        return 100
    if price < 500_000:
        return 500
    return 1_000


def _below_market_limit_price(current_price: float) -> int:
    tick = _tick_size(current_price)
    target = int(current_price * 0.9)
    return max(tick, (target // tick) * tick)


def _guard_paper(settings: Any) -> None:
    if settings.kis_env != "paper":
        raise RuntimeError(f"paper-only script resolved env={settings.kis_env}")
    if "openapivts" not in settings.kis_base_url:
        raise RuntimeError("paper-only script resolved non-paper KIS base URL")
    if not settings.kis_app_key or not settings.kis_account_no:
        raise RuntimeError("KIS paper credentials are not configured")


def _poll_status(
    client: KisClient,
    broker_order_id: str,
    *,
    attempts: int,
    sleep_sec: float,
) -> OrderResult:
    last: OrderResult | None = None
    for _ in range(max(attempts, 1)):
        last = client.get_order_status(broker_order_id)
        if last.status in {OrderStatus.FILLED, OrderStatus.CANCELED, OrderStatus.FAILED}:
            return last
        time.sleep(max(sleep_sec, 0.0))
    if last is None:
        raise RuntimeError("status polling returned no result")
    return last


def _record_order(
    repo: Repository,
    *,
    request: OrderRequest,
    placed: OrderResult,
    observed: OrderResult,
    expected: str,
    current_price: float | None,
    override_status: OrderStatus | None = None,
    note: str = "",
) -> RecordedOrder:
    status = override_status or observed.status
    order_price = observed.filled_price or request.price or current_price
    order_log_id = repo.create_order_log(
        condition_id=None,
        symbol=request.symbol,
        side=request.side.value,
        order_type=request.order_type.value,
        order_price=order_price,
        current_price=current_price,
        quantity=request.quantity,
        kis_order_id=placed.broker_order_id,
        order_status=status.value,
        fallback_to_market=False,
        error_message=note or observed.message,
    )
    execution_log_id: int | None = None
    if observed.filled_quantity > 0 and observed.filled_price is not None:
        execution_log_id = repo.create_execution_log(
            order_log_id=order_log_id,
            symbol=request.symbol,
            filled_price=observed.filled_price,
            filled_quantity=observed.filled_quantity,
            raw_status=observed.message,
        )
    return RecordedOrder(
        symbol=request.symbol,
        side=request.side.value,
        order_type=request.order_type.value,
        expected=expected,
        status=status.value,
        filled_quantity=observed.filled_quantity,
        order_log_id=order_log_id,
        execution_log_id=execution_log_id,
        broker_order_id_tail=placed.broker_order_id[-4:] if placed.broker_order_id else None,
        note=note,
    )


def _market_round_trip(
    client: KisClient,
    repo: Repository,
    *,
    symbol: str,
    qty: int,
    attempts: int,
    sleep_sec: float,
) -> list[RecordedOrder]:
    current = client.get_current_price(symbol).price
    buy_req = OrderRequest(symbol=symbol, side=Side.BUY, order_type=OrderType.MARKET, quantity=qty)
    buy_placed = client.place_order(buy_req)
    buy_status = _poll_status(client, buy_placed.broker_order_id, attempts=attempts, sleep_sec=sleep_sec)
    records = [
        _record_order(
            repo,
            request=buy_req,
            placed=buy_placed,
            observed=buy_status,
            expected="FILLED",
            current_price=current,
            note="paper transaction soak market buy",
        )
    ]
    if buy_status.status != OrderStatus.FILLED or buy_status.filled_quantity <= 0:
        return records

    sell_req = OrderRequest(
        symbol=symbol,
        side=Side.SELL,
        order_type=OrderType.MARKET,
        quantity=buy_status.filled_quantity,
    )
    sell_placed = client.place_order(sell_req)
    sell_status = _poll_status(client, sell_placed.broker_order_id, attempts=attempts, sleep_sec=sleep_sec)
    records.append(
        _record_order(
            repo,
            request=sell_req,
            placed=sell_placed,
            observed=sell_status,
            expected="FILLED",
            current_price=client.get_current_price(symbol).price,
            note="paper transaction soak market sell",
        )
    )
    return records


def _limit_cancel(
    client: KisClient,
    repo: Repository,
    *,
    symbol: str,
    qty: int,
    attempts: int,
    sleep_sec: float,
) -> RecordedOrder:
    current = client.get_current_price(symbol).price
    limit_price = _below_market_limit_price(current)
    req = OrderRequest(
        symbol=symbol,
        side=Side.BUY,
        order_type=OrderType.LIMIT,
        quantity=qty,
        price=float(limit_price),
    )
    placed = client.place_order(req)
    pending = _poll_status(client, placed.broker_order_id, attempts=max(min(attempts, 2), 1), sleep_sec=sleep_sec)
    cancel = client.cancel_order(placed.broker_order_id)
    return _record_order(
        repo,
        request=req,
        placed=placed,
        observed=pending,
        expected="CANCELED",
        current_price=current,
        override_status=cancel.status,
        note="paper transaction soak limit cancel",
    )


def _ui_sync_summary() -> dict[str, Any]:
    from app.ui import backend

    holdings = backend.holdings_df()
    recent = backend.recent_fills(limit=10)
    logs = backend.list_order_logs(limit=20)
    kis_orders = backend.kis_today_orders()
    return {
        "holdings_rows": int(len(holdings)),
        "recent_fills_rows": int(len(recent)),
        "order_log_rows": int(len(logs)),
        "kis_today_order_rows": int(len(kis_orders)),
        "recent_symbols": sorted(str(x) for x in recent.get("종목", [])) if not recent.empty else [],
        "order_log_statuses": logs.get("order_status", []).value_counts().to_dict() if not logs.empty else {},
    }


def _open_like_count(client: KisClient) -> int:
    rows = client.get_today_orders()
    open_like = [
        row
        for row in rows
        if str(row.get("status") or "").upper() in {"PENDING", "NEW", "PARTIAL"}
    ]
    return len(open_like)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="KIS paper transaction soak and UI sync verifier")
    parser.add_argument("--fill-symbol", default="069500")
    parser.add_argument("--unfilled-symbols", nargs="*", default=["005930", "000660"])
    parser.add_argument("--qty", type=int, default=1)
    parser.add_argument("--attempts", type=int, default=8)
    parser.add_argument("--sleep", type=float, default=1.0)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    settings = resolve_settings("paper")
    _guard_paper(settings)
    client = KisClient(settings)
    repo = Repository(settings.db_path)

    before = _ui_sync_summary()
    records: list[RecordedOrder] = []
    records.extend(
        _market_round_trip(
            client,
            repo,
            symbol=args.fill_symbol,
            qty=args.qty,
            attempts=args.attempts,
            sleep_sec=args.sleep,
        )
    )
    for symbol in args.unfilled_symbols:
        records.append(
            _limit_cancel(
                client,
                repo,
                symbol=symbol,
                qty=args.qty,
                attempts=args.attempts,
                sleep_sec=args.sleep,
            )
        )
    after = _ui_sync_summary()
    open_like = _open_like_count(client)
    filled_ok = all(
        r.status == OrderStatus.FILLED.value
        for r in records
        if r.expected == OrderStatus.FILLED.value
    )
    canceled_ok = all(
        r.status == OrderStatus.CANCELED.value
        for r in records
        if r.expected == OrderStatus.CANCELED.value
    )
    sync_ok = after["recent_fills_rows"] >= before["recent_fills_rows"]
    ok = filled_ok and canceled_ok and sync_ok and open_like == 0
    output = {
        "ok": ok,
        "env": settings.kis_env,
        "paper_endpoint": "openapivts" in settings.kis_base_url,
        "fill_symbol": args.fill_symbol,
        "unfilled_symbols": args.unfilled_symbols,
        "records": [asdict(record) for record in records],
        "before": before,
        "after": after,
        "post_open_like_count": open_like,
        "checks": {
            "filled_ok": filled_ok,
            "canceled_ok": canceled_ok,
            "ui_sync_ok": sync_ok,
            "no_open_like": open_like == 0,
        },
    }
    print(json.dumps(output, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
