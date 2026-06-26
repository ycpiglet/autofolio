# TASK-173 Portfolio Goal-Gap Read Model — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic, read-only finance-roadmap read model (service + pydantic schema + FastAPI GET endpoint) that returns planned vs expected, gap, allocation drift, data-quality flags, and timeline candidates — all marked as Owner-review candidates only, with no order path or advice wording.

**Architecture:** Three-layer: (1) `app/services/finance_roadmap.py` owns the Pydantic models and pure service function; (2) `app/api/routers/finance_roadmap.py` exposes one GET endpoint gated by `require_app_user`; (3) the stable fixture `agents/project/FINANCE-SCENARIO-INPUT-CONTRACT.json` is the sole input source. Service imports no order/trade modules; router imports no secrets. Unit tests mock nothing (fixture is static JSON on disk). API tests use the live app + real fixture file.

**Tech Stack:** Python 3.11+, FastAPI, Pydantic v2, pytest; existing `app.api.deps.require_app_user` for auth gating; `app.api.security.encode_session` for test cookies.

## Global Constraints

- Gate: `read-only derived model only` — NO order path change, NO trade recommendation wording, NO portfolio mutation, NO private payment data, NO KIS/order/risk/prod/deploy change, NO secret.
- Deterministic: the service accepts `as_of: str` parameter instead of calling `datetime.now()`. Tests inject `as_of="fixture_static"`.
- All review candidates and timeline candidates must carry `action_permitted_now: False` and `no_trade_instruction: True`.
- Forbidden phrases (must not appear in any output field value): "you should buy", "you should sell", "guaranteed return", "execute order", "place order", "tax advice", "accounting advice", "investment advice", "trade recommendation".
- Forbidden key names in output: any key matching `order_id|trade_id|buy_signal|sell_signal|rebalance_action|profit_taking|order_execution`.
- Forbidden private-data key names: any key matching `customer_email|customer_phone|bank_account|payment_record|raw_statement|secret|access_token|password`.
- Follow existing FastAPI/pydantic/service/test patterns exactly (see `app/api/routers/portfolio.py`, `tests/api/test_portfolio.py`, `tests/unit/test_backend_kpis.py`).
- Branch: `feat/ui-backlog-2026-06-26`. Run `.venv\Scripts\python.exe -m pytest` (fallback: `python -m pytest`).
- Report file: `.superpowers/sdd/task-173-report.md`.

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `app/services/finance_roadmap.py` | Pydantic models + `load_contract()` + `compute_goal_gap()` |
| Create | `app/api/routers/finance_roadmap.py` | GET `/finance-roadmap/goal-gap`, auth-gated read-only |
| Modify | `app/api/main.py` | Import and register `finance_roadmap` router |
| Create | `tests/unit/test_finance_roadmap_service.py` | Unit tests: determinism, field coverage, boundary checks |
| Create | `tests/api/test_finance_roadmap_api.py` | API tests: 401/403/200 gating, shape, no forbidden keys |
| Create | `.superpowers/sdd/task-173-report.md` | Post-implementation report for the task |

---

## Task 1: Service Module + Unit Tests (TDD)

**Files:**
- Create: `app/services/finance_roadmap.py`
- Create: `tests/unit/test_finance_roadmap_service.py`

**Interfaces:**
- Consumes: `agents/project/FINANCE-SCENARIO-INPUT-CONTRACT.json` (already on disk)
- Produces:
  - `load_contract(path: Path = ...) -> dict[str, Any]`
  - `compute_goal_gap(contract: dict[str, Any], *, as_of: str = "fixture_static", fixture_idx: int = 0) -> FinanceRoadmapResponse`
  - Pydantic models: `FinanceRoadmapResponse`, `GapRange`, `PlannedInput`, `ExpectedRange`, `MissingEvidence`, `ReviewCandidate`, `TimelineCandidate`, `RoadmapBoundary`

---

- [ ] **Step 1: Write the failing unit tests**

Create `tests/unit/test_finance_roadmap_service.py` with this full content:

