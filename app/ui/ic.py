"""투자위원회(IC) 워크플로 + 결정 로그. (P2)

전문가 의견 → 악마의 변호인(pre-mortem) → 리스크 게이트 → PM 종합 → CIO 결정 → 결정 로그.
ANTHROPIC_API_KEY가 없으면 각 단계가 데모 스텁으로 동작한다(오프라인에서도 흐름 검증 가능).
"""
from __future__ import annotations

import datetime as dt
import os
from pathlib import Path

from app.ui import agents_runtime as ar

_DECISIONS = Path(os.getenv("AUTOFOLIO_HOME", ".autofolio")) / "decisions"

DEFAULT_PANEL = [
    "macro-strategist",
    "kr-equity-specialist",
    "kr-etf-specialist",
    "kr-fixed-income-specialist",
]


def run_ic(topic: str, panel: list[str] | None = None, progress=None) -> dict:
    panel = panel or DEFAULT_PANEL
    transcript: list[dict] = []

    def step(role: str, agent: str, question: str, context: str = "") -> str:
        if progress:
            progress(role)
        text = ar.ask(agent, question, context)
        transcript.append({"role": role, "agent": agent, "text": text})
        return text

    views = []
    for agent in panel:
        t = step(f"전문가 의견 · {agent}", agent, f"다음 안건에 대한 너의 관점과 구체적 제안: {topic}")
        views.append(f"## {agent}\n{t}")
    views_ctx = "\n\n".join(views)

    da = step("악마의 변호인", "devils-advocate",
              f"안건 '{topic}'과 아래 전문가 의견들의 약점·반증·pre-mortem을 제시하라.", views_ctx)
    risk = step("리스크 매니저", "risk-manager",
                f"안건 '{topic}'의 제안들을 사이징·집중도·안전한도(화이트리스트·거래시간·예산·서킷브레이커) 관점에서 평가하라.",
                f"{views_ctx}\n\n## 악마의 변호인\n{da}")
    pm_ctx = f"{views_ctx}\n\n## 악마의 변호인\n{da}\n\n## 리스크\n{risk}"
    pm = step("포트폴리오 매니저", "portfolio-manager",
              f"위 의견을 종합해 '{topic}'에 대한 구체적 실행 제안(종목/방향/목표가/비중)을 만들어라.", pm_ctx)
    cio = step("CIO 결정", "cio",
               f"최종 하우스뷰와 결정(승인/보류/거부 + 우선순위 + 뷰가 틀렸음을 알 트리거)을 내려라. 안건: {topic}",
               f"{pm_ctx}\n\n## PM 제안\n{pm}")

    path = _write_log(topic, transcript)
    return {"topic": topic, "transcript": transcript, "decision": cio, "path": str(path)}


def _write_log(topic: str, transcript: list[dict]) -> Path:
    _DECISIONS.mkdir(parents=True, exist_ok=True)
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = _DECISIONS / f"IC_{ts}.md"
    lines = [f"# 투자위원회 결정 — {topic}", f"_{dt.datetime.now().isoformat(timespec='seconds')}_", ""]
    for t in transcript:
        lines += [f"## {t['role']} (`{t['agent']}`)", t["text"], ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def list_decisions(limit: int = 10) -> list[dict]:
    if not _DECISIONS.exists():
        return []
    files = sorted(_DECISIONS.glob("IC_*.md"), reverse=True)[:limit]
    return [{"file": f.name, "path": str(f)} for f in files]
