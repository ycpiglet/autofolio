# TASK-173 Report — Portfolio Goal-Gap Read Model

Bottom Line: Deterministic read-only goal-gap service + Pydantic schema +
GET /api/finance-roadmap/goal-gap endpoint implemented. All 48 tests pass.
No order path. No advice wording. No private data.

## What Was Built

### Service: `app/services/finance_roadmap.py`
- Pydantic models: `FinanceRoadmapResponse`, `GapRange`, `PlannedInput`,
  `ExpectedRange`, `MissingEvidence`, `ReviewCandidate`, `TimelineCandidate`,
  `RoadmapBoundary`.
- `load_contract(path)` — reads FINANCE-SCENARIO-INPUT-CONTRACT.json.
- `compute_goal_gap(contract, *, as_of, fixture_idx)` — deterministic; never
  calls datetime.now(); all candidates forced to action_permitted_now=False.
- Safety flags are Literal-locked at Pydantic type level:
  - `ReviewCandidate.action_permitted_now: Literal[False] = False`
  - `ReviewCandidate.no_trade_instruction: Literal[True] = True`
  - `TimelineCandidate.action_permitted_now: Literal[False] = False`
  - `preview_mode: Literal[True] = True`

### Schema / API Seam for TASK-174
- Endpoint: `GET /api/finance-roadmap/goal-gap`
- Response model: `FinanceRoadmapResponse` (from `app.services.finance_roadmap`)
- Auth: `require_app_user` (anon→401, guest→403, member/owner→200)

### Router: `app/api/routers/finance_roadmap.py`
- Prefix `/finance-roadmap`, tag `finance-roadmap`.
- Single GET endpoint; service functions imported lazily inside handler (follows portfolio.py pattern).

## TDD Evidence

### RED → GREEN for unit tests

**RED command:**
```
.venv\Scripts\python.exe -m pytest tests/unit/test_finance_roadmap_service.py -v
```
**RED output:**
```
31 items collected — all ERROR (module-level fixture setup failed: ImportError for
app.services.finance_roadmap) + 3 FAILED (TestDeterminism inline imports)
```

**GREEN command:**
```
.venv\Scripts\python.exe -m pytest tests/unit/test_finance_roadmap_service.py -v
```
**GREEN output:**
```
============================= 32 passed in 0.34s ==============================
```

(32 tests: 31 original + 1 added for `test_timeline_candidates_owner_review_only` per Task 1 review finding.)

### RED → GREEN for API tests

**RED command:**
```
.venv\Scripts\python.exe -m pytest tests/api/test_finance_roadmap_api.py -v
```
**RED output:**
```
tests/api/test_finance_roadmap_api.py::TestGoalGapAuth::test_anonymous_401 FAILED
...
E       assert 404 == 401
13 FAILED, 3 passed (tests that passed vacuously on empty dict)
```

**GREEN command:**
```
.venv\Scripts\python.exe -m pytest tests/api/test_finance_roadmap_api.py -v
```
**GREEN output:**
```
======================== 16 passed, 1 warning in 0.92s ========================
```

### Full focused run (Task 3 closeout)

