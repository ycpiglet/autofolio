"""Design system gate for Autofolio (TASK-140).

Checks that the adopted visual-asset design system invariants hold in web/src:

  1. No runtime CDN usage - self-host only.
       Rejects: @import url(https://...) in CSS,
                <link rel=stylesheet href="https://..."> in HTML/JSX,
                <script src="https://..."> in HTML/JSX.
       Ignores comment lines (// * /*).

  2. chart-palette.ts exposes PnL-semantic AND categorical AND sequential
     palette exports (namespace-separated so series colors never collide with
     up/down meaning).

  3. format.ts single-sources number formatting - fmtWonShort is exported.

  4. Third-party license notices file is present under docs/research/.

Usage:
  python scripts/design_system_gate.py --check
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

WEB_SRC = REPO_ROOT / "web" / "src"
CHART_PALETTE = WEB_SRC / "lib" / "chart-palette.ts"
FORMAT_FILE = WEB_SRC / "lib" / "format.ts"
DOCS_RESEARCH = REPO_ROOT / "docs" / "research"

# Source extensions to scan for CDN patterns.
_SCAN_EXTENSIONS = {".ts", ".tsx", ".css", ".html"}

# Patterns that indicate actual runtime CDN asset loading.
_CDN_PATTERNS = [
    # CSS: @import url(https://...)
    re.compile(r"@import\s+url\s*\(\s*['\"]?https?://", re.IGNORECASE),
    # HTML/JSX: <link rel="stylesheet" href="https://..."> (attribute order varies)
    re.compile(
        r'<link\b[^>]*\brel\s*=\s*["\']stylesheet["\'][^>]*\bhref\s*=\s*["\']https?://',
        re.IGNORECASE,
    ),
    re.compile(
        r'<link\b[^>]*\bhref\s*=\s*["\']https?://[^"\']*["\'][^>]*\brel\s*=\s*["\']stylesheet["\']',
        re.IGNORECASE,
    ),
    # HTML/JSX: <script src="https://...">
    re.compile(r'<script\b[^>]*\bsrc\s*=\s*["\']https?://', re.IGNORECASE),
]


def _is_comment_line(line: str) -> bool:
    """Return True if the line is a code comment and should be skipped."""
    stripped = line.strip()
    return (
        stripped.startswith("//")
        or stripped.startswith("*")
        or stripped.startswith("/*")
    )


def check_no_runtime_cdn(web_src_dir: Path = WEB_SRC) -> list[str]:
    """Scan web/src for runtime CDN asset references. Returns findings list."""
    findings: list[str] = []
    if not web_src_dir.is_dir():
        return [f"web/src directory not found: {web_src_dir}"]

    for path in sorted(web_src_dir.rglob("*")):
        if not path.is_file() or path.suffix not in _SCAN_EXTENSIONS:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if _is_comment_line(line):
                continue
            for pattern in _CDN_PATTERNS:
                if pattern.search(line):
                    try:
                        rel = path.relative_to(web_src_dir)
                    except ValueError:
                        rel = path
                    findings.append(
                        f"runtime CDN reference: {rel}:{lineno}: {line.strip()[:120]}"
                    )
                    break  # one finding per line

    return findings


def check_palette_namespace(chart_palette_file: Path = CHART_PALETTE) -> list[str]:
    """Check chart-palette.ts exposes PnL, categorical, AND sequential exports."""
    # Verifies STRUCTURAL namespace separation (pnl*/categorical*/sequential* exports exist),
    # NOT WCAG contrast / CVD color-value quality (validated at original adoption, PR #98/#119).
    findings: list[str] = []
    if not chart_palette_file.is_file():
        return [f"chart-palette.ts not found: {chart_palette_file}"]

    text = chart_palette_file.read_text(encoding="utf-8")

    if not re.search(r"\bexport\b[^\n]*(pnl|Pnl|PnL)", text):
        findings.append(
            "chart-palette.ts: missing PnL-semantic export "
            "(expected pnl*/Pnl*/PnL* named export)"
        )
    if not re.search(r"\bexport\b[^\n]*[Cc]ategorical", text):
        findings.append(
            "chart-palette.ts: missing categorical palette export "
            "(expected categorical* named export)"
        )
    if not re.search(r"\bexport\b[^\n]*[Ss]equential", text):
        findings.append(
            "chart-palette.ts: missing sequential palette export "
            "(expected sequential* named export)"
        )

    return findings


def check_format_single_source(format_file: Path = FORMAT_FILE) -> list[str]:
    """Check that format.ts exports fmtWonShort."""
    findings: list[str] = []
    if not format_file.is_file():
        return [f"format.ts not found: {format_file}"]

    text = format_file.read_text(encoding="utf-8")
    if not re.search(r"\bexport\b[^\n]*\bfmtWonShort\b", text):
        findings.append(
            "format.ts: fmtWonShort is not exported "
            "(number formatting must single-source through this function)"
        )

    return findings


def check_license_notices(docs_research_dir: Path = DOCS_RESEARCH) -> list[str]:
    """Check that at least one third-party-notices* file exists under docs/research/."""
    findings: list[str] = []
    if not docs_research_dir.is_dir():
        return [f"docs/research directory not found: {docs_research_dir}"]

    notices = list(docs_research_dir.glob("third-party-notices*"))
    if not notices:
        findings.append(
            "no third-party-notices* file found under docs/research/ "
            "(license NOTICE for adopted OSS deps required)"
        )

    return findings


def run_all_checks(
    web_src_dir: Path = WEB_SRC,
    chart_palette_file: Path = CHART_PALETTE,
    format_file: Path = FORMAT_FILE,
    docs_research_dir: Path = DOCS_RESEARCH,
) -> list[str]:
    """Run every design system invariant check and return all findings."""
    findings: list[str] = []
    findings.extend(check_no_runtime_cdn(web_src_dir))
    findings.extend(check_palette_namespace(chart_palette_file))
    findings.extend(check_format_single_source(format_file))
    findings.extend(check_license_notices(docs_research_dir))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate design system invariants; exit non-zero on findings",
    )
    args = parser.parse_args(argv)

    if not args.check:
        parser.print_help()
        return 0

    findings = run_all_checks()
    if findings:
        print("design_system_gate: FAIL")
        for finding in findings:
            print(f"  - {finding}")
        return 1

    print("design_system_gate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
