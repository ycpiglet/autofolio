from __future__ import annotations

import copy

from scripts.promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_preflight_contract_gate import (
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


def test_rejects_missing_submission_preflight_boundary():
    contract = _contract()
    contract["boundaries"]["submission_preflight_not_submission"] = False

    findings = validate_contract(contract)

    assert any("boundaries.submission_preflight_not_submission must be true" in finding for finding in findings)


def test_rejects_actual_review_submission_boundary():
    contract = _contract()
    contract["boundaries"]["not_actual_owner_r3_review_submission"] = False

    findings = validate_contract(contract)

    assert any("boundaries.not_actual_owner_r3_review_submission must be true" in finding for finding in findings)


def test_rejects_summary_preflight_record_count_drift():
    contract = _contract()
    contract["contract_summary"]["submission_preflight_records"] = 8

    findings = validate_contract(contract)

    assert any("contract_summary.submission_preflight_records must be 9" in finding for finding in findings)


def test_rejects_source_audit_summary_drift():
    contract = copy.deepcopy(_contract())
    contract["source_review_queue_audit_summaries"] = contract["source_review_queue_audit_summaries"][:-1]

    findings = validate_contract(contract)

    assert any("source_review_queue_audit_summaries must match source audit preview" in finding for finding in findings)


def test_rejects_missing_preflight_record():
    contract = copy.deepcopy(_contract())
    contract["submission_preflight_records"] = [
        item for item in contract["submission_preflight_records"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_contract(contract)

    assert any("submission_preflight_records missing decision types" in finding for finding in findings)


def test_rejects_preflight_as_submission():
    contract = _contract()
    contract["submission_preflight_records"][0]["preflight_is_submission"] = True

    findings = validate_contract(contract)

    assert any(
        "review-submission/refresh/approval/signature/public/export/customer/payment/platform/"
        "final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_actual_owner_r3_review_submitted():
    contract = _contract()
    contract["submission_preflight_records"][0]["actual_owner_r3_review_submitted"] = True

    findings = validate_contract(contract)

    assert any(
        "review-submission/refresh/approval/signature/public/export/customer/payment/platform/"
        "final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_actual_owner_review_started():
    contract = _contract()
    contract["submission_preflight_records"][0]["actual_owner_review_started"] = True

    findings = validate_contract(contract)

    assert any(
        "review-submission/refresh/approval/signature/public/export/customer/payment/platform/"
        "final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_missing_preflight_state():
    contract = copy.deepcopy(_contract())
    contract["submission_preflight_state_records"] = [
        item
        for item in contract["submission_preflight_state_records"]
        if item["state_id"] != "preflight_blocked_by_invalidating_trigger"
    ]

    findings = validate_contract(contract)

    assert any("submission_preflight_state_records missing state ids" in finding for finding in findings)


def test_rejects_preflight_state_live_action():
    contract = _contract()
    contract["submission_preflight_state_records"][0]["live_action"] = True

    findings = validate_contract(contract)

    assert any(
        "review-submission/refresh/approval/signature/public/export/customer/payment/platform/"
        "final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_missing_preflight_prerequisite():
    contract = copy.deepcopy(_contract())
    contract["submission_preflight_prerequisites"] = [
        item for item in contract["submission_preflight_prerequisites"] if item["decision_type"] != "sns_upload"
    ]

    findings = validate_contract(contract)

    assert any("submission_preflight_prerequisites missing decision types" in finding for finding in findings)


def test_rejects_short_preflight_prerequisite_list():
    contract = _contract()
    contract["submission_preflight_prerequisites"][0]["required_preconditions"] = ["source hash"]

    findings = validate_contract(contract)

    assert any("required_preconditions must contain at least 8 items" in finding for finding in findings)


def test_rejects_missing_owner_r3_decision_package_input():
    contract = copy.deepcopy(_contract())
    contract["owner_r3_decision_package_inputs"] = [
        item
        for item in contract["owner_r3_decision_package_inputs"]
        if item["decision_type"] != "customer_contact"
    ]

    findings = validate_contract(contract)

    assert any("owner_r3_decision_package_inputs missing decision types" in finding for finding in findings)


def test_rejects_owner_r3_input_signature_collected():
    contract = _contract()
    contract["owner_r3_decision_package_inputs"][0]["actual_owner_signature_collected"] = True

    findings = validate_contract(contract)

    assert any(
        "review-submission/refresh/approval/signature/public/export/customer/payment/platform/"
        "final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_missing_submission_blocker():
    contract = copy.deepcopy(_contract())
    contract["submission_blocker_records"] = [
        item for item in contract["submission_blocker_records"] if item["decision_type"] != "final_pdf_export"
    ]

    findings = validate_contract(contract)

    assert any("submission_blocker_records missing decision types" in finding for finding in findings)


def test_rejects_submission_blocker_action_permitted():
    contract = _contract()
    contract["submission_blocker_records"][0]["action_permitted_now"] = True

    findings = validate_contract(contract)

    assert any(
        "review-submission/refresh/approval/signature/public/export/customer/payment/platform/"
        "final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_missing_invalidating_trigger():
    contract = copy.deepcopy(_contract())
    contract["invalidating_trigger_map"] = [
        item for item in contract["invalidating_trigger_map"] if item["decision_type"] != "public_landing_use"
    ]

    findings = validate_contract(contract)

    assert any("invalidating_trigger_map missing decision types" in finding for finding in findings)


def test_rejects_invalidating_trigger_review_submission_allowed():
    contract = _contract()
    contract["invalidating_trigger_map"][0]["owner_r3_review_submission_allowed"] = True

    findings = validate_contract(contract)

    assert any(
        "review-submission/refresh/approval/signature/public/export/customer/payment/platform/"
        "final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_source_queue_state_drift():
    contract = copy.deepcopy(_contract())
    contract["source_queue_state_safety_scan"] = contract["source_queue_state_safety_scan"][:-1]

    findings = validate_contract(contract)

    assert any("source_queue_state_safety_scan must match source audit preview" in finding for finding in findings)


def test_rejects_blocked_scan_match():
    contract = _contract()
    contract["blocked_action_scan"]["owner_signature"]["matches"] = ["actual_owner_signature_collected"]

    findings = validate_contract(contract)

    assert any("blocked_action_scan.owner_signature must match source blocked action scan" in finding for finding in findings)


def test_rejects_forbidden_submission_key():
    contract = _contract()
    contract["submission_preflight_records"][0]["owner_review_submission_log"] = "submitted"

    findings = validate_contract(contract)

    assert any(
        "forbidden review-submission/approval/signature/export/customer/secret/final-advice key names"
        in finding
        for finding in findings
    )


def test_rejects_live_platform_flag():
    contract = _contract()
    contract["platform_api_call_enabled"] = True

    findings = validate_contract(contract)

    assert any(
        "review-submission/refresh/approval/signature/public/export/customer/payment/platform/"
        "final-advice/live flags must not be true"
        in finding
        for finding in findings
    )
