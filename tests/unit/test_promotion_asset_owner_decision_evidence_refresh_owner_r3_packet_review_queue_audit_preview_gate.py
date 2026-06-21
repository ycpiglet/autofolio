from __future__ import annotations

import copy

from scripts.promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_queue_audit_preview_gate import (
    load_preview,
    validate_preview,
)


def _preview() -> dict:
    return load_preview()


def test_current_preview_passes():
    assert validate_preview(_preview()) == []


def test_rejects_source_hash_mismatch():
    preview = _preview()
    preview["source_inputs"][0]["sha256"] = "0" * 64

    findings = validate_preview(preview)

    assert any("sha256 mismatch" in finding for finding in findings)


def test_rejects_missing_review_queue_audit_boundary():
    preview = _preview()
    preview["boundaries"]["review_queue_audit_not_approval"] = False

    findings = validate_preview(preview)

    assert any("boundaries.review_queue_audit_not_approval must be true" in finding for finding in findings)


def test_rejects_actual_review_submission_boundary():
    preview = _preview()
    preview["boundaries"]["not_actual_owner_r3_review_submission"] = False

    findings = validate_preview(preview)

    assert any("boundaries.not_actual_owner_r3_review_submission must be true" in finding for finding in findings)


def test_rejects_summary_review_queue_count_drift():
    preview = _preview()
    preview["audit_summary"]["review_queue_record_summaries"] = 8

    findings = validate_preview(preview)

    assert any("audit_summary.review_queue_record_summaries must be 9" in finding for finding in findings)


def test_rejects_missing_review_queue_summary():
    preview = copy.deepcopy(_preview())
    preview["review_queue_record_summaries"] = [
        item for item in preview["review_queue_record_summaries"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_preview(preview)

    assert any("review_queue_record_summaries missing decision types" in finding for finding in findings)


def test_rejects_review_queue_as_approval():
    preview = _preview()
    preview["review_queue_record_summaries"][0]["review_queue_is_approval"] = True

    findings = validate_preview(preview)

    assert any(
        "review-submission/refresh/approval/signature/public/export/customer/payment/platform/"
        "final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_queue_submitted_to_owner():
    preview = _preview()
    preview["review_queue_record_summaries"][0]["queue_submitted_to_owner"] = True

    findings = validate_preview(preview)

    assert any(
        "review-submission/refresh/approval/signature/public/export/customer/payment/platform/"
        "final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_actual_owner_review_started():
    preview = _preview()
    preview["review_queue_record_summaries"][0]["actual_owner_review_started"] = True

    findings = validate_preview(preview)

    assert any(
        "review-submission/refresh/approval/signature/public/export/customer/payment/platform/"
        "final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_missing_queue_state():
    preview = copy.deepcopy(_preview())
    preview["queue_state_safety_scan"] = [
        item for item in preview["queue_state_safety_scan"] if item["state_id"] != "blocked_until_evidence_refresh"
    ]

    findings = validate_preview(preview)

    assert any("queue_state_safety_scan missing state ids" in finding for finding in findings)


def test_rejects_queue_state_live_action():
    preview = _preview()
    preview["queue_state_safety_scan"][0]["live_action"] = True

    findings = validate_preview(preview)

    assert any(
        "review-submission/refresh/approval/signature/public/export/customer/payment/platform/"
        "final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_missing_precondition_summary():
    preview = copy.deepcopy(_preview())
    preview["queue_entry_precondition_summaries"] = [
        item for item in preview["queue_entry_precondition_summaries"] if item["decision_type"] != "sns_upload"
    ]

    findings = validate_preview(preview)

    assert any("queue_entry_precondition_summaries missing decision types" in finding for finding in findings)


def test_rejects_short_precondition_list():
    preview = _preview()
    preview["queue_entry_precondition_summaries"][0]["required_preconditions"] = ["source hash"]

    findings = validate_preview(preview)

    assert any("required_preconditions must contain at least 6 items" in finding for finding in findings)


def test_rejects_review_routing_public_action():
    preview = _preview()
    preview["review_routing_summaries"][0]["public_action_allowed"] = True

    findings = validate_preview(preview)

    assert any(
        "review-submission/refresh/approval/signature/public/export/customer/payment/platform/"
        "final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_missing_owner_r3_input_summary():
    preview = copy.deepcopy(_preview())
    preview["owner_r3_input_summaries"] = [
        item for item in preview["owner_r3_input_summaries"] if item["decision_type"] != "customer_contact"
    ]

    findings = validate_preview(preview)

    assert any("owner_r3_input_summaries missing decision types" in finding for finding in findings)


def test_rejects_owner_r3_input_signature_collected():
    preview = _preview()
    preview["owner_r3_input_summaries"][0]["actual_owner_signature_collected"] = True

    findings = validate_preview(preview)

    assert any(
        "review-submission/refresh/approval/signature/public/export/customer/payment/platform/"
        "final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_missing_expiry_trigger_summary():
    preview = copy.deepcopy(_preview())
    preview["expiry_invalidating_trigger_summaries"] = [
        item for item in preview["expiry_invalidating_trigger_summaries"] if item["decision_type"] != "final_pdf_export"
    ]

    findings = validate_preview(preview)

    assert any("expiry_invalidating_trigger_summaries missing decision types" in finding for finding in findings)


def test_rejects_expiry_trigger_refresh_allowed():
    preview = _preview()
    preview["expiry_invalidating_trigger_summaries"][0]["refresh_execution_allowed"] = True

    findings = validate_preview(preview)

    assert any(
        "review-submission/refresh/approval/signature/public/export/customer/payment/platform/"
        "final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_missing_source_state_reference():
    preview = copy.deepcopy(_preview())
    preview["source_state_reference_safety_scan"] = [
        item
        for item in preview["source_state_reference_safety_scan"]
        if item["state_id"] != "blocked_until_refresh"
    ]

    findings = validate_preview(preview)

    assert any("source_state_reference_safety_scan missing state ids" in finding for finding in findings)


def test_rejects_missing_source_trigger_reference():
    preview = copy.deepcopy(_preview())
    preview["source_trigger_reference_coverage_scan"] = [
        item
        for item in preview["source_trigger_reference_coverage_scan"]
        if item["trigger_id"] != "source_preview_hash_change"
    ]

    findings = validate_preview(preview)

    assert any("source_trigger_reference_coverage_scan missing trigger ids" in finding for finding in findings)


def test_rejects_blocked_scan_match():
    preview = _preview()
    preview["blocked_action_scan"]["owner_signature"]["matches"] = ["actual_owner_signature_collected"]

    findings = validate_preview(preview)

    assert any("blocked_action_scan.owner_signature must match source blocked action scan" in finding for finding in findings)


def test_rejects_forbidden_submission_key():
    preview = _preview()
    preview["review_queue_record_summaries"][0]["owner_review_submission_log"] = "submitted"

    findings = validate_preview(preview)

    assert any(
        "forbidden review-submission/approval/signature/export/customer/secret/final-advice key names"
        in finding
        for finding in findings
    )


def test_rejects_live_platform_flag():
    preview = _preview()
    preview["audit_summary"]["platform_api_call_enabled"] = True

    findings = validate_preview(preview)

    assert any(
        "review-submission/refresh/approval/signature/public/export/customer/payment/platform/"
        "final-advice/live flags must not be true"
        in finding
        for finding in findings
    )
