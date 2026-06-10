#!/usr/bin/env python3
"""PR 자동 코드 리뷰 — independent-auditor 서브에이전트 호출. [Autofolio 자동화]

사용:
  python scripts/review_pr.py <PR번호>          # PR diff 리뷰
  python scripts/review_pr.py <PR번호> --post   # GitHub 코멘트로 게시
  python scripts/review_pr.py --latest          # 최신 열린 PR 리뷰

AGENTS.md §17(upstream bug 분류) + §6(Autonomous Delivery Lane) 연계:
- upstream 버그 감지 시 scripts/report_upstream_bug.py 자동 호출
- 리뷰 결과는 .autofolio/reviews/REVIEW_PR{n}_*.md 에 저장
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
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

logger = get_logger("autofolio.review_pr")
_REVIEW_DIR = ROOT / ".autofolio" / "reviews"


def gh_json(pr: str, fields: str) -> dict:
    import json
    r = subprocess.run(
        ["gh", "pr", "view", pr, "--json", fields],
        capture_output=True, text=True, encoding="utf-8",
    )
    if r.returncode != 0:
        raise SystemExit(f"gh 실패: {r.stderr.strip()}")
    return json.loads(r.stdout)


def get_diff(pr: str) -> str:
    r = subprocess.run(
        ["gh", "pr", "diff", pr],
        capture_output=True, text=True, encoding="utf-8",
    )
    return r.stdout[:8000] if r.returncode == 0 else "(diff 조회 실패)"


def ask_agent_review(pr_title: str, diff: str) -> str:
    """independent-auditor에게 PR 리뷰 요청. API 키 없으면 스텁."""
    try:
        from app.ui import agents_runtime as ar
        ok, _ = ar.available()
        if not ok:
            return "[스텁] ANTHROPIC_API_KEY 미설정 — 실제 리뷰 생략"
        question = (
            f"다음 PR을 코드 리뷰해주세요.\n제목: {pr_title}\n\n"
            "체크 사항: 버그·보안취약점·agent_runtime 관련 오류·테스트 누락·안전규칙 위반.\n"
            "upstream(agent_runtime) 버그로 분류될 만한 내용이 있으면 명시.\n\n"
            f"[DIFF 요약 — 최대 6000자]\n{diff}"
        )
        return ar.ask("independent-auditor", question)
    except Exception as exc:  # noqa: BLE001
        return f"리뷰 에이전트 오류: {exc}"


def save_review(pr_num: str, title: str, review: str) -> Path:
    _REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = _REVIEW_DIR / f"REVIEW_PR{pr_num}_{ts}.md"
    path.write_text(
        f"# PR #{pr_num} 코드 리뷰\n\n"
        f"**제목**: {title}\n**시각**: {datetime.now().isoformat(timespec='seconds')}\n\n"
        f"---\n\n{review}\n",
        encoding="utf-8",
    )
    return path


def post_comment(pr_num: str, body: str) -> None:
    r = subprocess.run(
        ["gh", "pr", "comment", pr_num, "--body", body[:65000]],
        capture_output=True, text=True, encoding="utf-8",
    )
    if r.returncode != 0:
        logger.warning("코멘트 게시 실패: %s", r.stderr.strip())
    else:
        logger.info("코멘트 게시 완료: PR #%s", pr_num)


def main() -> int:
    ap = argparse.ArgumentParser(description="PR 자동 코드 리뷰")
    ap.add_argument("pr", nargs="?", help="PR 번호")
    ap.add_argument("--latest", action="store_true", help="최신 열린 PR 자동 선택")
    ap.add_argument("--post", action="store_true", help="리뷰를 GitHub 코멘트로 게시")
    args = ap.parse_args()

    if args.latest:
        import json
        r = subprocess.run(
            ["gh", "pr", "list", "--json", "number,title", "--limit", "1"],
            capture_output=True, text=True, encoding="utf-8",
        )
        prs = json.loads(r.stdout)
        if not prs:
            print("[skip] 열린 PR 없음")
            return 0
        pr_num = str(prs[0]["number"])
    elif args.pr:
        pr_num = args.pr
    else:
        ap.print_help()
        return 1

    info = gh_json(pr_num, "number,title")
    title = info.get("title", "?")
    print(f"[review] PR #{pr_num}: {title}")

    diff = get_diff(pr_num)
    review = ask_agent_review(title, diff)
    path = save_review(pr_num, title, review)
    print(f"[review] 저장: {path}")
    print("\n" + review[:1000])

    if args.post:
        post_comment(pr_num, f"🤖 **자동 코드 리뷰** (independent-auditor)\n\n{review[:65000]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
