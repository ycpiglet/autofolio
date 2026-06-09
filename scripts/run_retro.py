#!/usr/bin/env python3
"""Autofolio `/retro` 워크플로 — 주문로그 기반 멀티에이전트 회고 분석. [호스트 스크립트]

주문로그(DB)를 읽어 Performance Analyst + Devils Advocate + Risk Manager가
순차적으로 회고를 수행하고, 결과를 `.autofolio/retro/` 에 저장한다.
ANTHROPIC_API_KEY 없으면 스텁 응답으로 흐름만 검증한다.

사용:
  python scripts/run_retro.py                  # 최근 30일
  python scripts/run_retro.py --days 7
  python scripts/run_retro.py --dry-run        # 로그 출력만
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from dotenv import load_dotenv  # noqa: E402
load_dotenv(ROOT / ".env")

from app.common.logger import get_logger  # noqa: E402
from app.config.settings import settings  # noqa: E402
from app.database.repositories import Repository  # noqa: E402
from app.database.sqlite_db import initialize_database  # noqa: E402
from app.ui import agents_runtime as ar  # noqa: E402

logger = get_logger("autofolio.retro")
_RETRO_DIR = Path(os.getenv("AUTOFOLIO_HOME", ".autofolio")) / "retro"


def _build_context(logs: list[dict]) -> str:
    if not logs:
        return "주문 이력 없음."
    total = len(logs)
    filled = [l for l in logs if l.get("order_status") == "FILLED"]
    failed = [l for l in logs if l.get("order_status") == "FAILED"]
    lines = [
        f"기간 주문 총 {total}건: 체결 {len(filled)}건, 실패 {len(failed)}건.",
    ]
    for l in filled[:10]:
        sym = l.get("symbol", "?")
        side = l.get("side", "?")
        price = l.get("order_price") or l.get("current_price") or 0
        lines.append(f"- {sym} {side} @{float(price):,.0f}")
    if len(filled) > 10:
        lines.append(f"- ... 외 {len(filled) - 10}건")
    return "\n".join(lines)


def run_retro(days: int = 30, dry_run: bool = False) -> dict:
    initialize_database(settings.db_path)
    repo = Repository(settings.db_path)
    logs = repo.list_order_logs(limit=500)
    ctx = _build_context(logs)
    period = f"최근 {days}일"
    transcript = []

    def step(role: str, agent: str, question: str, context: str = "") -> str:
        logger.info("[retro] %s (%s)", role, agent)
        if dry_run:
            stub = f"[DRY-RUN] {role}: 응답 생략"
            transcript.append({"role": role, "agent": agent, "text": stub})
            return stub
        text = ar.ask(agent, question, context)
        transcript.append({"role": role, "agent": agent, "text": text})
        return text

    perf = step(
        "Performance Analyst", "lead-engineer",
        f"{period} 주문 이력을 분석해 승률·평균 손익·최대낙폭·주요 실수 패턴을 정리하라.",
        ctx,
    )
    da = step(
        "Devils Advocate", "devils-advocate",
        f"다음 성과 분석의 약점·과최적화·생존편향 우려를 제시하라. {period}",
        f"## Performance\n{perf}\n\n## 원본 로그\n{ctx}",
    )
    risk_review = step(
        "Risk Manager", "risk-manager",
        f"다음 거래 패턴이 안전 한도(주문한도·쿨다운·화이트리스트·서킷브레이커)를 잘 준수했는지 평가하라.",
        f"## Performance\n{perf}\n\n## 원본 로그\n{ctx}",
    )
    forward = step(
        "Forward Actions", "lead-engineer",
        "위 회고를 바탕으로 다음 사이클 개선사항 3~5개를 구체적 행동 항목으로 제시하라.",
        f"## Performance\n{perf}\n## DA\n{da}\n## Risk\n{risk_review}",
    )

    path = _write_retro(period, transcript, logs)
    logger.info("[retro] 완료 → %s", path)
    return {
        "period": period,
        "transcript": transcript,
        "forward_actions": forward,
        "path": str(path),
    }


def _write_retro(period: str, transcript: list[dict], logs: list[dict]) -> Path:
    _RETRO_DIR.mkdir(parents=True, exist_ok=True)
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = _RETRO_DIR / f"RETRO_{ts}.md"
    filled = len([l for l in logs if l.get("order_status") == "FILLED"])
    lines = [
        f"# 회고 — {period}",
        f"_{dt.datetime.now().isoformat(timespec='seconds')}_ · 주문 {len(logs)}건 · 체결 {filled}건",
        "",
    ]
    for t in transcript:
        lines += [f"## {t['role']} (`{t['agent']}`)", t["text"], ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description="Autofolio 회고 워크플로 (/retro)")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    result = run_retro(days=args.days, dry_run=args.dry_run)
    print(f"\n✅ 회고 완료: {result['path']}")
    print("\n## Forward Actions")
    print(result["forward_actions"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
