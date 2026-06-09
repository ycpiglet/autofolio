#!/usr/bin/env python3
"""업스트림(agent_runtime) 버그 보고 자동화 — Issue + 패치 PR 생성. [Autofolio 자동화]

사용:
  python scripts/report_upstream_bug.py --id BUG-001 --dry-run   # 내용 미리보기
  python scripts/report_upstream_bug.py --id BUG-001             # 실제 Issue + PR 생성
  python scripts/report_upstream_bug.py --evidence EVIDENCE-2026-06-09-001-agent-runtime-bugs.md

분류 규칙 (is_upstream_bug):
  - agent_runtime 패키지 파일 경로 포함: site-packages/agent_runtime/**
  - 업스트림 스크립트 파일: scripts/ 내 agent_runtime 프레임워크 스크립트
  - 에러 타입이 AttributeError/UnicodeEncodeError + agent_runtime 콜스택
  - EVIDENCE 파일의 scope 필드에 'agent_runtime upstream' 포함

보고 형식 (육하원칙 + BRIEF):
  GitHub Issue = Executive BRIEF v2 (frontmatter + Bottom Line + Signal + 재현 + 수정방향)
  GitHub PR    = 패치 코드 + 검증 증거

강제 규칙 (AGENTS.md §6 Autonomous Delivery Lane):
  - 에러 발생 → 분류(is_upstream_bug) → True면 72h 내 Issue 필수
  - 패치 가능하면 PR 동반
  - 미보고 시 SessionStart 훅이 WARN
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_REPO = "ycpiglet/agent_runtime"
EVIDENCE_DIR = ROOT / "agents" / "research_agent" / "notes"

# ---- 분류기 ----

UPSTREAM_SIGNALS = [
    re.compile(r"site-packages[\\/]agent_runtime"),
    re.compile(r"agent_runtime\.sync|agent_runtime\.config|agent_runtime\."),
    re.compile(r"in agent_runtime", re.I),
]


def is_upstream_bug(evidence_path: Path) -> tuple[bool, str]:
    """EVIDENCE 파일을 읽어 upstream bug 여부를 판정한다."""
    text = evidence_path.read_text(encoding="utf-8", errors="replace")
    if "agent_runtime upstream" in text or "upstream agent_runtime" in text:
        return True, "EVIDENCE scope에 'agent_runtime upstream' 포함"
    for sig in UPSTREAM_SIGNALS:
        m = sig.search(text)
        if m:
            return True, f"upstream 스택트레이스 패턴 발견: '{m.group()}'"
    return False, "upstream 신호 없음 — 로컬 버그로 판단"


# ---- EVIDENCE 파싱 ----

def parse_bugs_from_evidence(path: Path) -> list[dict]:
    """EVIDENCE 파일에서 BUG-NNN 항목들을 파싱한다."""
    text = path.read_text(encoding="utf-8", errors="replace")
    bugs = []
    # "## BUG-NNN:" 패턴
    blocks = re.split(r"(?=^## BUG-\d{3})", text, flags=re.M)
    for block in blocks:
        m = re.match(r"## (BUG-\d{3}): (.+?)$", block, re.M)
        if not m:
            continue
        bug_id, title = m.group(1), m.group(2)
        # 심각도
        sev_m = re.search(r"\|\s*심각도\s*\|\s*(.+?)\s*\|", block)
        severity = sev_m.group(1).strip() if sev_m else "Medium"
        # 소속
        owner_m = re.search(r"\|\s*소속\s*\|\s*(.+?)\s*\|", block)
        owner = owner_m.group(1).strip() if owner_m else "upstream agent_runtime"
        bugs.append({
            "id": bug_id, "title": title.strip("`").strip(),
            "severity": severity, "owner": owner,
            "body_block": block,
        })
    return bugs


# ---- Issue 본문 생성 ----

def make_issue_body(bug: dict, evidence_path: Path) -> str:
    block = bug["body_block"]
    # 육하원칙 표 추출
    table_m = re.search(r"(\| 항목 \| 내용 \|.+?)(?=###|\Z)", block, re.S)
    table = table_m.group(1).strip() if table_m else "(표 없음)"
    # 재현 코드
    code_m = re.search(r"```python(.+?)```", block, re.S)
    repro = f"```python{code_m.group(1)}```" if code_m else "(재현 코드 없음)"
    # 올바른 호출
    fix_m = re.findall(r"```python(.+?)```", block, re.S)
    fix = f"```python{fix_m[1]}```" if len(fix_m) >= 2 else "(수정 방향 별도 기술)"

    return f"""---
