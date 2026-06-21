from __future__ import annotations

import copy

from scripts.promotion_source_trace_audit_preview_readiness_index_audit_preview_source_trace_gate import (
    load_trace,
    validate_trace,
)


def _trace() -> dict:
    return load_trace()


def test_current_trace_passes():
    assert validate_trace(_trace()) == []


def test_rejects_source_hash_mismatch():
    trace = _trace()
    trace["source_inputs"][0]["sha256"] = "0" * 64

    findings = validate_trace(trace)

    assert any("sha256 mismatch" in finding for finding in findings)


def test_rejects_missing_source_trace_boundary():
    trace = _trace()
    trace["boundaries"]["source_trace_not_submission"] = False

    findings = validate_trace(trace)

    assert any("boundaries.source_trace_not_submission must be true" in finding for finding in findings)


def test_rejects_source_trace_public_clearance_boundary_drift():
    trace = _trace()
    trace["boundaries"]["source_trace_not_publication_clearance"] = False

    findings = validate_trace(trace)

    assert any("boundaries.source_trace_not_publication_clearance must be true" in finding for finding in findings)


def test_rejects_summary_chain_record_count_drift():
    trace = _trace()
    trace["source_trace_summary"]["chain_records"] = 3

    findings = validate_trace(trace)

    assert any("source_trace_summary.chain_records must be 4" in finding for finding in findings)


def test_rejects_coverage_chain_length_drift():
    trace = _trace()
    trace["source_trace_coverage"]["chain_length"] = 3

    findings = validate_trace(trace)

    assert any("source_trace_coverage.chain_length must be 4" in finding for finding in findings)


def test_rejects_stops_at_task_160_false():
    trace = _trace()
    trace["source_trace_summary"]["stops_at_task_160_source_trace"] = False

    findings = validate_trace(trace)

    assert any("source_trace_summary.stops_at_task_160_source_trace must be true" in finding for finding in findings)


def test_rejects_source_mutation_flag():
    trace = _trace()
    trace["source_trace_coverage"]["source_mutated"] = True

    findings = validate_trace(trace)

    assert any("source_trace_coverage.source_mutated must be false" in finding for finding in findings)
    assert any("source-trace/archive/rollback/review-start/submission/refresh/approval/signature/public/export/" in finding for finding in findings)


def test_rejects_non_action_archive_write_true():
    trace = _trace()
    trace["non_action_flags"]["actual_archive_written"] = True

    findings = validate_trace(trace)

    assert any("non_action_flags.actual_archive_written must be false" in finding for finding in findings)
    assert any("source-trace/archive/rollback/review-start/submission/refresh/approval/signature/public/export/" in finding for finding in findings)


def test_rejects_missing_source_chain_record():
    trace = copy.deepcopy(_trace())
    trace["source_chain"] = [
        item for item in trace["source_chain"] if item["trace_record_id"] != "source-trace-upstream-source-trace"
    ]

    findings = validate_trace(trace)

    assert any("source_chain must contain 4 records" in finding for finding in findings)


def test_rejects_chain_sequence_drift():
    trace = _trace()
    trace["source_chain"][0]["sequence"] = 99

    findings = validate_trace(trace)

    assert any("source_chain[0].sequence must be 1" in finding for finding in findings)


def test_rejects_chain_hash_drift():
    trace = _trace()
    trace["source_chain"][0]["sha256"] = "0" * 64

    findings = validate_trace(trace)

    assert any("source_chain[0].sha256 mismatch" in finding for finding in findings)


def test_rejects_chain_next_path_drift():
    trace = _trace()
    trace["source_chain"][0]["expected_source_input_next_path"] = "agents/project/WRONG.json"

    findings = validate_trace(trace)

    assert any("source_chain[0].expected_source_input_next_path must be" in finding for finding in findings)


def test_rejects_chain_next_relationship_drift():
    trace = _trace()
    trace["source_chain"][0]["expected_source_input_relationship"] = "wrong_relationship"

    findings = validate_trace(trace)

    assert any(
        "source_chain[0].expected_source_input_relationship must be audits_source_trace_audit_preview_readiness_index"
        in finding
        for finding in findings
    )


def test_rejects_chain_external_validation_true():
    trace = _trace()
    trace["source_chain"][0]["external_validation_performed"] = True

    findings = validate_trace(trace)

    assert any("source_chain[0].external_validation_performed must be false" in finding for finding in findings)
    assert any("source-trace/archive/rollback/review-start/submission/refresh/approval/signature/public/export/" in finding for finding in findings)


