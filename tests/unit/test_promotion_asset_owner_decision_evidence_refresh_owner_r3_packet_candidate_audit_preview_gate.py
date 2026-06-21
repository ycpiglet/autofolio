from __future__ import annotations

import copy

from scripts.promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_candidate_audit_preview_gate import (
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


def test_rejects_missing_packet_candidate_audit_boundary():
    preview = _preview()
    preview["boundaries"]["packet_candidate_audit_not_approval"] = False

    findings = validate_preview(preview)

    assert any("boundaries.packet_candidate_audit_not_approval must be true" in finding for finding in findings)


def test_rejects_summary_packet_candidate_record_drift():
    preview = _preview()
    preview["audit_summary"]["packet_candidate_record_summaries"] = 8

    findings = validate_preview(preview)

    assert any("audit_summary.packet_candidate_record_summaries must be 9" in finding for finding in findings)


def test_rejects_missing_packet_candidate_summary():
    preview = copy.deepcopy(_preview())
    preview["packet_candidate_record_summaries"] = [
        item for item in preview["packet_candidate_record_summaries"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_preview(preview)

    assert any("packet_candidate_record_summaries missing decision types" in finding for finding in findings)


def test_rejects_actual_refresh_executed():
    preview = _preview()
    preview["packet_candidate_record_summaries"][0]["actual_refresh_executed"] = True

    findings = validate_preview(preview)

    assert any(
        "refresh/approval/signature/public/export/customer/payment/platform/final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_actual_owner_approval_recorded():
    preview = _preview()
    preview["packet_candidate_record_summaries"][0]["actual_owner_approval_recorded"] = True

    findings = validate_preview(preview)

    assert any(
        "refresh/approval/signature/public/export/customer/payment/platform/final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_actual_owner_signature_collected():
    preview = _preview()
    preview["packet_candidate_record_summaries"][0]["actual_owner_signature_collected"] = True

    findings = validate_preview(preview)

    assert any(
        "refresh/approval/signature/public/export/customer/payment/platform/final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_packet_is_approval():
    preview = _preview()
    preview["packet_candidate_record_summaries"][0]["packet_is_approval"] = True

    findings = validate_preview(preview)

    assert any(
        "refresh/approval/signature/public/export/customer/payment/platform/final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_missing_evidence_bundle_reference_summary():
    preview = copy.deepcopy(_preview())
    preview["evidence_bundle_reference_summaries"] = [
        item for item in preview["evidence_bundle_reference_summaries"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_preview(preview)

    assert any("evidence_bundle_reference_summaries missing decision types" in finding for finding in findings)


def test_rejects_evidence_collection_status_drift():
    preview = _preview()
    preview["evidence_bundle_reference_summaries"][0]["collection_status"] = "collected"

    findings = validate_preview(preview)

    assert any("collection_status must match source evidence bundle reference" in finding for finding in findings)


def test_rejects_missing_owner_decision_prompt_summary():
    preview = copy.deepcopy(_preview())
    preview["owner_decision_prompt_summaries"] = [
        item for item in preview["owner_decision_prompt_summaries"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_preview(preview)

    assert any("owner_decision_prompt_summaries missing decision types" in finding for finding in findings)


def test_rejects_prompt_candidate_is_approval():
    preview = _preview()
    preview["owner_decision_prompt_summaries"][0]["candidate_is_approval"] = True

    findings = validate_preview(preview)

    assert any(
        "refresh/approval/signature/public/export/customer/payment/platform/final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_missing_unresolved_blocker_summary():
    preview = copy.deepcopy(_preview())
    preview["unresolved_blocker_summaries"] = [
        item for item in preview["unresolved_blocker_summaries"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_preview(preview)

    assert any("unresolved_blocker_summaries missing decision types" in finding for finding in findings)


def test_rejects_unresolved_blocker_status_drift():
    preview = _preview()
    preview["unresolved_blocker_summaries"][0]["status"] = "ready"

    findings = validate_preview(preview)

    assert any("status must match source unresolved blocker" in finding for finding in findings)


def test_rejects_missing_state_reference():
    preview = copy.deepcopy(_preview())
    preview["source_state_reference_safety_scan"] = [
        item
        for item in preview["source_state_reference_safety_scan"]
        if item["state_id"] != "blocked_until_refresh"
    ]

    findings = validate_preview(preview)

    assert any("source_state_reference_safety_scan missing state ids" in finding for finding in findings)


def test_rejects_trigger_refresh_execution_allowed():
    preview = _preview()
    preview["source_trigger_reference_coverage_scan"][0]["refresh_execution_allowed"] = True

    findings = validate_preview(preview)

    assert any(
        "refresh/approval/signature/public/export/customer/payment/platform/final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_blocked_scan_match():
    preview = _preview()
    preview["blocked_action_scan"]["owner_signature"]["matches"] = ["actual_owner_signature_collected"]

    findings = validate_preview(preview)

    assert any("blocked_action_scan.owner_signature must match source blocked action scan" in finding for finding in findings)


def test_rejects_forbidden_signature_key():
    preview = _preview()
    preview["packet_candidate_record_summaries"][0]["owner_signature_file"] = "signed"

    findings = validate_preview(preview)

    assert any(
        "forbidden refresh/approval/signature/export/customer/secret/final-advice key names" in finding
        for finding in findings
    )


def test_rejects_live_platform_flag():
    preview = _preview()
    preview["audit_summary"]["platform_api_call_enabled"] = True

    findings = validate_preview(preview)

    assert any(
        "refresh/approval/signature/public/export/customer/payment/platform/final-advice/live flags must not be true"
        in finding
        for finding in findings
    )
