from __future__ import annotations

import copy

from scripts.promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_gate import (
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
    preview["boundaries"]["archive_rollback_manifest_audit_not_submission"] = False

    findings = validate_preview(preview)

    assert any("boundaries.archive_rollback_manifest_audit_not_submission must be true" in finding for finding in findings)


def test_rejects_actual_archive_write_boundary():
    preview = _preview()
    preview["boundaries"]["not_actual_archive_write"] = False

    findings = validate_preview(preview)

    assert any("boundaries.not_actual_archive_write must be true" in finding for finding in findings)


def test_rejects_summary_coverage_record_count_drift():
    preview = _preview()
    preview["audit_summary"]["audit_coverage_records"] = 8

    findings = validate_preview(preview)

    assert any("audit_summary.audit_coverage_records must be 9" in finding for finding in findings)


def test_rejects_source_boundary_count_drift():
    preview = _preview()
    preview["audit_summary"]["source_boundaries"] = 40

    findings = validate_preview(preview)

    assert any("audit_summary.source_boundaries must be 41" in finding for finding in findings)


def test_rejects_source_reference_count_drift():
    preview = _preview()
    preview["source_reference_coverage"]["source_manifest_assembly_step_count"] = 7

    findings = validate_preview(preview)

    assert any("source_reference_coverage.source_manifest_assembly_step_count must be 8" in finding for finding in findings)


def test_rejects_source_mutation_flag():
    preview = _preview()
    preview["source_reference_coverage"]["source_mutated"] = True

    findings = validate_preview(preview)

    assert any("source_reference_coverage.source_mutated must be false" in finding for finding in findings)
    assert any("archive-audit/archive/rollback/review-start/submission/refresh/approval/signature/public/export/customer/" in finding for finding in findings)


def test_rejects_missing_coverage_record():
    preview = copy.deepcopy(_preview())
    preview["coverage_records"] = [
        item for item in preview["coverage_records"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_preview(preview)

    assert any("coverage_records missing decision types" in finding for finding in findings)


def test_rejects_archive_source_link_drift():
    preview = _preview()
    preview["coverage_records"][0]["source_archive_manifest_record_id"] = "wrong"

    findings = validate_preview(preview)

    assert any("source_archive_manifest_record_id must be" in finding for finding in findings)


def test_rejects_rollback_source_link_drift():
    preview = _preview()
    preview["coverage_records"][0]["source_rollback_trigger_record_id"] = "wrong"

    findings = validate_preview(preview)

    assert any("source_rollback_trigger_record_id must be" in finding for finding in findings)


def test_rejects_audit_preview_as_submission():
    preview = _preview()
    preview["coverage_records"][0]["audit_preview_is_submission"] = True

    findings = validate_preview(preview)

    assert any("archive-audit/archive/rollback/review-start/submission/refresh/approval/signature/public/export/customer/" in finding for finding in findings)


def test_rejects_actual_archive_written():
    preview = _preview()
    preview["coverage_records"][0]["actual_archive_written"] = True

    findings = validate_preview(preview)

    assert any("archive-audit/archive/rollback/review-start/submission/refresh/approval/signature/public/export/customer/" in finding for finding in findings)


def test_rejects_actual_rollback_executed():
    preview = _preview()
    preview["coverage_records"][0]["actual_rollback_executed"] = True

    findings = validate_preview(preview)

    assert any("archive-audit/archive/rollback/review-start/submission/refresh/approval/signature/public/export/customer/" in finding for finding in findings)


def test_rejects_action_permitted_now():
    preview = _preview()
    preview["coverage_records"][0]["action_permitted_now"] = True

    findings = validate_preview(preview)

    assert any("coverage_records[public_landing_use].action_permitted_now must be false" in finding for finding in findings)


def test_rejects_blocked_scan_drift():
    preview = _preview()
    preview["blocked_action_scan"]["owner_signature"]["matches"] = ["actual_owner_signature_collected"]

    findings = validate_preview(preview)

    assert any("blocked_action_scan must match source archive/rollback manifest" in finding for finding in findings)


def test_rejects_missing_audit_step():
    preview = copy.deepcopy(_preview())
    preview["audit_steps"] = [
        item for item in preview["audit_steps"] if item["step_id"] != "audit_blocked_action_scan"
    ]

    findings = validate_preview(preview)

    assert any("audit_steps missing audit_blocked_action_scan" in finding for finding in findings)


def test_rejects_external_audit_step():
    preview = _preview()
    preview["audit_steps"][0]["external_action"] = True

    findings = validate_preview(preview)

    assert any("audit_steps[0].external_action must be false" in finding for finding in findings)


def test_rejects_missing_audit_event():
    preview = copy.deepcopy(_preview())
    preview["audit_events"] = [
        item for item in preview["audit_events"] if item["event"] != "blocked_action_scan_passed"
    ]

    findings = validate_preview(preview)

    assert any("audit_events missing blocked_action_scan_passed" in finding for finding in findings)


def test_rejects_missing_forbidden_output():
    preview = copy.deepcopy(_preview())
    preview["forbidden_outputs"].remove("archive deletion")

    findings = validate_preview(preview)

    assert any("forbidden_outputs missing source outputs" in finding for finding in findings)


def test_rejects_handoff_next_task_drift():
    preview = _preview()
    preview["taskset_handoff"]["next_task_candidate"] = "TASK-999"

    findings = validate_preview(preview)

    assert any("taskset_handoff.next_task_candidate must be TASK-158" in finding for finding in findings)


def test_rejects_handoff_archive_write_allowed():
    preview = _preview()
    preview["taskset_handoff"]["actual_archive_write_allowed"] = True

    findings = validate_preview(preview)

    assert any("taskset_handoff.actual_archive_write_allowed must be false" in finding for finding in findings)
    assert any("archive-audit/archive/rollback/review-start/submission/refresh/approval/signature/public/export/customer/" in finding for finding in findings)


def test_rejects_verification_command_drift():
    preview = _preview()
    preview["verification"]["source_gate"] = "python wrong.py --check"

    findings = validate_preview(preview)

    assert any("verification.source_gate must be" in finding for finding in findings)


def test_rejects_forbidden_key_name():
    preview = _preview()
    preview["coverage_records"][0]["archive_audit_public_url"] = "https://example.invalid"

    findings = validate_preview(preview)

    assert any("forbidden archive-audit/review-submission/approval/signature/export/customer/secret/final-advice key names" in finding for finding in findings)
