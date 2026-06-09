#!/usr/bin/env python3
"""자율 머지 거버넌스 우선순위 점검 — 업스트림 §3.5 가 생기면 교체를 강제한다.

배경: `auto_merge.py`(프레임워크 ①)는 `AGENTS.md §3.5` 를 근거로 대지만 그 조항은 업스트림에
미커밋이라, 호스트가 [agents/lead_engineer/MERGE-POLICY.md] + `AGENTS.md` 오버레이 §15 로
**잠정 정본**을 둔다. 우선순위는 "업스트림 우선": 설치된 업스트림 템플릿 `AGENTS.md` 가
§3.5(자율 머지 거버넌스)를 얻으면 그쪽이 정본이 되고 호스트 잠정분은 애드덤으로 축소된다.

이 스크립트는 그 트리거를 감지한다.
  - 업스트림 §3.5 발견  → 교체(precedence swap) 지시 + **exit 1**(강제 주의).
  - 미발견(현재 상태)    → 호스트 잠정 정책 활성 + exit 0.
  - 템플릿 위치 불가     → 점검 불가 경고 + exit 0(환경 문제, 거짓경보 방지).

연결: docs/AGENT_RUNTIME_INTEGRATION.md §3.1 / §4 런북 4-bis, MERGE-POLICY.md §우선순위.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:  # Windows 콘솔 UTF-8
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]

# §3.5 헤더(예: "## 3.5", "### 3.5.2 ...") 또는 자율-머지 거버넌스 헤더 키워드.
_HEADER_35 = re.compile(r"^#{2,4}\s*3\.5(?:\b|\.|\s)", re.M)
_MERGE_KEYS = re.compile(r"(auto[- ]?merge|autonomous\s+merge|자율\s*머지|merge\s*gate)", re.I)


def find_template_agents_md() -> Path | None:
    """설치된 agent_runtime 템플릿의 AGENTS.md 경로를 찾는다(import → venv 경로 폴백)."""
    try:
        import agent_runtime  # noqa: WPS433

        cand = Path(agent_runtime.__file__).parent / "templates" / "project" / "AGENTS.md"
        if cand.exists():
            return cand
    except Exception:
        pass
    for rel in (
        ".venv/Lib/site-packages/agent_runtime/templates/project/AGENTS.md",
        "venv/Lib/site-packages/agent_runtime/templates/project/AGENTS.md",
        ".venv/lib/python3*/site-packages/agent_runtime/templates/project/AGENTS.md",
    ):
        for cand in ROOT.glob(rel):
            if cand.exists():
                return cand
    return None


def upstream_has_section_35(text: str) -> tuple[bool, str]:
    m = _HEADER_35.search(text)
    if m:
        return True, "업스트림 템플릿 AGENTS.md 에 '§3.5' 헤더 존재"
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("#") and _MERGE_KEYS.search(stripped):
            return True, f"업스트림 머지 거버넌스 헤더 발견: {stripped.strip()}"
    return False, ""


def main() -> int:
    template = find_template_agents_md()
    if template is None:
        print("[WARN] 업스트림 템플릿 AGENTS.md 를 못 찾음(agent_runtime 미설치?). 우선순위 점검 불가 — 호스트 잠정 정책 유지.")
        return 0

    text = template.read_text(encoding="utf-8")
    has_35, why = upstream_has_section_35(text)
    if has_35:
        print("[ACTION REQUIRED] 업스트림이 자율 머지 거버넌스(§3.5)를 도입했습니다 — 우선순위 교체 필요.")
        print(f"  근거: {why}")
        print(f"  템플릿: {template}")
        print("  교체 절차(MERGE-POLICY.md §우선순위 / INTEGRATION §3.1):")
        print("   1) 업스트림 §3.5 전부 채택(정본) — §4-4 로 AGENTS.md 본문에 수동 병합")
        print("   2) agents/lead_engineer/MERGE-POLICY.md → Autofolio R3 surface 애드덤만 잔존")
        print("   3) AGENTS.md 오버레이 §15 → 한 줄 포인터로 축소")
        print("   4) INTEGRATION §3.1 을 '반영 완료'로 갱신")
        return 1

    print("[OK] 업스트림 §3.5 미존재 — 호스트 잠정 정책(MERGE-POLICY.md + AGENTS.md §15) 활성. 충돌 없음.")
    print(f"  점검 대상: {template}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
