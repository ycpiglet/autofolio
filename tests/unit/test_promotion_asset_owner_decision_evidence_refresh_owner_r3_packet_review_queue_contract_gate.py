from __future__ import annotations

import copy

from scripts.promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_queue_contract_gate import (
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


def test_rejects_missing_review_queue_boundary():
    contract = _contract()
    contract["boundaries"]["review_queue_not_approval"] = False

    findings = validate_contract(contract)

    assert any("boundaries.review_queue_not_approval must be true" in finding for finding in findings)


def test_rejects_summary_review_queue_count_drift():
    contract = _contract()
    contract["contract_summary"]["review_queue_records"] = 8

    findings = validate_contract(contract)

    assert any("contract_summary.review_queue_records must be 9" in finding for finding in findings)


def test_rejects_missing_review_queue_record():
    contract = copy.deepcopy(_contract())
    contract["review_queue_records"] = [
        item for item in contract["review_queue_records"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_contract(contract)

    assert any("review_queue_records missing decision types" in finding for finding in findings)


def test_rejects_review_queue_as_approval():
    contract = _contract()
    contract["review_queue_records"][0]["review_queue_is_approval"] = True

    findings = validate_contract(contract)

    assert any(
        "review/refresh/approval/signature/public/export/customer/payment/platform/final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_queue_submitted_to_owner():
    contract = _contract()
    contract["review_queue_records"][0]["queue_submitted_to_owner"] = True

    findings = validate_contract(contract)

    assert any(
        "review/refresh/approval/signature/public/export/customer/payment/platform/final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_actual_owner_review_started():
    contract = _contract()
    contract["review_queue_records"][0]["actual_owner_review_started"] = True

    findings = validate_contract(contract)

    assert any(
        "review/refresh/approval/signature/public/export/customer/payment/platform/final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_actual_owner_signature_collected():
    contract = _contract()
    contract["review_queue_records"][0]["actual_owner_signature_collected"] = True

    findings = validate_contract(contract)

    assert any(
        "review/refresh/approval/signature/public/export/customer/payment/platform/final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_missing_queue_state():
    contract = copy.deepcopy(_contract())
    contract["queue_state_records"] = [
        item for item in contract["queue_state_records"] if item["state_id"] != "blocked_until_evidence_refresh"
    ]

    findings = validate_contract(contract)

    assert any("queue_state_records missing state ids" in finding for finding in findings)


def test_rejects_queue_state_live_action():
    contract = _contract()
    contract["queue_state_records"][0]["live_action"] = True

    findings = validate_contract(contract)

    assert any(
        "review/refresh/approval/signature/public/export/customer/payment/platform/final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_missing_precondition_record():
    contract = copy.deepcopy(_contract())
    contract["queue_entry_preconditions"] = [
        item for item in contract["queue_entry_preconditions"] if item["decision_type"] != "sns_upload"
    ]

    findings = validate_contract(contract)

    assert any("queue_entry_preconditions missing decision types" in finding for finding in findings)


def test_rejects_short_precondition_list():
    contract = _contract()
    contract["queue_entry_preconditions"][0]["required_preconditions"] = ["source hash"]

    findings = validate_contract(contract)

    assert any("required_preconditions must contain at least 6 items" in finding for finding in findings)


def test_rejects_review_routing_public_action():
    contract = _contract()
    contract["review_routing_records"][0]["public_action_allowed"] = True

    findings = validate_contract(contract)

    assert any("review_routing_records[0].public_action_allowed must be false" in finding for finding in findings)


def test_rejects_missing_owner_r3_input_record():
    contract = copy.deepcopy(_contract())
    contract["owner_r3_input_map"] = [
        item for item in contract["owner_r3_input_map"] if item["decision_type"] != "customer_contact"
    ]

    findings = validate_contract(contract)

    assert any("owner_r3_input_map missing decision types" in finding for finding in findings)


def test_rejects_owner_r3_input_signature_collected():
    contract = _contract()
    contract["owner_r3_input_map"][0]["actual_owner_signature_collected"] = True

    findings = validate_contract(contract)

    assert any(
        "review/refresh/approval/signature/public/export/customer/payment/platform/final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_missing_expiry_trigger_record():
    contract = copy.deepcopy(_contract())
    contract["expiry_invalidating_trigger_map"] = [
        item for item in contract["expiry_invalidating_trigger_map"] if item["decision_type"] != "final_pdf_export"
    ]

    findings = validate_contract(contract)

    assert any("expiry_invalidating_trigger_map missing decision types" in finding for finding in findings)


def test_rejects_expiry_trigger_refresh_allowed():
    contract = _contract()
    contract["expiry_invalidating_trigger_map"][0]["refresh_execution_allowed"] = True

    findings = validate_contract(contract)

    assert any(
        "review/refresh/approval/signature/public/export/customer/payment/platform/final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_blocked_scan_match():
    contract = _contract()
    contract["blocked_action_scan"]["owner_signature"]["matches"] = ["actual_owner_signature_collected"]

    findings = validate_contract(contract)

    assert any("blocked_action_scan.owner_signature must match source blocked action scan" in finding for finding in findings)


def test_rejects_forbidden_signature_key():
    contract = _contract()
    contract["review_queue_records"][0]["owner_signature_file"] = "signed"

    findings = validate_contract(contract)

    assert any(
        "forbidden review/approval/signature/export/customer/secret/final-advice key names" in finding
        for finding in findings
    )


def test_rejects_live_platform_flag():
    contract = _contract()
    contract["contract_summary"]["platform_api_call_enabled"] = True

    findings = validate_contract(contract)

    assert any(
        "review/refresh/approval/signature/public/export/customer/payment/platform/final-advice/live flags must not be true"
        in finding
        for finding in findings
    )
