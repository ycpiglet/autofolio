"""에이전트 서비스 — 런타임 + 투자위원회(IC) 워크플로.

에이전트 런타임 (app.ui.agents_runtime 원본):
  .claude/agents 페르소나 + .claude/skills 지식을 Anthropic API로 구동.
  ANTHROPIC_API_KEY가 없거나 anthropic 패키지가 없으면 결정적 스텁으로 폴백한다(데모/오프라인).

투자위원회 워크플로 (app.ui.ic 원본):
  전문가 의견 → 악마의 변호인(pre-mortem) → 리스크 게이트 → PM 종합 → CIO 결정 → 결정 로그.
  ANTHROPIC_API_KEY가 없으면 각 단계가 데모 스텁으로 동작한다(오프라인에서도 흐름 검증 가능).

shim: app/ui/agents_runtime.py, app/ui/ic.py (Phase 0 REAL move).
"""
from __future__ import annotations

import datetime as dt
import os
import re
from functools import lru_cache
from pathlib import Path

# ---------------------------------------------------------------------------
# agents_runtime 상수·경로
# ---------------------------------------------------------------------------

_ROOT = Path(__file__).resolve().parents[2]
_AGENTS_DIR = _ROOT / ".claude" / "agents"
_SKILLS_DIR = _ROOT / ".claude" / "skills"

MODEL = os.getenv("AUTOFOLIO_LLM_MODEL", "claude-opus-4-8")
EFFORT = os.getenv("AUTOFOLIO_LLM_EFFORT", "medium")

_GUARDRAIL = (
    "\n\n# 운영 지침\n"
    "- 한국어로 간결하고 구조적으로 답한다.\n"
    "- 너는 제안·분석만 한다. 실제 조건 저장·자동매매·주문은 사람이 승인한다(MVP_SPEC §6.6).\n"
    "- 확신도(상/중/하)와 핵심 리스크를 반드시 명시한다."
)

# ---------------------------------------------------------------------------
# ic 상수·경로
# ---------------------------------------------------------------------------

_DECISIONS = Path(os.getenv("AUTOFOLIO_HOME", ".autofolio")) / "decisions"

DEFAULT_PANEL = [
    "macro-strategist",
    "kr-equity-specialist",
    "kr-etf-specialist",
    "kr-fixed-income-specialist",
]

_EXPERT_AGENT_IDS = {
    "macro-strategist",
    "portfolio-manager",
    "risk-manager",
    "cio",
    "devils-advocate",
    "kr-equity-specialist",
    "kr-etf-specialist",
    "kr-fixed-income-specialist",
    "kr-fund-specialist",
    "us-equity-specialist",
    "us-etf-specialist",
    "us-fixed-income-specialist",
    "fx-specialist",
    "commodities-specialist",
    "futures-specialist",
    "options-specialist",
    "research-agent",
    "research",
    "quant-researcher",
    "performance-analyst",
    "backtest-engineer",
    "data-engineer",
    "optimization-quant",
}

_ROLE_LABELS = {
    "macro-strategist": "매크로 전략",
    "portfolio-manager": "포트폴리오 매니저",
    "risk-manager": "리스크 매니저",
    "cio": "CIO",
    "devils-advocate": "악마의 변호인",
    "kr-equity-specialist": "국내 주식",
    "kr-etf-specialist": "국내 ETF",
    "kr-fixed-income-specialist": "국내 채권",
    "kr-fund-specialist": "국내 펀드",
    "us-equity-specialist": "미국 주식",
    "us-etf-specialist": "미국 ETF",
    "us-fixed-income-specialist": "미국 채권",
    "fx-specialist": "FX",
    "commodities-specialist": "원자재",
    "futures-specialist": "선물",
    "options-specialist": "옵션",
    "research-agent": "리서치",
    "research": "리서치",
    "quant-researcher": "퀀트 리서치",
    "performance-analyst": "성과 분석",
    "backtest-engineer": "백테스트",
    "data-engineer": "데이터",
    "optimization-quant": "최적화 퀀트",
}

