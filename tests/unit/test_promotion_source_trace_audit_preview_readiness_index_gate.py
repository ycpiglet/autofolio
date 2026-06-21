from __future__ import annotations

import copy

from scripts.promotion_source_trace_audit_preview_readiness_index_gate import load_index, validate_index


def _index() -> dict:
    return load_index()


def test_current_index_passes():
    assert validate_index(_index()) == []


def test_rejects_source_hash_mismatch():
    index = _index()
    index["source_inputs"][0]["sha256"] = "0" * 64

    findings = validate_index(index)

    assert any("source_inputs[0].sha256 mismatch" in finding for finding in findings)


def test_rejects_missing_readiness_boundary():
    index = _index()
    index["boundaries"]["readiness_index_not_submission"] = False

    findings = validate_index(index)

    assert any("boundaries.readiness_index_not_submission must be true" in finding for finding in findings)


def test_rejects_source_audit_preview_boundary_drift():
    index = _index()
    index["boundaries"]["source_trace_audit_preview_not_publication_clearance"] = False

    findings = validate_index(index)

    assert any(
        "boundaries.source_trace_audit_preview_not_publication_clearance must be true" in finding
        for finding in findings
    )


def test_rejects_summary_readiness_count_drift():
    index = _index()
    index["readiness_summary"]["readiness_records"] = 8

    findings = validate_index(index)

    assert any("readiness_summary.readiness_records must be 9" in finding for finding in findings)


def test_rejects_summary_public_approval_count_drift():
    index = _index()
    index["readiness_summary"]["public_use_approvals"] = 1

    findings = validate_index(index)

    assert any("readiness_summary.public_use_approvals must be 0" in finding for finding in findings)


def test_rejects_reference_coverage_source_boundary_count_drift():
    index = _index()
    index["source_reference_coverage"]["source_boundaries"] = 45

    findings = validate_index(index)

    assert any("source_reference_coverage.source_boundaries must be 46" in finding for finding in findings)


def test_rejects_reference_source_mutation_flag():
    index = _index()
    index["source_reference_coverage"]["source_trace_audit_preview_mutated_source"] = True

    findings = validate_index(index)

    assert any(
        "source_reference_coverage.source_trace_audit_preview_mutated_source must be false" in finding
        for finding in findings
    )
    assert any("source-trace-readiness-index/archive/rollback/review-start/submission" in finding for finding in findings)


def test_rejects_non_action_archive_write_true():
    index = _index()
    index["non_action_flags"]["actual_archive_written"] = True

    findings = validate_index(index)

    assert any("non_action_flags.actual_archive_written must be false" in finding for finding in findings)
    assert any("source-trace-readiness-index/archive/rollback/review-start/submission" in finding for finding in findings)


