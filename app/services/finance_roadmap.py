"""Finance Roadmap read model — deterministic, read-only, no-action.

Service: compute_goal_gap() derives planned vs expected, gap, allocation drift,
data-quality flags, and timeline/review candidates from the stable finance
scenario input contract fixture.

GATE:
  - Read-only derived model only.
  - No order path. No trade instruction. No advice wording.
  - No portfolio mutation. No private payment data. No secrets.
  - All candidates are for Owner review only (action_permitted_now=False).
  - Deterministic: as_of is injected; datetime.now() is never called.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel

REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_CONTRACT = REPO_ROOT / "agents" / "project" / "FINANCE-SCENARIO-INPUT-CONTRACT.json"


# ── Pydantic models ───────────────────────────────────────────────────────────

class GapRange(BaseModel):
    """Derived gap between expected scenario and planned return. Diagnostic only."""

    low_pct_points: float
    high_pct_points: float


class PlannedInput(BaseModel):
    """Owner or business-plan target. Not generated guidance."""

    planned_return_pct: float
    planning_horizon: str


class ExpectedRange(BaseModel):
    """Scenario range with assumptions. Never guaranteed."""

    low_pct: float
    high_pct: float
    confidence: str
    not_guaranteed: bool = True


class MissingEvidence(BaseModel):
    """Evidence required before any Owner decision. Not a payment action."""

    id: str
    owner_decision_required: bool = True


class ReviewCandidate(BaseModel):
    """Owner-review candidate only. No trade instruction. No action permitted now."""

    id: str
    candidate_for_owner_review_only: bool = True
    action_permitted_now: Literal[False] = False
    no_trade_instruction: Literal[True] = True
    why_flagged: str
    missing_evidence: list[str]


class TimelineCandidate(BaseModel):
    """Candidate review horizon. Requires evidence. No action permitted now."""

    id: str
    candidate_for_owner_review_only: bool = True
    action_permitted_now: Literal[False] = False
    horizon: str
    trigger: str
    required_evidence: list[str]


class RoadmapBoundary(BaseModel):
    """Boundary flags carried in every response to make constraints machine-readable."""

    synthetic_fixture_only: bool = True
    read_only_planning_input_only: bool = True
    not_investment_recommendation: bool = True
    no_trade_instruction: bool = True
    no_order_execution: bool = True
    not_tax_accounting_final_advice: bool = True


class FinanceRoadmapResponse(BaseModel):
    """Read-only finance roadmap planning preview.

    Diagnostic read-model only. No order, no action, no advice.
    All candidates are for Owner review only (action_permitted_now=False).
    preview_mode=True marks this as a non-actionable planning tool.
    """

    preview_mode: Literal[True] = True
    preview_label: str = "read-only planning preview — no action, no order"
    as_of: str
    fixture_id: str
    planned: PlannedInput
    expected: ExpectedRange
    gap: GapRange
    allocation_drift: str
    data_quality_flags: list[MissingEvidence]
    review_candidates: list[ReviewCandidate]
    timeline_candidates: list[TimelineCandidate]
    boundary: RoadmapBoundary


# ── Service functions ─────────────────────────────────────────────────────────

def load_contract(path: Path = _DEFAULT_CONTRACT) -> dict[str, Any]:
    """Load the finance scenario input contract JSON.

    Deterministic file read. No network call. No secret handling.
    """
    return json.loads(path.read_text(encoding="utf-8"))


def compute_goal_gap(
    contract: dict[str, Any],
    *,
    as_of: str = "fixture_static",
    fixture_idx: int = 0,
) -> FinanceRoadmapResponse:
    """Compute the portfolio goal-gap read model from a finance scenario contract.

    Read-only derived model. No order path. No trade instruction. No advice.
    All candidates are for Owner review only.

    Args:
        contract: Finance scenario input contract dict
                  (from FINANCE-SCENARIO-INPUT-CONTRACT.json).
        as_of: Timestamp label injected by the caller. Never calls datetime.now().
               Use "fixture_static" for the default fixture (non-wall-clock).
        fixture_idx: Which sample_fixture to use (default 0).

    Returns:
        FinanceRoadmapResponse with planned/expected/gap/timeline fields.
        All review_candidates and timeline_candidates have action_permitted_now=False.
    """
    fixture: dict[str, Any] = contract["sample_fixtures"][fixture_idx]

    planned_return_pct: float = float(fixture["planned"]["planned_return_pct"])
    planning_horizon: str = str(fixture["planned"]["planning_horizon"])

    expected_range: list[float] = fixture["expected"]["expected_return_range_pct"]
    confidence: str = str(fixture["expected"]["confidence"])
    not_guaranteed: bool = bool(fixture["expected"]["not_guaranteed"])

    # Deterministic gap computation — no side effects
    gap_low = round(float(expected_range[0]) - planned_return_pct, 4)
    gap_high = round(float(expected_range[1]) - planned_return_pct, 4)

    allocation_drift: str = str(fixture["derived"]["allocation_drift"])

    # Missing evidence items from the contract's scenario_input_contract.missing bucket
    missing_items = [
        MissingEvidence(
            id=str(item["id"]),
            owner_decision_required=bool(item.get("owner_decision_required", True)),
        )
        for item in contract.get("scenario_input_contract", {}).get("missing", [])
        if isinstance(item, dict) and item.get("id")
    ]

    # Review candidates — forced safe: action_permitted_now=False, no_trade_instruction=True
    review_candidates = [
        ReviewCandidate(
            id=str(rc["id"]),
            candidate_for_owner_review_only=bool(rc.get("candidate_for_owner_review_only", True)),
            action_permitted_now=False,
            no_trade_instruction=True,
            why_flagged=str(rc.get("why_flagged", "")),
            missing_evidence=[str(item) for item in rc.get("missing_evidence", [])],
        )
        for rc in contract.get("portfolio_review_candidates", [])
        if isinstance(rc, dict) and rc.get("id")
    ]

    # Timeline candidates — forced safe: action_permitted_now=False
    timeline_candidates = [
        TimelineCandidate(
            id=str(tc["id"]),
            candidate_for_owner_review_only=bool(tc.get("candidate_for_owner_review_only", True)),
            action_permitted_now=False,
            horizon=str(tc.get("horizon", "")),
            trigger=str(tc.get("trigger", "")),
            required_evidence=[str(item) for item in tc.get("required_evidence", [])],
        )
        for tc in contract.get("timeline_candidates", [])
        if isinstance(tc, dict) and tc.get("id")
    ]

    return FinanceRoadmapResponse(
        as_of=as_of,
        fixture_id=str(fixture.get("id", "unknown")),
        planned=PlannedInput(
            planned_return_pct=planned_return_pct,
            planning_horizon=planning_horizon,
        ),
        expected=ExpectedRange(
            low_pct=float(expected_range[0]),
            high_pct=float(expected_range[1]),
            confidence=confidence,
            not_guaranteed=not_guaranteed,
        ),
        gap=GapRange(
            low_pct_points=gap_low,
            high_pct_points=gap_high,
        ),
        allocation_drift=allocation_drift,
        data_quality_flags=missing_items,
        review_candidates=review_candidates,
        timeline_candidates=timeline_candidates,
        boundary=RoadmapBoundary(),
    )
