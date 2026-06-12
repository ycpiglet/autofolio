#!/usr/bin/env python3
"""Bounded KIS paper transaction loop.

This wrapper repeatedly invokes ``kis_paper_transaction_soak.py`` with a fixed
symbol rotation. It is intentionally paper-only and bounded: it defaults to one
cycle, caps the number of cycles, and keeps quantity at one share.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
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

from app.config.settings import resolve_settings  # noqa: E402

ROTATION: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("069500", ("005930", "000660")),
    ("005930", ("069500", "000660")),
    ("000660", ("005930", "069500")),
)
MAX_CYCLES = 12


@dataclass(frozen=True)
class CyclePlan:
    cycle: int
    fill_symbol: str
    unfilled_symbols: tuple[str, ...]


def guard_paper_endpoint() -> dict[str, Any]:
    settings = resolve_settings("paper")
    if settings.kis_env != "paper":
        raise RuntimeError(f"paper-only loop resolved env={settings.kis_env}")
    if "openapivts" not in settings.kis_base_url:
        raise RuntimeError("paper-only loop resolved non-paper KIS base URL")
    return {"env": settings.kis_env, "paper_endpoint": True}


def build_cycle_plan(cycles: int) -> list[CyclePlan]:
    if cycles < 1:
        raise ValueError("cycles must be >= 1")
    if cycles > MAX_CYCLES:
        raise ValueError(f"cycles must be <= {MAX_CYCLES}")
    plans: list[CyclePlan] = []
    for index in range(cycles):
        fill_symbol, unfilled = ROTATION[index % len(ROTATION)]
        plans.append(CyclePlan(cycle=index + 1, fill_symbol=fill_symbol, unfilled_symbols=unfilled))
    return plans


def command_for_plan(
    plan: CyclePlan,
    *,
    qty: int,
    attempts: int,
    sleep_sec: float,
) -> list[str]:
    return [
        sys.executable,
        str(ROOT / "scripts" / "kis_paper_transaction_soak.py"),
        "--fill-symbol",
        plan.fill_symbol,
        "--unfilled-symbols",
        *plan.unfilled_symbols,
        "--qty",
        str(qty),
        "--attempts",
        str(attempts),
        "--sleep",
        str(sleep_sec),
    ]


def parse_json_stdout(stdout: str) -> dict[str, Any]:
    for line in reversed(stdout.splitlines()):
        text = line.strip()
        if text.startswith("{") and text.endswith("}"):
            return json.loads(text)
    raise ValueError("child command did not emit a JSON object")


def run_child(command: list[str], *, timeout_sec: int) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=timeout_sec,
        check=False,
    )
    if completed.returncode != 0:
        return {
            "ok": False,
            "returncode": completed.returncode,
            "stdout_tail": completed.stdout[-1000:],
            "stderr_tail": completed.stderr[-1000:],
        }
    output = parse_json_stdout(completed.stdout)
    output["returncode"] = completed.returncode
    return output


def summarize_child(output: dict[str, Any]) -> dict[str, Any]:
    records = output.get("records") or []
    return {
        "ok": bool(output.get("ok")),
        "fill_symbol": output.get("fill_symbol"),
        "filled_records": sum(1 for row in records if row.get("status") == "FILLED"),
        "canceled_records": sum(1 for row in records if row.get("status") == "CANCELED"),
        "post_open_like_count": output.get("post_open_like_count"),
        "order_log_rows_after": (output.get("after") or {}).get("order_log_rows"),
        "recent_fills_after": (output.get("after") or {}).get("recent_fills_rows"),
        "kis_today_order_rows_after": (output.get("after") or {}).get("kis_today_order_rows"),
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bounded KIS paper transaction loop")
    parser.add_argument("--cycles", type=int, default=1)
    parser.add_argument("--interval-sec", type=float, default=300.0)
    parser.add_argument("--qty", type=int, default=1)
    parser.add_argument("--attempts", type=int, default=8)
    parser.add_argument("--sleep", type=float, default=1.0)
    parser.add_argument("--timeout-sec", type=int, default=180)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--continue-on-failure", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.qty != 1:
        raise SystemExit("paper transaction loop keeps qty fixed at 1")
    guard = guard_paper_endpoint()
    plans = build_cycle_plan(args.cycles)
    commands = [
        command_for_plan(plan, qty=args.qty, attempts=args.attempts, sleep_sec=args.sleep)
        for plan in plans
    ]
    if args.dry_run:
        print(
            json.dumps(
                {
                    "ok": True,
                    "dry_run": True,
                    **guard,
                    "plans": [asdict(plan) for plan in plans],
                    "cycles": len(plans),
                },
                ensure_ascii=False,
            )
        )
        return 0

    results: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    for index, (plan, command) in enumerate(zip(plans, commands, strict=True), start=1):
        child = run_child(command, timeout_sec=args.timeout_sec)
        child["cycle"] = plan.cycle
        results.append(child)
        summaries.append({"cycle": plan.cycle, **summarize_child(child)})
        if not child.get("ok") and not args.continue_on_failure:
            break
        if index < len(commands):
            time.sleep(max(args.interval_sec, 0.0))

    ok = len(results) == len(plans) and all(bool(result.get("ok")) for result in results)
    output = {
        "ok": ok,
        **guard,
        "cycles_requested": len(plans),
        "cycles_completed": len(results),
        "summaries": summaries,
    }
    print(json.dumps(output, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
