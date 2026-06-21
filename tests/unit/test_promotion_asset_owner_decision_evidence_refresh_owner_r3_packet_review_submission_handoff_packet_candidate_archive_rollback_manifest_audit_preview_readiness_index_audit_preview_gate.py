from __future__ import annotations

import copy

from scripts.promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_readiness_index_audit_preview_gate import (
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


def test_rejects_missing_audit_preview_boundary():
    preview = _preview()
    preview["boundaries"]["readiness_index_audit_preview_not_submission"] = False

    findings = validate_preview(preview)

    assert any("boundaries.readiness_index_audit_preview_not_submission must be true" in finding for finding in findings)


def test_rejects_source_readiness_public_clearance_boundary_drift():
    preview = _preview()
    preview["boundaries"]["source_readiness_index_not_publication_clearance"] = False

    findings = validate_preview(preview)

    assert any("boundaries.source_readiness_index_not_publication_clearance must be true" in finding for finding in findings)


def test_rejects_summary_record_count_drift():
    preview = _preview()
    preview["audit_preview_summary"]["audit_preview_records"] = 8

    findings = validate_preview(preview)

    assert any("audit_preview_summary.audit_preview_records must be 9" in finding for finding in findings)


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
    assert any("readiness-audit/archive/rollback/review-start/submission/refresh/approval/signature/public/export/" in finding for finding in findings)


def test_rejects_missing_audit_preview_record():
    preview = copy.deepcopy(_preview())
    preview["audit_preview_records"] = [
        item for item in preview["audit_preview_records"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_preview(preview)

    assert any("audit_preview_records missing decision types" in finding for finding in findings)


def test_rejects_source_readiness_record_link_drift():
    preview = _preview()
    preview["audit_preview_records"][0]["source_readiness_record_id"] = "wrong"

    findings = validate_preview(preview)

    assert any("source_readiness_record_id must be" in finding for finding in findings)


def test_rejects_audit_preview_as_submission():
    preview = _preview()
    preview["audit_preview_records"][0]["audit_preview_is_submission"] = True

    findings = validate_preview(preview)

    assert any("audit_preview_records[public_landing_use].audit_preview_is_submission must be false" in finding for finding in findings)
    assert any("readiness-audit/archive/rollback/review-start/submission/refresh/approval/signature/public/export/" in finding for finding in findings)


def test_rejects_audit_preview_as_public_clearance():
    preview = _preview()
    preview["audit_preview_records"][0]["audit_preview_is_public_clearance"] = True

    findings = validate_preview(preview)

    assert any("audit_preview_records[public_landing_use].audit_preview_is_public_clearance must be false" in finding for finding in findings)
    assert any("readiness-audit/archive/rollback/review-start/submission/refresh/approval/signature/public/export/" in finding for finding in findings)


def test_rejects_actual_archive_written():
    preview = _preview()
    preview["audit_preview_records"][0]["actual_archive_written"] = True

    findings = validate_preview(preview)

    assert any("audit_preview_records[public_landing_use].actual_archive_written must be false" in finding for finding in findings)
    assert any("readiness-audit/archive/rollback/review-start/submission/refresh/approval/signature/public/export/" in finding for finding in findings)


def test_rejects_action_permitted_now():
    preview = _preview()
    preview["audit_preview_records"][0]["action_permitted_now"] = True

    findings = validate_preview(preview)

    assert any("audit_preview_records[public_landing_use].action_permitted_now must be false" in finding for finding in findings)


def test_rejects_missing_owner_r3_blocker_audit():
    preview = copy.deepcopy(_preview())
    preview["owner_r3_blocker_partition_audit"] = [
        item for item in preview["owner_r3_blocker_partition_audit"] if item["decision_type"] != "sns_upload"
    ]

    findings = validate_preview(preview)

    assert any("owner_r3_blocker_partition_audit missing decision types" in finding for finding in findings)


def test_rejects_owner_r3_blocker_audit_submission_flag():
    preview = _preview()
    preview["owner_r3_blocker_partition_audit"][0]["actual_owner_r3_review_submitted"] = True

    findings = validate_preview(preview)

    assert any("owner_r3_blocker_partition_audit[public_landing_use].actual_owner_r3_review_submitted must be false" in finding for finding in findings)


def test_rejects_local_next_action_public_action():
    preview = _preview()
    preview["local_next_action_partition_audit"][0]["public_action"] = True

    findings = validate_preview(preview)

    assert any("local_next_action_partition_audit[public_landing_use].public_action must be false" in finding for finding in findings)
    assert any("readiness-audit/archive/rollback/review-start/submission/refresh/approval/signature/public/export/" in finding for finding in findings)


def test_rejects_blocked_scan_drift():
    preview = _preview()
    preview["blocked_action_scan"]["owner_signature"]["matches"] = ["actual_owner_signature_collected"]

    findings = validate_preview(preview)

    assert any("blocked_action_scan must match source readiness index" in finding for finding in findings)


def test_rejects_missing_audit_preview_step():
    preview = copy.deepcopy(_preview())
    preview["audit_preview_steps"] = [
        item for item in preview["audit_preview_steps"] if item["step_id"] != "audit_blocked_action_scan"
    ]

    findings = validate_preview(preview)

    assert any("audit_preview_steps missing audit_blocked_action_scan" in finding for finding in findings)


def test_rejects_external_audit_preview_step():
    preview = _preview()
    preview["audit_preview_steps"][0]["external_action"] = True

    findings = validate_preview(preview)

    assert any("audit_preview_steps[0].external_action must be false" in finding for finding in findings)


def test_rejects_missing_audit_preview_event():
    preview = copy.deepcopy(_preview())
    preview["audit_preview_events"] = [
        item for item in preview["audit_preview_events"] if item["event"] != "blocked_action_scan_reused"
    ]

    findings = validate_preview(preview)

    assert any("audit_preview_events missing blocked_action_scan_reused" in finding for finding in findings)


def test_rejects_missing_forbidden_output():
    preview = copy.deepcopy(_preview())
    preview["forbidden_outputs"].remove("archive deletion")

    findings = validate_preview(preview)

    assert any("forbidden_outputs missing source outputs" in finding for finding in findings)


def test_rejects_handoff_next_task_drift():
    preview = _preview()
    preview["taskset_handoff"]["next_task_candidate"] = "TASK-999"

    findings = validate_preview(preview)

    assert any("taskset_handoff.next_task_candidate must be TASK-160" in finding for finding in findings)


def test_rejects_handoff_public_use_allowed():
    preview = _preview()
    preview["taskset_handoff"]["actual_public_use_allowed"] = True

    findings = validate_preview(preview)

    assert any("taskset_handoff.actual_public_use_allowed must be false" in finding for finding in findings)
    assert any("readiness-audit/archive/rollback/review-start/submission/refresh/approval/signature/public/export/" in finding for finding in findings)


def test_rejects_verification_command_drift():
    preview = _preview()
    preview["verification"]["source_gate"] = "python wrong.py --check"

    findings = validate_preview(preview)

    assert any("verification.source_gate must be" in finding for finding in findings)


def test_rejects_forbidden_key_name():
    preview = _preview()
    preview["audit_preview_records"][0]["readiness_audit_public_url"] = "https://example.invalid"

    findings = validate_preview(preview)

    assert any("forbidden readiness-audit/submission/approval/signature/export/customer/secret/final-advice key names" in finding for finding in findings)
