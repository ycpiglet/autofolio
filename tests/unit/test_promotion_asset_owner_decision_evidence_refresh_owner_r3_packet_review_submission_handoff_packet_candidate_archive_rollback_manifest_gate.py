from __future__ import annotations

import copy

from scripts.promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_gate import (
    load_manifest,
    validate_manifest,
)


def _manifest() -> dict:
    return load_manifest()


def test_current_manifest_passes():
    assert validate_manifest(_manifest()) == []


def test_rejects_source_hash_mismatch():
    manifest = _manifest()
    manifest["source_inputs"][0]["sha256"] = "0" * 64

    findings = validate_manifest(manifest)

    assert any("sha256 mismatch" in finding for finding in findings)


def test_rejects_missing_manifest_boundary():
    manifest = _manifest()
    manifest["boundaries"]["archive_rollback_manifest_not_submission"] = False

    findings = validate_manifest(manifest)

    assert any("boundaries.archive_rollback_manifest_not_submission must be true" in finding for finding in findings)


def test_rejects_actual_archive_write_boundary():
    manifest = _manifest()
    manifest["boundaries"]["not_actual_archive_write"] = False

    findings = validate_manifest(manifest)

    assert any("boundaries.not_actual_archive_write must be true" in finding for finding in findings)


def test_rejects_summary_archive_record_count_drift():
    manifest = _manifest()
    manifest["manifest_summary"]["archive_manifest_records"] = 8

    findings = validate_manifest(manifest)

    assert any("manifest_summary.archive_manifest_records must be 9" in finding for finding in findings)


def test_rejects_source_total_count_drift():
    manifest = _manifest()
    manifest["manifest_summary"]["total_source_required_evidence_items"] = 24

    findings = validate_manifest(manifest)

    assert any("manifest_summary.total_source_required_evidence_items must be 25" in finding for finding in findings)


def test_rejects_source_copy_drift():
    manifest = copy.deepcopy(_manifest())
    manifest["source_handoff_packet_record_summaries"] = manifest["source_handoff_packet_record_summaries"][:-1]

    findings = validate_manifest(manifest)

    assert any("source_handoff_packet_record_summaries must match source audit preview" in finding for finding in findings)


