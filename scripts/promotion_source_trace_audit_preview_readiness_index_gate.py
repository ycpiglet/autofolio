"""Validate the TASK-162 source-trace audit-preview readiness index.

This gate validates local readiness metadata only. It rejects actual Owner/R3
submission, review start, evidence refresh execution, archive writes, rollback
execution, archive deletion, approval evidence collection, approval records,
signatures, public approval, final exports, customer/CRM/payment action,
external account action, platform calls, secrets, final advice, and drift from
the TASK-161 source-trace audit preview.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX = REPO_ROOT / "agents" / "project" / "PROMOTION-SOURCE-TRACE-AUDIT-PREVIEW-READINESS-INDEX.json"
SOURCE_PREVIEW_REL = (
    "agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-REVIEW-SUBMISSION-HANDOFF-"
    "PACKET-CANDIDATE-ARCHIVE-ROLLBACK-MANIFEST-AUDIT-PREVIEW-READINESS-INDEX-AUDIT-PREVIEW-SOURCE-TRACE-"
    "AUDIT-PREVIEW.json"
)
SOURCE_PREVIEW_PATH = REPO_ROOT / SOURCE_PREVIEW_REL
EXPECTED_SCHEMA = "autofolio.promotion-source-trace-audit-preview-readiness-index/v1"
EXPECTED_ID = "promotion_source_trace_audit_preview_readiness_index"
EXPECTED_STATUS = "local_source_trace_audit_preview_readiness_index_not_actual_submission"


def _load_source_gate() -> Any:
    path = (
        REPO_ROOT
        / "scripts"
        / "promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_readiness_index_audit_preview_source_trace_audit_preview_gate.py"
    )
    spec = importlib.util.spec_from_file_location("source_trace_audit_preview_gate", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import source trace audit preview gate from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SOURCE_GATE = _load_source_gate()
SOURCE_PREVIEW_ID = SOURCE_GATE.EXPECTED_ID
SOURCE_PREVIEW_STATUS = SOURCE_GATE.EXPECTED_STATUS
REQUIRED_DECISION_TYPES = set(SOURCE_GATE.REQUIRED_DECISION_TYPES)
REQUIRED_BLOCKED_SCAN_KEYS = set(SOURCE_GATE.REQUIRED_BLOCKED_SCAN_KEYS)
REQUIRED_FORBIDDEN_OUTPUTS = set(SOURCE_GATE.REQUIRED_FORBIDDEN_OUTPUTS)
REQUIRED_BOUNDARIES = set(SOURCE_GATE.REQUIRED_BOUNDARIES) | {
    "local_source_trace_audit_preview_readiness_index_only",
    "readiness_index_not_submission",
    "readiness_index_not_approval",
    "readiness_index_not_publication_clearance",
    "readiness_index_not_external_archive",
    "source_trace_audit_preview_not_submission",
    "source_trace_audit_preview_not_approval",
    "source_trace_audit_preview_not_publication_clearance",
    "source_trace_audit_preview_not_external_archive",
}
FORBIDDEN_KEY_NAMES = set(SOURCE_GATE.FORBIDDEN_KEY_NAMES) | {
    "readiness_index_submission_id",
    "readiness_index_approval_id",
    "readiness_index_public_url",
    "readiness_index_archive_id",
}
LIVE_TRUE_KEYS = set(SOURCE_GATE.LIVE_TRUE_KEYS) | {
    "readiness_index_is_submission",
    "readiness_index_is_approval",
    "readiness_index_is_public_clearance",
    "readiness_index_external_archive",
    "source_trace_audit_preview_mutated_source",
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
    "readiness_index_is_submission",
    "readiness_index_is_approval",
    "readiness_index_is_public_clearance",
    "readiness_index_external_archive",
    "source_trace_audit_preview_mutated_source",
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
READINESS_RECORD_FALSE_FLAGS = {
    "readiness_index_is_submission",
    "readiness_index_is_approval",
    "readiness_index_is_public_clearance",
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
REQUIRED_READINESS_STEPS = {
    "record_source_trace_audit_preview_hash",
    "verify_source_trace_audit_preview_gate",
    "index_readiness_records",
    "partition_owner_r3_blockers",
    "partition_local_next_actions",
    "reuse_blocked_action_scan",
    "reuse_forbidden_outputs",
    "register_readiness_index_handoff",
}
REQUIRED_READINESS_EVENTS = {
    "readiness_index_generated",
    "source_trace_audit_preview_hash_recorded",
    "source_trace_audit_preview_gate_verified",
    "readiness_records_indexed",
    "owner_r3_blockers_partitioned",
    "local_next_actions_partitioned",
    "blocked_action_scan_reused",
    "readiness_index_handoff_registered",
}


def load_index(path: Path = DEFAULT_INDEX) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("promotion source trace audit preview readiness index root must be an object")
    return data


def validate_index(index: dict[str, Any], repo_root: Path = REPO_ROOT) -> list[str]:
    findings: list[str] = []
    source = SOURCE_GATE.load_preview(SOURCE_PREVIEW_PATH)
    source_findings = SOURCE_GATE.validate_preview(source, repo_root)
    findings.extend([f"source trace audit preview invalid: {finding}" for finding in source_findings])

    if index.get("$schema") != EXPECTED_SCHEMA:
        findings.append(f"$schema must be {EXPECTED_SCHEMA}")
    if index.get("id") != EXPECTED_ID:
        findings.append(f"id must be {EXPECTED_ID}")
    if index.get("status") != EXPECTED_STATUS:
        findings.append(f"status must be {EXPECTED_STATUS}")
    if index.get("owner") != "Compliance Officer":
        findings.append("owner must be Compliance Officer")
    if index.get("related_taskset") != "TASKSET-MARKETING-SOURCE-TRACE-AUDIT-PREVIEW-READINESS-INDEX":
        findings.append("related_taskset must be TASKSET-MARKETING-SOURCE-TRACE-AUDIT-PREVIEW-READINESS-INDEX")
    related_tasks = _string_list(index.get("related_tasks"))
    for task_id in ("TASK-161", "TASK-162"):
        if task_id not in related_tasks:
            findings.append(f"related_tasks missing {task_id}")

    findings.extend(_validate_boundaries(index))
    findings.extend(_validate_sources(index, repo_root, source))
    findings.extend(_validate_markdown(index, repo_root))
    findings.extend(_validate_summary(index, source))
    findings.extend(_validate_reference_coverage(index, source))
    findings.extend(_validate_non_action_flags(index))
    findings.extend(_validate_readiness_records(index, source))
    findings.extend(_validate_owner_r3_partition(index, source))
    findings.extend(_validate_local_next_actions(index, source))
    findings.extend(_validate_blocked_scan(index, source))
    findings.extend(_validate_steps_and_events(index))
    findings.extend(_validate_forbidden_outputs(index, source))
    findings.extend(_validate_handoff(index))
    findings.extend(_validate_verification(index))

    forbidden_keys = _find_forbidden_keys(index)
    if forbidden_keys:
        findings.append(f"forbidden key names present: {', '.join(forbidden_keys)}")
    live_true_keys = _find_live_true_keys(index)
    if live_true_keys:
        findings.append(
            "source-trace-readiness-index/archive/rollback/review-start/submission/refresh/approval/"
            f"signature/public/customer/payment/secret live-action flags must stay false: {', '.join(live_true_keys)}"
        )
    return findings


def _validate_boundaries(index: dict[str, Any]) -> list[str]:
    boundaries = index.get("boundaries")
    if not isinstance(boundaries, dict):
        return ["boundaries must be an object"]
    findings: list[str] = []
    for boundary in sorted(REQUIRED_BOUNDARIES):
        if boundaries.get(boundary) is not True:
            findings.append(f"boundaries.{boundary} must be true")
    return findings


def _validate_sources(index: dict[str, Any], repo_root: Path, source: dict[str, Any]) -> list[str]:
    sources = index.get("source_inputs")
    if not isinstance(sources, list) or len(sources) != 1 or not isinstance(sources[0], dict):
        return ["source_inputs must contain exactly one object"]
    item = sources[0]
    findings: list[str] = []
    if item.get("id") != SOURCE_PREVIEW_ID:
        findings.append(f"source_inputs[0].id must be {SOURCE_PREVIEW_ID}")
    if item.get("path") != SOURCE_PREVIEW_REL:
        findings.append(f"source_inputs[0].path must be {SOURCE_PREVIEW_REL}")
    if item.get("relationship") != "indexes_source_trace_audit_preview_readiness":
        findings.append("source_inputs[0].relationship must be indexes_source_trace_audit_preview_readiness")
    if item.get("source_status") != SOURCE_PREVIEW_STATUS:
        findings.append(f"source_inputs[0].source_status must be {SOURCE_PREVIEW_STATUS}")
    if item.get("source_gate_result") != "pass":
        findings.append("source_inputs[0].source_gate_result must be pass")
    source_path = _safe_repo_path(repo_root, SOURCE_PREVIEW_REL)
    if not source_path.exists():
        findings.append(f"source input path does not exist: {SOURCE_PREVIEW_REL}")
    else:
        digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
        if item.get("sha256") != digest:
            findings.append(f"source_inputs[0].sha256 mismatch for {SOURCE_PREVIEW_REL}")
    if source.get("id") != SOURCE_PREVIEW_ID:
        findings.append(f"source preview id must be {SOURCE_PREVIEW_ID}")
    return findings


def _validate_markdown(index: dict[str, Any], repo_root: Path) -> list[str]:
    rel = index.get("companion_markdown")
    if not isinstance(rel, str) or not rel:
        return ["companion_markdown must be a non-empty string"]
    path = _safe_repo_path(repo_root, rel)
    if not path.exists():
        return [f"companion_markdown does not exist: {rel}"]
    return []


def _validate_summary(index: dict[str, Any], source: dict[str, Any]) -> list[str]:
    summary = index.get("readiness_summary")
    if not isinstance(summary, dict):
        return ["readiness_summary must be an object"]
    source_summary = source.get("source_trace_audit_preview_summary", {})
    decisions = len(source.get("audit_preview_records", []))
    expected = {
        "source_trace_audit_preview": SOURCE_PREVIEW_ID,
        "source_status": SOURCE_PREVIEW_STATUS,
        "source_gate_result": "pass",
        "gate_result": "pass",
        "source_chain_audit_records": len(source.get("source_chain_audit", [])),
        "source_chain_records_with_hash_recorded": source_summary.get("source_trace_chain_records_with_hash_recorded"),
        "source_chain_records_with_existing_files": source_summary.get("source_trace_chain_records_with_existing_files"),
        "source_chain_records_with_non_action_status": source_summary.get("source_trace_chain_records_with_non_action_status"),
        "audit_preview_records": decisions,
        "owner_r3_blocker_trace_audit_records": len(source.get("owner_r3_blocker_trace_audit", [])),
        "blocked_action_scan_items": len(source.get("blocked_action_scan", {})),
        "forbidden_outputs": len(source.get("forbidden_outputs", [])),
        "source_boundaries": len(source.get("boundaries", {})),
        "readiness_records": decisions,
        "owner_r3_blocker_partition_records": decisions,
        "local_next_action_partition_records": decisions,
        "source_reference_records": 1,
        "records_requiring_owner_r3": decisions,
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
    return [f"readiness_summary.{key} must be {value}" for key, value in expected.items() if summary.get(key) != value]


def _validate_reference_coverage(index: dict[str, Any], source: dict[str, Any]) -> list[str]:
    coverage = index.get("source_reference_coverage")
    if not isinstance(coverage, dict):
        return ["source_reference_coverage must be an object"]
    findings: list[str] = []
    for key in (
        "source_trace_audit_preview_gate_reused",
        "source_trace_audit_preview_hash_recorded",
        "source_reference_coverage_passed",
        "source_chain_hashes_preserved",
        "owner_r3_blockers_preserved",
        "blocked_action_scan_reused",
        "forbidden_outputs_reused",
    ):
        if coverage.get(key) is not True:
            findings.append(f"source_reference_coverage.{key} must be true")
    for key in ("source_trace_audit_preview_mutated_source", "external_validation_performed"):
        if coverage.get(key) is not False:
            findings.append(f"source_reference_coverage.{key} must be false")
    expected_counts = {
        "source_chain_audit_records": len(source.get("source_chain_audit", [])),
        "audit_preview_records": len(source.get("audit_preview_records", [])),
        "owner_r3_blocker_trace_audit_records": len(source.get("owner_r3_blocker_trace_audit", [])),
        "blocked_action_scan_items": len(source.get("blocked_action_scan", {})),
        "forbidden_outputs": len(source.get("forbidden_outputs", [])),
        "source_boundaries": len(source.get("boundaries", {})),
    }
    for key, value in expected_counts.items():
        if coverage.get(key) != value:
            findings.append(f"source_reference_coverage.{key} must be {value}")
    return findings


def _validate_non_action_flags(index: dict[str, Any]) -> list[str]:
    flags = index.get("non_action_flags")
    if not isinstance(flags, dict):
        return ["non_action_flags must be an object"]
    return [f"non_action_flags.{key} must be false" for key in sorted(REQUIRED_FALSE_FLAGS) if flags.get(key) is not False]


def _validate_readiness_records(index: dict[str, Any], source: dict[str, Any]) -> list[str]:
    records = index.get("readiness_records")
    if not isinstance(records, list):
        return ["readiness_records must be a list"]
    findings: list[str] = []
    by_decision = _by_decision(records)
    source_by_decision = _by_decision(source.get("audit_preview_records"))
    missing = REQUIRED_DECISION_TYPES - set(by_decision)
    extra = set(by_decision) - REQUIRED_DECISION_TYPES
    if missing:
        findings.append(f"readiness_records missing decision types: {sorted(missing)}")
    if extra:
        findings.append(f"readiness_records unexpected decision types: {sorted(extra)}")
    for decision_type, item in sorted(by_decision.items()):
        source_item = source_by_decision.get(decision_type, {})
        if item.get("source_audit_preview_record_id") != source_item.get("audit_preview_record_id"):
            findings.append(f"readiness_records[{decision_type}].source_audit_preview_record_id must match source")
        if item.get("source_readiness_record_id") != source_item.get("source_readiness_record_id"):
            findings.append(f"readiness_records[{decision_type}].source_readiness_record_id must match source")
        if item.get("source_owner_r3_blocker_trace_status") != source_item.get("source_owner_r3_blocker_trace_status"):
            findings.append(f"readiness_records[{decision_type}].source_owner_r3_blocker_trace_status must match source")
        if item.get("readiness_status") != "blocked_until_owner_r3":
            findings.append(f"readiness_records[{decision_type}].readiness_status must be blocked_until_owner_r3")
        for key in ("source_trace_audit_preview_hash_recorded", "source_trace_audit_preview_status_preserved"):
            if item.get(key) is not True:
                findings.append(f"readiness_records[{decision_type}].{key} must be true")
        for key in (
            "owner_r3_required_before_submission",
            "owner_r3_required_before_public_use",
            "professional_review_required_before_reliance",
        ):
            if item.get(key) is not True:
                findings.append(f"readiness_records[{decision_type}].{key} must be true")
        if item.get("local_next_action") != "preserve_readiness_index_for_future_owner_r3_packet_review":
            findings.append(f"readiness_records[{decision_type}].local_next_action must preserve readiness index")
        for key in sorted(READINESS_RECORD_FALSE_FLAGS):
            if item.get(key) is not False:
                findings.append(f"readiness_records[{decision_type}].{key} must be false")
    return findings


def _validate_owner_r3_partition(index: dict[str, Any], source: dict[str, Any]) -> list[str]:
    records = index.get("owner_r3_blocker_partition")
    if not isinstance(records, list):
        return ["owner_r3_blocker_partition must be a list"]
    findings: list[str] = []
    by_decision = _by_decision(records)
    source_by_decision = _by_decision(source.get("audit_preview_records"))
    missing = REQUIRED_DECISION_TYPES - set(by_decision)
    extra = set(by_decision) - REQUIRED_DECISION_TYPES
    if missing:
        findings.append(f"owner_r3_blocker_partition missing decision types: {sorted(missing)}")
    if extra:
        findings.append(f"owner_r3_blocker_partition unexpected decision types: {sorted(extra)}")
    for decision_type, item in sorted(by_decision.items()):
        source_item = source_by_decision.get(decision_type, {})
        if item.get("source_audit_preview_record_id") != source_item.get("audit_preview_record_id"):
            findings.append(f"owner_r3_blocker_partition[{decision_type}].source_audit_preview_record_id must match source")
        if item.get("source_readiness_record_id") != source_item.get("source_readiness_record_id"):
            findings.append(f"owner_r3_blocker_partition[{decision_type}].source_readiness_record_id must match source")
        if item.get("blocker_status") != "blocked_until_owner_r3":
            findings.append(f"owner_r3_blocker_partition[{decision_type}].blocker_status must be blocked_until_owner_r3")
        for key in (
            "owner_r3_required_before_submission",
            "owner_r3_required_before_public_use",
            "professional_review_required_before_reliance",
        ):
            if item.get(key) is not True:
                findings.append(f"owner_r3_blocker_partition[{decision_type}].{key} must be true")
        for key in ("public_use_approved", "action_permitted_now"):
            if item.get(key) is not False:
                findings.append(f"owner_r3_blocker_partition[{decision_type}].{key} must be false")
    return findings


def _validate_local_next_actions(index: dict[str, Any], source: dict[str, Any]) -> list[str]:
    records = index.get("local_next_action_partition")
    if not isinstance(records, list):
        return ["local_next_action_partition must be a list"]
    findings: list[str] = []
    by_decision = _by_decision(records)
    source_decisions = set(_by_decision(source.get("audit_preview_records")))
    missing = REQUIRED_DECISION_TYPES - set(by_decision)
    extra = set(by_decision) - source_decisions
    if missing:
        findings.append(f"local_next_action_partition missing decision types: {sorted(missing)}")
    if extra:
        findings.append(f"local_next_action_partition unexpected decision types: {sorted(extra)}")
    for decision_type, item in sorted(by_decision.items()):
        if item.get("local_next_action") != "preserve_readiness_index_for_future_owner_r3_packet_review":
            findings.append(f"local_next_action_partition[{decision_type}].local_next_action must preserve readiness index")
        if item.get("owner_r3_required_before_action") is not True:
            findings.append(f"local_next_action_partition[{decision_type}].owner_r3_required_before_action must be true")
        for key in ("external_action", "public_action", "customer_contact", "crm_payment", "final_export", "action_permitted_now"):
            if item.get(key) is not False:
                findings.append(f"local_next_action_partition[{decision_type}].{key} must be false")
    return findings


def _validate_blocked_scan(index: dict[str, Any], source: dict[str, Any]) -> list[str]:
    scan = index.get("blocked_action_scan")
    if scan != source.get("blocked_action_scan"):
        return ["blocked_action_scan must match source trace audit preview"]
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


def _validate_steps_and_events(index: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    steps = index.get("readiness_steps")
    if not isinstance(steps, list):
        return ["readiness_steps must be a list"]
    step_ids = {item.get("step_id") for item in steps if isinstance(item, dict)}
    missing_steps = REQUIRED_READINESS_STEPS - step_ids
    if missing_steps:
        findings.append(f"readiness_steps missing {', '.join(sorted(missing_steps))}")
    for index_num, step in enumerate(steps):
        if not isinstance(step, dict):
            findings.append(f"readiness_steps[{index_num}] must be an object")
            continue
        if step.get("status") != "pass":
            findings.append(f"readiness_steps[{index_num}].status must be pass")
        for key in sorted(STEP_FALSE_FLAGS):
            if step.get(key) is not False:
                findings.append(f"readiness_steps[{index_num}].{key} must be false")

    events = index.get("readiness_events")
    if not isinstance(events, list):
        findings.append("readiness_events must be a list")
        return findings
    event_ids = {item.get("event_id") for item in events if isinstance(item, dict)}
    missing_events = REQUIRED_READINESS_EVENTS - event_ids
    if missing_events:
        findings.append(f"readiness_events missing {', '.join(sorted(missing_events))}")
    for index_num, event in enumerate(events):
        if not isinstance(event, dict):
            findings.append(f"readiness_events[{index_num}] must be an object")
            continue
        if event.get("status") != "pass":
            findings.append(f"readiness_events[{index_num}].status must be pass")
        if event.get("external_action") is not False:
            findings.append(f"readiness_events[{index_num}].external_action must be false")
    return findings


def _validate_forbidden_outputs(index: dict[str, Any], source: dict[str, Any]) -> list[str]:
    outputs = index.get("forbidden_outputs")
    if not isinstance(outputs, list) or not all(isinstance(item, str) for item in outputs):
        return ["forbidden_outputs must be a string list"]
    findings: list[str] = []
    if outputs != source.get("forbidden_outputs"):
        findings.append("forbidden_outputs must match source trace audit preview")
    missing_required = REQUIRED_FORBIDDEN_OUTPUTS - set(outputs)
    if missing_required:
        findings.append(f"forbidden_outputs missing required outputs: {sorted(missing_required)}")
    return findings


def _validate_handoff(index: dict[str, Any]) -> list[str]:
    handoff = index.get("taskset_handoff")
    if not isinstance(handoff, dict):
        return ["taskset_handoff must be an object"]
    findings: list[str] = []
    if handoff.get("task_162_readiness_index_ready") is not True:
        findings.append("taskset_handoff.task_162_readiness_index_ready must be true")
    if handoff.get("taskset_local_scope_complete_when_task_closes") is not True:
        findings.append("taskset_handoff.taskset_local_scope_complete_when_task_closes must be true")
    if handoff.get("next_task_candidate") != "TASK-163":
        findings.append("taskset_handoff.next_task_candidate must be TASK-163")
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


def _validate_verification(index: dict[str, Any]) -> list[str]:
    verification = index.get("verification")
    if not isinstance(verification, dict):
        return ["verification must be an object"]
    expected = {
        "local_gate": "python scripts/promotion_source_trace_audit_preview_readiness_index_gate.py --check",
        "focused_tests": "python -m pytest tests/unit/test_promotion_source_trace_audit_preview_readiness_index_gate.py -q",
        "source_gate": "python scripts/promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_readiness_index_audit_preview_source_trace_audit_preview_gate.py --check",
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
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--check", action="store_true", help="validate and return non-zero on findings")
    args = parser.parse_args()

    index = load_index(args.index)
    findings = validate_index(index)
    if findings:
        print("promotion source trace audit preview readiness index gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"promotion source trace audit preview readiness index gate: PASS ({args.index})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