def test_rejects_live_true_key_added_to_chain():
    trace = _trace()
    trace["source_chain"][0]["final_export_created"] = True

    findings = validate_trace(trace)

    assert any("source-trace/archive/rollback/review-start/submission/refresh/approval/signature/public/export/" in finding for finding in findings)


def test_rejects_missing_owner_r3_blocker_trace():
    trace = copy.deepcopy(_trace())
    trace["owner_r3_blocker_trace"] = [
        item for item in trace["owner_r3_blocker_trace"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_trace(trace)

    assert any("owner_r3_blocker_trace missing decision types" in finding for finding in findings)


def test_rejects_owner_r3_source_record_drift():
    trace = _trace()
    trace["owner_r3_blocker_trace"][0]["source_audit_preview_record_id"] = "wrong"

    findings = validate_trace(trace)

    assert any("source_audit_preview_record_id must match source" in finding for finding in findings)


def test_rejects_owner_r3_required_false():
    trace = _trace()
    trace["owner_r3_blocker_trace"][0]["owner_r3_required_before_submission"] = False

    findings = validate_trace(trace)

    assert any("owner_r3_blocker_trace[public_landing_use].owner_r3_required_before_submission must be true" in finding for finding in findings)


def test_rejects_owner_r3_action_permitted_now_true():
    trace = _trace()
    trace["owner_r3_blocker_trace"][0]["action_permitted_now"] = True

    findings = validate_trace(trace)

    assert any("owner_r3_blocker_trace[public_landing_use].action_permitted_now must be false" in finding for finding in findings)


def test_rejects_blocked_scan_drift():
    trace = _trace()
    trace["blocked_action_scan"]["sns_upload"]["matches"] = ["sns_uploaded"]

    findings = validate_trace(trace)

    assert any("blocked_action_scan must match source audit preview" in finding for finding in findings)


def test_rejects_missing_source_trace_step():
    trace = copy.deepcopy(_trace())
    trace["source_trace_steps"] = [
        item for item in trace["source_trace_steps"] if item["step_id"] != "verify_owner_r3_blocker_preservation"
    ]

    findings = validate_trace(trace)

    assert any("source_trace_steps missing verify_owner_r3_blocker_preservation" in finding for finding in findings)


def test_rejects_external_source_trace_step():
    trace = _trace()
    trace["source_trace_steps"][0]["external_action"] = True

    findings = validate_trace(trace)

    assert any("source_trace_steps[0].external_action must be false" in finding for finding in findings)


def test_rejects_missing_source_trace_event():
    trace = copy.deepcopy(_trace())
    trace["source_trace_events"] = [
        item for item in trace["source_trace_events"] if item["event_id"] != "source_audit_preview_gate_verified"
    ]

    findings = validate_trace(trace)

    assert any("source_trace_events missing source_audit_preview_gate_verified" in finding for finding in findings)


def test_rejects_external_source_trace_event():
    trace = _trace()
    trace["source_trace_events"][0]["external_action"] = True

    findings = validate_trace(trace)

    assert any("source_trace_events[0].external_action must be false" in finding for finding in findings)


def test_rejects_missing_forbidden_output():
    trace = copy.deepcopy(_trace())
    trace["forbidden_outputs"].remove("external archive upload")

    findings = validate_trace(trace)

    assert any("forbidden_outputs missing source outputs" in finding for finding in findings)


def test_rejects_handoff_next_task_drift():
    trace = _trace()
    trace["taskset_handoff"]["next_task_candidate"] = "TASK-999"

    findings = validate_trace(trace)

    assert any("taskset_handoff.next_task_candidate must be TASK-165" in finding for finding in findings)


def test_rejects_handoff_public_use_allowed():
    trace = _trace()
    trace["taskset_handoff"]["public_use_allowed"] = True

    findings = validate_trace(trace)

    assert any("taskset_handoff.public_use_allowed must be false" in finding for finding in findings)
    assert any("source-trace/archive/rollback/review-start/submission/refresh/approval/signature/public/export/" in finding for finding in findings)


def test_rejects_verification_command_drift():
    trace = _trace()
    trace["verification"]["source_gate"] = "python wrong.py --check"

    findings = validate_trace(trace)

    assert any("verification.source_gate must be" in finding for finding in findings)


def test_rejects_forbidden_key_name():
    trace = _trace()
    trace["source_trace_public_url"] = "https://example.invalid"

    findings = validate_trace(trace)

    assert any(
        "forbidden source-trace/submission/approval/signature/export/customer/secret/final-advice key names"
        in finding
        for finding in findings
    )
