"""Validate the TASK-163 source-trace audit-preview readiness-index audit preview.

This gate validates local audit-preview metadata only. It rejects actual
Owner/R3 submission, review start, evidence refresh execution, archive writes,
rollback execution, archive deletion, approval evidence collection, approval
records, signatures, public approval, final exports, customer/CRM/payment
action, external account action, platform calls, secrets, final advice, and
drift from the TASK-162 source readiness index.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PREVIEW = (
    REPO_ROOT
    / "agents"
    / "project"
    / "PROMOTION-SOURCE-TRACE-AUDIT-PREVIEW-READINESS-INDEX-AUDIT-PREVIEW.json"
)
SOURCE_INDEX_REL = "agents/project/PROMOTION-SOURCE-TRACE-AUDIT-PREVIEW-READINESS-INDEX.json"
SOURCE_INDEX_PATH = REPO_ROOT / SOURCE_INDEX_REL
EXPECTED_SCHEMA = "autofolio.promotion-source-trace-audit-preview-readiness-index-audit-preview/v1"
EXPECTED_ID = "promotion_source_trace_audit_preview_readiness_index_audit_preview"
EXPECTED_STATUS = "local_source_trace_audit_preview_readiness_index_audit_preview_not_actual_submission"


def _load_source_gate() -> Any:
    path = REPO_ROOT / "scripts" / "promotion_source_trace_audit_preview_readiness_index_gate.py"
    spec = importlib.util.spec_from_file_location("source_trace_readiness_index_gate", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import source readiness index gate from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SOURCE_GATE = _load_source_gate()
SOURCE_INDEX_ID = SOURCE_GATE.EXPECTED_ID
SOURCE_INDEX_STATUS = SOURCE_GATE.EXPECTED_STATUS
REQUIRED_DECISION_TYPES = set(SOURCE_GATE.REQUIRED_DECISION_TYPES)
REQUIRED_BLOCKED_SCAN_KEYS = set(SOURCE_GATE.REQUIRED_BLOCKED_SCAN_KEYS)
REQUIRED_FORBIDDEN_OUTPUTS = set(SOURCE_GATE.REQUIRED_FORBIDDEN_OUTPUTS)
REQUIRED_BOUNDARIES = set(SOURCE_GATE.REQUIRED_BOUNDARIES) | {
    "local_source_trace_audit_preview_readiness_index_audit_preview_only",
    "readiness_index_audit_preview_not_submission",
    "readiness_index_audit_preview_not_approval",
    "readiness_index_audit_preview_not_publication_clearance",
    "readiness_index_audit_preview_not_external_archive",
    "source_readiness_index_not_submission",
    "source_readiness_index_not_approval",
    "source_readiness_index_not_publication_clearance",
    "source_readiness_index_not_external_archive",
}
FORBIDDEN_KEY_NAMES = set(SOURCE_GATE.FORBIDDEN_KEY_NAMES) | {
    "readiness_index_audit_submission_id",
    "readiness_index_audit_approval_id",
    "readiness_index_audit_public_url",
    "readiness_index_audit_archive_id",
}
LIVE_TRUE_KEYS = set(SOURCE_GATE.LIVE_TRUE_KEYS) | {
    "readiness_index_audit_preview_is_submission",
    "readiness_index_audit_preview_is_approval",
    "readiness_index_audit_preview_is_public_clearance",
    "readiness_index_audit_preview_external_archive",
    "audit_preview_is_submission",
    "audit_preview_is_approval",
    "audit_preview_is_public_clearance",
    "source_readiness_index_mutated_source",
    "external_validation_performed",
    "external_action",
    "public_action",
    "owner_r3_submission",
    "owner_review_start",
    "archive_write",
    "rollback_execution",
    "archive_delete",
    "approval_evidence_collection",
    "final_export",
    "customer_contact",
    "crm_payment",
    "secret_handling",
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
    "action_permitted_now",
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
}
REQUIRED_FALSE_FLAGS = {
    "readiness_index_audit_preview_is_submission",
    "readiness_index_audit_preview_is_approval",
    "readiness_index_audit_preview_is_public_clearance",
    "readiness_index_audit_preview_external_archive",
    "source_readiness_index_mutated_source",
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
    "action_permitted_now",
}
AUDIT_RECORD_FALSE_FLAGS = {
    "audit_preview_is_submission",
    "audit_preview_is_approval",
    "audit_preview_is_public_clearance",
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
    "action_permitted_now",
}
STEP_FALSE_FLAGS = {
    "external_action",
    "owner_r3_submission",
    "owner_review_start",
    "archive_write",
    "rollback_execution",
    "archive_delete",
    "approval_evidence_collection",
    "final_export",
    "public_action",
    "customer_contact",
    "crm_payment",
    "secret_handling",
}
REQUIRED_AUDIT_STEPS = {
    "record_source_readiness_index_hash",
    "verify_source_readiness_index_gate",
    "audit_readiness_records",
    "audit_owner_r3_blocker_partition",
    "audit_local_next_actions",
    "audit_blocked_action_scan",
    "audit_forbidden_outputs",
    "register_audit_preview_handoff",
}
REQUIRED_AUDIT_EVENTS = {
    "readiness_index_audit_preview_generated",
    "source_readiness_index_hash_recorded",
    "source_readiness_index_gate_verified",
    "readiness_records_audited",
    "owner_r3_blocker_partition_audited",
    "local_next_actions_audited",
    "blocked_action_scan_reused",
    "audit_preview_handoff_registered",
}


def load_preview(path: Path = DEFAULT_PREVIEW) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("promotion source trace readiness index audit preview root must be an object")
    return data


def validate_preview(preview: dict[str, Any], repo_root: Path = REPO_ROOT) -> list[str]:
    findings: list[str] = []
    source = SOURCE_GATE.load_index(SOURCE_INDEX_PATH)
    source_findings = SOURCE_GATE.validate_index(source, repo_root)
    findings.extend([f"source readiness index invalid: {finding}" for finding in source_findings])

    if preview.get("$schema") != EXPECTED_SCHEMA:
        findings.append(f"$schema must be {EXPECTED_SCHEMA}")
    if preview.get("id") != EXPECTED_ID:
        findings.append(f"id must be {EXPECTED_ID}")
    if preview.get("status") != EXPECTED_STATUS:
        findings.append(f"status must be {EXPECTED_STATUS}")
    if preview.get("owner") != "QA":
        findings.append("owner must be QA")
    if preview.get("related_taskset") != "TASKSET-MARKETING-SOURCE-TRACE-AUDIT-PREVIEW-READINESS-INDEX-AUDIT-PREVIEW":
        findings.append("related_taskset must be TASKSET-MARKETING-SOURCE-TRACE-AUDIT-PREVIEW-READINESS-INDEX-AUDIT-PREVIEW")
    related_tasks = _string_list(preview.get("related_tasks"))
    for task_id in ("TASK-162", "TASK-163"):
        if task_id not in related_tasks:
            findings.append(f"related_tasks missing {task_id}")

    findings.extend(_validate_boundaries(preview))
    findings.extend(_validate_sources(preview, repo_root, source))
    findings.extend(_validate_markdown(preview, repo_root))
    findings.extend(_validate_summary(preview, source))
    findings.extend(_validate_reference_coverage(preview, source))
    findings.extend(_validate_non_action_flags(preview))
    findings.extend(_validate_audit_preview_records(preview, source))
    findings.extend(_validate_blocker_partition_audit(preview, source))
    findings.extend(_validate_local_next_actions_audit(preview, source))
    findings.extend(_validate_blocked_scan(preview, source))
    findings.extend(_validate_steps_and_events(preview))
    findings.extend(_validate_forbidden_outputs(preview, source))
    findings.extend(_validate_handoff(preview))
    findings.extend(_validate_verification(preview))

    forbidden_keys = _find_forbidden_keys(preview)
    if forbidden_keys:
        findings.append(f"forbidden key names present: {', '.join(forbidden_keys)}")
    live_true_keys = _find_live_true_keys(preview)
    if live_true_keys:
        findings.append(
            "readiness-index-audit-preview/archive/rollback/review-start/submission/refresh/approval/"
            f"signature/public/customer/payment/secret live-action flags must stay false: {', '.join(live_true_keys)}"
        )
    return findings


def _validate_boundaries(preview: dict[str, Any]) -> list[str]:
    boundaries = preview.get("boundaries")
    if not isinstance(boundaries, dict):
        return ["boundaries must be an object"]
    return [f"boundaries.{boundary} must be true" for boundary in sorted(REQUIRED_BOUNDARIES) if boundaries.get(boundary) is not True]


def _validate_sources(preview: dict[str, Any], repo_root: Path, source: dict[str, Any]) -> list[str]:
    sources = preview.get("source_inputs")
    if not isinstance(sources, list) or len(sources) != 1 or not isinstance(sources[0], dict):
        return ["source_inputs must contain exactly one object"]
    item = sources[0]
    findings: list[str] = []
    if item.get("id") != SOURCE_INDEX_ID:
        findings.append(f"source_inputs[0].id must be {SOURCE_INDEX_ID}")
    if item.get("path") != SOURCE_INDEX_REL:
        findings.append(f"source_inputs[0].path must be {SOURCE_INDEX_REL}")
    if item.get("relationship") != "audits_source_trace_audit_preview_readiness_index":
        findings.append("source_inputs[0].relationship must be audits_source_trace_audit_preview_readiness_index")
    if item.get("source_status") != SOURCE_INDEX_STATUS:
        findings.append(f"source_inputs[0].source_status must be {SOURCE_INDEX_STATUS}")
    if item.get("source_gate_result") != "pass":
        findings.append("source_inputs[0].source_gate_result must be pass")
    source_path = _safe_repo_path(repo_root, SOURCE_INDEX_REL)
    if not source_path.exists():
        findings.append(f"source input path does not exist: {SOURCE_INDEX_REL}")
    else:
        digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
        if item.get("sha256") != digest:
            findings.append(f"source_inputs[0].sha256 mismatch for {SOURCE_INDEX_REL}")
    if source.get("id") != SOURCE_INDEX_ID:
        findings.append(f"source readiness index id must be {SOURCE_INDEX_ID}")
    return findings


def _validate_markdown(preview: dict[str, Any], repo_root: Path) -> list[str]:
    rel = preview.get("companion_markdown")
    if not isinstance(rel, str) or not rel:
        return ["companion_markdown must be a non-empty string"]
    path = _safe_repo_path(repo_root, rel)
    if not path.exists():
        return [f"companion_markdown does not exist: {rel}"]
    return []


def _validate_summary(preview: dict[str, Any], source: dict[str, Any]) -> list[str]:
    summary = preview.get("audit_preview_summary")
    if not isinstance(summary, dict):
        return ["audit_preview_summary must be an object"]
    decisions = len(source.get("readiness_records", []))
    expected = {
        "source_readiness_index": SOURCE_INDEX_ID,
        "source_status": SOURCE_INDEX_STATUS,
        "source_gate_result": "pass",
        "gate_result": "pass",
        "source_readiness_records": decisions,
        "source_owner_r3_blocker_partition_records": len(source.get("owner_r3_blocker_partition", [])),
        "source_local_next_action_partition_records": len(source.get("local_next_action_partition", [])),
        "source_blocked_action_scan_items": len(source.get("blocked_action_scan", {})),
        "source_forbidden_outputs": len(source.get("forbidden_outputs", [])),
        "source_boundaries": len(source.get("boundaries", {})),
        "audit_preview_records": decisions,
        "owner_r3_blocker_partition_audit_records": decisions,
        "local_next_action_partition_audit_records": decisions,
        "blocked_action_scan_items": len(source.get("blocked_action_scan", {})),
        "forbidden_outputs": len(source.get("forbidden_outputs", [])),
        "records_requiring_owner_r3": decisions,
        "records_with_source_hash_recorded": decisions,
        "records_with_non_submission_status": decisions,
        "records_with_non_approval_status": decisions,
        "records_with_public_use_blocked": decisions,
        "actual_owner_r3_review_submissions": 0,
        "actual_owner_review_starts": 0,
        "actual_refresh_executions": 0,
        "actual_archive_writes": 0,
        "actual_rollback_executions": 0,
        "actual_archive_deletions": 0,
        "actual_owner_approval_records": 0,
        "actual_owner_signatures": 0,
        "actual_approval_evidence_collections": 0,
        "public_use_approvals": 0,
        "final_exports_created": 0,
        "public_urls_published": 0,
        "sns_uploads": 0,
        "customer_contacts": 0,
        "crm_payment_actions": 0,
        "secret_handling_events": 0,
        "platform_api_calls": 0,
        "ready_for_owner_r3_submission_records": 0,
        "ready_for_public_use_records": 0,
    }
    return [f"audit_preview_summary.{key} must be {value}" for key, value in expected.items() if summary.get(key) != value]


def _validate_reference_coverage(preview: dict[str, Any], source: dict[str, Any]) -> list[str]:
    coverage = preview.get("source_reference_coverage")
    if not isinstance(coverage, dict):
        return ["source_reference_coverage must be an object"]
    findings: list[str] = []
    for key in (
        "source_readiness_index_gate_reused",
        "source_readiness_index_hash_recorded",
        "source_reference_coverage_passed",
        "source_readiness_records_preserved",
        "owner_r3_blockers_preserved",
        "local_next_actions_preserved",
        "blocked_action_scan_reused",
        "forbidden_outputs_reused",
    ):
        if coverage.get(key) is not True:
            findings.append(f"source_reference_coverage.{key} must be true")
    for key in ("source_readiness_index_mutated_source", "external_validation_performed"):
        if coverage.get(key) is not False:
            findings.append(f"source_reference_coverage.{key} must be false")
    expected_counts = {
        "source_readiness_records": len(source.get("readiness_records", [])),
        "source_owner_r3_blocker_partition_records": len(source.get("owner_r3_blocker_partition", [])),
        "source_local_next_action_partition_records": len(source.get("local_next_action_partition", [])),
        "source_blocked_action_scan_items": len(source.get("blocked_action_scan", {})),
        "source_forbidden_outputs": len(source.get("forbidden_outputs", [])),
        "source_boundaries": len(source.get("boundaries", {})),
    }
    for key, value in expected_counts.items():
        if coverage.get(key) != value:
            findings.append(f"source_reference_coverage.{key} must be {value}")
    return findings


def _validate_non_action_flags(preview: dict[str, Any]) -> list[str]:
    flags = preview.get("non_action_flags")
    if not isinstance(flags, dict):
        return ["non_action_flags must be an object"]
    return [f"non_action_flags.{key} must be false" for key in sorted(REQUIRED_FALSE_FLAGS) if flags.get(key) is not False]


def _validate_audit_preview_records(preview: dict[str, Any], source: dict[str, Any]) -> list[str]:
    records = preview.get("audit_preview_records")
    if not isinstance(records, list):
        return ["audit_preview_records must be a list"]
    findings: list[str] = []
    by_decision = _by_decision(records)
    source_by_decision = _by_decision(source.get("readiness_records"))
    missing = REQUIRED_DECISION_TYPES - set(by_decision)
    extra = set(by_decision) - REQUIRED_DECISION_TYPES
    if missing:
        findings.append(f"audit_preview_records missing decision types: {sorted(missing)}")
    if extra:
        findings.append(f"audit_preview_records unexpected decision types: {sorted(extra)}")
    for decision_type, item in sorted(by_decision.items()):
        source_item = source_by_decision.get(decision_type, {})
        if item.get("source_readiness_record_id") != source_item.get("readiness_record_id"):
            findings.append(f"audit_preview_records[{decision_type}].source_readiness_record_id must match source")
        if item.get("source_audit_preview_record_id") != source_item.get("source_audit_preview_record_id"):
            findings.append(f"audit_preview_records[{decision_type}].source_audit_preview_record_id must match source")
        if item.get("source_origin_readiness_record_id") != source_item.get("source_readiness_record_id"):
            findings.append(f"audit_preview_records[{decision_type}].source_origin_readiness_record_id must match source")
        if item.get("source_owner_r3_blocker_trace_status") != source_item.get("source_owner_r3_blocker_trace_status"):
            findings.append(f"audit_preview_records[{decision_type}].source_owner_r3_blocker_trace_status must match source")
        if item.get("audit_preview_status") != "pass":
            findings.append(f"audit_preview_records[{decision_type}].audit_preview_status must be pass")
        if item.get("source_readiness_index_hash_recorded") is not True:
            findings.append(f"audit_preview_records[{decision_type}].source_readiness_index_hash_recorded must be true")
        for key in (
            "owner_r3_required_before_submission",
            "owner_r3_required_before_public_use",
            "professional_review_required_before_reliance",
        ):
            if item.get(key) is not True:
                findings.append(f"audit_preview_records[{decision_type}].{key} must be true")
        for key in sorted(AUDIT_RECORD_FALSE_FLAGS):
            if item.get(key) is not False:
                findings.append(f"audit_preview_records[{decision_type}].{key} must be false")
    return findings


def _validate_blocker_partition_audit(preview: dict[str, Any], source: dict[str, Any]) -> list[str]:
    records = preview.get("owner_r3_blocker_partition_audit")
    if not isinstance(records, list):
        return ["owner_r3_blocker_partition_audit must be a list"]
    findings: list[str] = []
    by_decision = _by_decision(records)
    source_by_decision = _by_decision(source.get("owner_r3_blocker_partition"))
    missing = REQUIRED_DECISION_TYPES - set(by_decision)
    extra = set(by_decision) - REQUIRED_DECISION_TYPES
    if missing:
        findings.append(f"owner_r3_blocker_partition_audit missing decision types: {sorted(missing)}")
    if extra:
        findings.append(f"owner_r3_blocker_partition_audit unexpected decision types: {sorted(extra)}")
    for decision_type, item in sorted(by_decision.items()):
        source_item = source_by_decision.get(decision_type, {})
        if item.get("source_partition_record_id") != source_item.get("partition_record_id"):
            findings.append(f"owner_r3_blocker_partition_audit[{decision_type}].source_partition_record_id must match source")
        if item.get("source_readiness_record_id") != source_item.get("source_readiness_record_id"):
            findings.append(f"owner_r3_blocker_partition_audit[{decision_type}].source_readiness_record_id must match source")
        if item.get("audit_status") != "pass":
            findings.append(f"owner_r3_blocker_partition_audit[{decision_type}].audit_status must be pass")
        if item.get("blocker_partition_preserved") is not True:
            findings.append(f"owner_r3_blocker_partition_audit[{decision_type}].blocker_partition_preserved must be true")
        for key in (
            "owner_r3_required_before_submission",
            "owner_r3_required_before_public_use",
            "professional_review_required_before_reliance",
        ):
            if item.get(key) is not True:
                findings.append(f"owner_r3_blocker_partition_audit[{decision_type}].{key} must be true")
        for key in ("public_use_approved", "action_permitted_now"):
            if item.get(key) is not False:
                findings.append(f"owner_r3_blocker_partition_audit[{decision_type}].{key} must be false")
    return findings


def _validate_local_next_actions_audit(preview: dict[str, Any], source: dict[str, Any]) -> list[str]:
    records = preview.get("local_next_action_partition_audit")
    if not isinstance(records, list):
        return ["local_next_action_partition_audit must be a list"]
    findings: list[str] = []
    by_decision = _by_decision(records)
    source_by_decision = _by_decision(source.get("local_next_action_partition"))
    missing = REQUIRED_DECISION_TYPES - set(by_decision)
    extra = set(by_decision) - REQUIRED_DECISION_TYPES
    if missing:
        findings.append(f"local_next_action_partition_audit missing decision types: {sorted(missing)}")
    if extra:
        findings.append(f"local_next_action_partition_audit unexpected decision types: {sorted(extra)}")
    for decision_type, item in sorted(by_decision.items()):
        source_item = source_by_decision.get(decision_type, {})
        if item.get("source_next_action_record_id") != source_item.get("next_action_record_id"):
            findings.append(f"local_next_action_partition_audit[{decision_type}].source_next_action_record_id must match source")
        if item.get("source_local_next_action") != source_item.get("local_next_action"):
            findings.append(f"local_next_action_partition_audit[{decision_type}].source_local_next_action must match source")
        if item.get("audit_status") != "pass":
            findings.append(f"local_next_action_partition_audit[{decision_type}].audit_status must be pass")
        if item.get("local_next_action_preserved") is not True:
            findings.append(f"local_next_action_partition_audit[{decision_type}].local_next_action_preserved must be true")
        if item.get("owner_r3_required_before_action") is not True:
            findings.append(f"local_next_action_partition_audit[{decision_type}].owner_r3_required_before_action must be true")
        for key in ("external_action", "public_action", "customer_contact", "crm_payment", "final_export", "action_permitted_now"):
            if item.get(key) is not False:
                findings.append(f"local_next_action_partition_audit[{decision_type}].{key} must be false")
    return findings


def _validate_blocked_scan(preview: dict[str, Any], source: dict[str, Any]) -> list[str]:
    scan = preview.get("blocked_action_scan")
    if scan != source.get("blocked_action_scan"):
        return ["blocked_action_scan must match source readiness index"]
    if not isinstance(scan, dict):
        return ["blocked_action_scan must be an object"]
    missing = REQUIRED_BLOCKED_SCAN_KEYS - set(scan)
    if missing:
        return [f"blocked_action_scan missing keys: {sorted(missing)}"]
    findings: list[str] = []
    for key in REQUIRED_BLOCKED_SCAN_KEYS:
        item = scan.get(key)
        if not isinstance(item, dict):
            findings.append(f"blocked_action_scan.{key} must be an object")
            continue
        if item.get("status") != "pass":
            findings.append(f"blocked_action_scan.{key}.status must be pass")
        if item.get("blocked_all") is not True:
            findings.append(f"blocked_action_scan.{key}.blocked_all must be true")
        if item.get("matches") != []:
            findings.append(f"blocked_action_scan.{key}.matches must be empty")
    return findings


def _validate_steps_and_events(preview: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    steps = preview.get("audit_preview_steps")
    if not isinstance(steps, list):
        return ["audit_preview_steps must be a list"]
    step_ids = {item.get("step_id") for item in steps if isinstance(item, dict)}
    missing_steps = REQUIRED_AUDIT_STEPS - step_ids
    if missing_steps:
        findings.append(f"audit_preview_steps missing {', '.join(sorted(missing_steps))}")
    for index_num, step in enumerate(steps):
        if not isinstance(step, dict):
            findings.append(f"audit_preview_steps[{index_num}] must be an object")
            continue
        if step.get("status") != "pass":
            findings.append(f"audit_preview_steps[{index_num}].status must be pass")
        for key in sorted(STEP_FALSE_FLAGS):
            if step.get(key) is not False:
                findings.append(f"audit_preview_steps[{index_num}].{key} must be false")

    events = preview.get("audit_preview_events")
    if not isinstance(events, list):
        findings.append("audit_preview_events must be a list")
        return findings
    event_ids = {item.get("event_id") for item in events if isinstance(item, dict)}
    missing_events = REQUIRED_AUDIT_EVENTS - event_ids
    if missing_events:
        findings.append(f"audit_preview_events missing {', '.join(sorted(missing_events))}")
    for index_num, event in enumerate(events):
        if not isinstance(event, dict):
            findings.append(f"audit_preview_events[{index_num}] must be an object")
            continue
        if event.get("status") != "pass":
            findings.append(f"audit_preview_events[{index_num}].status must be pass")
        if event.get("external_action") is not False:
            findings.append(f"audit_preview_events[{index_num}].external_action must be false")
    return findings


def _validate_forbidden_outputs(preview: dict[str, Any], source: dict[str, Any]) -> list[str]:
    outputs = preview.get("forbidden_outputs")
    if not isinstance(outputs, list) or not all(isinstance(item, str) for item in outputs):
        return ["forbidden_outputs must be a string list"]
    findings: list[str] = []
    if outputs != source.get("forbidden_outputs"):
        findings.append("forbidden_outputs must match source readiness index")
    missing_required = REQUIRED_FORBIDDEN_OUTPUTS - set(outputs)
    if missing_required:
        findings.append(f"forbidden_outputs missing required outputs: {sorted(missing_required)}")
    return findings


def _validate_handoff(preview: dict[str, Any]) -> list[str]:
    handoff = preview.get("taskset_handoff")
    if not isinstance(handoff, dict):
        return ["taskset_handoff must be an object"]
    findings: list[str] = []
    if handoff.get("task_163_audit_preview_ready") is not True:
        findings.append("taskset_handoff.task_163_audit_preview_ready must be true")
    if handoff.get("taskset_local_scope_complete_when_task_closes") is not True:
        findings.append("taskset_handoff.taskset_local_scope_complete_when_task_closes must be true")
    if handoff.get("next_task_candidate") != "TASK-164":
        findings.append("taskset_handoff.next_task_candidate must be TASK-164")
    for key in (
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
    ):
        if handoff.get(key) is not False:
            findings.append(f"taskset_handoff.{key} must be false")
    required_for = _string_list(handoff.get("owner_r3_required_for"))
    for item in (
        "actual Owner/R3 packet submission",
        "actual Owner review start",
        "refresh execution",
        "archive write or deletion",
        "rollback execution",
        "approval evidence collection",
        "legal/tax/securities reliance",
        "final PDF/PPTX export",
        "public URL/upload/SNS/customer/CRM/payment/platform/API use",
    ):
        if item not in required_for:
            findings.append(f"taskset_handoff.owner_r3_required_for missing {item}")
    return findings


def _validate_verification(preview: dict[str, Any]) -> list[str]:
    verification = preview.get("verification")
    if not isinstance(verification, dict):
        return ["verification must be an object"]
    expected = {
        "local_gate": "python scripts/promotion_source_trace_audit_preview_readiness_index_audit_preview_gate.py --check",
        "focused_tests": "python -m pytest tests/unit/test_promotion_source_trace_audit_preview_readiness_index_audit_preview_gate.py -q",
        "source_gate": "python scripts/promotion_source_trace_audit_preview_readiness_index_gate.py --check",
    }
    return [f"verification.{key} must be {value}" for key, value in expected.items() if verification.get(key) != value]


def _safe_repo_path(repo_root: Path, rel_path: str) -> Path:
    if not rel_path:
        raise ValueError("empty path")
    path = (repo_root / rel_path).resolve()
    root = repo_root.resolve()
    if path != root and root not in path.parents:
        raise ValueError(f"path escapes repo root: {rel_path}")
    return path


def _by_decision(value: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(value, list):
        return {}
    return {item.get("decision_type"): item for item in value if isinstance(item, dict)}


def _find_forbidden_keys(value: Any, prefix: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}"
            if key.lower() in FORBIDDEN_KEY_NAMES:
                findings.append(path)
            findings.extend(_find_forbidden_keys(child, path))
    elif isinstance(value, list):
        for index_num, child in enumerate(value):
            findings.extend(_find_forbidden_keys(child, f"{prefix}[{index_num}]"))
    return findings


def _find_live_true_keys(value: Any, prefix: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}"
            if key.lower() in LIVE_TRUE_KEYS and child is True:
                findings.append(path)
            findings.extend(_find_live_true_keys(child, path))
    elif isinstance(value, list):
        for index_num, child in enumerate(value):
            findings.extend(_find_live_true_keys(child, f"{prefix}[{index_num}]"))
    return findings


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", type=Path, default=DEFAULT_PREVIEW)
    parser.add_argument("--check", action="store_true", help="validate and return non-zero on findings")
    args = parser.parse_args()

    preview = load_preview(args.preview)
    findings = validate_preview(preview)
    if findings:
        print("promotion source trace audit preview readiness index audit preview gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"promotion source trace audit preview readiness index audit preview gate: PASS ({args.preview})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
