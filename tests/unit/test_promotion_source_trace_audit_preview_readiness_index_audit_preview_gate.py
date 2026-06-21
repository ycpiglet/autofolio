from __future__ import annotations

import copy

from scripts.promotion_source_trace_audit_preview_readiness_index_audit_preview_gate import (
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

    assert any("source_inputs[0].sha256 mismatch" in finding for finding in findings)


def test_rejects_missing_audit_preview_boundary():
    preview = _preview()
    preview["boundaries"]["readiness_index_audit_preview_not_submission"] = False

    findings = validate_preview(preview)

    assert any("boundaries.readiness_index_audit_preview_not_submission must be true" in finding for finding in findings)


def test_rejects_source_readiness_boundary_drift():
    preview = _preview()
    preview["boundaries"]["readiness_index_not_publication_clearance"] = False

    findings = validate_preview(preview)

    assert any("boundaries.readiness_index_not_publication_clearance must be true" in finding for finding in findings)


def test_rejects_summary_audit_count_drift():
    preview = _preview()
    preview["audit_preview_summary"]["audit_preview_records"] = 8

    findings = validate_preview(preview)

    assert any("audit_preview_summary.audit_preview_records must be 9" in finding for finding in findings)


def test_rejects_summary_public_approval_count_drift():
    preview = _preview()
    preview["audit_preview_summary"]["public_use_approvals"] = 1

    findings = validate_preview(preview)

    assert any("audit_preview_summary.public_use_approvals must be 0" in finding for finding in findings)


def test_rejects_reference_coverage_source_boundary_count_drift():
    preview = _preview()
    preview["source_reference_coverage"]["source_boundaries"] = 50

    findings = validate_preview(preview)

    assert any("source_reference_coverage.source_boundaries must be 51" in finding for finding in findings)


def test_rejects_reference_source_mutation_flag():
    preview = _preview()
    preview["source_reference_coverage"]["source_readiness_index_mutated_source"] = True

    findings = validate_preview(preview)

    assert any(
        "source_reference_coverage.source_readiness_index_mutated_source must be false" in finding
        for finding in findings
    )
    assert any("readiness-index-audit-preview/archive/rollback/review-start/submission" in finding for finding in findings)


def test_rejects_non_action_archive_write_true():
    preview = _preview()
    preview["non_action_flags"]["actual_archive_written"] = True

    findings = validate_preview(preview)

    assert any("non_action_flags.actual_archive_written must be false" in finding for finding in findings)
    assert any("readiness-index-audit-preview/archive/rollback/review-start/submission" in finding for finding in findings)


def test_rejects_missing_audit_preview_record():
    preview = copy.deepcopy(_preview())
    preview["audit_preview_records"] = [
        item for item in preview["audit_preview_records"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_preview(preview)

    assert any("audit_preview_records missing decision types" in finding for finding in findings)


def test_rejects_audit_preview_source_record_drift():
    preview = _preview()
    preview["audit_preview_records"][0]["source_readiness_record_id"] = "wrong"

    findings = validate_preview(preview)

    assert any(
        "audit_preview_records[public_landing_use].source_readiness_record_id must match source" in finding
        for finding in findings
    )


def test_rejects_audit_preview_as_submission_true():
    preview = _preview()
    preview["audit_preview_records"][0]["audit_preview_is_submission"] = True

    findings = validate_preview(preview)

    assert any("audit_preview_records[public_landing_use].audit_preview_is_submission must be false" in finding for finding in findings)
    assert any("readiness-index-audit-preview/archive/rollback/review-start/submission" in finding for finding in findings)


def test_rejects_audit_preview_archive_write_true():
    preview = _preview()
    preview["audit_preview_records"][0]["actual_archive_written"] = True

    findings = validate_preview(preview)

    assert any("audit_preview_records[public_landing_use].actual_archive_written must be false" in finding for finding in findings)
    assert any("readiness-index-audit-preview/archive/rollback/review-start/submission" in finding for finding in findings)


def test_rejects_missing_blocker_partition_audit():
    preview = copy.deepcopy(_preview())
    preview["owner_r3_blocker_partition_audit"] = [
        item for item in preview["owner_r3_blocker_partition_audit"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_preview(preview)

    assert any("owner_r3_blocker_partition_audit missing decision types" in finding for finding in findings)


def test_rejects_blocker_partition_required_false():
    preview = _preview()
    preview["owner_r3_blocker_partition_audit"][0]["owner_r3_required_before_submission"] = False

    findings = validate_preview(preview)

    assert any(
        "owner_r3_blocker_partition_audit[public_landing_use].owner_r3_required_before_submission must be true" in finding
        for finding in findings
    )


def test_rejects_blocker_partition_action_true():
    preview = _preview()
    preview["owner_r3_blocker_partition_audit"][0]["action_permitted_now"] = True

    findings = validate_preview(preview)

    assert any("owner_r3_blocker_partition_audit[public_landing_use].action_permitted_now must be false" in finding for finding in findings)


def test_rejects_missing_local_next_action_audit():
    preview = copy.deepcopy(_preview())
    preview["local_next_action_partition_audit"] = [
        item for item in preview["local_next_action_partition_audit"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_preview(preview)

    assert any("local_next_action_partition_audit missing decision types" in finding for finding in findings)


def test_rejects_local_next_action_external_true():
    preview = _preview()
    preview["local_next_action_partition_audit"][0]["external_action"] = True

    findings = validate_preview(preview)

    assert any("local_next_action_partition_audit[public_landing_use].external_action must be false" in finding for finding in findings)


def test_rejects_blocked_scan_drift():
    preview = _preview()
    preview["blocked_action_scan"]["sns_upload"]["matches"] = ["SNS upload"]

    findings = validate_preview(preview)

    assert any("blocked_action_scan must match source readiness index" in finding for finding in findings)


def test_rejects_missing_audit_step():
    preview = copy.deepcopy(_preview())
    preview["audit_preview_steps"] = [
        item for item in preview["audit_preview_steps"] if item["step_id"] != "audit_forbidden_outputs"
    ]

    findings = validate_preview(preview)

    assert any("audit_preview_steps missing audit_forbidden_outputs" in finding for finding in findings)


def test_rejects_external_audit_step():
    preview = _preview()
    preview["audit_preview_steps"][0]["external_action"] = True

    findings = validate_preview(preview)

    assert any("audit_preview_steps[0].external_action must be false" in finding for finding in findings)


def test_rejects_missing_audit_event():
    preview = copy.deepcopy(_preview())
    preview["audit_preview_events"] = [
        item for item in preview["audit_preview_events"] if item["event_id"] != "blocked_action_scan_reused"
    ]

    findings = validate_preview(preview)

    assert any("audit_preview_events missing blocked_action_scan_reused" in finding for finding in findings)


def test_rejects_external_audit_event():
    preview = _preview()
    preview["audit_preview_events"][0]["external_action"] = True

    findings = validate_preview(preview)

    assert any("audit_preview_events[0].external_action must be false" in finding for finding in findings)


def test_rejects_forbidden_output_missing():
    preview = copy.deepcopy(_preview())
    preview["forbidden_outputs"] = [
        item for item in preview["forbidden_outputs"] if item != "SNS upload"
    ]

    findings = validate_preview(preview)

    assert any("forbidden_outputs must match source readiness index" in finding for finding in findings)


def test_rejects_handoff_next_task_drift():
    preview = _preview()
    preview["taskset_handoff"]["next_task_candidate"] = "TASK-999"

    findings = validate_preview(preview)

    assert any("taskset_handoff.next_task_candidate must be TASK-164" in finding for finding in findings)


def test_rejects_handoff_public_use_allowed_true():
    preview = _preview()
    preview["taskset_handoff"]["public_use_allowed"] = True

    findings = validate_preview(preview)

    assert any("taskset_handoff.public_use_allowed must be false" in finding for finding in findings)
    assert any("readiness-index-audit-preview/archive/rollback/review-start/submission" in finding for finding in findings)


def test_rejects_verification_drift():
    preview = _preview()
    preview["verification"]["local_gate"] = "python wrong.py"

    findings = validate_preview(preview)

    assert any(
        "verification.local_gate must be python scripts/promotion_source_trace_audit_preview_readiness_index_audit_preview_gate.py --check"
        in finding
        for finding in findings
    )


def test_rejects_forbidden_key_name():
    preview = _preview()
    preview["readiness_index_audit_submission_id"] = "SUBMIT-1"

    findings = validate_preview(preview)

    assert any("forbidden key names present" in finding for finding in findings)


def test_rejects_live_true_key_added():
    preview = _preview()
    preview["platform_api_called"] = True

    findings = validate_preview(preview)

    assert any("platform_api_called" in finding for finding in findings)