def test_rejects_missing_archive_record():
    manifest = copy.deepcopy(_manifest())
    manifest["archive_manifest_records"] = [
        item for item in manifest["archive_manifest_records"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_manifest(manifest)

    assert any("archive_manifest_records missing decision types" in finding for finding in findings)


def test_rejects_archive_source_link_drift():
    manifest = _manifest()
    manifest["archive_manifest_records"][0]["source_handoff_packet_record_id"] = "wrong"

    findings = validate_manifest(manifest)

    assert any("source_handoff_packet_record_id must be" in finding for finding in findings)


def test_rejects_archive_as_submission():
    manifest = _manifest()
    manifest["archive_manifest_records"][0]["archive_record_is_submission"] = True

    findings = validate_manifest(manifest)

    assert any("archive/rollback/review-start/submission/refresh/approval/signature/public/export/customer/payment/platform/" in finding for finding in findings)


def test_rejects_actual_archive_written():
    manifest = _manifest()
    manifest["archive_manifest_records"][0]["actual_archive_written"] = True

    findings = validate_manifest(manifest)

    assert any("archive/rollback/review-start/submission/refresh/approval/signature/public/export/customer/payment/platform/" in finding for finding in findings)


def test_rejects_actual_archive_deleted():
    manifest = _manifest()
    manifest["archive_manifest_records"][0]["actual_archive_deleted"] = True

    findings = validate_manifest(manifest)

    assert any("archive/rollback/review-start/submission/refresh/approval/signature/public/export/customer/payment/platform/" in finding for finding in findings)


def test_rejects_actual_owner_review_started():
    manifest = _manifest()
    manifest["archive_manifest_records"][0]["actual_owner_review_started"] = True

    findings = validate_manifest(manifest)

    assert any("archive/rollback/review-start/submission/refresh/approval/signature/public/export/customer/payment/platform/" in finding for finding in findings)


def test_rejects_missing_rollback_record():
    manifest = copy.deepcopy(_manifest())
    manifest["rollback_trigger_records"] = [
        item for item in manifest["rollback_trigger_records"] if item["decision_type"] != "sns_upload"
    ]

    findings = validate_manifest(manifest)

    assert any("rollback_trigger_records missing decision types" in finding for finding in findings)


def test_rejects_rollback_trigger_source_drift():
    manifest = _manifest()
    manifest["rollback_trigger_records"][0]["invalidating_triggers"] = ["source changed"]

    findings = validate_manifest(manifest)

    assert any("invalidating_triggers must be" in finding for finding in findings)


def test_rejects_actual_rollback_executed():
    manifest = _manifest()
    manifest["rollback_trigger_records"][0]["actual_rollback_executed"] = True

    findings = validate_manifest(manifest)

    assert any("archive/rollback/review-start/submission/refresh/approval/signature/public/export/customer/payment/platform/" in finding for finding in findings)


def test_rejects_missing_retention_record():
    manifest = copy.deepcopy(_manifest())
    manifest["retention_supersession_records"] = [
        item for item in manifest["retention_supersession_records"] if item["decision_type"] != "customer_contact"
    ]

    findings = validate_manifest(manifest)

    assert any("retention_supersession_records missing decision types" in finding for finding in findings)


def test_rejects_short_retention_requirements():
    manifest = _manifest()
    manifest["retention_supersession_records"][0]["retention_requirements"] = ["source hash"]

    findings = validate_manifest(manifest)

    assert any("retention_requirements must contain at least 7 items" in finding for finding in findings)


def test_rejects_short_supersession_triggers():
    manifest = _manifest()
    manifest["retention_supersession_records"][0]["supersession_triggers"] = ["source hash changed"]

    findings = validate_manifest(manifest)

    assert any("supersession_triggers must contain at least 8 items" in finding for finding in findings)


def test_rejects_secret_material_retained():
    manifest = _manifest()
    manifest["retention_supersession_records"][0]["secret_material_retained"] = True

    findings = validate_manifest(manifest)

    assert any("archive/rollback/review-start/submission/refresh/approval/signature/public/export/customer/payment/platform/" in finding for finding in findings)


def test_rejects_external_archive_upload_enabled():
    manifest = _manifest()
    manifest["retention_supersession_records"][0]["external_archive_upload_enabled"] = True

    findings = validate_manifest(manifest)

    assert any("archive/rollback/review-start/submission/refresh/approval/signature/public/export/customer/payment/platform/" in finding for finding in findings)


def test_rejects_source_preflight_state_drift():
    manifest = copy.deepcopy(_manifest())
    manifest["source_preflight_state_safety_scan"] = manifest["source_preflight_state_safety_scan"][:-1]

    findings = validate_manifest(manifest)

    assert any("source_preflight_state_safety_scan must match source audit preview" in finding for finding in findings)


def test_rejects_blocked_scan_match():
    manifest = _manifest()
    manifest["blocked_action_scan"]["owner_signature"]["matches"] = ["actual_owner_signature_collected"]

    findings = validate_manifest(manifest)

    assert any("blocked_action_scan.owner_signature must match source blocked action scan" in finding for finding in findings)


def test_rejects_missing_manifest_step():
    manifest = copy.deepcopy(_manifest())
    manifest["manifest_assembly_steps"] = [
        item for item in manifest["manifest_assembly_steps"] if item["step_id"] != "validate_no_live_action"
    ]

    findings = validate_manifest(manifest)

    assert any("manifest_assembly_steps missing validate_no_live_action" in finding for finding in findings)


def test_rejects_external_manifest_step():
    manifest = _manifest()
    manifest["manifest_assembly_steps"][0]["external_action"] = True

    findings = validate_manifest(manifest)

    assert any("manifest_assembly_steps[0].external_action must be false" in finding for finding in findings)


def test_rejects_missing_manifest_event():
    manifest = copy.deepcopy(_manifest())
    manifest["manifest_events"] = [
        item for item in manifest["manifest_events"] if item["event"] != "blocked_action_scan_passed"
    ]

    findings = validate_manifest(manifest)

    assert any("manifest_events missing blocked_action_scan_passed" in finding for finding in findings)


def test_rejects_external_manifest_event():
    manifest = _manifest()
    manifest["manifest_events"][0]["external_action"] = True

    findings = validate_manifest(manifest)

    assert any("manifest_events[0].external_action must be false" in finding for finding in findings)


def test_rejects_forbidden_archive_key():
    manifest = _manifest()
    manifest["archive_manifest_records"][0]["archive_file_path"] = "archive.zip"

    findings = validate_manifest(manifest)

    assert any("forbidden archive/review-submission/approval/signature/export/customer/secret/final-advice key names" in finding for finding in findings)


def test_rejects_missing_forbidden_output():
    manifest = copy.deepcopy(_manifest())
    manifest["forbidden_outputs"] = [item for item in manifest["forbidden_outputs"] if item != "actual rollback execution"]

    findings = validate_manifest(manifest)

    assert any("forbidden_outputs missing" in finding for finding in findings)


def test_rejects_live_platform_flag():
    manifest = _manifest()
    manifest["platform_api_call_enabled"] = True

    findings = validate_manifest(manifest)

    assert any("archive/rollback/review-start/submission/refresh/approval/signature/public/export/customer/payment/platform/" in finding for finding in findings)
