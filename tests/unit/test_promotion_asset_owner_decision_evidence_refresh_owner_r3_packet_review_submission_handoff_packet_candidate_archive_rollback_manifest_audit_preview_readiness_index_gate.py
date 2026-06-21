from __future__ import annotations

import copy

from scripts.promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_readiness_index_gate import (
    load_index,
    validate_index,
)


def _index() -> dict:
    return load_index()


def test_current_index_passes():
    assert validate_index(_index()) == []


def test_rejects_source_hash_mismatch():
    index = _index()
    index["source_inputs"][0]["sha256"] = "0" * 64

    findings = validate_index(index)

    assert any("sha256 mismatch" in finding for finding in findings)


def test_rejects_missing_readiness_boundary():
    index = _index()
    index["boundaries"]["readiness_index_not_submission"] = False

    findings = validate_index(index)

    assert any("boundaries.readiness_index_not_submission must be true" in finding for finding in findings)


def test_rejects_public_clearance_boundary_drift():
    index = _index()
    index["boundaries"]["readiness_index_not_publication_clearance"] = False

    findings = validate_index(index)

    assert any("boundaries.readiness_index_not_publication_clearance must be true" in finding for finding in findings)


def test_rejects_summary_record_count_drift():
    index = _index()
    index["readiness_summary"]["readiness_records"] = 8

    findings = validate_index(index)

    assert any("readiness_summary.readiness_records must be 9" in finding for finding in findings)


def test_rejects_source_reference_count_drift():
    index = _index()
    index["source_reference_coverage"]["source_manifest_assembly_step_count"] = 7

    findings = validate_index(index)

    assert any("source_reference_coverage.source_manifest_assembly_step_count must be 8" in finding for finding in findings)


def test_rejects_source_mutation_flag():
    index = _index()
    index["source_reference_coverage"]["source_mutated"] = True

    findings = validate_index(index)

    assert any("source_reference_coverage.source_mutated must be false" in finding for finding in findings)
    assert any("readiness/archive/rollback/review-start/submission/refresh/approval/signature/public/export/customer/" in finding for finding in findings)


def test_rejects_missing_readiness_record():
    index = copy.deepcopy(_index())
    index["readiness_records"] = [
        item for item in index["readiness_records"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_index(index)

    assert any("readiness_records missing decision types" in finding for finding in findings)


def test_rejects_source_audit_record_link_drift():
    index = _index()
    index["readiness_records"][0]["source_audit_record_id"] = "wrong"

    findings = validate_index(index)

    assert any("source_audit_record_id must be" in finding for finding in findings)


def test_rejects_readiness_index_as_submission():
    index = _index()
    index["readiness_records"][0]["readiness_index_is_submission"] = True

    findings = validate_index(index)

    assert any("readiness/archive/rollback/review-start/submission/refresh/approval/signature/public/export/customer/" in finding for finding in findings)


def test_rejects_readiness_index_as_public_clearance():
    index = _index()
    index["readiness_records"][0]["readiness_index_is_public_clearance"] = True

    findings = validate_index(index)

    assert any("readiness/archive/rollback/review-start/submission/refresh/approval/signature/public/export/customer/" in finding for finding in findings)


def test_rejects_actual_archive_written():
    index = _index()
    index["readiness_records"][0]["actual_archive_written"] = True

    findings = validate_index(index)

    assert any("readiness/archive/rollback/review-start/submission/refresh/approval/signature/public/export/customer/" in finding for finding in findings)


def test_rejects_action_permitted_now():
    index = _index()
    index["readiness_records"][0]["action_permitted_now"] = True

    findings = validate_index(index)

    assert any("readiness_records[public_landing_use].action_permitted_now must be false" in finding for finding in findings)


def test_rejects_missing_owner_r3_blocker():
    index = copy.deepcopy(_index())
    index["owner_r3_blocker_partition"] = [
        item for item in index["owner_r3_blocker_partition"] if item["decision_type"] != "sns_upload"
    ]

    findings = validate_index(index)

    assert any("owner_r3_blocker_partition missing decision types" in finding for finding in findings)


def test_rejects_owner_r3_blocker_submission_flag():
    index = _index()
    index["owner_r3_blocker_partition"][0]["actual_owner_r3_review_submitted"] = True

    findings = validate_index(index)

    assert any("owner_r3_blocker_partition[public_landing_use].actual_owner_r3_review_submitted must be false" in finding for finding in findings)


def test_rejects_local_next_action_public_action():
    index = _index()
    index["local_next_action_partition"][0]["public_action"] = True

    findings = validate_index(index)

    assert any("local_next_action_partition[public_landing_use].public_action must be false" in finding for finding in findings)
    assert any("readiness/archive/rollback/review-start/submission/refresh/approval/signature/public/export/customer/" in finding for finding in findings)


def test_rejects_blocked_scan_drift():
    index = _index()
    index["blocked_action_scan"]["owner_signature"]["matches"] = ["actual_owner_signature_collected"]

    findings = validate_index(index)

    assert any("blocked_action_scan must match source audit preview" in finding for finding in findings)


def test_rejects_missing_readiness_step():
    index = copy.deepcopy(_index())
    index["readiness_steps"] = [
        item for item in index["readiness_steps"] if item["step_id"] != "verify_blocked_action_scan"
    ]

    findings = validate_index(index)

    assert any("readiness_steps missing verify_blocked_action_scan" in finding for finding in findings)


def test_rejects_external_readiness_step():
    index = _index()
    index["readiness_steps"][0]["external_action"] = True

    findings = validate_index(index)

    assert any("readiness_steps[0].external_action must be false" in finding for finding in findings)


def test_rejects_missing_readiness_event():
    index = copy.deepcopy(_index())
    index["readiness_events"] = [
        item for item in index["readiness_events"] if item["event"] != "blocked_action_scan_reused"
    ]

    findings = validate_index(index)

    assert any("readiness_events missing blocked_action_scan_reused" in finding for finding in findings)


def test_rejects_missing_forbidden_output():
    index = copy.deepcopy(_index())
    index["forbidden_outputs"].remove("archive deletion")

    findings = validate_index(index)

    assert any("forbidden_outputs missing source outputs" in finding for finding in findings)


def test_rejects_handoff_next_task_drift():
    index = _index()
    index["taskset_handoff"]["next_task_candidate"] = "TASK-999"

    findings = validate_index(index)

    assert any("taskset_handoff.next_task_candidate must be TASK-159" in finding for finding in findings)


def test_rejects_handoff_public_use_allowed():
    index = _index()
    index["taskset_handoff"]["actual_public_use_allowed"] = True

    findings = validate_index(index)

    assert any("taskset_handoff.actual_public_use_allowed must be false" in finding for finding in findings)
    assert any("readiness/archive/rollback/review-start/submission/refresh/approval/signature/public/export/customer/" in finding for finding in findings)


def test_rejects_verification_command_drift():
    index = _index()
    index["verification"]["source_gate"] = "python wrong.py --check"

    findings = validate_index(index)

    assert any("verification.source_gate must be" in finding for finding in findings)


def test_rejects_forbidden_key_name():
    index = _index()
    index["readiness_records"][0]["readiness_public_url"] = "https://example.invalid"

    findings = validate_index(index)

    assert any("forbidden readiness/review-submission/approval/signature/export/customer/secret/final-advice key names" in finding for finding in findings)
