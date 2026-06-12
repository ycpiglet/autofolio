from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("doc_steward_due.py")
SPEC = importlib.util.spec_from_file_location("doc_steward_due", MODULE_PATH)
doc_steward_due = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules["doc_steward_due"] = doc_steward_due
SPEC.loader.exec_module(doc_steward_due)


def _set_roots(monkeypatch, tmp_path: Path) -> None:
    agents = tmp_path / "agents"
    monkeypatch.setattr(doc_steward_due, "ROOT", tmp_path)
    monkeypatch.setattr(doc_steward_due, "AGENTS", agents)
    monkeypatch.setattr(doc_steward_due, "CLAUDE_MD", tmp_path / "CLAUDE.md")
    monkeypatch.setattr(doc_steward_due, "LEAD", agents / "lead_engineer")
    monkeypatch.setattr(doc_steward_due, "REVIEWS", agents / "lead_engineer" / "reviews")


def _write_cycle(tmp_path: Path, cycle_id: int, status: str) -> None:
    lead = tmp_path / "agents" / "lead_engineer"
    lead.mkdir(parents=True, exist_ok=True)
    (lead / f"CYCLE-{cycle_id:03d}.md").write_text(
        f"# CYCLE-{cycle_id:03d}\n\n상태: {status}\n",
        encoding="utf-8",
    )


def test_missing_review_ignores_in_progress_cycle(monkeypatch, tmp_path):
    _set_roots(monkeypatch, tmp_path)
    _write_cycle(tmp_path, 1, "진행 중")

    assert doc_steward_due.missing_review() == -1


def test_missing_review_flags_completed_cycle(monkeypatch, tmp_path):
    _set_roots(monkeypatch, tmp_path)
    _write_cycle(tmp_path, 1, "완료")

    assert doc_steward_due.missing_review() == 1


def test_missing_review_accepts_completed_cycle_with_review(monkeypatch, tmp_path):
    _set_roots(monkeypatch, tmp_path)
    _write_cycle(tmp_path, 1, "완료")
    reviews = tmp_path / "agents" / "lead_engineer" / "reviews"
    reviews.mkdir(parents=True, exist_ok=True)
    (reviews / "REVIEW-001.md").write_text("[REVIEW]\n", encoding="utf-8")

    assert doc_steward_due.missing_review() == -1
