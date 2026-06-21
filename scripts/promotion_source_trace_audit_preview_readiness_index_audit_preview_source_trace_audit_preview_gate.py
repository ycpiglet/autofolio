"""Validate TASK-165 source-trace audit preview metadata.

This gate validates local audit-preview metadata only. It rejects actual
Owner/R3 submission, review start, evidence refresh execution, archive writes,
rollback execution, archive deletion, approval evidence collection, approval
records, signatures, public approval, final exports, customer/CRM/payment
action, external account action, platform calls, secrets, final advice, and
drift from the TASK-164 source trace.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIT_PREVIEW = (
    REPO_ROOT
    / "agents"
    / "project"
    / "PROMOTION-SOURCE-TRACE-AUDIT-PREVIEW-READINESS-INDEX-AUDIT-PREVIEW-SOURCE-TRACE-AUDIT-PREVIEW.json"
)
SOURCE_TRACE_REL = (
    "agents/project/PROMOTION-SOURCE-TRACE-AUDIT-PREVIEW-READINESS-INDEX-AUDIT-PREVIEW-SOURCE-TRACE.json"
)
SOURCE_TRACE_PATH = REPO_ROOT / SOURCE_TRACE_REL
EXPECTED_SCHEMA = (
    "autofolio.promotion-source-trace-audit-preview-readiness-index-audit-preview-source-trace-audit-preview/v1"
)
EXPECTED_ID = "promotion_source_trace_audit_preview_readiness_index_audit_preview_source_trace_audit_preview"
EXPECTED_STATUS = (
    "local_source_trace_audit_preview_readiness_index_audit_preview_source_trace_audit_preview_not_actual_submission"
)
EXPECTED_COMPANION = (
    "agents/project/PROMOTION-SOURCE-TRACE-AUDIT-PREVIEW-READINESS-INDEX-AUDIT-PREVIEW-SOURCE-TRACE-AUDIT-PREVIEW.md"
)
EXPECTED_TASKSET = (
    "TASKSET-MARKETING-SOURCE-TRACE-AUDIT-PREVIEW-READINESS-INDEX-AUDIT-PREVIEW-SOURCE-TRACE-AUDIT-PREVIEW"
)


def _load_source_gate() -> Any:
    path = REPO_ROOT / "scripts" / "promotion_source_trace_audit_preview_readiness_index_audit_preview_source_trace_gate.py"
    spec = importlib.util.spec_from_file_location("source_trace_gate", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import source trace gate from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SOURCE_GATE = _load_source_gate()
SOURCE_TRACE_ID = SOURCE_GATE.EXPECTED_ID
SOURCE_TRACE_STATUS = SOURCE_GATE.EXPECTED_STATUS
REQUIRED_DECISION_TYPES = set(SOURCE_GATE.REQUIRED_DECISION_TYPES)

REQUIRED_BOUNDARIES = {
    "local_source_trace_audit_preview_only",
    "audit_preview_not_submission",
    "audit_preview_not_approval",
    "audit_preview_not_publication_clearance",
    "source_trace_not_submission",
    "source_trace_not_approval",
    "source_trace_not_publication_clearance",
    "source_trace_not_external_archive",
    "not_actual_owner_r3_review_submission",
    "not_actual_owner_review_started",
    "not_actual_refresh_execution",
    "not_actual_archive_write",
    "not_actual_rollback_execution",
    "not_archive_deletion",
    "not_external_archive_upload",
    "not_actual_owner_approval_record",
    "not_actual_owner_signature",
    "not_actual_approval_evidence_collection",
    "not_publication_approval",
    "no_public_use_clearance",
    "not_legal_tax_securities_final_advice",
    "no_final_pdf_export",
    "no_final_pptx_export",
    "no_public_url_or_upload",
    "no_sns_upload",
    "no_customer_contact",
    "no_customer_private_data",
    "no_crm_or_payment_action",
    "no_secret_or_token_storage",
    "no_external_account_action",
    "no_oauth_flow",
    "no_platform_api_call",
    "no_kis_order_risk_prod_deploy_change",
    "owner_approval_required_before_public_use",
    "professional_review_required_before_reliance",
}

REQUIRED_ZERO_COUNTS = {
    "actual_owner_r3_review_submissions",
    "actual_owner_review_starts",
    "actual_refresh_executions",
    "actual_archive_writes",
    "actual_rollback_executions",
    "actual_archive_deletions",
    "actual_owner_approval_records",
    "actual_owner_signatures",
    "actual_approval_evidence_collections",
    "public_use_approvals",
    "final_exports_created",
    "public_urls_published",
    "sns_uploads",
    "customer_contacts",
    "crm_payment_actions",
    "secret_handling_events",
    "platform_api_calls",
    "ready_for_owner_r3_submission_records",
    "ready_for_public_use_records",
}

REQUIRED_FALSE_FLAGS = {
    "actual_owner_r3_review_submitted",
    "actual_owner_review_started",
    "actual_refresh_executed",
    "actual_archive_written",
    "actual_rollback_executed",
    "actual_archive_deleted",
    "actual_owner_approval_recorded",
    "actual_owner_signature_collected",
    "actual_approval_evidence_collected",
    "public_use_approved",
    "final_export_created",
    "public_url_published",
    "sns_uploaded",
    "customer_contacted",
    "crm_payment_action",
    "secret_handled",
    "platform_api_called",
    "audit_preview_is_submission",
    "audit_preview_is_approval",
    "audit_preview_is_public_clearance",
    "source_trace_mutated_source",
    "action_permitted_now",
}

REQUIRED_STEPS = {
    "verify_source_trace_gate",
    "record_source_trace_hash",
    "verify_source_chain_continuity",
    "audit_owner_r3_blocker_preservation",
    "audit_blocked_action_scan_preservation",
    "confirm_non_action_boundary",
    "close_task_165_local_audit_preview",
}

FORBIDDEN_KEY_NAMES = {
    "secret_value",
    "token_value",
    "api_key",
    "password",
    "account_number",
    "customer_email",
    "customer_phone",
    "oauth_code",
    "access_token",
    "refresh_token",
}


def _json_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_audit_preview(path: Path = DEFAULT_AUDIT_PREVIEW) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_source_trace() -> dict[str, Any]:
    return SOURCE_GATE.load_trace(SOURCE_TRACE_PATH)


def validate_audit_preview(audit_preview: dict[str, Any], repo_root: Path = REPO_ROOT) -> list[str]:
    findings: list[str] = []

    source_trace = load_source_trace()
    source_findings = SOURCE_GATE.validate_trace(source_trace, repo_root)
    if source_findings:
        findings.extend(f"source trace invalid: {finding}" for finding in source_findings)

    expected_top = {
        "$schema": EXPECTED_SCHEMA,
        "id": EXPECTED_ID,
        "status": EXPECTED_STATUS,
        "companion_markdown": EXPECTED_COMPANION,
        "owner": "QA",
        "related_taskset": EXPECTED_TASKSET,
    }
    for key, expected in expected_top.items():
        if audit_preview.get(key) != expected:
            findings.append(f"{key} must be {expected}")

    if audit_preview.get("related_tasks") != ["TASK-160", "TASK-161", "TASK-162", "TASK-163", "TASK-164", "TASK-165"]:
        findings.append("related_tasks must list TASK-160 through TASK-165")

    findings.extend(_validate_source_input(audit_preview, source_trace))
    findings.extend(_validate_boundaries(audit_preview))
    findings.extend(_validate_summary(audit_preview, source_trace))
    findings.extend(_validate_records(audit_preview, source_trace))
    findings.extend(_validate_non_action_flags(audit_preview))
    findings.extend(_validate_steps(audit_preview))
    findings.extend(_validate_handoff(audit_preview))
    findings.extend(_validate_verification(audit_preview))
    findings.extend(_scan_for_forbidden_keys(audit_preview))

    return findings


def _validate_source_input(audit_preview: dict[str, Any], source_trace: dict[str, Any]) -> list[str]:
    source_inputs = audit_preview.get("source_inputs")
    if not isinstance(source_inputs, list) or len(source_inputs) != 1:
        return ["source_inputs must contain exactly one TASK-164 source trace input"]

    source_input = source_inputs[0]
    expected = {
        "id": SOURCE_TRACE_ID,
        "path": SOURCE_TRACE_REL,
        "companion_markdown": "agents/project/PROMOTION-SOURCE-TRACE-AUDIT-PREVIEW-READINESS-INDEX-AUDIT-PREVIEW-SOURCE-TRACE.md",
        "relationship": "audits_source_trace",
        "sha256": _file_hash(SOURCE_TRACE_PATH),
        "source_status": SOURCE_TRACE_STATUS,
        "source_gate_result": "pass",
    }
    findings = [f"source_inputs[0].{key} must be {value}" for key, value in expected.items() if source_input.get(key) != value]
    if source_trace.get("id") != source_input.get("id"):
        findings.append("source_inputs[0].id must match source trace id")
    return findings


def _validate_boundaries(audit_preview: dict[str, Any]) -> list[str]:
    boundaries = audit_preview.get("boundaries")
    if not isinstance(boundaries, dict):
        return ["boundaries must be an object"]
    missing = REQUIRED_BOUNDARIES - set(boundaries)
    findings = [f"boundaries missing keys: {sorted(missing)}"] if missing else []
    findings.extend(f"boundaries.{key} must be true" for key in REQUIRED_BOUNDARIES if boundaries.get(key) is not True)
    return findings


def _validate_summary(audit_preview: dict[str, Any], source_trace: dict[str, Any]) -> list[str]:
    summary = audit_preview.get("audit_preview_summary")
    if not isinstance(summary, dict):
        return ["audit_preview_summary must be an object"]

    expected = {
        "source_root": SOURCE_TRACE_ID,
        "source_root_status": SOURCE_TRACE_STATUS,
        "source_gate_result": "pass",
        "audit_preview_gate_result": "pass",
        "audit_preview_records": len(REQUIRED_DECISION_TYPES),
        "source_chain_records": len(source_trace.get("source_chain", [])),
        "source_chain_hash": _json_hash(source_trace.get("source_chain")),
        "owner_r3_blocker_trace_records": len(source_trace.get("owner_r3_blocker_trace", [])),
        "owner_r3_blocker_trace_hash": _json_hash(source_trace.get("owner_r3_blocker_trace")),
        "blocked_action_scan_items": len(source_trace.get("blocked_action_scan", {})),
        "blocked_action_scan_hash": _json_hash(source_trace.get("blocked_action_scan")),
        "forbidden_outputs": len(source_trace.get("forbidden_outputs", [])),
        "forbidden_outputs_hash": _json_hash(source_trace.get("forbidden_outputs")),
    }
    findings = [f"audit_preview_summary.{key} must be {value}" for key, value in expected.items() if summary.get(key) != value]
    findings.extend(f"audit_preview_summary.{key} must be 0" for key in REQUIRED_ZERO_COUNTS if summary.get(key) != 0)

    continuity = audit_preview.get("continuity_hashes")
    if not isinstance(continuity, dict):
        findings.append("continuity_hashes must be an object")
    else:
        for key, source_key in {
            "source_chain": "source_chain",
            "owner_r3_blocker_trace": "owner_r3_blocker_trace",
            "blocked_action_scan": "blocked_action_scan",
            "forbidden_outputs": "forbidden_outputs",
        }.items():
            expected_hash = _json_hash(source_trace.get(source_key))
            if continuity.get(key) != expected_hash:
                findings.append(f"continuity_hashes.{key} must be {expected_hash}")
    return findings


def _validate_records(audit_preview: dict[str, Any], source_trace: dict[str, Any]) -> list[str]:
    records = audit_preview.get("source_trace_audit_preview_records")
    if not isinstance(records, list):
        return ["source_trace_audit_preview_records must be a list"]
    findings: list[str] = []
    decision_types = {record.get("decision_type") for record in records if isinstance(record, dict)}
    if decision_types != REQUIRED_DECISION_TYPES:
        findings.append(f"source_trace_audit_preview_records decision types must be {sorted(REQUIRED_DECISION_TYPES)}")
    if len(records) != len(REQUIRED_DECISION_TYPES):
        findings.append(f"source_trace_audit_preview_records must contain {len(REQUIRED_DECISION_TYPES)} records")

    source_decisions = {record.get("decision_type") for record in source_trace.get("owner_r3_blocker_trace", [])}
    if source_decisions != REQUIRED_DECISION_TYPES:
        findings.append("source owner_r3_blocker_trace decision types drifted")

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            findings.append(f"source_trace_audit_preview_records[{index}] must be an object")
            continue
        if record.get("audit_preview_status") != "pass":
            findings.append(f"source_trace_audit_preview_records[{index}].audit_preview_status must be pass")
        for key in [
            "source_trace_coverage_verified",
            "owner_r3_blocker_preserved",
            "blocked_action_scan_preserved",
        ]:
            if record.get(key) is not True:
                findings.append(f"source_trace_audit_preview_records[{index}].{key} must be true")
        for key in ["action_permitted_now", "public_use_approved"]:
            if record.get(key) is not False:
                findings.append(f"source_trace_audit_preview_records[{index}].{key} must be false")
    return findings


def _validate_non_action_flags(audit_preview: dict[str, Any]) -> list[str]:
    flags = audit_preview.get("non_action_flags")
    if not isinstance(flags, dict):
        return ["non_action_flags must be an object"]
    return [f"non_action_flags.{key} must be false" for key in REQUIRED_FALSE_FLAGS if flags.get(key) is not False]


def _validate_steps(audit_preview: dict[str, Any]) -> list[str]:
    steps = audit_preview.get("audit_preview_steps")
    if not isinstance(steps, list):
        return ["audit_preview_steps must be a list"]
    step_ids = {step.get("step_id") for step in steps if isinstance(step, dict)}
    findings = []
    missing = REQUIRED_STEPS - step_ids
    if missing:
        findings.append(f"audit_preview_steps missing {sorted(missing)}")
    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            findings.append(f"audit_preview_steps[{index}] must be an object")
            continue
        if step.get("status") != "pass":
            findings.append(f"audit_preview_steps[{index}].status must be pass")
        if step.get("external_action") is not False:
            findings.append(f"audit_preview_steps[{index}].external_action must be false")
    return findings


def _validate_handoff(audit_preview: dict[str, Any]) -> list[str]:
    handoff = audit_preview.get("taskset_handoff")
    if not isinstance(handoff, dict):
        return ["taskset_handoff must be an object"]
    expected_false = [
        "actual_owner_r3_review_submission_allowed",
        "actual_owner_review_start_allowed",
        "actual_refresh_execution_allowed",
        "actual_archive_write_allowed",
        "actual_rollback_execution_allowed",
        "actual_archive_delete_allowed",
        "approval_evidence_collection_allowed",
        "final_export_allowed",
        "public_use_allowed",
        "customer_or_payment_action_allowed",
    ]
    findings = []
    if handoff.get("task_165_local_audit_preview_complete") is not True:
        findings.append("taskset_handoff.task_165_local_audit_preview_complete must be true")
    if handoff.get("taskset_local_scope_complete_when_task_closes") is not True:
        findings.append("taskset_handoff.taskset_local_scope_complete_when_task_closes must be true")
    findings.extend(f"taskset_handoff.{key} must be false" for key in expected_false if handoff.get(key) is not False)
    required_for = handoff.get("owner_r3_required_for")
    if not isinstance(required_for, list) or len(required_for) < 5:
        findings.append("taskset_handoff.owner_r3_required_for must list Owner/R3 gated actions")
    return findings


def _validate_verification(audit_preview: dict[str, Any]) -> list[str]:
    verification = audit_preview.get("verification")
    if not isinstance(verification, dict):
        return ["verification must be an object"]
    expected = {
        "local_gate": "python scripts/promotion_source_trace_audit_preview_readiness_index_audit_preview_source_trace_audit_preview_gate.py --check",
        "focused_tests": "python -m pytest tests/unit/test_promotion_source_trace_audit_preview_readiness_index_audit_preview_source_trace_audit_preview_gate.py -q",
        "source_gate": "python scripts/promotion_source_trace_audit_preview_readiness_index_audit_preview_source_trace_gate.py --check",
    }
    return [f"verification.{key} must be {value}" for key, value in expected.items() if verification.get(key) != value]


def _scan_for_forbidden_keys(value: Any, path: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in FORBIDDEN_KEY_NAMES:
                findings.append(f"forbidden key present at {path}.{key}")
            findings.extend(_scan_for_forbidden_keys(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(_scan_for_forbidden_keys(child, f"{path}[{index}]"))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate TASK-165 local audit-preview metadata.")
    parser.add_argument("--path", type=Path, default=DEFAULT_AUDIT_PREVIEW)
    parser.add_argument("--check", action="store_true", help="print status and exit non-zero on findings")
    args = parser.parse_args()

    findings = validate_audit_preview(load_audit_preview(args.path))
    if args.check:
        if findings:
            for finding in findings:
                print(f"FAIL: {finding}")
            return 1
        print("OK: TASK-165 source trace audit preview gate passed")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