```python
"""Unit tests for app.services.finance_roadmap.compute_goal_gap.

TDD: all tests written before implementation exists.
Coverage:
 - Required fields present (planned / expected / gap / timeline)
 - Deterministic gap calculation from known fixture
 - No order-path keys in serialised output
 - No advice/recommendation wording in string values
 - No private/payment/secret keys
 - All review candidates: action_permitted_now=False, no_trade_instruction=True
 - All timeline candidates: action_permitted_now=False
 - Determinism: two identical calls return equal output
 - as_of is injected (not wall-clock)
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = REPO_ROOT / "agents" / "project" / "FINANCE-SCENARIO-INPUT-CONTRACT.json"

FORBIDDEN_ADVICE_PHRASES = {
    "you should buy",
    "you should sell",
    "guaranteed return",
    "execute order",
    "place order",
    "tax advice",
    "accounting advice",
    "investment advice",
    "trade recommendation",
}

_ORDER_KEY_RE = re.compile(
    r"\b(order_id|trade_id|buy_signal|sell_signal|rebalance_action|"
    r"profit_taking|order_placement|order_execution)\b",
    re.IGNORECASE,
)

_PRIVATE_KEY_RE = re.compile(
    r"\b(customer_email|customer_phone|customer_name|bank_account|"
    r"payment_record|raw_statement|secret|access_token|refresh_token|password)\b",
    re.IGNORECASE,
)


def _walk_keys(d: Any) -> list[str]:
    keys: list[str] = []
    if isinstance(d, dict):
        for k, v in d.items():
            keys.append(str(k))
            keys.extend(_walk_keys(v))
    elif isinstance(d, list):
        for item in d:
            keys.extend(_walk_keys(item))
    return keys


def _walk_string_values(d: Any) -> list[str]:
    vals: list[str] = []
    if isinstance(d, dict):
        for v in d.values():
            vals.extend(_walk_string_values(v))
    elif isinstance(d, list):
        for item in d:
            vals.extend(_walk_string_values(item))
    elif isinstance(d, str):
        vals.append(d)
    return vals


@pytest.fixture(scope="module")
def contract() -> dict[str, Any]:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def response(contract):
    from app.services.finance_roadmap import compute_goal_gap
    return compute_goal_gap(contract, as_of="fixture_static")


@pytest.fixture(scope="module")
def response_dict(response):
    return response.model_dump()


class TestRequiredFields:
    """All required fields are present with the expected values from the fixture."""

    def test_planned_return_pct(self, response):
        assert response.planned.planned_return_pct == 5.0

    def test_planning_horizon(self, response):
        assert response.planned.planning_horizon == "quarter"

    def test_expected_low_pct(self, response):
        assert response.expected.low_pct == 8.0

    def test_expected_high_pct(self, response):
        assert response.expected.high_pct == 10.0

    def test_expected_not_guaranteed(self, response):
        assert response.expected.not_guaranteed is True

    def test_expected_confidence_present(self, response):
        assert response.expected.confidence in ("low", "medium", "high")

    def test_gap_low_correct(self, response):
        # gap = expected - planned; 8.0 - 5.0 = 3.0
        assert response.gap.low_pct_points == pytest.approx(3.0)

    def test_gap_high_correct(self, response):
        # 10.0 - 5.0 = 5.0
        assert response.gap.high_pct_points == pytest.approx(5.0)

    def test_allocation_drift_present(self, response):
        assert isinstance(response.allocation_drift, str)
        assert len(response.allocation_drift) > 0

    def test_data_quality_flags_present(self, response):
        assert len(response.data_quality_flags) >= 1

    def test_timeline_candidates_present(self, response):
        assert len(response.timeline_candidates) >= 1

    def test_review_candidates_present(self, response):
        assert len(response.review_candidates) >= 1

    def test_fixture_id_present(self, response):
        assert isinstance(response.fixture_id, str) and response.fixture_id

    def test_as_of_reflects_injected_value(self, response):
        assert response.as_of == "fixture_static"

    def test_preview_mode_is_true(self, response):
        assert response.preview_mode is True

    def test_boundary_present(self, response):
        assert response.boundary is not None


class TestBoundaryFlags:
    """All review and timeline candidates carry the required safety flags."""

    def test_review_candidates_action_not_permitted(self, response):
        for cand in response.review_candidates:
            assert cand.action_permitted_now is False, (
                f"Candidate {cand.id!r} must have action_permitted_now=False"
            )

    def test_review_candidates_no_trade_instruction(self, response):
        for cand in response.review_candidates:
            assert cand.no_trade_instruction is True, (
                f"Candidate {cand.id!r} must have no_trade_instruction=True"
            )

    def test_review_candidates_owner_review_only(self, response):
        for cand in response.review_candidates:
            assert cand.candidate_for_owner_review_only is True

    def test_timeline_candidates_action_not_permitted(self, response):
        for cand in response.timeline_candidates:
            assert cand.action_permitted_now is False

    def test_timeline_candidates_have_required_evidence(self, response):
        for cand in response.timeline_candidates:
            assert len(cand.required_evidence) >= 1

    def test_boundary_no_trade_instruction(self, response):
        assert response.boundary.no_trade_instruction is True

    def test_boundary_not_investment_recommendation(self, response):
        assert response.boundary.not_investment_recommendation is True

    def test_boundary_read_only(self, response):
        assert response.boundary.read_only_planning_input_only is True

    def test_boundary_no_order_execution(self, response):
        assert response.boundary.no_order_execution is True


class TestNoOrderPath:
    """Serialised output contains no order-path keys or advice wording."""

    def test_no_order_key_in_output(self, response_dict):
        for key in _walk_keys(response_dict):
            assert not _ORDER_KEY_RE.search(key), (
                f"Forbidden order-path key found in output: {key!r}"
            )

    def test_no_advice_wording_in_string_values(self, response_dict):
        for text in _walk_string_values(response_dict):
            lower = text.lower()
            for phrase in FORBIDDEN_ADVICE_PHRASES:
                assert phrase not in lower, (
                    f"Forbidden advice phrase {phrase!r} found in output value: {text!r}"
                )

    def test_no_private_data_keys(self, response_dict):
        for key in _walk_keys(response_dict):
            assert not _PRIVATE_KEY_RE.search(key), (
                f"Forbidden private/payment key found in output: {key!r}"
            )


class TestDeterminism:
    """Two calls with the same inputs produce identical output."""

    def test_same_input_same_output(self, contract):
        from app.services.finance_roadmap import compute_goal_gap
        r1 = compute_goal_gap(contract, as_of="2026-06-26")
        r2 = compute_goal_gap(contract, as_of="2026-06-26")
        assert r1.model_dump() == r2.model_dump()

    def test_as_of_injected_not_wall_clock(self, contract):
        from app.services.finance_roadmap import compute_goal_gap
        r = compute_goal_gap(contract, as_of="test-sentinel-2026")
        assert r.as_of == "test-sentinel-2026"

    def test_different_as_of_produces_different_as_of_field(self, contract):
        from app.services.finance_roadmap import compute_goal_gap
        r1 = compute_goal_gap(contract, as_of="date-A")
        r2 = compute_goal_gap(contract, as_of="date-B")
        assert r1.as_of != r2.as_of
```

