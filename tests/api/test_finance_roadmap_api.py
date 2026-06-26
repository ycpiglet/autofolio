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
