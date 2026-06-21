from __future__ import annotations

import copy

from scripts.promotion_asset_owner_decision_evidence_refresh_queue_contract_gate import (
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


def test_rejects_missing_actual_evidence_boundary():
    contract = _contract()
    contract["boundaries"]["not_actual_approval_evidence_collection"] = False

    findings = validate_contract(contract)

    assert any("boundaries.not_actual_approval_evidence_collection must be true" in finding for finding in findings)


def test_rejects_summary_queue_record_drift():
    contract = _contract()
    contract["contract_summary"]["refresh_queue_records"] = 8

    findings = validate_contract(contract)

    assert any("contract_summary.refresh_queue_records must be 9" in finding for finding in findings)


def test_rejects_missing_refresh_queue_record():
    contract = copy.deepcopy(_contract())
    contract["refresh_queue_records"] = [
        item for item in contract["refresh_queue_records"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_contract(contract)

    assert any("refresh_queue_records missing decision types" in finding for finding in findings)


def test_rejects_actual_approval_evidence_collected():
    contract = _contract()
    contract["refresh_queue_records"][0]["actual_approval_evidence_collected"] = True

    findings = validate_contract(contract)

    assert any("approval/public/export/customer/payment/platform/final-advice/live flags must not be true" in finding for finding in findings)


def test_rejects_action_permitted():
    contract = _contract()
    contract["refresh_queue_records"][0]["action_permitted_now"] = True

    findings = validate_contract(contract)

    assert any("approval/public/export/customer/payment/platform/final-advice/live flags must not be true" in finding for finding in findings)


def test_rejects_state_live_action():
    contract = _contract()
    contract["queue_states"][0]["live_action"] = True

    findings = validate_contract(contract)

    assert any("approval/public/export/customer/payment/platform/final-advice/live flags must not be true" in finding for finding in findings)


def test_rejects_missing_trigger_map_item():
    contract = copy.deepcopy(_contract())
    contract["invalidating_trigger_map"] = [
        item for item in contract["invalidating_trigger_map"] if item["trigger_id"] != "blocked_action_scan_change"
    ]

    findings = validate_contract(contract)

    assert any("invalidating_trigger_map missing triggers" in finding for finding in findings)


def test_rejects_trigger_map_action_permitted():
    contract = _contract()
    contract["invalidating_trigger_map"][0]["action_permitted_now"] = True

    findings = validate_contract(contract)

    assert any("approval/public/export/customer/payment/platform/final-advice/live flags must not be true" in finding for finding in findings)


def test_rejects_target_queue_state_drift():
    contract = _contract()
    contract["invalidating_trigger_map"][0]["target_queue_state"] = "future_owner_r3_packet_candidate_after_refresh"

    findings = validate_contract(contract)

    assert any("target_queue_state must match source target_refresh_state" in finding for finding in findings)


def test_rejects_source_count_mismatch():
    contract = _contract()
    contract["refresh_queue_records"][0]["source_required_evidence_count"] = 99

    findings = validate_contract(contract)

    assert any("source_required_evidence_count must match source preview" in finding for finding in findings)


def test_rejects_missing_source_hash_invalidating_event():
    contract = _contract()
    contract["refresh_queue_records"][0]["source_hash_invalidating_event_present"] = False

    findings = validate_contract(contract)

    assert any("source_hash_invalidating_event_present must be true" in finding for finding in findings)


def test_rejects_scan_match():
    contract = _contract()
    contract["blocked_action_scan"]["approval_evidence_collection"]["matches"] = ["actual_approval_evidence_collected"]

    findings = validate_contract(contract)

    assert any("blocked_action_scan.approval_evidence_collection.matches must be empty" in finding for finding in findings)


def test_rejects_forbidden_approval_key():
    contract = _contract()
    contract["refresh_queue_records"][0]["owner_signature_file"] = "signed"

    findings = validate_contract(contract)

    assert any("forbidden approval/export/customer/secret/final-advice key names" in finding for finding in findings)


def test_rejects_live_platform_flag():
    contract = _contract()
    contract["contract_summary"]["platform_api_call_enabled"] = True

    findings = validate_contract(contract)

    assert any("approval/public/export/customer/payment/platform/final-advice/live flags must not be true" in finding for finding in findings)