def test_rejects_missing_readiness_record():
    index = copy.deepcopy(_index())
    index["readiness_records"] = [
        item for item in index["readiness_records"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_index(index)

    assert any("readiness_records missing decision types" in finding for finding in findings)


def test_rejects_readiness_record_source_id_drift():
    index = _index()
    index["readiness_records"][0]["source_audit_preview_record_id"] = "wrong"

    findings = validate_index(index)

    assert any(
        "readiness_records[public_landing_use].source_audit_preview_record_id must match source" in finding
        for finding in findings
    )


def test_rejects_readiness_index_as_submission_true():
    index = _index()
    index["readiness_records"][0]["readiness_index_is_submission"] = True

    findings = validate_index(index)

    assert any("readiness_records[public_landing_use].readiness_index_is_submission must be false" in finding for finding in findings)
    assert any("source-trace-readiness-index/archive/rollback/review-start/submission" in finding for finding in findings)


def test_rejects_readiness_archive_write_true():
    index = _index()
    index["readiness_records"][0]["actual_archive_written"] = True

    findings = validate_index(index)

    assert any("readiness_records[public_landing_use].actual_archive_written must be false" in finding for finding in findings)
    assert any("source-trace-readiness-index/archive/rollback/review-start/submission" in finding for finding in findings)


def test_rejects_readiness_action_permitted_true():
    index = _index()
    index["readiness_records"][0]["action_permitted_now"] = True

    findings = validate_index(index)

    assert any("readiness_records[public_landing_use].action_permitted_now must be false" in finding for finding in findings)


def test_rejects_missing_owner_r3_partition_record():
    index = copy.deepcopy(_index())
    index["owner_r3_blocker_partition"] = [
        item for item in index["owner_r3_blocker_partition"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_index(index)

    assert any("owner_r3_blocker_partition missing decision types" in finding for finding in findings)


def test_rejects_owner_r3_partition_required_false():
    index = _index()
    index["owner_r3_blocker_partition"][0]["owner_r3_required_before_submission"] = False

    findings = validate_index(index)

    assert any(
        "owner_r3_blocker_partition[public_landing_use].owner_r3_required_before_submission must be true" in finding
        for finding in findings
    )


def test_rejects_owner_r3_partition_action_true():
    index = _index()
    index["owner_r3_blocker_partition"][0]["action_permitted_now"] = True

    findings = validate_index(index)

    assert any("owner_r3_blocker_partition[public_landing_use].action_permitted_now must be false" in finding for finding in findings)


def test_rejects_missing_local_next_action_record():
    index = copy.deepcopy(_index())
    index["local_next_action_partition"] = [
        item for item in index["local_next_action_partition"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_index(index)

    assert any("local_next_action_partition missing decision types" in finding for finding in findings)


def test_rejects_local_next_action_external_true():
    index = _index()
    index["local_next_action_partition"][0]["external_action"] = True

    findings = validate_index(index)

    assert any("local_next_action_partition[public_landing_use].external_action must be false" in finding for finding in findings)


def test_rejects_blocked_scan_drift():
    index = _index()
    index["blocked_action_scan"]["sns_upload"]["matches"] = ["sns_uploaded"]

    findings = validate_index(index)

    assert any("blocked_action_scan must match source trace audit preview" in finding for finding in findings)


def test_rejects_missing_readiness_step():
    index = copy.deepcopy(_index())
    index["readiness_steps"] = [
        item for item in index["readiness_steps"] if item["step_id"] != "reuse_forbidden_outputs"
    ]

    findings = validate_index(index)

    assert any("readiness_steps missing reuse_forbidden_outputs" in finding for finding in findings)


def test_rejects_external_readiness_step():
    index = _index()
    index["readiness_steps"][0]["external_action"] = True

    findings = validate_index(index)

    assert any("readiness_steps[0].external_action must be false" in finding for finding in findings)


def test_rejects_missing_readiness_event():
    index = copy.deepcopy(_index())
    index["readiness_events"] = [
        item for item in index["readiness_events"] if item["event_id"] != "blocked_action_scan_reused"
    ]

    findings = validate_index(index)

    assert any("readiness_events missing blocked_action_scan_reused" in finding for finding in findings)


def test_rejects_external_readiness_event():
    index = _index()
    index["readiness_events"][0]["external_action"] = True

    findings = validate_index(index)

    assert any("readiness_events[0].external_action must be false" in finding for finding in findings)


def test_rejects_forbidden_output_missing():
    index = copy.deepcopy(_index())
    index["forbidden_outputs"] = [
        item for item in index["forbidden_outputs"] if item != "SNS upload"
    ]

    findings = validate_index(index)

    assert any("forbidden_outputs must match source trace audit preview" in finding for finding in findings)


def test_rejects_handoff_next_task_drift():
    index = _index()
    index["taskset_handoff"]["next_task_candidate"] = "TASK-999"

    findings = validate_index(index)

    assert any("taskset_handoff.next_task_candidate must be TASK-163" in finding for finding in findings)


def test_rejects_handoff_public_use_allowed_true():
    index = _index()
    index["taskset_handoff"]["public_use_allowed"] = True

    findings = validate_index(index)

    assert any("taskset_handoff.public_use_allowed must be false" in finding for finding in findings)
    assert any("source-trace-readiness-index/archive/rollback/review-start/submission" in finding for finding in findings)


def test_rejects_verification_drift():
    index = _index()
    index["verification"]["local_gate"] = "python wrong.py"

    findings = validate_index(index)

    assert any("verification.local_gate must be python scripts/promotion_source_trace_audit_preview_readiness_index_gate.py --check" in finding for finding in findings)


def test_rejects_forbidden_key_name():
    index = _index()
    index["readiness_index_submission_id"] = "SUBMIT-1"

    findings = validate_index(index)

    assert any("forbidden key names present" in finding for finding in findings)


def test_rejects_live_true_key_added():
    index = _index()
    index["platform_api_called"] = True

    findings = validate_index(index)

    assert any("platform_api_called" in finding for finding in findings)
