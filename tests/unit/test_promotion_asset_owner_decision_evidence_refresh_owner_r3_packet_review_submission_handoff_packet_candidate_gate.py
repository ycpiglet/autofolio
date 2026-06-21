from __future__ import annotations

import copy

from scripts.promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_gate import (
    load_candidate,
    validate_candidate,
)


def _candidate() -> dict:
    return load_candidate()


def test_current_candidate_passes():
    assert validate_candidate(_candidate()) == []


def test_rejects_source_hash_mismatch():
    candidate = _candidate()
    candidate["source_inputs"][0]["sha256"] = "0" * 64

    findings = validate_candidate(candidate)

    assert any("sha256 mismatch" in finding for finding in findings)


def test_rejects_missing_handoff_boundary():
    candidate = _candidate()
    candidate["boundaries"]["handoff_packet_candidate_not_submission"] = False

    findings = validate_candidate(candidate)

    assert any("boundaries.handoff_packet_candidate_not_submission must be true" in finding for finding in findings)


def test_rejects_actual_review_start_boundary():
    candidate = _candidate()
    candidate["boundaries"]["not_actual_owner_review_started"] = False

    findings = validate_candidate(candidate)

    assert any("boundaries.not_actual_owner_review_started must be true" in finding for finding in findings)


def test_rejects_summary_handoff_record_count_drift():
    candidate = _candidate()
    candidate["candidate_summary"]["handoff_packet_records"] = 8

    findings = validate_candidate(candidate)

    assert any("candidate_summary.handoff_packet_records must be 9" in finding for finding in findings)


def test_rejects_source_total_count_drift():
    candidate = _candidate()
    candidate["candidate_summary"]["total_source_required_evidence_items"] = 24

    findings = validate_candidate(candidate)

    assert any("candidate_summary.total_source_required_evidence_items must be 25" in finding for finding in findings)