type: bug-report
reporter: Autofolio host (automated via scripts/report_upstream_bug.py)
evidence: agents/research_agent/notes/{evidence_path.name}
autofolio_pr: https://github.com/ycpiglet/autofolio/pull/3
severity: {bug['severity']}
---

## Bottom Line

{bug['id']}: **{bug['title']}** — Autofolio 업그레이드(v0.1.5→v0.1.8) 중 재현됨. 패치 필요.

## 육하원칙 (6W1H)

{table}

## 재현 코드

{repro}

## 수정 방향

{fix}

## 영향 범위

{bug['id']}를 포함한 agent_runtime 사용 호스트 프로젝트 전체 영향.
Windows 환경(cp949 콘솔)의 경우 BUG-002는 `sync --diff` 전혀 사용 불가.

## 참조

- Autofolio EVIDENCE: `agents/research_agent/notes/{evidence_path.name}`
- 재현 환경: Python 3.10, Windows 11, agent_runtime v0.1.8
- 관련 PR: https://github.com/ycpiglet/autofolio/pull/3
"""


# ---- GitHub 조작 ----

def gh(*args) -> str:
    r = subprocess.run(["gh", *args], capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} 실패: {r.stderr.strip()}")
    return r.stdout.strip()


def create_issue(title: str, body: str, labels: list[str], dry_run: bool) -> str | None:
    label_str = ",".join(labels)
    if dry_run:
        print(f"[DRY-RUN] gh issue create --repo {UPSTREAM_REPO}")
        print(f"  title: {title}")
        print(f"  labels: {label_str}")
        print(f"  body ({len(body)} chars):\n{body[:400]}...")
        return None
    # 라벨이 없으면 생성 시도
    url = gh("issue", "create", "--repo", UPSTREAM_REPO,
             "--title", title, "--body", body)
    print(f"  Issue created: {url}")
    return url


# ---- main ----

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="upstream bug report automation")
    ap.add_argument("--evidence", default=None, help="EVIDENCE 파일명(notes/ 기준)")
    ap.add_argument("--id", default=None, help="특정 BUG-NNN만 처리")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    # EVIDENCE 파일 탐색
    if args.evidence:
        ev_path = EVIDENCE_DIR / args.evidence
    else:
        # 최신 EVIDENCE 파일 자동 탐색
        candidates = sorted(EVIDENCE_DIR.glob("EVIDENCE-*.md"), reverse=True)
        if not candidates:
            print("[WARN] EVIDENCE 파일을 못 찾음.")
            return 1
        ev_path = candidates[0]

    if not ev_path.exists():
        print(f"[ERROR] 파일 없음: {ev_path}")
        return 1

    print(f"[info] EVIDENCE: {ev_path.name}")
    is_up, reason = is_upstream_bug(ev_path)
    print(f"[classify] upstream bug: {is_up} — {reason}")
    if not is_up:
        print("[skip] upstream 버그 아님 → Issue 생성 안 함.")
        return 0

    bugs = parse_bugs_from_evidence(ev_path)
    if not bugs:
        print("[WARN] BUG 항목을 파싱 못함. EVIDENCE 형식 확인 필요.")
        return 1

    target_bugs = [b for b in bugs if args.id is None or b["id"] == args.id]
    if not target_bugs:
        print(f"[WARN] '{args.id}'를 EVIDENCE에서 찾지 못함. 사용 가능: {[b['id'] for b in bugs]}")
        return 1

    upstream_bugs = [b for b in target_bugs if "upstream" in b["owner"].lower()]
    if not upstream_bugs:
        print("[skip] 대상 BUG들이 모두 로컬 버그 → upstream Issue 불필요.")
        return 0

    issues_created = []
    for bug in upstream_bugs:
        title = f"[{bug['severity']}] {bug['id']}: {bug['title']}"
        body = make_issue_body(bug, ev_path)
        print(f"\n=== {bug['id']} ===")
        url = create_issue(title, body, ["bug", "needs-triage"], args.dry_run)
        if url:
            issues_created.append((bug["id"], url))

    if issues_created and not args.dry_run:
        print(f"\n[완료] Issue {len(issues_created)}건 생성:")
        for bug_id, url in issues_created:
            print(f"  {bug_id}: {url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