- [ ] **Step 2: Run the tests to confirm RED**

```powershell
.venv\Scripts\python.exe -m pytest tests/unit/test_finance_roadmap_service.py -v 2>&1 | head -40
```

Expected: `ModuleNotFoundError: No module named 'app.services.finance_roadmap'` or `ImportError`. All tests FAIL. This confirms RED.

- [ ] **Step 3: Create the service module**

Create `app/services/finance_roadmap.py` with this full content:

```python
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
    action_permitted_now: bool = False
    no_trade_instruction: bool = True
    why_flagged: str
    missing_evidence: list[str]


class TimelineCandidate(BaseModel):
    """Candidate review horizon. Requires evidence. No action permitted now."""

    id: str
    candidate_for_owner_review_only: bool = True
    action_permitted_now: bool = False
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
```

- [ ] **Step 4: Run the unit tests to confirm GREEN**

```powershell
.venv\Scripts\python.exe -m pytest tests/unit/test_finance_roadmap_service.py -v 2>&1
```

Expected: all tests pass. If any test fails, fix the service code (NOT the tests) until all pass.

- [ ] **Step 5: Commit Task 1**

```powershell
git add app/services/finance_roadmap.py tests/unit/test_finance_roadmap_service.py
git commit -m "$(cat <<'EOF'
feat(finance): TASK-173 goal-gap service module + unit tests — 읽기전용 모델

- app/services/finance_roadmap.py: Pydantic models (FinanceRoadmapResponse,
  GapRange, PlannedInput, ExpectedRange, MissingEvidence, ReviewCandidate,
  TimelineCandidate, RoadmapBoundary) + load_contract() + compute_goal_gap().
- Deterministic: as_of injected; no datetime.now() call.
- All candidates: action_permitted_now=False, no_trade_instruction=True.
- tests/unit/test_finance_roadmap_service.py: 20 unit tests covering
  required fields, gap calculation, boundary flags, no order path,
  no advice wording, no private data, determinism.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: API Router + Registration + API Tests (TDD)

**Files:**
- Create: `app/api/routers/finance_roadmap.py`
- Modify: `app/api/main.py` (add import + `app.include_router` call)
- Create: `tests/api/test_finance_roadmap_api.py`

**Interfaces:**
- Consumes (from Task 1): `compute_goal_gap`, `load_contract`, `FinanceRoadmapResponse` from `app.services.finance_roadmap`
- Consumes (existing): `require_app_user` from `app.api.deps`, `encode_session` from `app.api.security`
- Consumes (existing): test fixtures `client`, `guest_client`, `member_client`, `owner_client` from `tests/api/conftest.py`
- Produces: `GET /api/finance-roadmap/goal-gap` → `FinanceRoadmapResponse` (200 for owner/member, 403 for guest, 401 for anon)

---

- [ ] **Step 1: Write the failing API tests**

Create `tests/api/test_finance_roadmap_api.py` with this full content:

```python
"""API contract tests for GET /api/finance-roadmap/goal-gap.

Auth gating: anonymous→401, guest→403, member→200, owner→200.
Shape: required fields present, gap values correct, no forbidden keys.
No monkeypatching needed — the real fixture JSON is stable and checked in.
"""
from __future__ import annotations