def test_rejects_missing_handoff_record():
    candidate = copy.deepcopy(_candidate())
    candidate["handoff_packet_records"] = [
        item for item in candidate["handoff_packet_records"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_candidate(candidate)

    assert any("handoff_packet_records missing decision types" in finding for finding in findings)


def test_rejects_source_link_drift():
    candidate = _candidate()
    candidate["handoff_packet_records"][0]["source_submission_preflight_record_id"] = "wrong"

    findings = validate_candidate(candidate)

    assert any("source_submission_preflight_record_id must match source preflight summary" in finding for finding in findings)


def test_rejects_handoff_as_submission():
    candidate = _candidate()
    candidate["handoff_packet_records"][0]["handoff_packet_is_submission"] = True

    findings = validate_candidate(candidate)

    assert any("review-start/submission/refresh/approval/signature/public/export/customer/payment/platform/" in finding for finding in findings)


def test_rejects_actual_owner_review_started():
    candidate = _candidate()
    candidate["handoff_packet_records"][0]["actual_owner_review_started"] = True

    findings = validate_candidate(candidate)

    assert any("review-start/submission/refresh/approval/signature/public/export/customer/payment/platform/" in finding for finding in findings)


def test_rejects_actual_owner_r3_review_submitted():
    candidate = _candidate()
    candidate["handoff_packet_records"][0]["actual_owner_r3_review_submitted"] = True

    findings = validate_candidate(candidate)

    assert any("review-start/submission/refresh/approval/signature/public/export/customer/payment/platform/" in finding for finding in findings)


def test_rejects_missing_owner_r3_input_summary():
    candidate = copy.deepcopy(_candidate())
    candidate["owner_r3_required_input_summaries"] = [
        item for item in candidate["owner_r3_required_input_summaries"] if item["decision_type"] != "sns_upload"
    ]

    findings = validate_candidate(candidate)

    assert any("owner_r3_required_input_summaries missing decision types" in finding for finding in findings)


def test_rejects_owner_r3_input_values_collected():
    candidate = _candidate()
    candidate["owner_r3_required_input_summaries"][0]["handoff_packet_includes_actual_input_values"] = True

    findings = validate_candidate(candidate)

    assert any("handoff_packet_includes_actual_input_values must be false" in finding for finding in findings)


def test_rejects_owner_signature_collected():
    candidate = _candidate()
    candidate["owner_r3_required_input_summaries"][0]["actual_owner_signature_collected"] = True

    findings = validate_candidate(candidate)

    assert any("review-start/submission/refresh/approval/signature/public/export/customer/payment/platform/" in finding for finding in findings)


def test_rejects_missing_unresolved_blocker():
    candidate = copy.deepcopy(_candidate())
    candidate["unresolved_blocker_summaries"] = [
        item for item in candidate["unresolved_blocker_summaries"] if item["decision_type"] != "final_pdf_export"
    ]

    findings = validate_candidate(candidate)

    assert any("unresolved_blocker_summaries missing decision types" in finding for finding in findings)


def test_rejects_blocker_action_permitted():
    candidate = _candidate()
    candidate["unresolved_blocker_summaries"][0]["action_permitted_now"] = True

    findings = validate_candidate(candidate)

    assert any("review-start/submission/refresh/approval/signature/public/export/customer/payment/platform/" in finding for finding in findings)


def test_rejects_missing_invalidating_trigger():
    candidate = copy.deepcopy(_candidate())
    candidate["invalidating_trigger_summaries"] = [
        item for item in candidate["invalidating_trigger_summaries"] if item["decision_type"] != "public_landing_use"
    ]

    findings = validate_candidate(candidate)

    assert any("invalidating_trigger_summaries missing decision types" in finding for finding in findings)


def test_rejects_invalidating_trigger_review_start():
    candidate = _candidate()
    candidate["invalidating_trigger_summaries"][0]["actual_owner_review_started"] = True

    findings = validate_candidate(candidate)

    assert any("review-start/submission/refresh/approval/signature/public/export/customer/payment/platform/" in finding for finding in findings)


def test_rejects_source_preflight_state_drift():
    candidate = copy.deepcopy(_candidate())
    candidate["source_preflight_state_safety_scan"] = candidate["source_preflight_state_safety_scan"][:-1]

    findings = validate_candidate(candidate)

    assert any("source_preflight_state_safety_scan must match source preview" in finding for finding in findings)


def test_rejects_source_trigger_reference_drift():
    candidate = copy.deepcopy(_candidate())
    candidate["source_trigger_reference_coverage_scan"] = candidate["source_trigger_reference_coverage_scan"][:-1]

    findings = validate_candidate(candidate)

    assert any("source_trigger_reference_coverage_scan must match source preview" in finding for finding in findings)


def test_rejects_blocked_scan_match():
    candidate = _candidate()
    candidate["blocked_action_scan"]["owner_signature"]["matches"] = ["actual_owner_signature_collected"]

    findings = validate_candidate(candidate)

    assert any("blocked_action_scan.owner_signature must match source blocked action scan" in finding for finding in findings)


def test_rejects_missing_assembly_step():
    candidate = copy.deepcopy(_candidate())
    candidate["handoff_packet_assembly_steps"] = [
        item for item in candidate["handoff_packet_assembly_steps"] if item["step_id"] != "scan_blocked_actions"
    ]

    findings = validate_candidate(candidate)

    assert any("handoff_packet_assembly_steps missing scan_blocked_actions" in finding for finding in findings)


def test_rejects_external_assembly_action():
    candidate = _candidate()
    candidate["handoff_packet_assembly_steps"][0]["external_action"] = True

    findings = validate_candidate(candidate)

    assert any("handoff_packet_assembly_steps[0].external_action must be false" in finding for finding in findings)


def test_rejects_forbidden_submission_key():
    candidate = _candidate()
    candidate["handoff_packet_records"][0]["review_submission_receipt"] = "submitted"

    findings = validate_candidate(candidate)

    assert any("forbidden review-submission/approval/signature/export/customer/secret/final-advice key names" in finding for finding in findings)


def test_rejects_live_platform_flag():
    candidate = _candidate()
    candidate["platform_api_call_enabled"] = True

    findings = validate_candidate(candidate)

    assert any("review-start/submission/refresh/approval/signature/public/export/customer/payment/platform/" in finding for finding in findings)
