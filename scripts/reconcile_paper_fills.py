#!/usr/bin/env python3
"""Reconcile KIS paper fills that were missed after polling timeouts."""
from __future__ import annotations

import argparse
import json
import os
import sys
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

from app.brokers.kis.kis_client import KisClient  # noqa: E402
from app.common.enums import OrderStatus, OrderType, Side  # noqa: E402
from app.config.settings import resolve_settings  # noqa: E402
from app.database.repositories import Repository  # noqa: E402
from scripts.kis_paper_transaction_soak import _guard_paper  # noqa: E402


@dataclass(frozen=True)
class ReconciledFill:
    symbol: str
    side: str
    order_type: str
    quantity: int
    filled_quantity: int
    order_log_id: int
    execution_log_id: int


def _order_key(order_id: Any) -> str:
    text = str(order_id or "").strip()
    return text.lstrip("0") or text


def _as_int(value: Any) -> int:
    return int(float(str(value or "0").replace(",", "") or 0))


def _as_float(value: Any) -> float:
    return float(str(value or "0").replace(",", "") or 0.0)


def _side_from_code(code: Any) -> str:
    return Side.SELL.value if str(code or "").strip() == "01" else Side.BUY.value


def _order_type_from_row(row: dict[str, Any]) -> str:
    price = _as_float(row.get("ord_unpr"))
    return OrderType.MARKET.value if price == 0 else OrderType.LIMIT.value


def _existing_order_keys(repo: Repository, limit: int) -> set[str]:
    return {
        _order_key(row.get("kis_order_id"))
        for row in repo.list_order_logs(limit=limit)
        if row.get("kis_order_id")
    }


def _candidate_rows(
    rows: list[dict[str, Any]],
    *,
    symbols: set[str],
    existing_keys: set[str],
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for row in rows:
        symbol = str(row.get("pdno") or "").strip()
        order_key = _order_key(row.get("odno"))
        if symbols and symbol not in symbols:
            continue
        if not order_key or order_key in existing_keys:
            continue
        if _as_int(row.get("tot_ccld_qty")) <= 0:
            continue
        if str(row.get("cncl_yn") or "").upper() == "Y":
            continue
        candidates.append(row)
    return candidates


def reconcile(
    repo: Repository,
    rows: list[dict[str, Any]],
    *,
    symbols: set[str],
    existing_limit: int,
) -> list[ReconciledFill]:
    existing_keys = _existing_order_keys(repo, limit=existing_limit)
    reconciled: list[ReconciledFill] = []
    for row in _candidate_rows(rows, symbols=symbols, existing_keys=existing_keys):
        symbol = str(row.get("pdno") or "").strip()
        side = _side_from_code(row.get("sll_buy_dvsn_cd"))
        order_type = _order_type_from_row(row)
        quantity = _as_int(row.get("ord_qty"))
        filled_quantity = _as_int(row.get("tot_ccld_qty"))
        filled_price = _as_float(row.get("avg_prvs"))
        order_log_id = repo.create_order_log(
            condition_id=None,
            symbol=symbol,
            side=side,
            order_type=order_type,
            order_price=filled_price,
            current_price=filled_price,
            quantity=quantity or filled_quantity,
            kis_order_id=str(row.get("odno") or ""),
            order_status=OrderStatus.FILLED.value,
            fallback_to_market=False,
            error_message="reconciled from KIS today-orders after polling timeout",
        )
        execution_log_id = repo.create_execution_log(
            order_log_id=order_log_id,
            symbol=symbol,
            filled_price=filled_price,
            filled_quantity=filled_quantity,
            raw_status="reconciled from KIS today-orders",
        )
        existing_keys.add(_order_key(row.get("odno")))
        reconciled.append(
            ReconciledFill(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity or filled_quantity,
                filled_quantity=filled_quantity,
                order_log_id=order_log_id,
                execution_log_id=execution_log_id,
            )
        )
    return reconciled


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Reconcile missed KIS paper fills into local logs")
    parser.add_argument("--symbols", nargs="*", required=True)
    parser.add_argument("--existing-limit", type=int, default=500)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    settings = resolve_settings("paper")
    _guard_paper(settings)
    client = KisClient(settings)
    repo = Repository(settings.db_path)
    rows = client.get_today_orders(suppress_errors=False)
    reconciled = reconcile(
        repo,
        rows,
        symbols={str(symbol).strip() for symbol in args.symbols if str(symbol).strip()},
        existing_limit=args.existing_limit,
    )
    output = {
        "ok": True,
        "env": settings.kis_env,
        "paper_endpoint": "openapivts" in settings.kis_base_url,
        "requested_symbols": args.symbols,
        "reconciled_count": len(reconciled),
        "reconciled": [asdict(item) for item in reconciled],
    }
    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