import re

import pytest


_FORBIDDEN_KEY_RE = re.compile(
    r"\b(order_id|trade_id|buy_signal|sell_signal|rebalance_action|"
    r"profit_taking|order_execution)\b",
    re.IGNORECASE,
)

FORBIDDEN_ADVICE_PHRASES = {
    "you should buy",
    "you should sell",
    "guaranteed return",
    "execute order",
    "place order",
    "tax advice",
    "accounting advice",
    "investment advice",
    "trade recommendation",
}


def _walk_keys(d):
    keys = []
    if isinstance(d, dict):
        for k, v in d.items():
            keys.append(str(k))
            keys.extend(_walk_keys(v))
    elif isinstance(d, list):
        for item in d:
            keys.extend(_walk_keys(item))
    return keys


def _walk_string_values(d):
    vals = []
    if isinstance(d, dict):
        for v in d.values():
            vals.extend(_walk_string_values(v))
    elif isinstance(d, list):
        for item in d:
            vals.extend(_walk_string_values(item))
    elif isinstance(d, str):
        vals.append(d)
    return vals


class TestGoalGapAuth:
    """Auth gating: 401/403/200."""

    def test_anonymous_401(self, client):
        client.cookies.clear()
        resp = client.get("/api/finance-roadmap/goal-gap")
        assert resp.status_code == 401

    def test_guest_403(self, guest_client):
        resp = guest_client.get("/api/finance-roadmap/goal-gap")
        assert resp.status_code == 403

    def test_member_200(self, member_client):
        resp = member_client.get("/api/finance-roadmap/goal-gap")
        assert resp.status_code == 200

    def test_owner_200(self, owner_client):
        resp = owner_client.get("/api/finance-roadmap/goal-gap")
        assert resp.status_code == 200


