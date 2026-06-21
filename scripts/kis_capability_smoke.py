#!/usr/bin/env python3
"""Redacted KIS capability smoke for paper and prod read-only surfaces.

This script intentionally never places, cancels, modifies, or enables orders.
Prod is limited to read-only checks. Numeric account amounts, tokens, raw
broker payloads, and account numbers are not printed.
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")

from app.brokers.kis.kis_auth import KisAuth  # noqa: E402
from app.brokers.kis.kis_client import KisClient  # noqa: E402
from app.config.settings import resolve_settings  # noqa: E402
from scripts.kis_paper_order_smoke import _is_open_like_order  # noqa: E402


Check = dict[str, Any]


def _redact_text(value: Any) -> str:
    text = str(value)
    text = re.sub(r"[A-Za-z0-9_\-]{32,}", "[redacted]", text)
    text = re.sub(r"\d{6,}", "[digits]", text)
    return text[:240]


def _safe_error(error: Exception) -> str:
    return f"{type(error).__name__}: {_redact_text(error)}"


def _check(name: str, fn: Callable[[], dict[str, Any]]) -> Check:
    try:
        details = fn()
    except Exception as exc:  # noqa: BLE001 - live broker smoke must keep going.
        return {"name": name, "status": "fail", "details": {"error": _safe_error(exc)}}
    status = "fail" if details.pop("ok", True) is False else "pass"
    return {"name": name, "status": status, "details": details}


def _skip(name: str, reason: str) -> Check:
    return {"name": name, "status": "skip", "details": {"reason": reason}}


def _has_broker_credentials(settings: Any) -> bool:
    return bool(settings.kis_app_key and settings.kis_app_secret)


def _has_account_credentials(settings: Any) -> bool:
    return bool(settings.kis_account_no and settings.kis_account_product_code)


def _tune_client(client: KisClient, *, request_timeout: float, max_retries: int) -> None:
    client._timeout = max(float(request_timeout), 1.0)
    client._max_retries = max(int(max_retries), 0)


def _keys_present(data: dict[str, Any], keys: list[str]) -> list[str]:
    return [key for key in keys if data.get(key) not in (None, "")]


def _summarize_positions(positions: list[Any]) -> dict[str, Any]:
    return {
        "count": len(positions),
        "markets": sorted({getattr(position, "market", "") for position in positions if getattr(position, "market", "")}),
    }


def _summarize_today_orders(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "count": len(rows),
        "open_like_count": sum(1 for row in rows if _is_open_like_order(row)),
        "canceled_count": sum(1 for row in rows if str(row.get("cncl_yn") or "").upper() == "Y"),
    }


def _summarize_account_summary(summary: dict[str, Any]) -> dict[str, Any]:
    numeric_fields = [
        "dnca_tot_amt",
        "tot_evlu_amt",
        "nass_amt",
        "pchs_amt_smtl_amt",
        "evlu_pfls_smtl_amt",
    ]
    return {
        "source": summary.get("source", ""),
        "numeric_field_count": sum(1 for key in numeric_fields if key in summary),
    }


def _env_status(checks: list[Check]) -> str:
    statuses = [check["status"] for check in checks]
    if not statuses or all(status == "skip" for status in statuses):
        return "skip"
    if "fail" in statuses:
        return "fail"
    if "skip" in statuses:
        return "watch"
    return "pass"


def smoke_env(
    env: str,
    *,
    symbol: str,
    batch_symbols: list[str],
    deep: bool = False,
    request_timeout: float = 10.0,
    max_retries: int = 1,
) -> dict[str, Any]:
    settings = resolve_settings(env)
    checks: list[Check] = []
    result: dict[str, Any] = {
        "env": env,
        "base_url": settings.kis_base_url,
        "mode": "read-only",
        "profile": "deep" if deep else "core",
        "request_timeout_sec": max(float(request_timeout), 1.0),
        "max_retries": max(int(max_retries), 0),
        "checks": checks,
    }

    if not _has_broker_credentials(settings):
        checks.append(_skip("credentials", f"KIS_{env.upper()}_APP_KEY/SECRET missing"))
        result["status"] = _env_status(checks)
        return result

    client = KisClient(settings)
    _tune_client(client, request_timeout=request_timeout, max_retries=max_retries)
    current_price: dict[str, float] = {"value": 0.0}

    checks.append(
        _check(
            "token",
            lambda: {"token_len": len(KisAuth(settings).get_access_token() or "")},
        )
    )

    def current_price_check() -> dict[str, Any]:
        quote = client.get_current_price(symbol)
        current_price["value"] = float(quote.price or 0.0)
        return {"ok": current_price["value"] > 0, "symbol": symbol, "price_positive": current_price["value"] > 0}

    def batch_prices_check() -> dict[str, Any]:
        prices = client.get_prices_batch(batch_symbols)
        return {
            "ok": len(prices) == len(set(batch_symbols)),
            "requested": len(batch_symbols),
            "returned": len(prices),
        }

    def intraday_chart_check() -> dict[str, Any]:
        rows = len(client.get_intraday_chart(symbol, count=10))
        return {"ok": rows > 0, "rows": rows}

    def price_history_check() -> dict[str, Any]:
        rows = len(client.get_price_history(symbol, count=10))
        return {"ok": rows > 0, "rows": rows}

    def index_price_kospi_check() -> dict[str, Any]:
        fields = _keys_present(client.get_index_price("KOSPI"), ["code", "name", "price"])
        return {"ok": "price" in fields, "fields_present": fields}

    def order_book_check() -> dict[str, Any]:
        levels = len(client.get_order_book(symbol).get("levels", []))
        return {"ok": levels > 0, "levels": levels}

    checks.append(_check("current_price", current_price_check))
    checks.append(_check("batch_prices", batch_prices_check))
    checks.append(_check("intraday_chart", intraday_chart_check))
    checks.append(_check("price_history", price_history_check))
    checks.append(_check("index_price_kospi", index_price_kospi_check))
    checks.append(_check("order_book", order_book_check))

    if deep:
        def index_price_kosdaq_check() -> dict[str, Any]:
            fields = _keys_present(client.get_index_price("KOSDAQ"), ["code", "name", "price"])
            return {"ok": "price" in fields, "fields_present": fields}

        def sector_price_check() -> dict[str, Any]:
            fields = _keys_present(
                client.get_sector_price("KOSPI_ELECTRONICS"),
                ["code", "name", "price"],
            )
            return {"ok": "price" in fields, "fields_present": fields}

        def fundamental_check() -> dict[str, Any]:
            fields = _keys_present(
                client.get_fundamental(symbol, include_finance_ratio=False),
                ["symbol", "per", "pbr", "eps"],
            )
            return {"ok": "symbol" in fields, "fields_present": fields}

        checks.append(
            _check(
                "index_price_kosdaq",
                index_price_kosdaq_check,
            )
        )
        checks.append(
            _check(
                "sector_price",
                sector_price_check,
            )
        )
        checks.append(
            _check(
                "disclosures",
                lambda: {"rows": len(client.get_disclosures(symbol, days=1))},
            )
        )
        checks.append(
            _check(
                "fundamental",
                fundamental_check,
            )
        )
        checks.append(
            _check(
                "dividend_info",
                lambda: {"records": len(client.get_dividend_info(symbol).get("records", []))},
            )
        )

    core_account_checks = ["account_summary_shape", "today_orders"]
    deep_account_checks = [
        "buying_power_shape",
        "positions",
        "cash_balance_shape",
        "order_history_7d",
    ]
    account_checks = core_account_checks + (deep_account_checks if deep else [])
    if not _has_account_credentials(settings):
        for name in account_checks:
            checks.append(_skip(name, f"KIS_{env.upper()}_ACCOUNT_NO/PRODUCT_CODE missing"))
        result["status"] = _env_status(checks)
        return result

    def account_summary_shape_check() -> dict[str, Any]:
        summary = {"source": "", "numeric_field_count": 0}
        for attempt in range(2):
            summary = _summarize_account_summary(client.get_account_summary())
            if summary["numeric_field_count"] > 0 or attempt == 1:
                break
            time.sleep(0.7)
        return {**summary, "ok": summary["numeric_field_count"] > 0}

    checks.append(
        _check(
            "account_summary_shape",
            account_summary_shape_check,
        )
    )
    checks.append(
        _check(
            "today_orders",
            lambda: _summarize_today_orders(client.get_today_orders(suppress_errors=False)),
        )
    )

    if deep:
        def buying_power_check() -> dict[str, Any]:
            price = current_price["value"] or client.get_current_price(symbol).price
            buying_power = client.get_buying_power(symbol, price)
            return {
                "keys_present": _keys_present(buying_power, ["max_quantity", "available_cash"]),
                "numeric_values_redacted": True,
            }

        checks.append(_check("buying_power_shape", buying_power_check))
        checks.append(_check("positions", lambda: _summarize_positions(client.get_positions())))
        checks.append(
            _check(
                "cash_balance_shape",
                lambda: {"numeric_value_redacted": isinstance(client.get_cash_balance(), (int, float))},
            )
        )

        def order_history_check() -> dict[str, Any]:
            end = datetime.now().date()
            start = end - timedelta(days=7)
            rows = client.get_order_history(start.strftime("%Y%m%d"), end.strftime("%Y%m%d"))
            return {"rows": len(rows)}

        checks.append(_check("order_history_7d", order_history_check))
    result["status"] = _env_status(checks)
    return result


def build_smoke(
    env: str,
    *,
    symbol: str,
    batch_symbols: list[str],
    deep: bool = False,
    request_timeout: float = 10.0,
    max_retries: int = 1,
) -> dict[str, Any]:
    envs = ["paper", "prod"] if env == "both" else [env]
    results = [
        smoke_env(
            target_env,
            symbol=symbol,
            batch_symbols=batch_symbols,
            deep=deep,
            request_timeout=request_timeout,
            max_retries=max_retries,
        )
        for target_env in envs
    ]
    statuses = [item["status"] for item in results]
    if all(status == "skip" for status in statuses):
        overall = "skip"
    elif "fail" in statuses:
        overall = "fail"
    elif "watch" in statuses or "skip" in statuses:
        overall = "watch"
    else:
        overall = "pass"
    return {
        "overall_status": overall,
        "order_actions": "not-run",
        "prod_boundary": "read-only",
        "profile": "deep" if deep else "core",
        "results": results,
    }


def _print_text(summary: dict[str, Any]) -> None:
    print(f"overall={summary['overall_status']} order_actions={summary['order_actions']} prod={summary['prod_boundary']}")
    for env_result in summary["results"]:
        print(f"[{env_result['env']}] status={env_result['status']} base={env_result['base_url']}")
        for check in env_result["checks"]:
            details = json.dumps(check["details"], ensure_ascii=False, sort_keys=True)
            print(f"  {check['status']:4s} {check['name']} {details}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Redacted KIS read-only capability smoke")
    parser.add_argument("--env", choices=["paper", "prod", "both"], default="both")
    parser.add_argument("--symbol", default="005930")
    parser.add_argument("--batch-symbols", nargs="+", default=["005930", "000660", "069500"])
    parser.add_argument("--deep", action="store_true", help="Run slower optional read-only checks too")
    parser.add_argument("--request-timeout", type=float, default=10.0)
    parser.add_argument("--max-retries", type=int, default=1)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if not args.verbose:
        logging.getLogger("app.brokers.kis.kis_client").setLevel(logging.CRITICAL)

    summary = build_smoke(
        args.env,
        symbol=args.symbol,
        batch_symbols=args.batch_symbols,
        deep=args.deep,
        request_timeout=args.request_timeout,
        max_retries=args.max_retries,
    )
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    else:
        _print_text(summary)

    if summary["overall_status"] == "fail":
        return 1
    if summary["overall_status"] == "skip":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
