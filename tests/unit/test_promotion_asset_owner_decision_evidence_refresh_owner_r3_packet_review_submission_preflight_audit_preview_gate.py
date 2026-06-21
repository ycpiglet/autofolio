from __future__ import annotations

import copy

from scripts.promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_preflight_audit_preview_gate import (
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


def test_rejects_missing_audit_boundary():
    preview = _preview()
    preview["boundaries"]["submission_preflight_audit_not_submission"] = False

    findings = validate_preview(preview)

    assert any("boundaries.submission_preflight_audit_not_submission must be true" in finding for finding in findings)


def test_rejects_actual_review_submission_boundary():
    preview = _preview()
    preview["boundaries"]["not_actual_owner_r3_review_submission"] = False

    findings = validate_preview(preview)

    assert any("boundaries.not_actual_owner_r3_review_submission must be true" in finding for finding in findings)


def test_rejects_summary_preflight_record_count_drift():
    preview = _preview()
    preview["audit_summary"]["submission_preflight_record_summaries"] = 8

    findings = validate_preview(preview)

    assert any("audit_summary.submission_preflight_record_summaries must be 9" in finding for finding in findings)


def test_rejects_source_preflight_record_drift():
    preview = copy.deepcopy(_preview())
    preview["submission_preflight_record_summaries"] = preview["submission_preflight_record_summaries"][:-1]

    findings = validate_preview(preview)

    assert any("submission_preflight_record_summaries must match source contract" in finding for finding in findings)


def test_rejects_missing_preflight_summary():
    preview = copy.deepcopy(_preview())
    preview["submission_preflight_record_summaries"] = [
        item for item in preview["submission_preflight_record_summaries"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_preview(preview)

    assert any("submission_preflight_record_summaries missing decision types" in finding for finding in findings)


def test_rejects_preflight_as_submission():
    preview = _preview()
    preview["submission_preflight_record_summaries"][0]["preflight_is_submission"] = True

    findings = validate_preview(preview)

    assert any(
        "review-submission/refresh/approval/signature/public/export/customer/payment/platform/"
        "final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_actual_owner_r3_review_submitted():
    preview = _preview()
    preview["submission_preflight_record_summaries"][0]["actual_owner_r3_review_submitted"] = True

    findings = validate_preview(preview)

    assert any(
        "review-submission/refresh/approval/signature/public/export/customer/payment/platform/"
        "final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_actual_owner_review_started():
    preview = _preview()
    preview["submission_preflight_record_summaries"][0]["actual_owner_review_started"] = True

    findings = validate_preview(preview)

    assert any(
        "review-submission/refresh/approval/signature/public/export/customer/payment/platform/"
        "final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_missing_preflight_state():
    preview = copy.deepcopy(_preview())
    preview["preflight_state_safety_scan"] = [
        item
        for item in preview["preflight_state_safety_scan"]
        if item["state_id"] != "preflight_blocked_by_invalidating_trigger"
    ]

    findings = validate_preview(preview)

    assert any("preflight_state_safety_scan missing state ids" in finding for finding in findings)


def test_rejects_preflight_state_live_action():
    preview = _preview()
    preview["preflight_state_safety_scan"][0]["live_action"] = True

    findings = validate_preview(preview)

    assert any(
        "review-submission/refresh/approval/signature/public/export/customer/payment/platform/"
        "final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_missing_prerequisite_summary():
    preview = copy.deepcopy(_preview())
    preview["preflight_prerequisite_summaries"] = [
        item for item in preview["preflight_prerequisite_summaries"] if item["decision_type"] != "sns_upload"
    ]

    findings = validate_preview(preview)

    assert any("preflight_prerequisite_summaries missing decision types" in finding for finding in findings)


def test_rejects_short_prerequisite_list():
    preview = _preview()
    preview["preflight_prerequisite_summaries"][0]["required_preconditions"] = ["source hash"]

    findings = validate_preview(preview)

    assert any("required_preconditions must contain at least 8 items" in finding for finding in findings)


def test_rejects_missing_owner_r3_input_summary():
    preview = copy.deepcopy(_preview())
    preview["owner_r3_decision_package_input_summaries"] = [
        item
        for item in preview["owner_r3_decision_package_input_summaries"]
        if item["decision_type"] != "customer_contact"
    ]

    findings = validate_preview(preview)

    assert any("owner_r3_decision_package_input_summaries missing decision types" in finding for finding in findings)


def test_rejects_owner_r3_input_signature_collected():
    preview = _preview()
    preview["owner_r3_decision_package_input_summaries"][0]["actual_owner_signature_collected"] = True

    findings = validate_preview(preview)

    assert any(
        "review-submission/refresh/approval/signature/public/export/customer/payment/platform/"
        "final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_missing_submission_blocker():
    preview = copy.deepcopy(_preview())
    preview["submission_blocker_summaries"] = [
        item for item in preview["submission_blocker_summaries"] if item["decision_type"] != "final_pdf_export"
    ]

    findings = validate_preview(preview)

    assert any("submission_blocker_summaries missing decision types" in finding for finding in findings)


def test_rejects_submission_blocker_action_permitted():
    preview = _preview()
    preview["submission_blocker_summaries"][0]["action_permitted_now"] = True

    findings = validate_preview(preview)

    assert any(
        "review-submission/refresh/approval/signature/public/export/customer/payment/platform/"
        "final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_missing_invalidating_trigger():
    preview = copy.deepcopy(_preview())
    preview["invalidating_trigger_summaries"] = [
        item for item in preview["invalidating_trigger_summaries"] if item["decision_type"] != "public_landing_use"
    ]

    findings = validate_preview(preview)

    assert any("invalidating_trigger_summaries missing decision types" in finding for finding in findings)


def test_rejects_invalidating_trigger_review_submission_allowed():
    preview = _preview()
    preview["invalidating_trigger_summaries"][0]["owner_r3_review_submission_allowed"] = True

    findings = validate_preview(preview)

    assert any(
        "review-submission/refresh/approval/signature/public/export/customer/payment/platform/"
        "final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_source_queue_state_drift():
    preview = copy.deepcopy(_preview())
    preview["source_queue_state_safety_scan"] = preview["source_queue_state_safety_scan"][:-1]

    findings = validate_preview(preview)

    assert any("source_queue_state_safety_scan must match source contract" in finding for finding in findings)


def test_rejects_blocked_scan_match():
    preview = _preview()
    preview["blocked_action_scan"]["owner_signature"]["matches"] = ["actual_owner_signature_collected"]

    findings = validate_preview(preview)

    assert any("blocked_action_scan.owner_signature must match source blocked action scan" in finding for finding in findings)


def test_rejects_forbidden_submission_key():
    preview = _preview()
    preview["submission_preflight_record_summaries"][0]["owner_review_submission_log"] = "submitted"

    findings = validate_preview(preview)

    assert any(
        "forbidden review-submission/approval/signature/export/customer/secret/final-advice key names"
        in finding
        for finding in findings
    )


def test_rejects_live_platform_flag():
    preview = _preview()
    preview["platform_api_call_enabled"] = True

    findings = validate_preview(preview)

    assert any(
        "review-submission/refresh/approval/signature/public/export/customer/payment/platform/"
        "final-advice/live flags must not be true"
        in finding
        for finding in findings
    )
