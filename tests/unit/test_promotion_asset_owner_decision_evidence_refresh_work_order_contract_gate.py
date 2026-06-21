from __future__ import annotations

import copy

from scripts.promotion_asset_owner_decision_evidence_refresh_work_order_contract_gate import (
    load_contract,
    validate_contract,
)


def _contract() -> dict:
    return load_contract()


def test_current_contract_passes():
    assert validate_contract(_contract()) == []


def test_rejects_source_hash_mismatch():
    contract = _contract()
    contract["source_inputs"][0]["sha256"] = "0" * 64

    findings = validate_contract(contract)

    assert any("sha256 mismatch" in finding for finding in findings)


def test_rejects_missing_not_actual_refresh_execution_boundary():
    contract = _contract()
    contract["boundaries"]["not_actual_refresh_execution"] = False

    findings = validate_contract(contract)

    assert any("boundaries.not_actual_refresh_execution must be true" in finding for finding in findings)


def test_rejects_summary_work_order_drift():
    contract = _contract()
    contract["contract_summary"]["refresh_work_order_records"] = 8

    findings = validate_contract(contract)

    assert any("contract_summary.refresh_work_order_records must be 9" in finding for finding in findings)


def test_rejects_missing_work_order_record():
    contract = copy.deepcopy(_contract())
    contract["refresh_work_order_records"] = [
        item for item in contract["refresh_work_order_records"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_contract(contract)

    assert any("refresh_work_order_records missing decision types" in finding for finding in findings)


def test_rejects_actual_refresh_executed():
    contract = _contract()
    contract["refresh_work_order_records"][0]["actual_refresh_executed"] = True

    findings = validate_contract(contract)

    assert any("refresh/approval/public/export/customer/payment/platform/final-advice/live flags must not be true" in finding for finding in findings)


def test_rejects_actual_approval_evidence_collected():
    contract = _contract()
    contract["refresh_work_order_records"][0]["actual_approval_evidence_collected"] = True

    findings = validate_contract(contract)

    assert any("refresh/approval/public/export/customer/payment/platform/final-advice/live flags must not be true" in finding for finding in findings)


def test_rejects_action_permitted():
    contract = _contract()
    contract["refresh_work_order_records"][0]["action_permitted_now"] = True

    findings = validate_contract(contract)

    assert any("refresh/approval/public/export/customer/payment/platform/final-advice/live flags must not be true" in finding for finding in findings)


def test_rejects_work_order_state_live_action():
    contract = _contract()
    contract["work_order_states"][0]["live_action"] = True

    findings = validate_contract(contract)

    assert any("refresh/approval/public/export/customer/payment/platform/final-advice/live flags must not be true" in finding for finding in findings)


def test_rejects_missing_preconditions():
    contract = _contract()
    contract["refresh_work_order_records"][0]["preconditions"] = []

    findings = validate_contract(contract)

    assert any("preconditions must include at least three local preconditions" in finding for finding in findings)


def test_rejects_missing_proof_requirements():
    contract = _contract()
    contract["refresh_work_order_records"][0]["proof_requirements"] = []

    findings = validate_contract(contract)

    assert any("proof_requirements must include at least three local proof requirements" in finding for finding in findings)


def test_rejects_missing_trigger_map_item():
    contract = copy.deepcopy(_contract())
    contract["invalidating_trigger_to_work_order_map"] = [
        item for item in contract["invalidating_trigger_to_work_order_map"] if item["trigger_id"] != "blocked_action_scan_change"
    ]

    findings = validate_contract(contract)

    assert any("invalidating_trigger_to_work_order_map missing triggers" in finding for finding in findings)


def test_rejects_trigger_map_refresh_execution_allowed():
    contract = _contract()
    contract["invalidating_trigger_to_work_order_map"][0]["refresh_execution_allowed"] = True

    findings = validate_contract(contract)

    assert any("refresh/approval/public/export/customer/payment/platform/final-advice/live flags must not be true" in finding for finding in findings)


def test_rejects_source_count_mismatch():
    contract = _contract()
    contract["refresh_work_order_records"][0]["source_required_evidence_count"] = 99

    findings = validate_contract(contract)

    assert any("source_required_evidence_count must match source preview source_required_evidence_count" in finding for finding in findings)


def test_rejects_scan_match():
    contract = _contract()
    contract["blocked_action_scan"]["actual_refresh_execution"]["matches"] = ["actual_refresh_executed"]

    findings = validate_contract(contract)

    assert any("blocked_action_scan.actual_refresh_execution.matches must be empty" in finding for finding in findings)


def test_rejects_forbidden_approval_key():
    contract = _contract()
    contract["refresh_work_order_records"][0]["owner_signature_file"] = "signed"

    findings = validate_contract(contract)

    assert any("forbidden refresh/approval/export/customer/secret/final-advice key names" in finding for finding in findings)


def test_rejects_live_platform_flag():
    contract = _contract()
    contract["contract_summary"]["platform_api_call_enabled"] = True

    findings = validate_contract(contract)

    assert any("refresh/approval/public/export/customer/payment/platform/final-advice/live flags must not be true" in finding for finding in findings)
