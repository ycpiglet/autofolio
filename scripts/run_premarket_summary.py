#!/usr/bin/env python3
"""Generate a manual pre-market agent summary file.

This command is explicit by design. It does not install a scheduler, start a
daemon, place orders, save trade conditions, or call KIS order endpoints.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")

from app.services.premarket_summary import generate_summary  # noqa: E402


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="정규장 시작 전 기준의 리서치·금융 전문가 핵심 요약을 파일로 저장합니다."
    )
    parser.add_argument("--date", default=None, help="요약 기준일 YYYY-MM-DD. 기본값: 오늘.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="파일 저장 없이 stdout으로만 출력합니다.",
    )
    parser.add_argument(
        "--limit-symbols",
        type=int,
        default=5,
        help="관심종목/화이트리스트에서 포함할 최대 종목 수.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    result = generate_summary(
        target_date=args.date,
        save=not args.dry_run,
        limit_symbols=max(1, args.limit_symbols),
    )
    print(result["content"])
    if args.dry_run:
        print("\n[dry-run] 파일 저장 생략")
    else:
        print(f"\n[saved] {result['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
