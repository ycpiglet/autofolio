from pathlib import Path

import scripts.check_upstream_issues as check_upstream_issues


def test_find_unreported_flags_agent_runtime_signal_without_issue(tmp_path: Path):
    notes = tmp_path / "agents" / "research_agent" / "notes"
    notes.mkdir(parents=True)
    (notes / "EVIDENCE-2026-06-12-001.md").write_text(
        "---\nscope: agent_runtime upstream\n---\n"
        "site-packages/agent_runtime/sync.py failed\n",
        encoding="utf-8",
    )

    findings = check_upstream_issues.find_unreported(tmp_path)

    assert len(findings) == 1
    assert findings[0].path.endswith("EVIDENCE-2026-06-12-001.md")


def test_find_unreported_ignores_issue_reference(tmp_path: Path):
    notes = tmp_path / "agents" / "research_agent" / "notes"
    notes.mkdir(parents=True)
    (notes / "EVIDENCE-2026-06-12-002.md").write_text(
        "---\nscope: agent_runtime upstream\n---\n"
        "Reported at https://github.com/ycpiglet/agent_runtime/issues/19\n",
        encoding="utf-8",
    )

    assert check_upstream_issues.find_unreported(tmp_path) == []


def test_find_unreported_ignores_autofolio_only_text(tmp_path: Path):
    notes = tmp_path / "agents" / "research_agent" / "notes"
    notes.mkdir(parents=True)
    (notes / "EVIDENCE-2026-06-12-003.md").write_text(
        "Autofolio local script check_upstream_issues.py is missing.\n",
        encoding="utf-8",
    )

    assert check_upstream_issues.find_unreported(tmp_path) == []
