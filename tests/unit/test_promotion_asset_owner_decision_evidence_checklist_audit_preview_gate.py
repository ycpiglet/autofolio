from __future__ import annotations

import copy

from scripts.promotion_asset_owner_decision_evidence_checklist_audit_preview_gate import (
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


def test_rejects_missing_actual_evidence_boundary():
    preview = _preview()
    preview["boundaries"]["not_actual_approval_evidence_collection"] = False

    findings = validate_preview(preview)

    assert any("boundaries.not_actual_approval_evidence_collection must be true" in finding for finding in findings)


def test_rejects_summary_actual_evidence_count_drift():
    preview = _preview()
    preview["audit_summary"]["actual_approval_evidence_records"] = 1

    findings = validate_preview(preview)

    assert any("audit_summary.actual_approval_evidence_records must be 0" in finding for finding in findings)


def test_rejects_missing_checklist_item_summary():
    preview = copy.deepcopy(_preview())
    preview["checklist_item_summaries"] = [
        item for item in preview["checklist_item_summaries"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_preview(preview)

    assert any("checklist_item_summaries missing checklist items" in finding for finding in findings)


def test_rejects_actual_approval_evidence_collected():
    preview = _preview()
    preview["checklist_item_summaries"][0]["actual_approval_evidence_collected"] = True

    findings = validate_preview(preview)

    assert any("approval/public/export/customer/payment/platform/final-advice flags must not be true" in finding for finding in findings)


def test_rejects_item_action_permitted():
    preview = _preview()
    preview["checklist_item_summaries"][0]["action_permitted_now"] = True

    findings = validate_preview(preview)

    assert any("approval/public/export/customer/payment/platform/final-advice flags must not be true" in finding for finding in findings)


def test_rejects_public_use_unblocked():
    preview = _preview()
    preview["checklist_item_summaries"][0]["public_use_blocked"] = False

    findings = validate_preview(preview)

    assert any("public_use_blocked must be true" in finding for finding in findings)


def test_rejects_missing_evidence_alignment_decision():
    preview = copy.deepcopy(_preview())
    preview["evidence_alignment_scan"] = [
        item for item in preview["evidence_alignment_scan"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_preview(preview)

    assert any("evidence_alignment_scan missing decision types" in finding for finding in findings)


def test_rejects_evidence_count_mismatch():
    preview = _preview()
    preview["evidence_alignment_scan"][0]["required_evidence_count"] = 1

    findings = validate_preview(preview)

    assert any("required_evidence_count must match source checklist" in finding for finding in findings)


def test_rejects_missing_stale_coverage():
    preview = _preview()
    preview["evidence_alignment_scan"][0]["stale_evidence_status"] = "missing"

    findings = validate_preview(preview)

    assert any("stale_evidence_status must be covered" in finding for finding in findings)


def test_rejects_scan_match():
    preview = _preview()
    preview["blocked_action_scan"]["approval_evidence_collection"]["matches"] = ["actual_approval_evidence_collected"]

    findings = validate_preview(preview)

    assert any("blocked_action_scan.approval_evidence_collection.matches must be empty" in finding for finding in findings)


def test_rejects_forbidden_approval_key():
    preview = _preview()
    preview["checklist_item_summaries"][0]["owner_signature_file"] = "signed"

    findings = validate_preview(preview)

    assert any("forbidden approval/export/customer/secret/final-advice key names" in finding for finding in findings)


def test_rejects_live_platform_flag():
    preview = _preview()
    preview["audit_summary"]["platform_api_call_enabled"] = True

    findings = validate_preview(preview)

    assert any("approval/public/export/customer/payment/platform/final-advice flags must not be true" in finding for finding in findings)
