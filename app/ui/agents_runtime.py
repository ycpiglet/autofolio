"""에이전트 실연결 — .claude/agents 페르소나 + .claude/skills 지식을 Anthropic API로 구동. (P2)

ANTHROPIC_API_KEY가 없거나 anthropic 패키지가 없으면 결정적 스텁으로 폴백한다(데모/오프라인).
"""
from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path

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
        out[short] = {"name": name, "system": body, "skill": skill_name, "skill_body": skill_body}

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
            }
    return out


def list_agents() -> list[str]:
    return sorted(_personas().keys())


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
