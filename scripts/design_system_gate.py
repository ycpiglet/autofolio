#!/usr/bin/env python3
"""Advisory design-system drift gate for the Next.js UI."""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB_SRC = Path("web/src")
TOKEN_LITERAL_ALLOWLIST = {
    "web/src/app/globals.css",
    "web/src/lib/design-tokens.ts",
}
RAW_COLOR_RE = re.compile(r"#(?:[0-9A-Fa-f]{3,8})\b|rgba?\(")
BARE_CONTROL_RE = re.compile(r"<(button|input|select|textarea)\b", re.IGNORECASE)
CLASSNAME_RE = re.compile(r'className="([^"]+)"')
DEFAULT_PAGE_LIMIT_BYTES = 12_000
REPEATED_CLASS_MIN_CHARS = 40
REPEATED_CLASS_MIN_COUNT = 3


@dataclass(frozen=True)
class Finding:
    severity: str
    category: str
    path: str
    detail: str


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _iter_source_files(root: Path) -> list[Path]:
    src = root / WEB_SRC
    if not src.exists():
        return []
    out: list[Path] = []
    for suffix in ("*.tsx", "*.ts", "*.css"):
        out.extend(src.rglob(suffix))
    return sorted(path for path in out if path.is_file())


def analyze(root: Path = ROOT, page_limit_bytes: int = DEFAULT_PAGE_LIMIT_BYTES) -> tuple[list[Finding], list[Finding]]:
    """Return (findings, warnings).

    The first baseline is warning-first. Hard failures are reserved for future
    promotion after cleanup, so current known drift does not block unrelated work.
    """
    findings: list[Finding] = []
    warnings: list[Finding] = []

    for path in _iter_source_files(root):
        rel = _rel(root, path)
        text = _read(path)
        if rel not in TOKEN_LITERAL_ALLOWLIST:
            matches = RAW_COLOR_RE.findall(text)
            if matches:
                examples = ", ".join(sorted(set(matches))[:5])
                warnings.append(
                    Finding(
                        "warn",
                        "raw-color-literal",
                        rel,
                        f"{len(matches)} raw color literal(s); move repeatable values to design tokens or token bridge helpers. examples={examples}",
                    )
                )

    app_dir = root / "web" / "src" / "app"
    if app_dir.exists():
        repeated_classes: dict[str, set[str]] = defaultdict(set)
        for page in sorted(app_dir.rglob("page.tsx")):
            rel = _rel(root, page)
            text = _read(page)
            size = len(text.encode("utf-8"))
            if size > page_limit_bytes:
                warnings.append(
                    Finding(
                        "warn",
                        "oversized-page",
                        rel,
                        f"{size} bytes exceeds {page_limit_bytes}; page should stay focused on layout and data wiring.",
                    )
                )

            controls = BARE_CONTROL_RE.findall(text)
            if controls:
                names = ", ".join(sorted(set(c.lower() for c in controls)))
                warnings.append(
                    Finding(
                        "warn",
                        "bare-control-in-page",
                        rel,
                        f"{len(controls)} native control(s) ({names}); prefer components/ui primitives or extract a pattern.",
                    )
                )

            for match in CLASSNAME_RE.finditer(text):
                value = " ".join(match.group(1).split())
                if len(value) >= REPEATED_CLASS_MIN_CHARS:
                    repeated_classes[value].add(rel)

        for class_name, paths in sorted(repeated_classes.items(), key=lambda item: (-len(item[1]), item[0])):
            if len(paths) < REPEATED_CLASS_MIN_COUNT:
                continue
            sample = class_name[:100] + ("..." if len(class_name) > 100 else "")
            warnings.append(
                Finding(
                    "warn",
                    "repeated-class-cluster",
                    ", ".join(sorted(paths)[:3]),
                    f"class cluster appears in {len(paths)} page files; extract a primitive or pattern. className={sample}",
                )
            )

    return findings, warnings


def render(findings: list[Finding], warnings: list[Finding]) -> str:
    status = "fail" if findings else "watch" if warnings else "pass"
    lines = [
        f"design-system-gate: {status}",
        f"findings={len(findings)}",
    ]
    for finding in findings:
        lines.append(f"- {finding.category}: {finding.path}: {finding.detail}")
    lines.append(f"warnings={len(warnings)}")
    for warning in warnings:
        lines.append(f"- {warning.category}: {warning.path}: {warning.detail}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Autofolio design-system drift gate")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--page-limit-bytes", type=int, default=DEFAULT_PAGE_LIMIT_BYTES)
    parser.add_argument("--check", action="store_true", help="return non-zero for findings")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    findings, warnings = analyze(root, page_limit_bytes=args.page_limit_bytes)
    print(render(findings, warnings))
    if args.check and findings:
        return 1
    if args.check and args.strict and warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