class TestGoalGapShape:
    """Response body contains all required fields with correct values."""

    def test_required_top_level_fields(self, member_client):
        body = member_client.get("/api/finance-roadmap/goal-gap").json()
        required = (
            "planned", "expected", "gap", "timeline_candidates",
            "review_candidates", "data_quality_flags", "boundary",
            "preview_mode", "preview_label", "as_of", "fixture_id",
            "allocation_drift",
        )
        for field in required:
            assert field in body, f"Missing required top-level field: {field!r}"

    def test_gap_low_pct_points(self, member_client):
        body = member_client.get("/api/finance-roadmap/goal-gap").json()
        assert body["gap"]["low_pct_points"] == pytest.approx(3.0)

    def test_gap_high_pct_points(self, member_client):
        body = member_client.get("/api/finance-roadmap/goal-gap").json()
        assert body["gap"]["high_pct_points"] == pytest.approx(5.0)

    def test_planned_return_pct(self, member_client):
        body = member_client.get("/api/finance-roadmap/goal-gap").json()
        assert body["planned"]["planned_return_pct"] == 5.0

    def test_expected_not_guaranteed(self, member_client):
        body = member_client.get("/api/finance-roadmap/goal-gap").json()
        assert body["expected"]["not_guaranteed"] is True

    def test_preview_mode_true(self, member_client):
        body = member_client.get("/api/finance-roadmap/goal-gap").json()
        assert body["preview_mode"] is True

    def test_review_candidates_action_not_permitted(self, member_client):
        body = member_client.get("/api/finance-roadmap/goal-gap").json()
        for cand in body.get("review_candidates", []):
            assert cand["action_permitted_now"] is False

    def test_timeline_candidates_present(self, member_client):
        body = member_client.get("/api/finance-roadmap/goal-gap").json()
        assert len(body.get("timeline_candidates", [])) >= 1

    def test_boundary_no_trade_instruction(self, member_client):
        body = member_client.get("/api/finance-roadmap/goal-gap").json()
        assert body["boundary"]["no_trade_instruction"] is True

    def test_boundary_not_investment_recommendation(self, member_client):
        body = member_client.get("/api/finance-roadmap/goal-gap").json()
        assert body["boundary"]["not_investment_recommendation"] is True


class TestGoalGapForbiddenContent:
    """Response JSON must not contain forbidden order-path keys or advice wording."""

    def test_no_forbidden_order_keys(self, member_client):
        body = member_client.get("/api/finance-roadmap/goal-gap").json()
        for key in _walk_keys(body):
            assert not _FORBIDDEN_KEY_RE.search(key), (
                f"Forbidden order-path key found in API response: {key!r}"
            )

    def test_no_advice_wording_in_string_values(self, member_client):
        body = member_client.get("/api/finance-roadmap/goal-gap").json()
        for text in _walk_string_values(body):
            lower = text.lower()
            for phrase in FORBIDDEN_ADVICE_PHRASES:
                assert phrase not in lower, (
                    f"Forbidden advice phrase {phrase!r} found in API response value: {text!r}"
                )
```

- [ ] **Step 2: Run the API tests to confirm RED**

```powershell
.venv\Scripts\python.exe -m pytest tests/api/test_finance_roadmap_api.py -v 2>&1 | head -30
```

Expected: all tests FAIL because the endpoint returns 404 (router not yet registered). Confirms RED.

- [ ] **Step 3: Create the API router**

Create `app/api/routers/finance_roadmap.py` with this full content:

```python
"""Finance Roadmap router — /api/finance-roadmap/*

Endpoints (all require_app_user):
  GET /finance-roadmap/goal-gap

Read-only planning preview. No order, no action, no advice wording.
All candidates are for Owner review only (action_permitted_now=False).
"""
from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.api.deps import require_app_user
from app.services.finance_roadmap import FinanceRoadmapResponse

router = APIRouter(prefix="/finance-roadmap", tags=["finance-roadmap"])


