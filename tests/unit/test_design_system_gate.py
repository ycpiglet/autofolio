"""Tests for scripts/design_system_gate.py (TASK-140 closeout).

TDD order:
  1. This file was written BEFORE the gate module existed (RED).
  2. Gate implemented → all tests green (GREEN).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from scripts.design_system_gate import (
    check_format_single_source,
    check_license_notices,
    check_no_runtime_cdn,
    check_palette_namespace,
    run_all_checks,
)

# ── helpers ──────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parents[2]
REAL_WEB_SRC = REPO_ROOT / "web" / "src"
REAL_CHART_PALETTE = REAL_WEB_SRC / "lib" / "chart-palette.ts"
REAL_FORMAT = REAL_WEB_SRC / "lib" / "format.ts"
REAL_DOCS_RESEARCH = REPO_ROOT / "docs" / "research"


# ── CDN runtime check ─────────────────────────────────────────────────────────

class TestNoRuntimeCdn:
    def test_passes_on_actual_web_src(self):
        """The live web/src must have 0 runtime CDN references."""
        assert check_no_runtime_cdn(REAL_WEB_SRC) == []

    def test_comment_mentioning_cdn_is_not_flagged(self, tmp_path: Path):
        """A JSDoc comment like '* Downloaded from: https://cdn.jsdelivr.net/...' must not fire."""
        f = tmp_path / "layout.tsx"
        f.write_text(
            " * Downloaded from: https://cdn.jsdelivr.net/gh/orioncactus/pretendard/...\n"
            "const font = localFont({ src: '../fonts/Pretendard.woff2' });\n"
        )
        assert check_no_runtime_cdn(tmp_path) == []

    def test_fails_on_css_import_url(self, tmp_path: Path):
        """@import url(https://fonts.googleapis.com/...) must be flagged (RED fixture)."""
        (tmp_path / "bad.css").write_text(
            "@import url(https://fonts.googleapis.com/css2?family=Inter);\n"
        )
        findings = check_no_runtime_cdn(tmp_path)
        assert findings, "expected at least one CDN finding"
        assert any("bad.css" in f for f in findings)

    def test_fails_on_script_cdn_src(self, tmp_path: Path):
        """<script src='https://cdn.example.com/...'> must be flagged."""
        (tmp_path / "layout.tsx").write_text(
            "<script src=\"https://cdn.example.com/lib.min.js\"></script>\n"
        )
        findings = check_no_runtime_cdn(tmp_path)
        assert findings, "expected at least one CDN finding"

    def test_ignores_relative_css_imports(self, tmp_path: Path):
        """@import 'tailwindcss' without a URL must not be flagged."""
        (tmp_path / "globals.css").write_text(
            '@import "tailwindcss";\n@import "tw-animate-css";\n'
        )
        assert check_no_runtime_cdn(tmp_path) == []


# ── Palette namespace check ───────────────────────────────────────────────────

class TestPaletteNamespace:
    def test_passes_on_actual_chart_palette(self):
        """The live chart-palette.ts must pass namespace separation."""
        assert check_palette_namespace(REAL_CHART_PALETTE) == []

    def test_fails_when_pnl_export_missing(self, tmp_path: Path):
        """chart-palette.ts with no pnl* export must fail."""
        f = tmp_path / "chart-palette.ts"
        f.write_text("export const categoricalOrder = ['#0072B2'];\n"
                     "export const sequentialViridis = ['#440154'];\n")
        findings = check_palette_namespace(f)
        assert findings, "expected pnl-namespace finding"
        assert any("PnL" in finding or "pnl" in finding.lower() for finding in findings)

    def test_fails_when_categorical_export_missing(self, tmp_path: Path):
        """chart-palette.ts with no categorical* export must fail."""
        f = tmp_path / "chart-palette.ts"
        f.write_text("export const pnlDivergingRampKR = ['#0571b0'];\n"
                     "export const sequentialViridis = ['#440154'];\n")
        findings = check_palette_namespace(f)
        assert findings, "expected categorical-namespace finding"

    def test_fails_when_sequential_export_missing(self, tmp_path: Path):
        """chart-palette.ts with no sequential* export must fail."""
        f = tmp_path / "chart-palette.ts"
        f.write_text("export const pnlDivergingRampKR = ['#0571b0'];\n"
                     "export const categoricalOrder = ['#0072B2'];\n")
        findings = check_palette_namespace(f)
        assert findings, "expected sequential-namespace finding"

    def test_fails_when_file_missing(self, tmp_path: Path):
        """A missing chart-palette.ts must fail."""
        findings = check_palette_namespace(tmp_path / "chart-palette.ts")
        assert findings


# ── Format single-source check ────────────────────────────────────────────────

class TestFormatSingleSource:
    def test_passes_on_actual_format_ts(self):
        """The live format.ts must export fmtWonShort."""
        assert check_format_single_source(REAL_FORMAT) == []

    def test_fails_when_file_missing(self, tmp_path: Path):
        """A missing format.ts must fail."""
        findings = check_format_single_source(tmp_path / "format.ts")
        assert findings

    def test_fails_when_fmtwonshort_not_exported(self, tmp_path: Path):
        """format.ts without fmtWonShort export must fail (RED fixture)."""
        f = tmp_path / "format.ts"
        f.write_text("export function fmtWon(v: number): string { return ''; }\n")
        findings = check_format_single_source(f)
        assert findings, "expected fmtWonShort finding"
        assert any("fmtWonShort" in finding for finding in findings)

    def test_passes_when_fmtwonshort_exported(self, tmp_path: Path):
        """format.ts with fmtWonShort export must pass."""
        f = tmp_path / "format.ts"
        f.write_text("export function fmtWonShort(v: number): string { return ''; }\n")
        assert check_format_single_source(f) == []


# ── License notices check ─────────────────────────────────────────────────────

class TestLicenseNotices:
    def test_passes_on_actual_docs_research(self):
        """docs/research/ must contain a third-party-notices* file."""
        assert check_license_notices(REAL_DOCS_RESEARCH) == []

    def test_fails_when_no_notice_file(self, tmp_path: Path):
        """An empty dir must fail (RED fixture)."""
        findings = check_license_notices(tmp_path)
        assert findings, "expected missing-notices finding"

    def test_passes_when_notice_file_present(self, tmp_path: Path):
        """Any third-party-notices* file satisfies the check."""
        (tmp_path / "third-party-notices-draft.md").write_text("# Notices\n")
        assert check_license_notices(tmp_path) == []


# ── Integration: run_all_checks on live repo ─────────────────────────────────

class TestRunAllChecks:
    def test_live_repo_passes_all_checks(self):
        """The current repo must pass every design system invariant."""
        findings = run_all_checks()
        assert findings == [], f"gate findings: {findings}"
