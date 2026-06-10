#!/usr/bin/env python3
"""09:00 KST까지 대기 후 market-test 실행. KST-aware."""
from __future__ import annotations
import subprocess, sys, time
from datetime import datetime, timezone, timedelta
from pathlib import Path

KST = timezone(timedelta(hours=9))
ROOT = Path(__file__).resolve().parent.parent

def kst_now():
    return datetime.now(KST)

def main() -> int:
    target = kst_now().replace(hour=9, minute=0, second=0, microsecond=0)
    remaining = (target - kst_now()).total_seconds()
    if remaining <= 0:
        print(f"[{kst_now():%H:%M:%S} KST] 이미 09:00 이후 — 즉시 실행")
    else:
        print(f"[{kst_now():%H:%M:%S} KST] 09:00까지 {int(remaining//60)}분 대기 중…")
        while kst_now() < target:
            time.sleep(15)
    print(f"[{kst_now():%H:%M:%S} KST] 장 개시 — market-test 실행")
    result = subprocess.run([sys.executable, str(ROOT/"scripts"/"kis_paper_order_smoke.py"), "--market-test"], cwd=str(ROOT))
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
