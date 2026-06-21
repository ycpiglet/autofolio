from __future__ import annotations

import copy

from scripts.finance_scenario_input_contract_gate import load_contract, validate_contract


def _contract() -> dict:
    return copy.deepcopy(load_contract())


def test_current_contract_passes():
    assert validate_contract(_contract()) == []


def test_rejects_non_synthetic_fixture():
    contract = _contract()
    contract["sample_fixtures"][0]["synthetic"] = False

    findings = validate_contract(contract)

    assert any("must be synthetic" in finding for finding in findings)


def test_rejects_current_portfolio_fact_drift():
    contract = _contract()
    contract["sample_fixtures"][0]["example_is_not_current_portfolio_fact"] = False

    findings = validate_contract(contract)

    assert any("not current portfolio fact" in finding for finding in findings)


def test_rejects_real_customer_payment_data():
    contract = _contract()
    contract["sample_fixtures"][0]["real_customer_payment_data"] = True

    findings = validate_contract(contract)

    assert any("real_customer_payment_data" in finding for finding in findings)


def test_rejects_missing_input_bucket():
    contract = _contract()
    del contract["scenario_input_contract"]["missing"]

    findings = validate_contract(contract)

    assert any("scenario_input_contract missing" in finding for finding in findings)


def test_rejects_missing_required_metric():
    contract = _contract()
    contract["metric_contract"] = [
        item for item in contract["metric_contract"] if item["id"] != "timeline_candidate"
    ]

    findings = validate_contract(contract)

    assert any("metric_contract missing" in finding for finding in findings)


def test_rejects_wrong_planned_return_fixture():
    contract = _contract()
    contract["sample_fixtures"][0]["planned"]["planned_return_pct"] = 7.0

    findings = validate_contract(contract)

    assert any("planned_return_pct must be 5.0" in finding for finding in findings)


def test_rejects_expected_range_without_ten_percent():
    contract = _contract()
    contract["sample_fixtures"][0]["expected"]["expected_return_range_pct"] = [6.0, 9.5]

    findings = validate_contract(contract)

    assert any("expected_return_range_pct must include 10.0" in finding for finding in findings)


def test_rejects_missing_not_guaranteed_flag():
    contract = _contract()
    contract["sample_fixtures"][0]["expected"]["not_guaranteed"] = False

    findings = validate_contract(contract)

    assert any("not_guaranteed must be true" in finding for finding in findings)


def test_rejects_action_enabled_flag():
    contract = _contract()
    contract["trade_recommendation_enabled"] = True

    findings = validate_contract(contract)

    assert any("trade_recommendation_enabled" in finding for finding in findings)


def test_rejects_forbidden_private_key_name():
    contract = _contract()
    contract["raw_statement_text"] = "redacted"

    findings = validate_contract(contract)

    assert any("forbidden private/secret/payment key name" in finding for finding in findings)


def test_rejects_forbidden_advice_phrase_outside_blocked_context():
    contract = _contract()
    contract["notes"] = "This is tax advice."

    findings = validate_contract(contract)

    assert any("forbidden advice/action phrase" in finding for finding in findings)


def test_allows_forbidden_terms_inside_explicit_blocked_context():
    contract = _contract()
    contract["sample_fixtures"][0]["blocked"].append("tax advice")

    findings = validate_contract(contract)

    assert findings == []


def test_rejects_portfolio_candidate_action_permission():
    contract = _contract()
    contract["portfolio_review_candidates"][0]["action_permitted_now"] = True

    findings = validate_contract(contract)

    assert any("portfolio_review_candidates action_permitted_now" in finding for finding in findings)


def test_rejects_candidate_without_no_trade_instruction():
    contract = _contract()
    contract["portfolio_review_candidates"][0]["no_trade_instruction"] = False

    findings = validate_contract(contract)

    assert any("no_trade_instruction" in finding for finding in findings)


def test_rejects_timeline_candidate_action_permission():
    contract = _contract()
    contract["timeline_candidates"][0]["action_permitted_now"] = True

    findings = validate_contract(contract)

    assert any("timeline_candidates action_permitted_now" in finding for finding in findings)


def test_rejects_wrong_handoff_task():
    contract = _contract()
    contract["handoff"]["next_task"] = "TASK-174"

    findings = validate_contract(contract)

    assert any("handoff.next_task must be TASK-173" in finding for finding in findings)