# ---------------------------------------------------------------------------
# __all__
# ---------------------------------------------------------------------------

__all__ = [
    "list_agents",
    "list_agent_infos",
    "available",
    "ask",
    "run_ic",
    "list_decisions",
    "extract_condition_from_ic",
    "DEFAULT_PANEL",
    "MODEL",
    "EFFORT",
]


# ---------------------------------------------------------------------------
# agents_runtime 구현
# ---------------------------------------------------------------------------

def _parse_frontmatter(text: str) -> tuple[dict, str]:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            fm = {}
            for line in text[3:end].splitlines():
                if ":" in line:
                    k, _, v = line.partition(":")
                    fm[k.strip()] = v.strip()
            return fm, text[end + 4:].lstrip("\n")
    return {}, text


@lru_cache(maxsize=1)
def _personas() -> dict:
    """{short_name: {name, system, skill, skill_body}}; short = name without 'autofolio-' prefix."""
    out: dict[str, dict] = {}
    if not _AGENTS_DIR.exists():
        return out
    for md in _AGENTS_DIR.rglob("*.md"):
        fm, body = _parse_frontmatter(md.read_text(encoding="utf-8"))
        name = fm.get("name")
        if not name:
            continue  # 프론트매터 name이 없는 문서(예: retros/README.md)는 에이전트 아님
        short = name[len("autofolio-"):] if name.startswith("autofolio-") else name
        m = re.search(r"Use the \*\*`([^`]+)`\*\* skill", body)
        skill_name = m.group(1) if m else ""
        skill_body = ""
        if skill_name and (_SKILLS_DIR / skill_name / "SKILL.md").exists():
            _, skill_body = _parse_frontmatter((_SKILLS_DIR / skill_name / "SKILL.md").read_text(encoding="utf-8"))
        out[short] = {
            "name": name,
            "system": body,
            "skill": skill_name,
            "skill_body": skill_body,
            "description": fm.get("description", ""),
            "source": str(md.relative_to(_ROOT)),
        }

    # agent_runtime 프레임워크 정본 개발팀: agents/<role>/SKILL.md (프론트매터 없음, name=폴더)
    fw = _ROOT / "agents"
    if fw.exists():
        for skill in sorted(fw.glob("*/SKILL.md")):
            short = skill.parent.name.replace("_", "-")
            if short in out:
                continue  # .claude 정의가 있으면 우선
            out[short] = {
                "name": f"autofolio-{short}",
                "system": skill.read_text(encoding="utf-8"),
                "skill": "",
                "skill_body": "",
                "description": "",
                "source": str(skill.relative_to(_ROOT)),
            }
    return out


def list_agents() -> list[str]:
    return sorted(_personas().keys())


def list_agent_infos(*, experts_only: bool = False) -> list[dict]:
    """Return public agent metadata for UI/API consumers."""
    items: list[dict] = []
    for short, persona in sorted(_personas().items()):
        source = str(persona.get("source", ""))
        expert = _is_expert_agent(short, source)
        if experts_only and not expert:
            continue
        items.append({
            "name": short,
            "role": _ROLE_LABELS.get(short) or _title_from_short(short),
            "category": _category_for(short, source),
            "description": _description_for(persona),
            "expert": expert,
        })
    return items


def _is_expert_agent(short: str, source: str) -> bool:
    return short in _EXPERT_AGENT_IDS or ".claude/agents/asset-team" in source.replace("\\", "/")


def _category_for(short: str, source: str) -> str:
    normalized = source.replace("\\", "/")
    if "asset-team/leadership" in normalized:
        return "투자 리더십"
    if "asset-team/korea-desk" in normalized:
        return "국내 금융"
    if "asset-team/us-desk" in normalized:
        return "글로벌 금융"
    if "asset-team/global-desk" in normalized:
        return "글로벌 금융"
    if "asset-team/governance" in normalized:
        return "투자 거버넌스"
    if short in {"research", "research-agent", "quant-researcher", "backtest-engineer", "data-engineer", "optimization-quant"}:
        return "리서치"
    if short == "performance-analyst":
        return "성과/리스크"
    return "운영"


