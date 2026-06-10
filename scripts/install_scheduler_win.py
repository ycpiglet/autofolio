#!/usr/bin/env python3
"""Windows Task Scheduler 등록 도우미 — Autofolio 스크립트 자동 실행 설정. [T-34]

등록할 작업:
  - run_paper_engine.py (장중 30초 간격) → KIS_ENV=paper 에서만
  - run_daily_summary.py (15:35 장후) → 시장 마감 후 일일 요약

사용:
  python scripts/install_scheduler_win.py --list          # 등록된 Autofolio 작업 확인
  python scripts/install_scheduler_win.py --install       # 작업 등록
  python scripts/install_scheduler_win.py --uninstall     # 작업 제거
  python scripts/install_scheduler_win.py --dry-run       # 명령만 출력
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable

TASKS = [
    {
        "name": "Autofolio_PaperEngine",
        "desc": "Autofolio 모의투자 엔진 (장중 30초 간격)",
        "script": str(ROOT / "scripts" / "run_paper_engine.py"),
        "args": "--interval 30",
        # 스케줄: 매일 09:10~15:20 (장중), 실제로는 스크립트 내부 시간 가드로 제어
        "trigger": "/SC MINUTE /MO 1 /ST 09:10 /ET 15:20",
    },
    {
        "name": "Autofolio_DailySummary",
        "desc": "Autofolio 일일 요약 (15:35 장후)",
        "script": str(ROOT / "scripts" / "run_daily_summary.py"),
        "args": "",
        "trigger": "/SC DAILY /ST 15:35",
    },
]


def schtasks(*args: str, dry_run: bool = False) -> bool:
    cmd = ["schtasks", *args]
    print("CMD:", " ".join(cmd))
    if dry_run:
        return True
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.stdout:
        print(r.stdout.strip())
    if r.returncode != 0 and r.stderr:
        print("STDERR:", r.stderr.strip())
    return r.returncode == 0


def install(dry_run: bool = False) -> None:
    for t in TASKS:
        run_cmd = f'"{PYTHON}" "{t["script"]}" {t["args"]}'.strip()
        args = [
            "/Create", "/F",
            "/TN", t["name"],
            "/TR", run_cmd,
            "/SC", "MINUTE", "/MO", "1",
        ]
        # 간단 등록: schtasks 직접 구성
        full_args = ["/Create", "/F",
                     "/TN", t["name"],
                     "/TR", run_cmd,
                     *t["trigger"].split()]
        ok = schtasks(*full_args, dry_run=dry_run)
        print(f"{'[OK]' if ok else '[FAIL]'} {t['name']}: {t['desc']}")


def uninstall(dry_run: bool = False) -> None:
    for t in TASKS:
        ok = schtasks("/Delete", "/F", "/TN", t["name"], dry_run=dry_run)
        print(f"{'[OK]' if ok else '[FAIL]'} 제거: {t['name']}")


def list_tasks() -> None:
    schtasks("/Query", "/FO", "LIST", "/V", "/TN", "Autofolio")


def main() -> int:
    ap = argparse.ArgumentParser(description="Autofolio Windows Task Scheduler 등록")
    ap.add_argument("--install", action="store_true")
    ap.add_argument("--uninstall", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.list:
        list_tasks()
    elif args.uninstall:
        uninstall(args.dry_run)
    elif args.install or args.dry_run:
        install(args.dry_run)
    else:
        ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
