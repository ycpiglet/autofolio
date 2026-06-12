#!/usr/bin/env python3
"""Warn about upstream agent_runtime bugs that lack a GitHub issue reference.

This is a lightweight session-start check for Autofolio's AGENTS.md overlay.
It does not contact GitHub. It scans local evidence and audit notes for
agent_runtime-upstream signals and reports records that do not mention an
agent_runtime issue URL or issue number.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]

UPSTREAM_PATTERNS = [
    re.compile(r"site-packages[\\/]agent_runtime", re.I),
    re.compile(r"\bagent_runtime upstream\b", re.I),
    re.compile(r"\bupstream agent_runtime\b", re.I),
    re.compile(r"\bagent_runtime\.(sync|config|cli|templates)\b", re.I),
]
REPORTED_PATTERNS = [
    re.compile(r"https://github\.com/ycpiglet/agent_runtime/issues/\d+", re.I),
    re.compile(r"\bycpiglet/agent_runtime#\d+\b", re.I),
    re.compile(r"\bagent_runtime\s+Issue\s+#?\d+\b", re.I),
]


@dataclass
class Finding:
    path: str
    reason: str


def _is_upstream_text(text: str) -> str | None:
    for pattern in UPSTREAM_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group(0)
    return None


def _has_issue_reference(text: str) -> bool:
    return any(pattern.search(text) for pattern in REPORTED_PATTERNS)


def candidate_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    notes = root / "agents" / "research_agent" / "notes"
    if notes.exists():
        paths.extend(sorted(notes.glob("EVIDENCE-*.md")))
    for rel in [
        Path("agents/lead_engineer/AUDIT-LOG.md"),
        Path(".remember/now.md"),
    ]:
        path = root / rel
        if path.exists():
            paths.append(path)
    return paths


def find_unreported(root: Path = ROOT) -> list[Finding]:
    findings: list[Finding] = []
    for path in candidate_paths(root):
        text = path.read_text(encoding="utf-8", errors="replace")
        reason = _is_upstream_text(text)
        if reason and not _has_issue_reference(text):
            findings.append(
                Finding(path=path.relative_to(root).as_posix(), reason=reason)
            )
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--warn", action="store_true", help="print warnings and exit 0")
    parser.add_argument("--strict", action="store_true", help="exit 1 when findings exist")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)

    findings = find_unreported(ROOT)
    if args.json:
        print(json.dumps([asdict(item) for item in findings], ensure_ascii=False, indent=2))
    elif findings:
        for item in findings:
            print(f"WARN: unreported upstream bug signal in {item.path}: {item.reason}")
    else:
        print("OK: no unreported upstream bug signals")

    if args.strict and findings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
