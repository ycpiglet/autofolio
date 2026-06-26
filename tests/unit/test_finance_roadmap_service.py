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

    def test_timeline_candidates_owner_review_only(self, response):
        for cand in response.timeline_candidates:
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


class TestRuntimeAdviceGuard:
    """Runtime _assert_no_advice_wording guard rejects forbidden wording in free-text fields."""

    def test_advice_wording_in_fixture_is_rejected(self, contract):
        import copy
        from app.services.finance_roadmap import compute_goal_gap
        tampered = copy.deepcopy(contract)
        tampered["portfolio_review_candidates"][0]["why_flagged"] = "you should buy more now"
        with pytest.raises(ValueError):
            compute_goal_gap(tampered, as_of="fixture_static")


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
