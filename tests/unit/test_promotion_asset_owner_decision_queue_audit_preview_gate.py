from __future__ import annotations

import copy

from scripts.promotion_asset_owner_decision_queue_audit_preview_gate import load_preview, validate_preview


def _preview() -> dict:
    return load_preview()


def test_current_preview_passes():
    assert validate_preview(_preview()) == []


def test_rejects_source_hash_mismatch():
    preview = _preview()
    preview["source_inputs"][0]["sha256"] = "0" * 64

    findings = validate_preview(preview)

    assert any("sha256 mismatch" in finding for finding in findings)


def test_rejects_missing_boundary():
    preview = _preview()
    preview["boundaries"]["not_actual_owner_approval_record"] = False

    findings = validate_preview(preview)

    assert any("boundaries.not_actual_owner_approval_record must be true" in finding for finding in findings)


def test_rejects_summary_count_drift():
    preview = _preview()
    preview["audit_summary"]["actual_approval_records"] = 1

    findings = validate_preview(preview)

    assert any("audit_summary.actual_approval_records must be 0" in finding for finding in findings)


def test_rejects_missing_decision_record_summary():
    preview = copy.deepcopy(_preview())
    preview["decision_record_summaries"] = [
        item for item in preview["decision_record_summaries"] if item["decision_type"] != "sns_upload"
    ]

    findings = validate_preview(preview)

    assert any("decision_record_summaries missing records" in finding for finding in findings)


def test_rejects_summary_actual_approval():
    preview = _preview()
    preview["decision_record_summaries"][0]["actual_approval_recorded"] = True

    findings = validate_preview(preview)

    assert any("approval/public/export/customer/payment/platform/final-advice flags must not be true" in finding for finding in findings)


def test_rejects_public_use_unblocked():
    preview = _preview()
    preview["decision_record_summaries"][0]["public_use_blocked"] = False

    findings = validate_preview(preview)

    assert any("public_use_blocked must be true" in finding for finding in findings)


def test_rejects_missing_evidence_gap_decision():
    preview = copy.deepcopy(_preview())
    preview["evidence_gap_scan"] = [
        item for item in preview["evidence_gap_scan"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_preview(preview)

    assert any("evidence_gap_scan missing decision types" in finding for finding in findings)


def test_rejects_evidence_gap_action_permitted():
    preview = _preview()
    preview["evidence_gap_scan"][0]["action_permitted_now"] = True

    findings = validate_preview(preview)

    assert any("approval/public/export/customer/payment/platform/final-advice flags must not be true" in finding for finding in findings)


def test_rejects_scan_not_blocked_all():
    preview = _preview()
    preview["blocked_action_scan"]["actual_approval_record"]["blocked_all"] = False

    findings = validate_preview(preview)

    assert any("blocked_action_scan.actual_approval_record.blocked_all must be true" in finding for finding in findings)


def test_rejects_scan_match():
    preview = _preview()
    preview["blocked_action_scan"]["external_action"]["matches"] = ["platform_api_call_enabled"]

    findings = validate_preview(preview)

    assert any("blocked_action_scan.external_action.matches must be empty" in finding for finding in findings)


def test_rejects_forbidden_approval_key():
    preview = _preview()
    preview["decision_record_summaries"][0]["approval_signature"] = "signed"

    findings = validate_preview(preview)

    assert any("forbidden approval/export/customer/secret/final-advice key names" in finding for finding in findings)


def test_rejects_live_platform_flag():
    preview = _preview()
    preview["audit_summary"]["platform_api_call_enabled"] = True

    findings = validate_preview(preview)

    assert any("approval/public/export/customer/payment/platform/final-advice flags must not be true" in finding for finding in findings)
