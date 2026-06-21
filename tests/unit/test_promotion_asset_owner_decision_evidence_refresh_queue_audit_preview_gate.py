from __future__ import annotations

import copy

from scripts.promotion_asset_owner_decision_evidence_refresh_queue_audit_preview_gate import (
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


def test_rejects_summary_record_drift():
    preview = _preview()
    preview["audit_summary"]["refresh_queue_record_summaries"] = 8

    findings = validate_preview(preview)

    assert any("audit_summary.refresh_queue_record_summaries must be 9" in finding for finding in findings)


def test_rejects_missing_refresh_queue_summary():
    preview = copy.deepcopy(_preview())
    preview["refresh_queue_record_summaries"] = [
        item for item in preview["refresh_queue_record_summaries"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_preview(preview)

    assert any("refresh_queue_record_summaries missing decision types" in finding for finding in findings)


def test_rejects_actual_approval_evidence_collected():
    preview = _preview()
    preview["refresh_queue_record_summaries"][0]["actual_approval_evidence_collected"] = True

    findings = validate_preview(preview)

    assert any("approval/public/export/customer/payment/platform/final-advice/live flags must not be true" in finding for finding in findings)


def test_rejects_action_permitted():
    preview = _preview()
    preview["refresh_queue_record_summaries"][0]["action_permitted_now"] = True

    findings = validate_preview(preview)

    assert any("approval/public/export/customer/payment/platform/final-advice/live flags must not be true" in finding for finding in findings)


def test_rejects_state_live_action():
    preview = _preview()
    preview["queue_state_safety_scan"][0]["live_action"] = True

    findings = validate_preview(preview)

    assert any("approval/public/export/customer/payment/platform/final-advice/live flags must not be true" in finding for finding in findings)


def test_rejects_missing_trigger_map_coverage():
    preview = copy.deepcopy(_preview())
    preview["invalidating_trigger_map_coverage_scan"] = [
        item for item in preview["invalidating_trigger_map_coverage_scan"] if item["trigger_id"] != "blocked_action_scan_change"
    ]

    findings = validate_preview(preview)

    assert any("invalidating_trigger_map_coverage_scan missing triggers" in finding for finding in findings)


def test_rejects_trigger_map_action_permitted():
    preview = _preview()
    preview["invalidating_trigger_map_coverage_scan"][0]["action_permitted_now"] = True

    findings = validate_preview(preview)

    assert any("approval/public/export/customer/payment/platform/final-advice/live flags must not be true" in finding for finding in findings)


def test_rejects_target_queue_state_drift():
    preview = _preview()
    preview["invalidating_trigger_map_coverage_scan"][0]["target_queue_state"] = "future_owner_r3_packet_candidate_after_refresh"

    findings = validate_preview(preview)

    assert any("target_queue_state must match source contract" in finding for finding in findings)


def test_rejects_source_count_mismatch():
    preview = _preview()
    preview["refresh_queue_record_summaries"][0]["source_required_evidence_count"] = 99

    findings = validate_preview(preview)

    assert any("source_required_evidence_count must match source contract" in finding for finding in findings)


def test_rejects_missing_source_hash_archive_scan():
    preview = _preview()
    preview["source_hash_archive_rollback_scan"][0]["source_hash_invalidating_event_present"] = False

    findings = validate_preview(preview)

    assert any("source_hash_invalidating_event_present must be true" in finding for finding in findings)


def test_rejects_scan_match():
    preview = _preview()
    preview["blocked_action_scan"]["approval_evidence_collection"]["matches"] = ["actual_approval_evidence_collected"]

    findings = validate_preview(preview)

    assert any("blocked_action_scan.approval_evidence_collection.matches must be empty" in finding for finding in findings)


def test_rejects_forbidden_approval_key():
    preview = _preview()
    preview["refresh_queue_record_summaries"][0]["owner_signature_file"] = "signed"

    findings = validate_preview(preview)

    assert any("forbidden approval/export/customer/secret/final-advice key names" in finding for finding in findings)


def test_rejects_live_platform_flag():
    preview = _preview()
    preview["audit_summary"]["platform_api_call_enabled"] = True

    findings = validate_preview(preview)

    assert any("approval/public/export/customer/payment/platform/final-advice/live flags must not be true" in finding for finding in findings)
