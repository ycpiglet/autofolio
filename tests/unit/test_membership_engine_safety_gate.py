from __future__ import annotations

import copy

from scripts.membership_engine_safety_gate import load_contract, validate_contract


def test_membership_engine_safety_gate_accepts_current_contract():
    contract = load_contract()
    assert validate_contract(contract) == []


def test_membership_engine_safety_gate_requires_user_scope_on_surfaces():
    contract = load_contract()
    broken = copy.deepcopy(contract)
    broken["runtime_surfaces"][0]["production_owner_field"] = "account_id"

    findings = validate_contract(broken)

    assert any("production_owner_field must be user_id" in finding for finding in findings)


def test_membership_engine_safety_gate_rejects_live_execution_allowed():
    contract = load_contract()
    broken = copy.deepcopy(contract)
    broken["runtime_surfaces"][0]["live_execution_allowed"] = True

    findings = validate_contract(broken)

    assert any("live_execution_allowed must be false" in finding for finding in findings)


def test_membership_engine_safety_gate_requires_append_only_order_intents():
    contract = load_contract()
    broken = copy.deepcopy(contract)
    for surface in broken["runtime_surfaces"]:
        if surface["id"] == "order_intents":
            surface["append_only"] = False
            break

    findings = validate_contract(broken)

    assert "order_intents: append_only must be true" in findings


def test_membership_engine_safety_gate_requires_user_context_failure_mode():
    contract = load_contract()
    broken = copy.deepcopy(contract)
    broken["worker_contract"]["failure_behavior"] = []

    findings = validate_contract(broken)

    assert any("missing failure behavior entries" in finding for finding in findings)