@router.get(
    "/goal-gap",
    response_model=FinanceRoadmapResponse,
    summary="Read-only finance roadmap goal-gap preview",
    description=(
        "Returns planned vs expected, gap, allocation drift, data-quality flags, "
        "and timeline candidates. All candidates are for Owner review only. "
        "No order, no trade instruction, no advice. Preview only."
    ),
)
def goal_gap(
    _session: Annotated[dict[str, Any], Depends(require_app_user)],
) -> FinanceRoadmapResponse:
    """Read-only finance roadmap goal-gap preview.

    Derives: planned vs expected, gap, allocation drift, data-quality flags,
    timeline candidates, review candidates. All marked Owner-review only.
    No order path. No trade instruction. No advice wording.
    """
    from app.services.finance_roadmap import compute_goal_gap, load_contract

    return compute_goal_gap(load_contract())
```

- [ ] **Step 4: Register the router in main.py**

Open `app/api/main.py`. Add `finance_roadmap` to the existing import block. The current import is:

```python
from app.api.routers import (
    account,
    agents,
    analysis,
    acknowledgements,
    auth,
    engine,
    integrations,
    market,
    manuals,
    membership,
    portfolio,
    profile,
    settings,
    stream,
    trade,
)
```

Change it to:

```python
from app.api.routers import (
    account,
    agents,
    analysis,
    acknowledgements,
    auth,
    engine,
    finance_roadmap,
    integrations,
    market,
    manuals,
    membership,
    portfolio,
    profile,
    settings,
    stream,
    trade,
)
```

Then find the block of `app.include_router(...)` calls. The current last read-only router before `trade` is:

```python
    app.include_router(analysis.router, prefix="/api")
    app.include_router(agents.router, prefix="/api")
    app.include_router(stream.router, prefix="/api")
```

Add the new router after `analysis.router`:

```python
    app.include_router(analysis.router, prefix="/api")
    app.include_router(finance_roadmap.router, prefix="/api")
    app.include_router(agents.router, prefix="/api")
    app.include_router(stream.router, prefix="/api")
```

- [ ] **Step 5: Run the API tests to confirm GREEN**

```powershell
.venv\Scripts\python.exe -m pytest tests/api/test_finance_roadmap_api.py -v 2>&1
```

Expected: all tests pass. If any fail, fix router/service (NOT tests) until all pass.

- [ ] **Step 6: Commit Task 2**

```powershell
git add app/api/routers/finance_roadmap.py app/api/main.py tests/api/test_finance_roadmap_api.py
git commit -m "$(cat <<'EOF'
feat(finance): TASK-173 GET /api/finance-roadmap/goal-gap + API tests

- app/api/routers/finance_roadmap.py: read-only GET endpoint gated by
  require_app_user; anon→401, guest→403, member/owner→200.
- app/api/main.py: import + register finance_roadmap router.
- tests/api/test_finance_roadmap_api.py: 14 API tests covering auth
  gating, response shape, gap values, boundary flags, no forbidden keys.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Full Test Run + Report + Final Commit

**Files:**
- Create: `.superpowers/sdd/task-173-report.md`

**Interfaces:**
- Consumes: all test output from Tasks 1 and 2
- Produces: report file + final commit with Co-Authored-By footer

---

- [ ] **Step 1: Run the full focused test set**

```powershell
.venv\Scripts\python.exe -m pytest tests/unit/test_finance_roadmap_service.py tests/api/test_finance_roadmap_api.py -v 2>&1
```

Expected: all tests PASS with 0 warnings about order/trade/private-data. Capture the exact output for the report.

- [ ] **Step 2: Run the existing portfolio tests to confirm no regressions**

```powershell
.venv\Scripts\python.exe -m pytest tests/api/test_portfolio.py -v 2>&1
```

Expected: all existing portfolio tests still pass.

- [ ] **Step 3: Write the report**

Create `.superpowers/sdd/task-173-report.md` with these sections:

