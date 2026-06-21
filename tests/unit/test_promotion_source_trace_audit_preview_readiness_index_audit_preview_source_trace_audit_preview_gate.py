from __future__ import annotations

import copy

from scripts.promotion_source_trace_audit_preview_readiness_index_audit_preview_source_trace_audit_preview_gate import (
    load_audit_preview,
    validate_audit_preview,
)


def _audit_preview() -> dict:
    return load_audit_preview()


def test_current_audit_preview_passes():
    assert validate_audit_preview(_audit_preview()) == []


def test_rejects_source_hash_mismatch():
    audit_preview = _audit_preview()
    audit_preview["source_inputs"][0]["sha256"] = "0" * 64

    findings = validate_audit_preview(audit_preview)

    assert any("source_inputs[0].sha256" in finding for finding in findings)


def test_rejects_missing_boundary():
    audit_preview = _audit_preview()
    audit_preview["boundaries"]["audit_preview_not_submission"] = False

    findings = validate_audit_preview(audit_preview)

    assert any("boundaries.audit_preview_not_submission must be true" in finding for finding in findings)


def test_rejects_summary_count_drift():
    audit_preview = _audit_preview()
    audit_preview["audit_preview_summary"]["audit_preview_records"] = 8

    findings = validate_audit_preview(audit_preview)

    assert any("audit_preview_summary.audit_preview_records must be 9" in finding for finding in findings)


def test_rejects_continuity_hash_drift():
    audit_preview = _audit_preview()
    audit_preview["continuity_hashes"]["source_chain"] = "0" * 64

    findings = validate_audit_preview(audit_preview)

    assert any("continuity_hashes.source_chain" in finding for finding in findings)


def test_rejects_missing_decision_record():
    audit_preview = copy.deepcopy(_audit_preview())
    audit_preview["source_trace_audit_preview_records"] = [
        record
        for record in audit_preview["source_trace_audit_preview_records"]
        if record["decision_type"] != "sns_upload"
    ]

    findings = validate_audit_preview(audit_preview)

    assert any("source_trace_audit_preview_records decision types" in finding for finding in findings)
    assert any("source_trace_audit_preview_records must contain 9 records" in finding for finding in findings)


def test_rejects_public_use_approval():
    audit_preview = _audit_preview()
    audit_preview["source_trace_audit_preview_records"][0]["public_use_approved"] = True

    findings = validate_audit_preview(audit_preview)

    assert any("public_use_approved must be false" in finding for finding in findings)


def test_rejects_non_action_flag_true():
    audit_preview = _audit_preview()
    audit_preview["non_action_flags"]["actual_archive_written"] = True

    findings = validate_audit_preview(audit_preview)

    assert any("non_action_flags.actual_archive_written must be false" in finding for finding in findings)


def test_rejects_missing_step():
    audit_preview = copy.deepcopy(_audit_preview())
    audit_preview["audit_preview_steps"] = [
        step for step in audit_preview["audit_preview_steps"] if step["step_id"] != "verify_source_trace_gate"
    ]

    findings = validate_audit_preview(audit_preview)

    assert any("audit_preview_steps missing" in finding for finding in findings)


def test_rejects_handoff_live_permission():
    audit_preview = _audit_preview()
    audit_preview["taskset_handoff"]["public_use_allowed"] = True

    findings = validate_audit_preview(audit_preview)

    assert any("taskset_handoff.public_use_allowed must be false" in finding for finding in findings)


def test_rejects_verification_drift():
    audit_preview = _audit_preview()
    audit_preview["verification"]["local_gate"] = "python wrong.py"

    findings = validate_audit_preview(audit_preview)

    assert any("verification.local_gate" in finding for finding in findings)


def test_rejects_forbidden_secret_key():
    audit_preview = _audit_preview()
    audit_preview["secret_value"] = "not allowed"

    findings = validate_audit_preview(audit_preview)

    assert any("forbidden key present" in finding for finding in findings)