def _title_from_short(short: str) -> str:
    return " ".join(part.capitalize() for part in short.split("-"))


def _description_for(persona: dict) -> str:
    desc = str(persona.get("description") or "").strip()
    if desc:
        return desc
    for line in str(persona.get("system") or "").splitlines():
        stripped = line.strip(" #")
        if stripped and not stripped.startswith("---"):
            return stripped[:180]
    return ""


def available() -> tuple[bool, str]:
    if not os.getenv("ANTHROPIC_API_KEY"):
        return False, "ANTHROPIC_API_KEY 미설정 (데모 응답)"
    try:
        import anthropic  # noqa: F401
    except Exception:
        return False, "anthropic 패키지 미설치"
    return True, MODEL


def ask(agent_short: str, question: str, context: str = "") -> str:
    persona = _personas().get(agent_short)
    if persona is None:
        return f"[{agent_short}] 아직 구현되지 않은 에이전트입니다 (설계 단계)."

    ok, _ = available()
    if not ok:
        return _stub(agent_short, question)

    import anthropic

    system = persona["system"]
    if persona["skill_body"]:
        system += f"\n\n# 도메인 방법론 (skill: {persona['skill']})\n{persona['skill_body']}"
    system += _GUARDRAIL
    user = (f"[배경]\n{context}\n\n" if context else "") + f"[질문]\n{question}"

    try:
        client = anthropic.Anthropic()
        resp = client.messages.create(
            model=MODEL,
            max_tokens=8000,
            cache_control={"type": "ephemeral"},  # 시스템(페르소나+스킬) 자동 캐싱
            system=system,
            thinking={"type": "adaptive"},
            output_config={"effort": EFFORT},
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(b.text for b in resp.content if b.type == "text").strip()
        return text or "(빈 응답)"
    except Exception as exc:  # noqa: BLE001
        return f"[{agent_short}] 호출 오류: {exc}"


def _stub(agent_short: str, question: str) -> str:
    return (
        f"**[{agent_short} · 데모 응답]**\n\n"
        f"질문: {question}\n\n"
        "`.env`에 ANTHROPIC_API_KEY를 설정하면 이 에이전트의 실제 분석이 제공됩니다. 지금은 데모 스텁입니다.\n\n"
        "- 핵심: 분할 접근 · 리스크 한도 점검 권고\n- 확신도: 중"
    )


# ---------------------------------------------------------------------------
# ic 구현
# ---------------------------------------------------------------------------

def run_ic(topic: str, panel: list[str] | None = None, progress=None) -> dict:
    panel = panel or DEFAULT_PANEL
    transcript: list[dict] = []

    def step(role: str, agent: str, question: str, context: str = "") -> str:
        if progress:
            progress(role)
        text = ask(agent, question, context)
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


def extract_condition_from_ic(ic_result: dict) -> dict | None:
    """CIO 결정 텍스트에서 매매 조건을 파싱 (best-effort). 파싱 실패 시 None.

    결정문에 '종목코드 XXXXXX', '목표가 NNNNNN', '방향 매수/매도' 패턴을 찾아 반환.
    """
    text = ic_result.get("decision", "")
    sym_m = re.search(r"(?:종목코드|종목)[:\s]+([A-Z0-9]{6})", text)
    price_m = re.search(r"목표가[:\s]+([0-9,]+)", text)
    side_m = re.search(r"(매수|매도|BUY|SELL)", text, re.I)
    qty_m = re.search(r"수량[:\s]+([0-9]+)주?", text)
    if not (sym_m and price_m and side_m):
        return None
    side_raw = side_m.group(1).upper()
    side = "BUY" if side_raw in ("매수", "BUY") else "SELL"
    return {
        "symbol": sym_m.group(1),
        "side": side,
        "target_price": float(price_m.group(1).replace(",", "")),
        "quantity": int(qty_m.group(1)) if qty_m else 1,
    }
