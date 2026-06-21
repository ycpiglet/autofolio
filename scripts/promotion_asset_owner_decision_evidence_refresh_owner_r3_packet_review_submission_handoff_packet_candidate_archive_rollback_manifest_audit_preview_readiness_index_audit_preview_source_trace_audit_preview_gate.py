"""Validate the TASK-161 source-trace audit preview.

This gate validates local audit-preview metadata only. It rejects actual
Owner/R3 review submission, review start, evidence refresh execution, archive
writes, rollback execution, archive deletion, approval records, signatures,
approval evidence collection, public approval, final exports, customer/CRM/
payment action, external account action, platform calls, secrets, final advice,
and drift from the TASK-160 source trace.
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
    / "PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-REVIEW-SUBMISSION-HANDOFF-PACKET-CANDIDATE-ARCHIVE-ROLLBACK-MANIFEST-AUDIT-PREVIEW-READINESS-INDEX-AUDIT-PREVIEW-SOURCE-TRACE-AUDIT-PREVIEW.json"
)
SOURCE_TRACE_PATH = (
    REPO_ROOT
    / "agents"
    / "project"
    / "PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-REVIEW-SUBMISSION-HANDOFF-PACKET-CANDIDATE-ARCHIVE-ROLLBACK-MANIFEST-AUDIT-PREVIEW-READINESS-INDEX-AUDIT-PREVIEW-SOURCE-TRACE.json"
)
SOURCE_TRACE_REL = (
    "agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-REVIEW-SUBMISSION-HANDOFF-"
    "PACKET-CANDIDATE-ARCHIVE-ROLLBACK-MANIFEST-AUDIT-PREVIEW-READINESS-INDEX-AUDIT-PREVIEW-SOURCE-TRACE.json"
)
EXPECTED_SCHEMA = (
    "autofolio.promotion-asset-owner-decision-evidence-refresh-owner-r3-packet-review-submission-handoff-packet-"
    "candidate-archive-rollback-manifest-audit-preview-readiness-index-audit-preview-source-trace-audit-preview/v1"
)
EXPECTED_STATUS = (
    "local_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_"
    "readiness_index_audit_preview_source_trace_audit_preview_not_actual_submission"
)


def _load_source_gate() -> Any:
    path = (
        REPO_ROOT
        / "scripts"
        / "promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_readiness_index_audit_preview_source_trace_gate.py"
    )
    spec = importlib.util.spec_from_file_location("readiness_index_source_trace_gate", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import source trace gate from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SOURCE_GATE = _load_source_gate()
SOURCE_TRACE_ID = f"{SOURCE_GATE.SOURCE_AUDIT_PREVIEW_ID}_source_trace"
SOURCE_TRACE_STATUS = SOURCE_GATE.EXPECTED_STATUS
EXPECTED_ID = f"{SOURCE_TRACE_ID}_audit_preview"

REQUIRED_DECISION_TYPES = set(SOURCE_GATE.REQUIRED_DECISION_TYPES)
REQUIRED_BLOCKED_SCAN_KEYS = set(SOURCE_GATE.REQUIRED_BLOCKED_SCAN_KEYS)
REQUIRED_FORBIDDEN_OUTPUTS = set(SOURCE_GATE.REQUIRED_FORBIDDEN_OUTPUTS)
REQUIRED_BOUNDARIES = set(SOURCE_GATE.REQUIRED_BOUNDARIES) | {
    "local_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_readiness_index_audit_preview_source_trace_audit_preview_only",
    "source_trace_audit_preview_not_submission",
    "source_trace_audit_preview_not_approval",
    "source_trace_audit_preview_not_publication_clearance",
    "source_trace_audit_preview_not_external_archive",
}
FORBIDDEN_KEY_NAMES = set(SOURCE_GATE.FORBIDDEN_KEY_NAMES) | {
    "source_trace_audit_submission_id",
    "source_trace_audit_approval_id",
    "source_trace_audit_public_url",
    "source_trace_audit_archive_id",
}
LIVE_TRUE_KEYS = set(SOURCE_GATE.LIVE_TRUE_KEYS) | {
    "source_trace_audit_preview_is_submission",
    "source_trace_audit_preview_is_approval",
    "source_trace_audit_preview_is_public_clearance",
    "source_trace_audit_preview_external_archive",
    "audit_preview_is_submission",
    "audit_preview_is_approval",
    "audit_preview_is_public_clearance",
    "source_trace_mutated",
    "source_trace_mutated_source",
    "source_mutated",
    "external_validation_performed",
    "action_permitted_now",
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
    "source_trace_audit_preview_is_submission",
    "source_trace_audit_preview_is_approval",
    "source_trace_audit_preview_is_public_clearance",
    "source_trace_audit_preview_external_archive",
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
    "source_trace_mutated_source",
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
    "record_source_trace_hash",
    "verify_source_trace_gate",
    "audit_source_chain_records",
    "audit_owner_r3_blocker_trace",
    "audit_source_trace_reference_coverage",
    "audit_blocked_action_scan",
    "audit_forbidden_outputs",
    "register_source_trace_audit_preview_handoff",
}
REQUIRED_AUDIT_EVENTS = {
    "source_trace_audit_preview_generated",
    "source_trace_hash_recorded",
    "source_trace_gate_verified",
    "source_chain_records_audited",
    "owner_r3_blocker_trace_audited",
    "blocked_action_scan_reused",
    "forbidden_outputs_reused",
    "source_trace_audit_preview_handoff_registered",
}


def load_preview(path: Path = DEFAULT_PREVIEW) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("promotion asset source trace audit preview root must be an object")
    return data


def validate_preview(preview: dict[str, Any], repo_root: Path = REPO_ROOT) -> list[str]:
    source = SOURCE_GATE.load_trace(SOURCE_TRACE_PATH)
    findings: list[str] = []

    source_findings = SOURCE_GATE.validate_trace(source, repo_root)
    if source_findings:
        findings.append(f"source trace gate must pass: {source_findings}")

    if preview.get("$schema") != EXPECTED_SCHEMA:
        findings.append("unexpected or missing promotion asset source trace audit preview schema")
    if preview.get("id") != EXPECTED_ID:
        findings.append(f"id must be {EXPECTED_ID}")
    if preview.get("status") != EXPECTED_STATUS:
        findings.append(f"status must be {EXPECTED_STATUS}")

    findings.extend(_validate_boundaries(preview))
    findings.extend(_validate_sources(preview, repo_root, source))
    findings.extend(_validate_markdown(preview, repo_root))
    findings.extend(_validate_summary(preview, source))
    findings.extend(_validate_reference_coverage(preview, source))
    findings.extend(_validate_non_action_flags(preview))
    findings.extend(_validate_source_chain_audit(preview, source))
    findings.extend(_validate_audit_preview_records(preview, source))
    findings.extend(_validate_blocker_trace_audit(preview, source))
    findings.extend(_validate_blocked_scan(preview, source))
    findings.extend(_validate_steps_and_events(preview))
    findings.extend(_validate_forbidden_outputs(preview, source))
    findings.extend(_validate_handoff(preview))
    findings.extend(_validate_verification(preview))

    forbidden_keys = _find_forbidden_keys(preview)
    if forbidden_keys:
        findings.append(
            "forbidden source-trace-audit/submission/approval/signature/export/customer/secret/final-advice key names "
            f"present: {forbidden_keys}"
        )
    live_true_paths = _find_live_true_keys(preview)
    if live_true_paths:
        findings.append(
            "source-trace-audit/archive/rollback/review-start/submission/refresh/approval/signature/public/"
            f"export/customer/payment/platform/final-advice/live flags must not be true: {live_true_paths}"
        )
    return findings


def _validate_boundaries(preview: dict[str, Any]) -> list[str]:
    boundaries = preview.get("boundaries")
    if not isinstance(boundaries, dict):
        return ["boundaries must be an object"]
    return [f"boundaries.{key} must be true" for key in sorted(REQUIRED_BOUNDARIES) if boundaries.get(key) is not True]


def _validate_sources(preview: dict[str, Any], repo_root: Path, source: dict[str, Any]) -> list[str]:
    sources = preview.get("source_inputs")
    if not isinstance(sources, list) or len(sources) != 1 or not isinstance(sources[0], dict):
        return ["source_inputs must contain exactly one source trace object"]
    item = sources[0]
    findings: list[str] = []
    checks = {
        "id": SOURCE_TRACE_ID,
        "path": SOURCE_TRACE_REL,
        "relationship": "audits_source_trace",
        "source_status": SOURCE_TRACE_STATUS,
    }
    findings.extend(f"source_inputs[0].{key} must be {value}" for key, value in checks.items() if item.get(key) != value)
    try:
        path = _safe_repo_path(repo_root, SOURCE_TRACE_REL)
    except ValueError as exc:
        findings.append(f"source_inputs[0].path invalid: {exc}")
        return findings
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if item.get("sha256") != digest:
        findings.append(f"source_inputs[0].sha256 mismatch for {SOURCE_TRACE_REL}: expected {digest}")
    if source.get("id") != SOURCE_TRACE_ID:
        findings.append("source trace id must match source_inputs[0].id")
    if source.get("status") != SOURCE_TRACE_STATUS:
        findings.append("source trace status must match source_inputs[0].source_status")
    return findings


def _validate_markdown(preview: dict[str, Any], repo_root: Path) -> list[str]:
    markdown = preview.get("companion_markdown")
    if not isinstance(markdown, str):
        return ["companion_markdown must be a string"]
    try:
        path = _safe_repo_path(repo_root, markdown)
    except ValueError as exc:
        return [f"companion_markdown invalid: {exc}"]
    if not path.exists():
        return [f"companion_markdown missing: {markdown}"]
    return []


def _validate_summary(preview: dict[str, Any], source: dict[str, Any]) -> list[str]:
    summary = preview.get("source_trace_audit_preview_summary")
    if not isinstance(summary, dict):
        return ["source_trace_audit_preview_summary must be an object"]
    source_summary = source.get("source_trace_summary")
    if not isinstance(source_summary, dict):
        return ["source source_trace_summary must be an object"]

    decisions = len(source.get("owner_r3_blocker_trace", []))
    chain_records = len(source.get("source_chain", []))
    checks = {
        "source_trace": SOURCE_TRACE_ID,
        "source_trace_status": source.get("status"),
        "source_trace_gate_result": "pass",
        "gate_result": "pass",
        "source_trace_chain_records": chain_records,
        "source_trace_chain_records_with_hash_recorded": source_summary.get("chain_records_with_hash_recorded"),
        "source_trace_chain_records_with_existing_files": source_summary.get("chain_records_with_existing_files"),
        "source_trace_chain_records_with_non_action_status": source_summary.get("chain_records_with_non_action_status"),
        "source_trace_upstream_source_links_verified": source_summary.get("upstream_source_links_verified"),
        "source_trace_owner_r3_blocker_records": decisions,
        "source_trace_blocked_action_scan_items": len(source.get("blocked_action_scan", {})),
        "source_trace_forbidden_outputs": len(source.get("forbidden_outputs", [])),
        "source_chain_audit_records": chain_records,
        "audit_preview_records": decisions,
        "owner_r3_blocker_trace_audit_records": decisions,
        "blocked_action_scan_items": len(source.get("blocked_action_scan", {})),
        "forbidden_outputs": len(source.get("forbidden_outputs", [])),
        "records_requiring_owner_r3": decisions,
        "audit_preview_records_passed": decisions,
        "records_with_source_hash_recorded": decisions,
        "source_chain_records_passed": chain_records,
        "records_with_non_submission_status": decisions,
        "records_with_non_approval_status": decisions,
        "records_with_public_use_blocked": decisions,
        "ready_for_owner_r3_submission_records": 0,
        "ready_for_public_use_records": 0,
    }
    zero_counts = {
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
    }
    findings = [f"source_trace_audit_preview_summary.{key} must be {value}" for key, value in checks.items() if summary.get(key) != value]
    findings.extend(f"source_trace_audit_preview_summary.{key} must be 0" for key in sorted(zero_counts) if summary.get(key) != 0)
    return findings


def _validate_reference_coverage(preview: dict[str, Any], source: dict[str, Any]) -> list[str]:
    coverage = preview.get("source_trace_reference_coverage")
    if not isinstance(coverage, dict):
        return ["source_trace_reference_coverage must be an object"]
    checks = {
        "chain_length": len(source.get("source_chain", [])),
        "source_trace_boundaries": len(source.get("boundaries", {})),
        "upstream_source_links_verified": source.get("source_trace_summary", {}).get("upstream_source_links_verified"),
        "source_owner_r3_blocker_records": len(source.get("owner_r3_blocker_trace", [])),
        "source_blocked_action_scan_items": len(source.get("blocked_action_scan", {})),
        "source_forbidden_outputs": len(source.get("forbidden_outputs", [])),
    }
    findings = [f"source_trace_reference_coverage.{key} must be {value}" for key, value in checks.items() if coverage.get(key) != value]
    for key in (
        "source_trace_gate_reused",
        "source_hash_recorded",
        "source_reference_coverage_passed",
        "source_chain_hashes_recorded",
        "source_chain_links_followed",
        "owner_r3_blockers_preserved",
        "blocked_action_scan_reused",
        "forbidden_outputs_reused",
    ):
        if coverage.get(key) is not True:
            findings.append(f"source_trace_reference_coverage.{key} must be true")
    for key in ("source_mutated", "external_validation_performed"):
        if coverage.get(key) is not False:
            findings.append(f"source_trace_reference_coverage.{key} must be false")
    return findings


def _validate_non_action_flags(preview: dict[str, Any]) -> list[str]:
    flags = preview.get("non_action_flags")
    if not isinstance(flags, dict):
        return ["non_action_flags must be an object"]
    return [f"non_action_flags.{key} must be false" for key in sorted(REQUIRED_FALSE_FLAGS) if flags.get(key) is not False]


def _validate_source_chain_audit(preview: dict[str, Any], source: dict[str, Any]) -> list[str]:
    records = preview.get("source_chain_audit")
    source_chain = source.get("source_chain")
    if not isinstance(records, list):
        return ["source_chain_audit must be a list"]
    if not isinstance(source_chain, list):
        return ["source source_chain must be a list"]
    findings: list[str] = []
    if len(records) != len(source_chain):
        findings.append(f"source_chain_audit must contain {len(source_chain)} records")
    by_id = {item.get("trace_record_id"): item for item in records if isinstance(item, dict)}
    source_by_id = {item.get("trace_record_id"): item for item in source_chain if isinstance(item, dict)}
    missing = set(source_by_id) - set(by_id)
    extra = set(by_id) - set(source_by_id)
    if missing:
        findings.append(f"source_chain_audit missing trace records: {sorted(missing)}")
    if extra:
        findings.append(f"source_chain_audit unexpected trace records: {sorted(extra)}")
    for trace_id, source_item in sorted(source_by_id.items()):
        item = by_id.get(trace_id)
        if not isinstance(item, dict):
            continue
        for key in (
            "sequence",
            "artifact_type",
            "source_id",
            "path",
            "sha256",
            "status",
            "expected_source_input_next_path",
            "expected_source_input_relationship",
        ):
            if item.get(key) != source_item.get(key):
                findings.append(f"source_chain_audit[{trace_id}].{key} must match source trace")
        if item.get("audit_status") != "pass":
            findings.append(f"source_chain_audit[{trace_id}].audit_status must be pass")
        for key in ("source_chain_record_preserved", "source_hash_recorded"):
            if item.get(key) is not True:
                findings.append(f"source_chain_audit[{trace_id}].{key} must be true")
        for key in ("source_mutated", "external_validation_performed", "action_permitted_now"):
            if item.get(key) is not False:
                findings.append(f"source_chain_audit[{trace_id}].{key} must be false")
    return findings


def _validate_audit_preview_records(preview: dict[str, Any], source: dict[str, Any]) -> list[str]:
    records = preview.get("audit_preview_records")
    if not isinstance(records, list):
        return ["audit_preview_records must be a list"]
    findings: list[str] = []
    by_decision = {item.get("decision_type"): item for item in records if isinstance(item, dict)}
    source_by_decision = _by_decision(source.get("owner_r3_blocker_trace"))
    missing = REQUIRED_DECISION_TYPES - set(by_decision)
    extra = set(by_decision) - REQUIRED_DECISION_TYPES
    if missing:
        findings.append(f"audit_preview_records missing decision types: {sorted(missing)}")
    if extra:
        findings.append(f"audit_preview_records unexpected decision types: {sorted(extra)}")
    for decision_type, item in sorted(by_decision.items()):
        source_item = source_by_decision.get(decision_type, {})
        if item.get("source_audit_preview_record_id") != source_item.get("source_audit_preview_record_id"):
            findings.append(f"audit_preview_records[{decision_type}].source_audit_preview_record_id must match source")
        if item.get("source_readiness_record_id") != source_item.get("source_readiness_record_id"):
            findings.append(f"audit_preview_records[{decision_type}].source_readiness_record_id must match source")
        if item.get("source_owner_r3_blocker_trace_status") != source_item.get("blocker_trace_status"):
            findings.append(f"audit_preview_records[{decision_type}].source_owner_r3_blocker_trace_status must match source")
        if item.get("audit_preview_status") != "pass":
            findings.append(f"audit_preview_records[{decision_type}].audit_preview_status must be pass")
        if item.get("source_trace_hash_recorded") is not True:
            findings.append(f"audit_preview_records[{decision_type}].source_trace_hash_recorded must be true")
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


def _validate_blocker_trace_audit(preview: dict[str, Any], source: dict[str, Any]) -> list[str]:
    records = preview.get("owner_r3_blocker_trace_audit")
    if not isinstance(records, list):
        return ["owner_r3_blocker_trace_audit must be a list"]
    findings: list[str] = []
    by_decision = {item.get("decision_type"): item for item in records if isinstance(item, dict)}
    source_by_decision = _by_decision(source.get("owner_r3_blocker_trace"))
    missing = REQUIRED_DECISION_TYPES - set(by_decision)
    extra = set(by_decision) - REQUIRED_DECISION_TYPES
    if missing:
        findings.append(f"owner_r3_blocker_trace_audit missing decision types: {sorted(missing)}")
    if extra:
        findings.append(f"owner_r3_blocker_trace_audit unexpected decision types: {sorted(extra)}")
    for decision_type, item in sorted(by_decision.items()):
        source_item = source_by_decision.get(decision_type, {})
        for key in ("source_audit_preview_record_id", "source_readiness_record_id"):
            if item.get(key) != source_item.get(key):
                findings.append(f"owner_r3_blocker_trace_audit[{decision_type}].{key} must match source")
        if item.get("audit_status") != "pass":
            findings.append(f"owner_r3_blocker_trace_audit[{decision_type}].audit_status must be pass")
        if item.get("blocker_trace_preserved") is not True:
            findings.append(f"owner_r3_blocker_trace_audit[{decision_type}].blocker_trace_preserved must be true")
        for key in (
            "owner_r3_required_before_submission",
            "owner_r3_required_before_public_use",
            "professional_review_required_before_reliance",
        ):
            if item.get(key) is not True:
                findings.append(f"owner_r3_blocker_trace_audit[{decision_type}].{key} must be true")
        for key in ("public_use_approved", "action_permitted_now"):
            if item.get(key) is not False:
                findings.append(f"owner_r3_blocker_trace_audit[{decision_type}].{key} must be false")
    return findings


def _validate_blocked_scan(preview: dict[str, Any], source: dict[str, Any]) -> list[str]:
    scan = preview.get("blocked_action_scan")
    if scan != source.get("blocked_action_scan"):
        return ["blocked_action_scan must match source trace"]
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
        findings.append("forbidden_outputs must match source trace")
    missing_required = REQUIRED_FORBIDDEN_OUTPUTS - set(outputs)
    if missing_required:
        findings.append(f"forbidden_outputs missing required outputs: {sorted(missing_required)}")
    return findings


def _validate_handoff(preview: dict[str, Any]) -> list[str]:
    handoff = preview.get("taskset_handoff")
    if not isinstance(handoff, dict):
        return ["taskset_handoff must be an object"]
    findings: list[str] = []
    if handoff.get("task_161_audit_preview_ready") is not True:
        findings.append("taskset_handoff.task_161_audit_preview_ready must be true")
    if handoff.get("taskset_local_scope_complete_when_task_closes") is not True:
        findings.append("taskset_handoff.taskset_local_scope_complete_when_task_closes must be true")
    if handoff.get("next_task_candidate") != "TASK-162":
        findings.append("taskset_handoff.next_task_candidate must be TASK-162")
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
        "local_gate": "python scripts/promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_readiness_index_audit_preview_source_trace_audit_preview_gate.py --check",
        "focused_tests": "python -m pytest tests/unit/test_promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_readiness_index_audit_preview_source_trace_audit_preview_gate.py -q",
        "source_gate": "python scripts/promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_readiness_index_audit_preview_source_trace_gate.py --check",
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
        print("promotion asset Owner/R3 source trace audit preview gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"promotion asset Owner/R3 source trace audit preview gate: PASS ({args.preview})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
