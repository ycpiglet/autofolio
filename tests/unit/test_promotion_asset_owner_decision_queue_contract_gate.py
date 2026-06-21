from __future__ import annotations

import copy

from scripts.promotion_asset_owner_decision_queue_contract_gate import load_contract, validate_contract


def _contract() -> dict:
    return load_contract()


def test_current_contract_passes():
    assert validate_contract(_contract()) == []


def test_rejects_source_hash_mismatch():
    contract = _contract()
    contract["source_inputs"][0]["sha256"] = "0" * 64

    findings = validate_contract(contract)

    assert any("sha256 mismatch" in finding for finding in findings)


def test_rejects_missing_boundary():
    contract = _contract()
    contract["boundaries"]["not_actual_owner_approval_record"] = False

    findings = validate_contract(contract)

    assert any("boundaries.not_actual_owner_approval_record must be true" in finding for finding in findings)


def test_rejects_missing_required_queue_field():
    contract = _contract()
    contract["decision_queue_contract"]["required_fields"].remove("actual_approval_recorded")

    findings = validate_contract(contract)

    assert any("required_fields missing" in finding for finding in findings)


def test_rejects_live_action_state():
    contract = _contract()
    contract["decision_queue_contract"]["allowed_states"][0]["live_action"] = True

    findings = validate_contract(contract)

    assert any("live_action must be false" in finding for finding in findings)


def test_rejects_state_actual_approval_recorded():
    contract = _contract()
    contract["decision_queue_contract"]["allowed_states"][2]["actual_approval_recorded"] = True

    findings = validate_contract(contract)

    assert any("actual_approval_recorded must be false" in finding for finding in findings)


def test_rejects_missing_decision_type():
    contract = copy.deepcopy(_contract())
    contract["decision_types"] = [
        item for item in contract["decision_types"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_contract(contract)

    assert any("decision_types missing" in finding for finding in findings)


def test_rejects_decision_not_owner_r3_required():
    contract = _contract()
    contract["decision_types"][0]["owner_r3_required"] = False

    findings = validate_contract(contract)

    assert any("owner_r3_required must be true" in finding for finding in findings)


def test_rejects_missing_seed_record():
    contract = copy.deepcopy(_contract())
    contract["seed_decision_records"] = [
        item for item in contract["seed_decision_records"] if item["decision_type"] != "sns_upload"
    ]

    findings = validate_contract(contract)

    assert any("seed_decision_records missing decision types" in finding for finding in findings)


def test_rejects_seed_record_actual_approval():
    contract = _contract()
    contract["seed_decision_records"][0]["actual_approval_recorded"] = True

    findings = validate_contract(contract)

    assert any("actual_approval_recorded must be false" in finding for finding in findings)


def test_rejects_public_use_unblocked():
    contract = _contract()
    contract["seed_decision_records"][0]["public_use_blocked"] = False

    findings = validate_contract(contract)

    assert any("public_use_blocked must be true" in finding for finding in findings)


def test_rejects_forbidden_approval_key():
    contract = _contract()
    contract["seed_decision_records"][0]["approval_signature"] = "signed"

    findings = validate_contract(contract)

    assert any("forbidden approval/export/customer/secret/final-advice key names" in finding for finding in findings)


def test_rejects_live_platform_flag():
    contract = _contract()
    contract["queue_summary"]["platform_api_call_enabled"] = True

    findings = validate_contract(contract)

    assert any("approval/public/export/customer/payment/platform/final-advice flags must not be true" in finding for finding in findings)
