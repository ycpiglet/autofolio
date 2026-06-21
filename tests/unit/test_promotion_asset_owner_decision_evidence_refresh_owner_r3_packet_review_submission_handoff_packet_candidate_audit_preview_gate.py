from __future__ import annotations

import copy

from scripts.promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_audit_preview_gate import (
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
    preview["boundaries"]["handoff_packet_candidate_audit_not_submission"] = False

    findings = validate_preview(preview)

    assert any("boundaries.handoff_packet_candidate_audit_not_submission must be true" in finding for finding in findings)


def test_rejects_actual_review_start_boundary():
    preview = _preview()
    preview["boundaries"]["not_actual_owner_review_started"] = False

    findings = validate_preview(preview)

    assert any("boundaries.not_actual_owner_review_started must be true" in finding for finding in findings)


def test_rejects_summary_handoff_record_count_drift():
    preview = _preview()
    preview["audit_summary"]["handoff_packet_record_summaries"] = 8

    findings = validate_preview(preview)

    assert any("audit_summary.handoff_packet_record_summaries must be 9" in finding for finding in findings)


def test_rejects_source_total_count_drift():
    preview = _preview()
    preview["audit_summary"]["total_source_required_evidence_items"] = 24

    findings = validate_preview(preview)

    assert any("audit_summary.total_source_required_evidence_items must be 25" in finding for finding in findings)


def test_rejects_missing_handoff_record():
    preview = copy.deepcopy(_preview())
    preview["handoff_packet_record_summaries"] = [
        item for item in preview["handoff_packet_record_summaries"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_preview(preview)

    assert any("handoff_packet_record_summaries missing decision types" in finding for finding in findings)


def test_rejects_source_record_drift():
    preview = _preview()
    preview["handoff_packet_record_summaries"][0]["source_submission_preflight_record_id"] = "wrong"

    findings = validate_preview(preview)

    assert any("handoff_packet_record_summaries must match source candidate" in finding for finding in findings)


def test_rejects_handoff_as_submission():
    preview = _preview()
    preview["handoff_packet_record_summaries"][0]["handoff_packet_is_submission"] = True

    findings = validate_preview(preview)

    assert any("review-start/submission/refresh/approval/signature/public/export/customer/payment/platform/" in finding for finding in findings)


def test_rejects_actual_owner_review_started():
    preview = _preview()
    preview["handoff_packet_record_summaries"][0]["actual_owner_review_started"] = True

    findings = validate_preview(preview)

    assert any("review-start/submission/refresh/approval/signature/public/export/customer/payment/platform/" in finding for finding in findings)


def test_rejects_actual_owner_r3_review_submitted():
    preview = _preview()
    preview["handoff_packet_record_summaries"][0]["actual_owner_r3_review_submitted"] = True

    findings = validate_preview(preview)

    assert any("review-start/submission/refresh/approval/signature/public/export/customer/payment/platform/" in finding for finding in findings)


def test_rejects_missing_owner_r3_input_summary():
    preview = copy.deepcopy(_preview())
    preview["owner_r3_required_input_summaries"] = [
        item for item in preview["owner_r3_required_input_summaries"] if item["decision_type"] != "sns_upload"
    ]

    findings = validate_preview(preview)

    assert any("owner_r3_required_input_summaries missing decision types" in finding for finding in findings)


def test_rejects_owner_r3_input_values_collected():
    preview = _preview()
    preview["owner_r3_required_input_summaries"][0]["handoff_packet_includes_actual_input_values"] = True

    findings = validate_preview(preview)

    assert any("handoff_packet_includes_actual_input_values" in finding for finding in findings)


def test_rejects_owner_signature_collected():
    preview = _preview()
    preview["owner_r3_required_input_summaries"][0]["actual_owner_signature_collected"] = True

    findings = validate_preview(preview)

    assert any("review-start/submission/refresh/approval/signature/public/export/customer/payment/platform/" in finding for finding in findings)


def test_rejects_missing_unresolved_blocker():
    preview = copy.deepcopy(_preview())
    preview["unresolved_blocker_summaries"] = [
        item for item in preview["unresolved_blocker_summaries"] if item["decision_type"] != "final_pdf_export"
    ]

    findings = validate_preview(preview)

    assert any("unresolved_blocker_summaries missing decision types" in finding for finding in findings)


def test_rejects_blocker_action_permitted():
    preview = _preview()
    preview["unresolved_blocker_summaries"][0]["action_permitted_now"] = True

    findings = validate_preview(preview)

    assert any("review-start/submission/refresh/approval/signature/public/export/customer/payment/platform/" in finding for finding in findings)


def test_rejects_missing_invalidating_trigger():
    preview = copy.deepcopy(_preview())
    preview["invalidating_trigger_summaries"] = [
        item for item in preview["invalidating_trigger_summaries"] if item["decision_type"] != "public_landing_use"
    ]

    findings = validate_preview(preview)

    assert any("invalidating_trigger_summaries missing decision types" in finding for finding in findings)


def test_rejects_invalidating_trigger_review_start():
    preview = _preview()
    preview["invalidating_trigger_summaries"][0]["actual_owner_review_started"] = True

    findings = validate_preview(preview)

    assert any("review-start/submission/refresh/approval/signature/public/export/customer/payment/platform/" in finding for finding in findings)


def test_rejects_source_preflight_state_drift():
    preview = copy.deepcopy(_preview())
    preview["source_preflight_state_safety_scan"] = preview["source_preflight_state_safety_scan"][:-1]

    findings = validate_preview(preview)

    assert any("source_preflight_state_safety_scan must match source candidate" in finding for finding in findings)


def test_rejects_source_trigger_reference_drift():
    preview = copy.deepcopy(_preview())
    preview["source_trigger_reference_coverage_scan"] = preview["source_trigger_reference_coverage_scan"][:-1]

    findings = validate_preview(preview)

    assert any("source_trigger_reference_coverage_scan must match source candidate" in finding for finding in findings)


def test_rejects_blocked_scan_match():
    preview = _preview()
    preview["blocked_action_scan"]["owner_signature"]["matches"] = ["actual_owner_signature_collected"]

    findings = validate_preview(preview)

    assert any("blocked_action_scan.owner_signature must match source blocked action scan" in finding for finding in findings)


def test_rejects_missing_assembly_step():
    preview = copy.deepcopy(_preview())
    preview["handoff_packet_assembly_step_summaries"] = [
        item for item in preview["handoff_packet_assembly_step_summaries"] if item["step_id"] != "scan_blocked_actions"
    ]

    findings = validate_preview(preview)

    assert any("handoff_packet_assembly_step_summaries must match source candidate" in finding for finding in findings)


def test_rejects_external_assembly_action():
    preview = _preview()
    preview["handoff_packet_assembly_step_summaries"][0]["external_action"] = True

    findings = validate_preview(preview)

    assert any("handoff_packet_assembly_step_summaries[0].external_action must be false" in finding for finding in findings)


def test_rejects_missing_audit_event():
    preview = copy.deepcopy(_preview())
    preview["audit_events"] = [item for item in preview["audit_events"] if item["event"] != "blocked_action_scan_passed"]

    findings = validate_preview(preview)

    assert any("audit_events missing blocked_action_scan_passed" in finding for finding in findings)


def test_rejects_external_audit_event():
    preview = _preview()
    preview["audit_events"][0]["external_action"] = True

    findings = validate_preview(preview)

    assert any("audit_events[0].external_action must be false" in finding for finding in findings)


def test_rejects_forbidden_submission_key():
    preview = _preview()
    preview["handoff_packet_record_summaries"][0]["review_submission_receipt"] = "submitted"

    findings = validate_preview(preview)

    assert any("forbidden review-submission/approval/signature/export/customer/secret/final-advice key names" in finding for finding in findings)


def test_rejects_live_platform_flag():
    preview = _preview()
    preview["platform_api_call_enabled"] = True

    findings = validate_preview(preview)

    assert any("review-start/submission/refresh/approval/signature/public/export/customer/payment/platform/" in finding for finding in findings)
