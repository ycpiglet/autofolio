from __future__ import annotations

import copy

from scripts.promotion_asset_owner_decision_evidence_refresh_work_order_audit_preview_gate import (
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


def test_rejects_missing_not_actual_refresh_execution_boundary():
    preview = _preview()
    preview["boundaries"]["not_actual_refresh_execution"] = False

    findings = validate_preview(preview)

    assert any("boundaries.not_actual_refresh_execution must be true" in finding for finding in findings)


def test_rejects_summary_record_drift():
    preview = _preview()
    preview["audit_summary"]["refresh_work_order_record_summaries"] = 8

    findings = validate_preview(preview)

    assert any("audit_summary.refresh_work_order_record_summaries must be 9" in finding for finding in findings)


def test_rejects_missing_work_order_summary():
    preview = copy.deepcopy(_preview())
    preview["refresh_work_order_record_summaries"] = [
        item for item in preview["refresh_work_order_record_summaries"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_preview(preview)

    assert any("refresh_work_order_record_summaries missing decision types" in finding for finding in findings)


def test_rejects_actual_refresh_executed():
    preview = _preview()
    preview["refresh_work_order_record_summaries"][0]["actual_refresh_executed"] = True

    findings = validate_preview(preview)

    assert any("refresh/approval/public/export/customer/payment/platform/final-advice/live flags must not be true" in finding for finding in findings)


def test_rejects_actual_approval_evidence_collected():
    preview = _preview()
    preview["refresh_work_order_record_summaries"][0]["actual_approval_evidence_collected"] = True

    findings = validate_preview(preview)

    assert any("refresh/approval/public/export/customer/payment/platform/final-advice/live flags must not be true" in finding for finding in findings)


def test_rejects_action_permitted():
    preview = _preview()
    preview["refresh_work_order_record_summaries"][0]["action_permitted_now"] = True

    findings = validate_preview(preview)

    assert any("refresh/approval/public/export/customer/payment/platform/final-advice/live flags must not be true" in finding for finding in findings)


def test_rejects_state_live_action():
    preview = _preview()
    preview["work_order_state_safety_scan"][0]["live_action"] = True

    findings = validate_preview(preview)

    assert any("refresh/approval/public/export/customer/payment/platform/final-advice/live flags must not be true" in finding for finding in findings)


def test_rejects_missing_precondition_proof_expiry_coverage():
    preview = copy.deepcopy(_preview())
    preview["precondition_proof_expiry_coverage_scan"] = [
        item for item in preview["precondition_proof_expiry_coverage_scan"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_preview(preview)

    assert any("precondition_proof_expiry_coverage_scan missing decision types" in finding for finding in findings)


def test_rejects_expiry_trigger_count_drift():
    preview = _preview()
    preview["precondition_proof_expiry_coverage_scan"][0]["expiry_trigger_count"] = 0

    findings = validate_preview(preview)

    assert any("expiry_trigger_count must match source contract expiry_triggers" in finding for finding in findings)


def test_rejects_missing_trigger_map_coverage():
    preview = copy.deepcopy(_preview())
    preview["invalidating_trigger_map_coverage_scan"] = [
        item for item in preview["invalidating_trigger_map_coverage_scan"] if item["trigger_id"] != "blocked_action_scan_change"
    ]

    findings = validate_preview(preview)

    assert any("invalidating_trigger_map_coverage_scan missing triggers" in finding for finding in findings)


def test_rejects_trigger_map_refresh_execution_allowed():
    preview = _preview()
    preview["invalidating_trigger_map_coverage_scan"][0]["refresh_execution_allowed"] = True

    findings = validate_preview(preview)

    assert any("refresh/approval/public/export/customer/payment/platform/final-advice/live flags must not be true" in finding for finding in findings)


def test_rejects_source_count_mismatch():
    preview = _preview()
    preview["refresh_work_order_record_summaries"][0]["source_required_evidence_count"] = 99

    findings = validate_preview(preview)

    assert any("source_required_evidence_count must match source contract source_required_evidence_count" in finding for finding in findings)


def test_rejects_scan_match():
    preview = _preview()
    preview["blocked_action_scan"]["actual_refresh_execution"]["matches"] = ["actual_refresh_executed"]

    findings = validate_preview(preview)

    assert any("blocked_action_scan.actual_refresh_execution.matches must be empty" in finding for finding in findings)


def test_rejects_forbidden_approval_key():
    preview = _preview()
    preview["refresh_work_order_record_summaries"][0]["owner_signature_file"] = "signed"

    findings = validate_preview(preview)

    assert any("forbidden refresh/approval/export/customer/secret/final-advice key names" in finding for finding in findings)


def test_rejects_live_platform_flag():
    preview = _preview()
    preview["audit_summary"]["platform_api_call_enabled"] = True

    findings = validate_preview(preview)

    assert any("refresh/approval/public/export/customer/payment/platform/final-advice/live flags must not be true" in finding for finding in findings)