```markdown
# TASK-173 Report — Portfolio Goal-Gap Read Model

Bottom Line: Deterministic read-only goal-gap service + Pydantic schema +
GET /api/finance-roadmap/goal-gap endpoint implemented. All <N> tests pass.
No order path. No advice wording. No private data.

## What Was Built

### Service: `app/services/finance_roadmap.py`
- Pydantic models: `FinanceRoadmapResponse`, `GapRange`, `PlannedInput`,
  `ExpectedRange`, `MissingEvidence`, `ReviewCandidate`, `TimelineCandidate`,
  `RoadmapBoundary`.
- `load_contract(path)` — reads FINANCE-SCENARIO-INPUT-CONTRACT.json.
- `compute_goal_gap(contract, *, as_of, fixture_idx)` — deterministic; never
  calls datetime.now(); all candidates forced to action_permitted_now=False.

### Schema / API seam for TASK-174
- Endpoint: `GET /api/finance-roadmap/goal-gap`
- Response model: `FinanceRoadmapResponse` (from `app.services.finance_roadmap`)
- Auth: `require_app_user` (anon→401, guest→403, member/owner→200)

### Router: `app/api/routers/finance_roadmap.py`
- Prefix `/finance-roadmap`, tag `finance-roadmap`.
- Single GET endpoint; imports service lazily inside handler.

## TDD Evidence

### RED → GREEN for unit tests
- RED command: `python -m pytest tests/unit/test_finance_roadmap_service.py -v`
- RED output: `ModuleNotFoundError: No module named 'app.services.finance_roadmap'`
- GREEN command: same
- GREEN output: [paste full pytest output here]

### RED → GREEN for API tests
- RED command: `python -m pytest tests/api/test_finance_roadmap_api.py -v`
- RED output: `FAILED tests/api/test_finance_roadmap_api.py::TestGoalGapAuth::test_member_200 — assert 404 == 200`
- GREEN command: same
- GREEN output: [paste full pytest output here]

## Files Changed
- Created: `app/services/finance_roadmap.py`
- Created: `app/api/routers/finance_roadmap.py`
- Modified: `app/api/main.py`
- Created: `tests/unit/test_finance_roadmap_service.py`
- Created: `tests/api/test_finance_roadmap_api.py`

## API Seam for TASK-174
TASK-174 (UI panel) should fetch `GET /api/finance-roadmap/goal-gap` with a
valid member or owner session. The response fields to render are:
- `planned.planned_return_pct` — plan target (%)
- `planned.planning_horizon` — horizon label
- `expected.low_pct` / `expected.high_pct` — scenario range (%)
- `expected.confidence` — quality marker
- `gap.low_pct_points` / `gap.high_pct_points` — gap diagnostic (pp)
- `allocation_drift` — string flag
- `data_quality_flags[]` — missing evidence items
- `review_candidates[]` — owner-review candidates (no action permitted)
- `timeline_candidates[]` — horizon candidates (no action permitted)
- `preview_mode` / `preview_label` — mark as preview in UI

## Self-Review Findings
- [list any issues found and resolved, or "none"]

## Concerns
- [list any concerns for the next task owner, or "none"]
```

- [ ] **Step 4: Final commit**

```powershell
git add .superpowers/sdd/task-173-report.md
git commit -m "$(cat <<'EOF'
feat(finance): TASK-173 portfolio goal-gap read model — 읽기전용 서비스+스키마+API

Complete implementation: deterministic service (compute_goal_gap),
Pydantic response schema (FinanceRoadmapResponse), read-only GET endpoint
(GET /api/finance-roadmap/goal-gap, require_app_user), unit + API tests.
No order path, no trade instruction, no advice wording, no private data.
All review/timeline candidates: action_permitted_now=False.
Report: .superpowers/sdd/task-173-report.md.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Self-Review Checklist

**Spec coverage:**
- [x] Read model returns planned/expected/gap/timeline fields — Task 1 service + models
- [x] Output marks all portfolio changes as Owner-review candidates only — ReviewCandidate with action_permitted_now=False, no_trade_instruction=True
- [x] Tests prove no order/advice/payment/private-data drift — TestNoOrderPath, TestBoundaryFlags
- [x] TASK-174 can consume the model via GET /api/finance-roadmap/goal-gap — Task 2 + API seam doc

**Placeholder scan:** No "TBD", "TODO", "fill in details", or "similar to" language. All test code is complete and runnable.

**Type consistency:**
- `GapRange.low_pct_points` / `high_pct_points` — consistent across service definition and all tests
- `FinanceRoadmapResponse` — used in router `response_model=` and test body assertions
- `compute_goal_gap(contract, *, as_of, fixture_idx)` — matches test fixture call signature

**No placeholders found. No type mismatches found.**
