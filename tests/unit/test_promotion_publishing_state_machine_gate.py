from __future__ import annotations

import copy

from scripts.promotion_publishing_state_machine_gate import load_contract, validate_contract


def test_promotion_publishing_state_machine_gate_accepts_current_contract():
    contract = load_contract()
    assert validate_contract(contract) == []


def test_promotion_publishing_state_machine_gate_rejects_live_transition():
    contract = load_contract()
    broken = copy.deepcopy(contract)
    broken["transitions"][0]["live_action"] = True

    findings = validate_contract(broken)

    assert any("transitions[0].live_action must be false" in finding for finding in findings)


def test_promotion_publishing_state_machine_gate_requires_record_only_live_state():
    contract = load_contract()
    broken = copy.deepcopy(contract)
    for state in broken["states"]:
        if state["id"] == "live_recorded_after_owner_action":
            state["action_type"] = "publish_api_call"

    findings = validate_contract(broken)

    assert any("must be record-only" in finding for finding in findings)


def test_promotion_publishing_state_machine_gate_rejects_secret_key_names():
    contract = load_contract()
    broken = copy.deepcopy(contract)
    broken["access_token"] = "placeholder"

    findings = validate_contract(broken)

    assert any("forbidden secret/customer key names present" in finding for finding in findings)


def test_promotion_publishing_state_machine_gate_requires_owner_boundary():
    contract = load_contract()
    broken = copy.deepcopy(contract)
    broken["boundaries"]["owner_approval_required_before_any_live_record"] = False

    findings = validate_contract(broken)

    assert any("owner_approval_required_before_any_live_record must be true" in finding for finding in findings)


def test_promotion_publishing_state_machine_gate_rejects_action_text():
    contract = load_contract()
    broken = copy.deepcopy(contract)
    broken["transitions"][0]["executor"] = "publish_now"

    findings = validate_contract(broken)

    assert any("forbidden action-like text present" in finding for finding in findings)