**Command:**
```
.venv\Scripts\python.exe -m pytest tests/unit/test_finance_roadmap_service.py tests/api/test_finance_roadmap_api.py -v
```
**Output:**
```
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-9.0.3, pluggy-1.6.0
collected 48 items

tests/unit/test_finance_roadmap_service.py::TestRequiredFields::test_planned_return_pct PASSED
tests/unit/test_finance_roadmap_service.py::TestRequiredFields::test_planning_horizon PASSED
tests/unit/test_finance_roadmap_service.py::TestRequiredFields::test_expected_low_pct PASSED
tests/unit/test_finance_roadmap_service.py::TestRequiredFields::test_expected_high_pct PASSED
tests/unit/test_finance_roadmap_service.py::TestRequiredFields::test_expected_not_guaranteed PASSED
tests/unit/test_finance_roadmap_service.py::TestRequiredFields::test_expected_confidence_present PASSED
tests/unit/test_finance_roadmap_service.py::TestRequiredFields::test_gap_low_correct PASSED
tests/unit/test_finance_roadmap_service.py::TestRequiredFields::test_gap_high_correct PASSED
tests/unit/test_finance_roadmap_service.py::TestRequiredFields::test_allocation_drift_present PASSED
tests/unit/test_finance_roadmap_service.py::TestRequiredFields::test_data_quality_flags_present PASSED
tests/unit/test_finance_roadmap_service.py::TestRequiredFields::test_timeline_candidates_present PASSED
tests/unit/test_finance_roadmap_service.py::TestRequiredFields::test_review_candidates_present PASSED
tests/unit/test_finance_roadmap_service.py::TestRequiredFields::test_fixture_id_present PASSED
tests/unit/test_finance_roadmap_service.py::TestRequiredFields::test_as_of_reflects_injected_value PASSED
tests/unit/test_finance_roadmap_service.py::TestRequiredFields::test_preview_mode_is_true PASSED
tests/unit/test_finance_roadmap_service.py::TestRequiredFields::test_boundary_present PASSED
tests/unit/test_finance_roadmap_service.py::TestBoundaryFlags::test_review_candidates_action_not_permitted PASSED
tests/unit/test_finance_roadmap_service.py::TestBoundaryFlags::test_review_candidates_no_trade_instruction PASSED
tests/unit/test_finance_roadmap_service.py::TestBoundaryFlags::test_review_candidates_owner_review_only PASSED
tests/unit/test_finance_roadmap_service.py::TestBoundaryFlags::test_timeline_candidates_owner_review_only PASSED
tests/unit/test_finance_roadmap_service.py::TestBoundaryFlags::test_timeline_candidates_action_not_permitted PASSED
tests/unit/test_finance_roadmap_service.py::TestBoundaryFlags::test_timeline_candidates_have_required_evidence PASSED
tests/unit/test_finance_roadmap_service.py::TestBoundaryFlags::test_boundary_no_trade_instruction PASSED
tests/unit/test_finance_roadmap_service.py::TestBoundaryFlags::test_boundary_not_investment_recommendation PASSED
tests/unit/test_finance_roadmap_service.py::TestBoundaryFlags::test_boundary_read_only PASSED
tests/unit/test_finance_roadmap_service.py::TestBoundaryFlags::test_boundary_no_order_execution PASSED
tests/unit/test_finance_roadmap_service.py::TestNoOrderPath::test_no_order_key_in_output PASSED
tests/unit/test_finance_roadmap_service.py::TestNoOrderPath::test_no_advice_wording_in_string_values PASSED
tests/unit/test_finance_roadmap_service.py::TestNoOrderPath::test_no_private_data_keys PASSED
tests/unit/test_finance_roadmap_service.py::TestDeterminism::test_same_input_same_output PASSED
tests/unit/test_finance_roadmap_service.py::TestDeterminism::test_as_of_injected_not_wall_clock PASSED
tests/unit/test_finance_roadmap_service.py::TestDeterminism::test_different_as_of_produces_different_as_of_field PASSED
tests/api/test_finance_roadmap_api.py::TestGoalGapAuth::test_anonymous_401 PASSED
tests/api/test_finance_roadmap_api.py::TestGoalGapAuth::test_guest_403 PASSED
tests/api/test_finance_roadmap_api.py::TestGoalGapAuth::test_member_200 PASSED
tests/api/test_finance_roadmap_api.py::TestGoalGapAuth::test_owner_200 PASSED
tests/api/test_finance_roadmap_api.py::TestGoalGapShape::test_required_top_level_fields PASSED
tests/api/test_finance_roadmap_api.py::TestGoalGapShape::test_gap_low_pct_points PASSED
tests/api/test_finance_roadmap_api.py::TestGoalGapShape::test_gap_high_pct_points PASSED
tests/api/test_finance_roadmap_api.py::TestGoalGapShape::test_planned_return_pct PASSED
tests/api/test_finance_roadmap_api.py::TestGoalGapShape::test_expected_not_guaranteed PASSED
tests/api/test_finance_roadmap_api.py::TestGoalGapShape::test_preview_mode_true PASSED
tests/api/test_finance_roadmap_api.py::TestGoalGapShape::test_review_candidates_action_not_permitted PASSED
tests/api/test_finance_roadmap_api.py::TestGoalGapShape::test_timeline_candidates_present PASSED
tests/api/test_finance_roadmap_api.py::TestGoalGapShape::test_boundary_no_trade_instruction PASSED
tests/api/test_finance_roadmap_api.py::TestGoalGapShape::test_boundary_not_investment_recommendation PASSED
tests/api/test_finance_roadmap_api.py::TestGoalGapForbiddenContent::test_no_forbidden_order_keys PASSED
tests/api/test_finance_roadmap_api.py::TestGoalGapForbiddenContent::test_no_advice_wording_in_string_values PASSED

============================== warnings summary ===============================
StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated
======================== 48 passed, 1 warning in 0.48s ========================
```

### Portfolio no-regression check

**Command:**
```
.venv\Scripts\python.exe -m pytest tests/api/test_portfolio.py -v
```
**Output:**
```
collected 21 items
... (21 PASSED)
======================== 21 passed, 1 warning in 0.90s ========================
```

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

1. **Task 2 review finding applied (Task 3 closeout):** `test_review_candidates_action_not_permitted` was vacuous when `review_candidates` is empty. Added `assert len(candidates) >= 1` guard before the loop to make the assertion load-bearing. The fixture always returns at least one review candidate, so the guard passes.
2. **Task 1 review finding applied:** Safety flags locked with `Literal` types (`Literal[False]`/`Literal[True]`) to prevent silent override at construction time.
3. **Task 1 review finding applied:** Added `test_timeline_candidates_owner_review_only` unit test for symmetry with review candidates check.
4. Only one pytest warning present (starlette/httpx deprecation) — pre-existing, not introduced by this task.

## Concerns
None. All 48 task-specific tests pass, 21 portfolio regression tests pass, boundary flags are Literal-locked, no wall-clock calls, no order path, no advice wording, no private data.
