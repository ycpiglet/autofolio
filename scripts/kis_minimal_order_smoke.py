#!/usr/bin/env python3
"""Shared KIS minimal order-path smoke runner.

This module is intentionally small and conservative:

- paper and prod use the same read/order/reconcile logic;
- prod execution requires an explicit flag and same-day paper evidence;
- output is redacted and avoids account, cash amount, token, and full order ids;
- only ordinary domestic KRX cash stock orders are used.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, datetime, time as dt_time
import json
from pathlib import Path
import sys
import time
from typing import Any, Iterable
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")

from app.brokers.base import OrderRequest  # noqa: E402
from app.brokers.kis.kis_client import KisClient  # noqa: E402
from app.common.enums import OrderType, Side  # noqa: E402
from app.config.settings import resolve_settings  # noqa: E402
from scripts.kis_paper_order_smoke import (  # noqa: E402
    _below_market_limit_price,
    _is_open_like_order,
    _mask_account,
)

KST = ZoneInfo("Asia/Seoul")
RUN_DIR = ROOT / ".autofolio" / "kis_smoke"
LATEST_PAPER_PATH = RUN_DIR / "latest_paper.json"
DEFAULT_CANDIDATES: tuple[tuple[str, str], ...] = (
    ("004870", "티웨이홀딩스"),
    ("000040", "KR모터스"),
    ("001520", "동양"),
    ("014160", "대영포장"),
    ("093240", "형지엘리트"),
    ("015260", "에이엔피"),
    ("090080", "평화산업"),
    ("027970", "한국제지"),
    ("001210", "금호전기"),
    ("145270", "케이탑리츠"),
    ("357430", "마스턴프리미어리츠"),
)


class CandidateSelectionError(RuntimeError):
    def __init__(self, checked: list[dict[str, Any]]) -> None:
        super().__init__("no candidate passed minimal smoke readiness")
        self.checked = checked


@dataclass(frozen=True)
class Candidate:
    symbol: str
    name: str


def _now_kst() -> datetime:
    return datetime.now(KST)


def _parse_hhmm(value: str) -> dt_time:
    try:
        hour, minute = value.split(":", 1)
        return dt_time(int(hour), int(minute))
    except Exception as exc:  # noqa: BLE001 - CLI validation.
        raise argparse.ArgumentTypeError(f"expected HH:MM, got {value!r}") from exc


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"expected YYYY-MM-DD, got {value!r}") from exc


def _safe_error(exc: Exception) -> str:
    return f"{type(exc).__name__}: {str(exc)[:180]}"


def _parse_int(value: Any, default: int = 0) -> int:
    try:
        text = str(value if value is not None else "").replace(",", "").strip()
        return int(float(text)) if text else default
    except (TypeError, ValueError):
        return default


def _order_tail(value: Any) -> str:
    raw = str(value or "").strip()
    return f"***{raw[-4:]}" if raw else ""


def _is_regular_session(
    now: datetime,
    *,
    start: dt_time,
    end: dt_time,
    expected_date: date | None,
) -> tuple[bool, str]:
    if expected_date and now.date() != expected_date:
        return False, f"date {now.date().isoformat()} != expected {expected_date.isoformat()}"
    if now.weekday() >= 5:
        return False, "KST date is weekend"
    current = now.time().replace(tzinfo=None)
    if current < start or current > end:
        return False, f"KST time {current.strftime('%H:%M:%S')} outside {start.strftime('%H:%M')}-{end.strftime('%H:%M')}"
    return True, "regular session guard pass"


def _candidate_map() -> dict[str, Candidate]:
    return {symbol: Candidate(symbol, name) for symbol, name in DEFAULT_CANDIDATES}


def _candidate_list(symbol: str | None) -> list[Candidate]:
    mapping = _candidate_map()
    if symbol:
        if symbol not in mapping:
            raise ValueError(f"symbol {symbol} is not in the minimal-smoke whitelist")
        return [mapping[symbol]]
    return list(mapping.values())


def _position_qty(client: KisClient, symbol: str) -> int:
    return sum(int(pos.quantity) for pos in client.get_positions() if str(pos.symbol).strip() == symbol)


def _order_probe(client: KisClient, broker_order_id: str, *, attempts: int, sleep_seconds: float) -> dict[str, Any]:
    last_error = ""
    for attempt in range(1, max(attempts, 1) + 1):
        try:
            rows = client.get_today_orders(suppress_errors=False)
            needle = str(broker_order_id or "").strip()
            normalized = needle.lstrip("0") or needle
            matches = []
            for row in rows:
                odno = str(row.get("odno") or "").strip()
                if odno == needle or (odno.lstrip("0") or odno) == normalized:
                    matches.append(row)
            return {
                "available": True,
                "attempt": attempt,
                "matching_rows": len(matches),
                "open_like_count": sum(1 for row in matches if _is_open_like_order(row)),
                "filled_qty_rows": sum(_parse_int(row.get("tot_ccld_qty")) for row in matches),
                "remaining_qty_rows": sum(_parse_int(row.get("rmn_qty")) for row in matches),
            }
        except Exception as exc:  # noqa: BLE001 - live broker readout must stay redacted.
            last_error = _safe_error(exc)
            if attempt < attempts:
                time.sleep(max(sleep_seconds, 0.0))
    return {"available": False, "error": last_error}


def _poll_order_status(client: KisClient, broker_order_id: str, *, attempts: int, sleep_seconds: float) -> dict[str, Any]:
    last: dict[str, Any] = {
        "status": "UNKNOWN",
        "filled_quantity": 0,
        "filled_price_present": False,
        "message": "",
    }
    for attempt in range(1, max(attempts, 1) + 1):
        try:
            status = client.get_order_status(broker_order_id)
            last = {
                "status": status.status.value,
                "filled_quantity": int(status.filled_quantity or 0),
                "filled_price_present": status.filled_price is not None,
                "message": (status.message or "")[:120],
                "attempt": attempt,
            }
            if status.status.value in {"FILLED", "CANCELED", "FAILED"}:
                return last
        except Exception as exc:  # noqa: BLE001 - keep broker payloads out of output.
            last = {
                "status": "STATUS_ERROR",
                "filled_quantity": 0,
                "filled_price_present": False,
                "message": _safe_error(exc),
                "attempt": attempt,
            }
        if attempt < attempts:
            time.sleep(max(sleep_seconds, 0.0))
    return last


def _choose_candidate(
    client: KisClient,
    *,
    symbol: str | None,
    requested_qty: int,
    max_qty: int,
    max_notional: int,
    min_orderbook_levels: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    checked: list[dict[str, Any]] = []
    for candidate in _candidate_list(symbol):
        rec: dict[str, Any] = {"symbol": candidate.symbol, "name": candidate.name}
        try:
            price = float(client.get_current_price(candidate.symbol).price)
            levels = len((client.get_order_book(candidate.symbol).get("levels") or []))
            buying_power = client.get_buying_power(candidate.symbol, price)
            affordable_qty = int(max_notional // max(price, 1.0))
            planned_qty = min(requested_qty, max_qty, affordable_qty)
            rec.update(
                {
                    "price": price,
                    "orderbook_levels": levels,
                    "planned_qty": planned_qty,
                    "notional_estimate": int(price * max(planned_qty, 0)),
                    "buying_power_ok": int(buying_power.get("max_quantity") or 0) >= planned_qty > 0,
                    "cash_positive": float(buying_power.get("available_cash") or 0) > 0,
                }
            )
            if (
                price > 0
                and levels >= min_orderbook_levels
                and planned_qty > 0
                and price * planned_qty <= max_notional
                and rec["buying_power_ok"]
                and rec["cash_positive"]
            ):
                checked.append(rec.copy())
                return rec, checked
        except Exception as exc:  # noqa: BLE001 - live candidate diagnostics stay redacted.
            rec["error"] = _safe_error(exc)
        checked.append(rec)
    raise CandidateSelectionError(checked)


def _write_local_result(payload: dict[str, Any], *, env: str) -> Path:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    stamp = payload["started_at"].replace(":", "").replace("-", "")
    path = RUN_DIR / f"{env}_minimal_smoke_{stamp}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if env == "paper" and payload.get("execute") is True and payload.get("overall_status") == "pass":
        LATEST_PAPER_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _load_paper_evidence(expected_date: date | None) -> dict[str, Any]:
    if not LATEST_PAPER_PATH.exists():
        raise RuntimeError(f"paper evidence missing: {LATEST_PAPER_PATH.relative_to(ROOT)}")
    payload = json.loads(LATEST_PAPER_PATH.read_text(encoding="utf-8"))
    if payload.get("env") != "paper":
        raise RuntimeError("latest paper evidence is not paper")
    if payload.get("overall_status") != "pass":
        raise RuntimeError(f"latest paper evidence is not pass: {payload.get('overall_status')}")
    started_at = str(payload.get("started_at") or "")
    run_date = started_at[:10]
    if expected_date and run_date != expected_date.isoformat():
        raise RuntimeError(f"paper evidence date {run_date} != expected {expected_date.isoformat()}")
    return payload


def _prod_confirmation_ok(args: argparse.Namespace) -> bool:
    return bool(args.execute and args.i_understand_this_places_real_orders)


def _run_smoke(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    now = _now_kst()
    expected = _parse_date(args.expected_date)
    session_ok, session_reason = _is_regular_session(
        now,
        start=args.session_start,
        end=args.session_end,
        expected_date=expected,
    )
    result: dict[str, Any] = {
        "env": args.env,
        "started_at": now.isoformat(timespec="seconds"),
        "expected_date": expected.isoformat() if expected else None,
        "execute": bool(args.execute),
        "guard": {
            "regular_session": session_ok,
            "regular_session_reason": session_reason,
            "max_qty": args.max_qty,
            "max_notional": args.max_notional,
            "min_orderbook_levels": args.min_orderbook_levels,
        },
        "steps": [],
    }
    if not session_ok and not args.allow_outside_regular_session:
        result["overall_status"] = "blocked"
        result["error"] = "regular session guard failed"
        return 2, result

    settings = resolve_settings(args.env)
    result["account"] = _mask_account(settings.kis_account_no, settings.kis_account_product_code)
    if args.env == "paper":
        if settings.kis_env != "paper" or "openapivts" not in settings.kis_base_url:
            result["overall_status"] = "blocked"
            result["error"] = "paper endpoint guard failed"
            return 2, result
    elif args.env == "prod":
        if settings.kis_env != "prod" or "openapi.koreainvestment.com" not in settings.kis_base_url or "openapivts" in settings.kis_base_url:
            result["overall_status"] = "blocked"
            result["error"] = "prod endpoint guard failed"
            return 2, result
        if args.execute and not _prod_confirmation_ok(args):
            result["overall_status"] = "blocked"
            result["error"] = "prod execution requires --i-understand-this-places-real-orders"
            return 2, result
        if args.require_paper_evidence:
            try:
                paper = _load_paper_evidence(expected)
                paper_symbol = ((paper.get("selected") or {}).get("symbol") or "").strip()
                if args.symbol and paper_symbol and args.symbol != paper_symbol:
                    raise RuntimeError(f"requested prod symbol {args.symbol} != paper symbol {paper_symbol}")
                if not args.symbol:
                    args.symbol = paper_symbol
                result["paper_evidence"] = {
                    "path": str(LATEST_PAPER_PATH.relative_to(ROOT)),
                    "symbol": paper_symbol,
                    "started_at": paper.get("started_at"),
                }
            except Exception as exc:  # noqa: BLE001 - plain blocked reason.
                result["overall_status"] = "blocked"
                result["error"] = _safe_error(exc)
                return 2, result
    else:
        result["overall_status"] = "blocked"
        result["error"] = f"unsupported env: {args.env}"
        return 2, result

    client = KisClient(settings)
    client._timeout = args.request_timeout
    client._max_retries = args.max_retries

    try:
        selected, checked = _choose_candidate(
            client,
            symbol=args.symbol,
            requested_qty=args.qty,
            max_qty=args.max_qty,
            max_notional=args.max_notional,
            min_orderbook_levels=args.min_orderbook_levels,
        )
        result["selected"] = selected
        result["candidate_checked"] = checked
    except CandidateSelectionError as exc:
        result["candidate_checked"] = exc.checked
        result["overall_status"] = "blocked"
        result["error"] = _safe_error(exc)
        return 2, result
    except Exception as exc:  # noqa: BLE001
        result["overall_status"] = "blocked"
        result["error"] = _safe_error(exc)
        return 2, result

    if not args.execute:
        result["overall_status"] = "dry-run"
        result["planned_steps"] = [
            "market buy selected qty",
            "poll buy status and position delta",
            "market sell filled/delta qty",
            "below-market limit buy 1 share",
            "cancel limit order",
            "confirm final position delta and open-like count",
        ]
        return 0, result

    symbol = selected["symbol"]
    qty = int(selected["planned_qty"])
    before_qty = _position_qty(client, symbol)
    result["before_position_qty"] = before_qty

    buy = client.place_order(OrderRequest(symbol=symbol, side=Side.BUY, order_type=OrderType.MARKET, quantity=qty))
    result["steps"].append({"action": "BUY_MARKET", "qty": qty, "status": buy.status.value, "odno_tail": _order_tail(buy.broker_order_id)})
    buy_status = _poll_order_status(client, buy.broker_order_id, attempts=args.poll_attempts, sleep_seconds=args.poll_sleep)
    buy_probe = _order_probe(client, buy.broker_order_id, attempts=args.probe_attempts, sleep_seconds=args.poll_sleep)
    after_buy_qty = _position_qty(client, symbol)
    position_delta = max(after_buy_qty - before_qty, 0)
    filled_qty = max(_parse_int(buy_status.get("filled_quantity")), _parse_int(buy_probe.get("filled_qty_rows")), position_delta)
    cleanup_reason = ""
    if filled_qty <= 0 and before_qty == 0:
        filled_qty = qty
        cleanup_reason = "buy fill uncertain; cleanup sell submitted for requested qty because starting position was zero"
    result["steps"].append(
        {
            "action": "BUY_STATUS",
            "status": buy_status.get("status"),
            "filled_quantity_hint": filled_qty,
            "position_delta": position_delta,
            "cleanup_reason": cleanup_reason,
            "order_probe": buy_probe,
        }
    )

    sell_qty = min(qty, filled_qty)
    if sell_qty <= 0:
        result["steps"].append({"action": "SELL_MARKET", "status": "SKIPPED", "reason": "no filled quantity detected"})
    else:
        sell = client.place_order(OrderRequest(symbol=symbol, side=Side.SELL, order_type=OrderType.MARKET, quantity=sell_qty))
        result["steps"].append({"action": "SELL_MARKET", "qty": sell_qty, "status": sell.status.value, "odno_tail": _order_tail(sell.broker_order_id)})
        sell_status = _poll_order_status(client, sell.broker_order_id, attempts=args.poll_attempts, sleep_seconds=args.poll_sleep)
        sell_probe = _order_probe(client, sell.broker_order_id, attempts=args.probe_attempts, sleep_seconds=args.poll_sleep)
        after_sell_qty = _position_qty(client, symbol)
        result["steps"].append(
            {
                "action": "SELL_STATUS",
                "status": sell_status.get("status"),
                "filled_quantity": sell_status.get("filled_quantity"),
                "final_position_delta": after_sell_qty - before_qty,
                "order_probe": sell_probe,
            }
        )

    if not args.skip_limit_cancel:
        latest_price = float(client.get_current_price(symbol).price)
        limit_price = _below_market_limit_price(latest_price)
        limit = client.place_order(
            OrderRequest(symbol=symbol, side=Side.BUY, order_type=OrderType.LIMIT, quantity=1, price=float(limit_price))
        )
        result["steps"].append(
            {
                "action": "BUY_LIMIT_BELOW_MARKET",
                "qty": 1,
                "limit_price": limit_price,
                "status": limit.status.value,
                "odno_tail": _order_tail(limit.broker_order_id),
            }
        )
        time.sleep(max(args.poll_sleep, 0.0))
        cancel = client.cancel_order(limit.broker_order_id)
        cancel_probe = _order_probe(client, limit.broker_order_id, attempts=args.probe_attempts, sleep_seconds=args.poll_sleep)
        result["steps"].append(
            {
                "action": "CANCEL_LIMIT",
                "status": cancel.status.value,
                "odno_tail": _order_tail(limit.broker_order_id),
                "order_probe": cancel_probe,
            }
        )

    final_qty = _position_qty(client, symbol)
    result["final_position_qty"] = final_qty
    result["final_position_delta"] = final_qty - before_qty
    open_like_total = 0
    probe_unavailable = False
    for step in result["steps"]:
        probe = step.get("order_probe")
        if isinstance(probe, dict):
            if probe.get("available") is False:
                probe_unavailable = True
            open_like_total += int(probe.get("open_like_count") or 0)
    result["open_like_total_for_touched_orders"] = open_like_total

    buy_ok = any(step.get("action") == "BUY_STATUS" and int(step.get("filled_quantity_hint") or 0) > 0 for step in result["steps"])
    sell_ok = any(step.get("action") == "SELL_STATUS" and int(step.get("final_position_delta") or 0) == 0 for step in result["steps"])
    cancel_ok = args.skip_limit_cancel or any(
        step.get("action") == "CANCEL_LIMIT"
        and step.get("status") == "CANCELED"
        and isinstance(step.get("order_probe"), dict)
        and int(step["order_probe"].get("open_like_count") or 0) == 0
        for step in result["steps"]
    )
    result["overall_status"] = "pass" if buy_ok and sell_ok and cancel_ok and final_qty == before_qty and open_like_total == 0 and not probe_unavailable else "watch"
    return (0 if result["overall_status"] == "pass" else 1), result


def build_parser(default_env: str | None = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="KIS minimal paper/prod order smoke")
    parser.add_argument("--env", choices=["paper", "prod"], default=default_env or "paper")
    parser.add_argument("--symbol", default=None, help="Whitelist symbol. Omit to auto-select; prod defaults to latest paper symbol.")
    parser.add_argument("--qty", type=int, default=5)
    parser.add_argument("--max-qty", type=int, default=5)
    parser.add_argument("--max-notional", type=int, default=5_000)
    parser.add_argument("--min-orderbook-levels", type=int, default=5)
    parser.add_argument("--execute", action="store_true", help="Actually place orders. Without this, only read-only planning is performed.")
    parser.add_argument("--expected-date", default=None, help="KST date guard, YYYY-MM-DD. Use tomorrow's date for the planned run.")
    parser.add_argument("--session-start", type=_parse_hhmm, default=dt_time(9, 0))
    parser.add_argument("--session-end", type=_parse_hhmm, default=dt_time(15, 20))
    parser.add_argument("--allow-outside-regular-session", action="store_true")
    parser.add_argument("--request-timeout", type=float, default=10.0)
    parser.add_argument("--max-retries", type=int, default=1)
    parser.add_argument("--poll-attempts", type=int, default=10)
    parser.add_argument("--probe-attempts", type=int, default=5)
    parser.add_argument("--poll-sleep", type=float, default=1.0)
    parser.add_argument("--skip-limit-cancel", action="store_true")
    parser.add_argument("--require-paper-evidence", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--i-understand-this-places-real-orders", action="store_true")
    parser.add_argument("--json", action=argparse.BooleanOptionalAction, default=True)
    return parser


def main(argv: list[str] | None = None, *, default_env: str | None = None, locked_env: bool = False) -> int:
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    if locked_env and any(arg == "--env" or arg.startswith("--env=") for arg in raw_argv):
        print("This entrypoint has a locked KIS env; do not pass --env.", file=sys.stderr)
        return 2
    parser = build_parser(default_env)
    args = parser.parse_args(raw_argv)
    if locked_env and default_env:
        args.env = default_env
    exit_code, payload = _run_smoke(args)
    try:
        path = _write_local_result(payload, env=args.env)
        payload["local_result_path"] = str(path.relative_to(ROOT))
    except Exception as exc:  # noqa: BLE001 - result persistence should not mask broker safety output.
        payload["local_result_error"] = _safe_error(exc)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
