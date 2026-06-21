from __future__ import annotations

import copy

from scripts.promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_readiness_index_audit_preview_source_trace_audit_preview_gate import (
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


def test_rejects_missing_source_trace_audit_boundary():
    preview = _preview()
    preview["boundaries"]["source_trace_audit_preview_not_submission"] = False

    findings = validate_preview(preview)

    assert any("boundaries.source_trace_audit_preview_not_submission must be true" in finding for finding in findings)


def test_rejects_source_trace_boundary_drift():
    preview = _preview()
    preview["boundaries"]["source_trace_not_publication_clearance"] = False

    findings = validate_preview(preview)

    assert any("boundaries.source_trace_not_publication_clearance must be true" in finding for finding in findings)


def test_rejects_summary_chain_count_drift():
    preview = _preview()
    preview["source_trace_audit_preview_summary"]["source_trace_chain_records"] = 9

    findings = validate_preview(preview)

    assert any("source_trace_audit_preview_summary.source_trace_chain_records must be 10" in finding for finding in findings)


def test_rejects_summary_ready_count_drift():
    preview = _preview()
    preview["source_trace_audit_preview_summary"]["ready_for_public_use_records"] = 1

    findings = validate_preview(preview)

    assert any("source_trace_audit_preview_summary.ready_for_public_use_records must be 0" in finding for finding in findings)


def test_rejects_coverage_chain_length_drift():
    preview = _preview()
    preview["source_trace_reference_coverage"]["chain_length"] = 9

    findings = validate_preview(preview)

    assert any("source_trace_reference_coverage.chain_length must be 10" in finding for finding in findings)


def test_rejects_source_trace_boundary_count_drift():
    preview = _preview()
    preview["source_trace_reference_coverage"]["source_trace_boundaries"] = 40

    findings = validate_preview(preview)

    assert any("source_trace_reference_coverage.source_trace_boundaries must be 41" in finding for finding in findings)


def test_rejects_reference_source_mutation_flag():
    preview = _preview()
    preview["source_trace_reference_coverage"]["source_mutated"] = True

    findings = validate_preview(preview)

    assert any("source_trace_reference_coverage.source_mutated must be false" in finding for finding in findings)
    assert any("source-trace-audit/archive/rollback/review-start/submission/refresh/approval/signature/public/" in finding for finding in findings)


def test_rejects_non_action_archive_write_true():
    preview = _preview()
    preview["non_action_flags"]["actual_archive_written"] = True

    findings = validate_preview(preview)

    assert any("non_action_flags.actual_archive_written must be false" in finding for finding in findings)
    assert any("source-trace-audit/archive/rollback/review-start/submission/refresh/approval/signature/public/" in finding for finding in findings)


def test_rejects_missing_source_chain_audit_record():
    preview = copy.deepcopy(_preview())
    preview["source_chain_audit"] = [
        item for item in preview["source_chain_audit"] if item["trace_record_id"] != "source-trace-handoff-packet-candidate"
    ]

    findings = validate_preview(preview)

    assert any("source_chain_audit must contain 10 records" in finding for finding in findings)


def test_rejects_source_chain_hash_drift():
    preview = _preview()
    preview["source_chain_audit"][0]["sha256"] = "0" * 64

    findings = validate_preview(preview)

    assert any("source_chain_audit[source-trace-readiness-index-audit-preview].sha256 must match source trace" in finding for finding in findings)


def test_rejects_source_chain_next_path_drift():
    preview = _preview()
    preview["source_chain_audit"][0]["expected_source_input_next_path"] = "agents/project/WRONG.json"

    findings = validate_preview(preview)

    assert any("source_chain_audit[source-trace-readiness-index-audit-preview].expected_source_input_next_path must match source trace" in finding for finding in findings)


def test_rejects_source_chain_mutation_true():
    preview = _preview()
    preview["source_chain_audit"][0]["source_mutated"] = True

    findings = validate_preview(preview)

    assert any("source_chain_audit[source-trace-readiness-index-audit-preview].source_mutated must be false" in finding for finding in findings)
    assert any("source-trace-audit/archive/rollback/review-start/submission/refresh/approval/signature/public/" in finding for finding in findings)


def test_rejects_missing_audit_preview_record():
    preview = copy.deepcopy(_preview())
    preview["audit_preview_records"] = [
        item for item in preview["audit_preview_records"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_preview(preview)

    assert any("audit_preview_records missing decision types" in finding for finding in findings)


def test_rejects_audit_preview_source_record_drift():
    preview = _preview()
    preview["audit_preview_records"][0]["source_audit_preview_record_id"] = "wrong"

    findings = validate_preview(preview)

    assert any("audit_preview_records[public_landing_use].source_audit_preview_record_id must match source" in finding for finding in findings)


def test_rejects_audit_preview_as_submission_true():
    preview = _preview()
    preview["audit_preview_records"][0]["audit_preview_is_submission"] = True

    findings = validate_preview(preview)

    assert any("audit_preview_records[public_landing_use].audit_preview_is_submission must be false" in finding for finding in findings)
    assert any("source-trace-audit/archive/rollback/review-start/submission/refresh/approval/signature/public/" in finding for finding in findings)


def test_rejects_audit_preview_archive_write_true():
    preview = _preview()
    preview["audit_preview_records"][0]["actual_archive_written"] = True

    findings = validate_preview(preview)

    assert any("audit_preview_records[public_landing_use].actual_archive_written must be false" in finding for finding in findings)
    assert any("source-trace-audit/archive/rollback/review-start/submission/refresh/approval/signature/public/" in finding for finding in findings)


def test_rejects_missing_blocker_trace_audit():
    preview = copy.deepcopy(_preview())
    preview["owner_r3_blocker_trace_audit"] = [
        item for item in preview["owner_r3_blocker_trace_audit"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_preview(preview)

    assert any("owner_r3_blocker_trace_audit missing decision types" in finding for finding in findings)


def test_rejects_blocker_trace_required_false():
    preview = _preview()
    preview["owner_r3_blocker_trace_audit"][0]["owner_r3_required_before_submission"] = False

    findings = validate_preview(preview)

    assert any("owner_r3_blocker_trace_audit[public_landing_use].owner_r3_required_before_submission must be true" in finding for finding in findings)


def test_rejects_blocker_trace_action_true():
    preview = _preview()
    preview["owner_r3_blocker_trace_audit"][0]["action_permitted_now"] = True

    findings = validate_preview(preview)

    assert any("owner_r3_blocker_trace_audit[public_landing_use].action_permitted_now must be false" in finding for finding in findings)


def test_rejects_blocked_scan_drift():
    preview = _preview()
    preview["blocked_action_scan"]["sns_upload"]["matches"] = ["sns_uploaded"]

    findings = validate_preview(preview)

    assert any("blocked_action_scan must match source trace" in finding for finding in findings)


def test_rejects_missing_audit_step():
    preview = copy.deepcopy(_preview())
    preview["audit_preview_steps"] = [
        item for item in preview["audit_preview_steps"] if item["step_id"] != "audit_owner_r3_blocker_trace"
    ]

    findings = validate_preview(preview)

    assert any("audit_preview_steps missing audit_owner_r3_blocker_trace" in finding for finding in findings)


def test_rejects_external_audit_step():
    preview = _preview()
    preview["audit_preview_steps"][0]["external_action"] = True

    findings = validate_preview(preview)

    assert any("audit_preview_steps[0].external_action must be false" in finding for finding in findings)


def test_rejects_missing_audit_event():
    preview = copy.deepcopy(_preview())
    preview["audit_preview_events"] = [
        item for item in preview["audit_preview_events"] if item["event_id"] != "source_trace_gate_verified"
    ]

    findings = validate_preview(preview)

    assert any("audit_preview_events missing source_trace_gate_verified" in finding for finding in findings)


def test_rejects_external_audit_event():
    preview = _preview()
    preview["audit_preview_events"][0]["external_action"] = True

    findings = validate_preview(preview)

    assert any("audit_preview_events[0].external_action must be false" in finding for finding in findings)


def test_rejects_missing_forbidden_output():
    preview = copy.deepcopy(_preview())
    preview["forbidden_outputs"].remove("external archive upload")

    findings = validate_preview(preview)

    assert any("forbidden_outputs must match source trace" in finding for finding in findings)


def test_rejects_handoff_next_task_drift():
    preview = _preview()
    preview["taskset_handoff"]["next_task_candidate"] = "TASK-999"

    findings = validate_preview(preview)

    assert any("taskset_handoff.next_task_candidate must be TASK-162" in finding for finding in findings)


def test_rejects_handoff_public_use_allowed():
    preview = _preview()
    preview["taskset_handoff"]["public_use_allowed"] = True

    findings = validate_preview(preview)

    assert any("taskset_handoff.public_use_allowed must be false" in finding for finding in findings)
    assert any("source-trace-audit/archive/rollback/review-start/submission/refresh/approval/signature/public/" in finding for finding in findings)


def test_rejects_verification_command_drift():
    preview = _preview()
    preview["verification"]["source_gate"] = "python wrong.py --check"

    findings = validate_preview(preview)

    assert any("verification.source_gate must be" in finding for finding in findings)


def test_rejects_forbidden_key_name():
    preview = _preview()
    preview["source_trace_audit_public_url"] = "https://example.invalid"

    findings = validate_preview(preview)

    assert any("forbidden source-trace-audit/submission/approval/signature/export/customer/secret/final-advice key names" in finding for finding in findings)


def test_rejects_live_true_key_added():
    preview = _preview()
    preview["final_export_created"] = True

    findings = validate_preview(preview)

    assert any("source-trace-audit/archive/rollback/review-start/submission/refresh/approval/signature/public/" in finding for finding in findings)
