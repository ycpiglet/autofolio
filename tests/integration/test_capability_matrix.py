"""Lightweight structural tests for BROKER-CAPABILITY-PARITY-MATRIX.md.

Verifies that the capability matrix document exists, contains all required
sections, and that the status legend defines the required labels. Does NOT
test product behavior — this is a doc-gate test only.
"""
from __future__ import annotations

from pathlib import Path

import pytest

_MATRIX_PATH = (
    Path(__file__).parents[2] / "docs" / "BROKER-CAPABILITY-PARITY-MATRIX.md"
)

# Required top-level section headers (## N. ...) that must appear in the doc.
_REQUIRED_SECTIONS = [
    "## 1. Asset Class Capability",
    "## 2. Trading Session",
    "## 3. Order Type",
    "## 4. Order Lifecycle",
    "## 5. Fee / Slippage / Fill Model",
    "## 6. Data Source",
    "## 7. Alert / Backtest Feature Flags",
    "## 8. External Connector / API Permission Classes",
    "## 12. UI Exposure Rules",
    "## 13. Task Cross-Reference",
]

# Status labels that must appear in the legend/doc (core vocabulary).
_REQUIRED_STATUS_LABELS = [
    "`SUPPORTED`",
    "`MOCK-ONLY`",
    "`PAPER-ONLY`",
    "`CONDITIONAL`",
    "`R3-HOLD`",
    "`REJECTED`",
    "`NOT-IMPL`",
]

# Tasks that represent blocked capabilities and must be referenced.
_REQUIRED_TASK_REFS = [
    "TASK-014",
    "TASK-021",
    "TASK-022",
    "TASK-028",
    "TASK-030",
    "TASK-031",
    "TASK-032",
]

# Asset classes from Decision Record that must appear.
_REQUIRED_ASSET_MENTIONS = [
    "레버리지/인버스 ETP",
    "DeFi",
    "해외주식",
    "코인",
]


@pytest.fixture(scope="module")
def matrix_text() -> str:
    assert _MATRIX_PATH.exists(), (
        f"Capability matrix not found: {_MATRIX_PATH}\n"
        "Create docs/BROKER-CAPABILITY-PARITY-MATRIX.md (TASK-041)."
    )
    return _MATRIX_PATH.read_text(encoding="utf-8")


def test_matrix_file_exists() -> None:
    """The capability matrix document must exist."""
    assert _MATRIX_PATH.exists(), (
        f"Missing: {_MATRIX_PATH} — create via TASK-041."
    )


@pytest.mark.parametrize("section", _REQUIRED_SECTIONS)
def test_required_section_present(matrix_text: str, section: str) -> None:
    """Each required section header must appear in the document."""
    assert section in matrix_text, (
        f"Required section missing from capability matrix: {section!r}"
    )


@pytest.mark.parametrize("label", _REQUIRED_STATUS_LABELS)
def test_status_label_defined(matrix_text: str, label: str) -> None:
    """Every status legend label must be defined in the matrix."""
    assert label in matrix_text, (
        f"Status label not defined in capability matrix: {label!r}"
    )


@pytest.mark.parametrize("task_ref", _REQUIRED_TASK_REFS)
def test_blocking_task_referenced(matrix_text: str, task_ref: str) -> None:
    """Each R3-hold task must be cross-referenced in the matrix."""
    assert task_ref in matrix_text, (
        f"Blocking task not referenced in capability matrix: {task_ref!r}"
    )


@pytest.mark.parametrize("asset", _REQUIRED_ASSET_MENTIONS)
def test_asset_class_mentioned(matrix_text: str, asset: str) -> None:
    """Key rejected/conditional asset classes must appear in the matrix."""
    assert asset in matrix_text, (
        f"Asset class not mentioned in capability matrix: {asset!r}"
    )


def test_rejected_leveraged_etp_not_supported(matrix_text: str) -> None:
    """Leveraged/inverse ETP must appear with REJECTED status, not SUPPORTED."""
    # Find the row for 레버리지/인버스 ETP and verify it contains REJECTED.
    lines = matrix_text.splitlines()
    for line in lines:
        if "레버리지/인버스 ETP" in line:
            assert "REJECTED" in line or "기각" in line, (
                f"레버리지/인버스 ETP row must be REJECTED, got: {line!r}"
            )
            # Must NOT have SUPPORTED in the same row.
            assert "SUPPORTED" not in line, (
                f"레버리지/인버스 ETP must not be marked SUPPORTED: {line!r}"
            )
            return
    pytest.fail("레버리지/인버스 ETP row not found in capability matrix.")


def test_r3_hold_tasks_not_marked_supported(matrix_text: str) -> None:
    """R3-HOLD rows must not be labeled SUPPORTED in the Autofolio Status column.

    Scans rows containing R3-HOLD tasks and asserts the word SUPPORTED does not
    appear in the same line alongside an R3-HOLD marker.
    """
    lines = matrix_text.splitlines()
    violations: list[str] = []
    for line in lines:
        has_r3 = "`R3-HOLD`" in line or "R3-보류" in line
        has_supported = "`SUPPORTED`" in line
        # A table row with both R3-HOLD and SUPPORTED in the status columns is
        # suspect — skip section-header and legend lines (start with #, |---).
        if has_r3 and has_supported and line.strip().startswith("|"):
            # Allow legend row (the row that defines the label itself).
            if "Status Legend" not in matrix_text.splitlines()[
                max(0, lines.index(line) - 20):lines.index(line)
            ]:
                violations.append(line.strip())
    assert not violations, (
        "These matrix rows have both R3-HOLD and SUPPORTED — review:\n"
        + "\n".join(violations)
    )


def test_frontmatter_has_required_fields(matrix_text: str) -> None:
    """Matrix frontmatter must declare type, task, and prod_boundary."""
    assert "type: capability-matrix" in matrix_text
    assert "task: TASK-041" in matrix_text
    assert "prod_boundary:" in matrix_text
