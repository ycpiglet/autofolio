"""Validate the TASK-164 source-trace audit-preview readiness-index audit-preview source trace.

This gate validates local source-trace metadata only. It rejects actual
Owner/R3 submission, review start, evidence refresh execution, archive writes,
rollback execution, archive deletion, approval evidence collection, approval
records, signatures, public approval, final exports, customer/CRM/payment
action, external account action, platform calls, secrets, final advice, and
drift from the TASK-163 source audit preview.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRACE = (
    REPO_ROOT
    / "agents"
    / "project"
    / "PROMOTION-SOURCE-TRACE-AUDIT-PREVIEW-READINESS-INDEX-AUDIT-PREVIEW-SOURCE-TRACE.json"
)
SOURCE_AUDIT_PREVIEW_REL = (
    "agents/project/PROMOTION-SOURCE-TRACE-AUDIT-PREVIEW-READINESS-INDEX-AUDIT-PREVIEW.json"
)
SOURCE_AUDIT_PREVIEW_PATH = REPO_ROOT / SOURCE_AUDIT_PREVIEW_REL
EXPECTED_SCHEMA = (
    "autofolio.promotion-source-trace-audit-preview-readiness-index-audit-preview-source-trace/v1"
)
EXPECTED_ID = "promotion_source_trace_audit_preview_readiness_index_audit_preview_source_trace"
EXPECTED_STATUS = (
    "local_source_trace_audit_preview_readiness_index_audit_preview_source_trace_not_actual_submission"
)


def _load_source_gate() -> Any:
    path = REPO_ROOT / "scripts" / "promotion_source_trace_audit_preview_readiness_index_audit_preview_gate.py"
    spec = importlib.util.spec_from_file_location("source_trace_readiness_index_audit_preview_gate", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import source audit preview gate from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SOURCE_GATE = _load_source_gate()
SOURCE_AUDIT_PREVIEW_ID = SOURCE_GATE.EXPECTED_ID
SOURCE_AUDIT_PREVIEW_STATUS = SOURCE_GATE.EXPECTED_STATUS
REQUIRED_DECISION_TYPES = set(SOURCE_GATE.REQUIRED_DECISION_TYPES)
REQUIRED_BLOCKED_SCAN_KEYS = set(SOURCE_GATE.REQUIRED_BLOCKED_SCAN_KEYS)
REQUIRED_FORBIDDEN_OUTPUTS = set(SOURCE_GATE.REQUIRED_FORBIDDEN_OUTPUTS)

TRACE_CHAIN = [
    {
        "trace_record_id": "source-trace-readiness-index-audit-preview",
        "artifact_type": "readiness_index_audit_preview",
        "source_id": SOURCE_AUDIT_PREVIEW_ID,
        "path": SOURCE_AUDIT_PREVIEW_REL,
        "status": SOURCE_AUDIT_PREVIEW_STATUS,
        "next_path": "agents/project/PROMOTION-SOURCE-TRACE-AUDIT-PREVIEW-READINESS-INDEX.json",
        "relationship": "audits_source_trace_audit_preview_readiness_index",
    },
    {
        "trace_record_id": "source-trace-readiness-index",
        "artifact_type": "readiness_index",
        "source_id": "promotion_source_trace_audit_preview_readiness_index",
        "path": "agents/project/PROMOTION-SOURCE-TRACE-AUDIT-PREVIEW-READINESS-INDEX.json",
        "status": "local_source_trace_audit_preview_readiness_index_not_actual_submission",
        "next_path": (
            "agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-REVIEW-SUBMISSION-"
            "HANDOFF-PACKET-CANDIDATE-ARCHIVE-ROLLBACK-MANIFEST-AUDIT-PREVIEW-READINESS-INDEX-AUDIT-PREVIEW-"
            "SOURCE-TRACE-AUDIT-PREVIEW.json"
        ),
        "relationship": "indexes_source_trace_audit_preview_readiness",
    },
    {
        "trace_record_id": "source-trace-upstream-audit-preview",
        "artifact_type": "source_trace_audit_preview",
        "source_id": (
            "promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_"
            "archive_rollback_manifest_audit_preview_readiness_index_audit_preview_source_trace_audit_preview"
        ),
        "path": (
            "agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-REVIEW-SUBMISSION-"
            "HANDOFF-PACKET-CANDIDATE-ARCHIVE-ROLLBACK-MANIFEST-AUDIT-PREVIEW-READINESS-INDEX-AUDIT-PREVIEW-"
            "SOURCE-TRACE-AUDIT-PREVIEW.json"
        ),
        "status": (
            "local_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_"
            "readiness_index_audit_preview_source_trace_audit_preview_not_actual_submission"
        ),
        "next_path": (
            "agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-REVIEW-SUBMISSION-"
            "HANDOFF-PACKET-CANDIDATE-ARCHIVE-ROLLBACK-MANIFEST-AUDIT-PREVIEW-READINESS-INDEX-AUDIT-PREVIEW-"
            "SOURCE-TRACE.json"
        ),
        "relationship": "audits_source_trace",
    },
    {
        "trace_record_id": "source-trace-upstream-source-trace",
        "artifact_type": "source_trace",
        "source_id": (
            "promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_"
            "archive_rollback_manifest_audit_preview_readiness_index_audit_preview_source_trace"
        ),
        "path": (
            "agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-REVIEW-SUBMISSION-"
            "HANDOFF-PACKET-CANDIDATE-ARCHIVE-ROLLBACK-MANIFEST-AUDIT-PREVIEW-READINESS-INDEX-AUDIT-PREVIEW-"
            "SOURCE-TRACE.json"
        ),
        "status": (
            "local_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_"
            "readiness_index_audit_preview_source_trace_not_actual_submission"
        ),
        "next_path": None,
        "relationship": None,
    },
]

REQUIRED_BOUNDARIES = {
    "local_source_trace_audit_preview_readiness_index_audit_preview_source_trace_only",
    "source_trace_not_submission",
    "source_trace_not_approval",
    "source_trace_not_publication_clearance",
    "source_trace_not_external_archive",
    "source_audit_preview_not_submission",
    "source_audit_preview_not_approval",
    "source_audit_preview_not_publication_clearance",
    "source_readiness_index_not_submission",
    "source_readiness_index_not_approval",
    "source_readiness_index_not_publication_clearance",
    "source_trace_audit_preview_not_submission",
    "source_trace_audit_preview_not_approval",
    "source_trace_audit_preview_not_publication_clearance",
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

REQUIRED_SUMMARY_COUNTS = {
    "chain_records": len(TRACE_CHAIN),
    "chain_records_with_hash_recorded": len(TRACE_CHAIN),
    "chain_records_with_existing_files": len(TRACE_CHAIN),
    "chain_records_with_non_action_status": len(TRACE_CHAIN),
    "upstream_source_links_verified": len(TRACE_CHAIN) - 1,
    "source_audit_preview_records": 9,
    "source_readiness_records": 9,
    "source_owner_r3_blocker_records": 9,
    "source_local_next_action_records": 9,
    "source_blocked_action_scan_items": 13,
    "source_forbidden_outputs": 26,
    "source_trace_links": len(TRACE_CHAIN),
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

REQUIRED_NON_ACTION_FLAGS = {
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
    "source_trace_is_submission",
    "source_trace_is_approval",
    "source_trace_is_public_clearance",
    "source_trace_external_archive",
    "source_trace_mutated_source",
    "action_permitted_now",
}

REQUIRED_TRACE_STEPS = {
    "record_source_audit_preview_hash",
    "verify_source_audit_preview_gate",
    "trace_source_readiness_index",
    "trace_source_trace_audit_preview",
    "trace_upstream_source_trace",
    "verify_owner_r3_blocker_preservation",
    "verify_blocked_action_scan",
    "register_source_trace_audit_preview_handoff",
}

REQUIRED_TRACE_EVENTS = {
    "source_trace_generated",
    "source_audit_preview_hash_recorded",
    "source_audit_preview_gate_verified",
    "source_readiness_index_traced",
    "source_trace_audit_preview_traced",
    "upstream_source_trace_traced",
    "blocked_action_scan_preserved",
    "source_trace_audit_preview_handoff_registered",
}

FORBIDDEN_KEY_NAMES = set(SOURCE_GATE.FORBIDDEN_KEY_NAMES) | {
    "source_trace_submission_id",
    "source_trace_approval_id",
    "source_trace_public_url",
    "source_trace_archive_id",
}

LIVE_TRUE_KEYS = set(SOURCE_GATE.LIVE_TRUE_KEYS) | REQUIRED_NON_ACTION_FLAGS | {
    "source_mutated",
    "external_validation_performed",
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


def load_trace(path: Path = DEFAULT_TRACE) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("promotion source readiness-index audit-preview source trace root must be an object")
    return data


def validate_trace(trace: dict[str, Any], repo_root: Path = REPO_ROOT) -> list[str]:
    source = SOURCE_GATE.load_preview(SOURCE_AUDIT_PREVIEW_PATH)
    findings: list[str] = []

    source_findings = SOURCE_GATE.validate_preview(source, repo_root)
    if source_findings:
        findings.append(f"source audit preview gate must pass: {source_findings}")

    if trace.get("$schema") != EXPECTED_SCHEMA:
        findings.append(f"$schema must be {EXPECTED_SCHEMA}")
    if trace.get("id") != EXPECTED_ID:
        findings.append(f"id must be {EXPECTED_ID}")
    if trace.get("status") != EXPECTED_STATUS:
        findings.append(f"status must be {EXPECTED_STATUS}")
    if trace.get("owner") != "Doc Steward":
        findings.append("owner must be Doc Steward")
    if trace.get("related_taskset") != "TASKSET-MARKETING-SOURCE-TRACE-AUDIT-PREVIEW-READINESS-INDEX-AUDIT-PREVIEW-SOURCE-TRACE":
        findings.append("related_taskset must be TASKSET-MARKETING-SOURCE-TRACE-AUDIT-PREVIEW-READINESS-INDEX-AUDIT-PREVIEW-SOURCE-TRACE")
    related_tasks = _string_list(trace.get("related_tasks"))
    for task_id in ("TASK-160", "TASK-161", "TASK-162", "TASK-163", "TASK-164"):
        if task_id not in related_tasks:
            findings.append(f"related_tasks missing {task_id}")

    findings.extend(_validate_boundaries(trace))
    findings.extend(_validate_sources(trace, repo_root, source))
    findings.extend(_validate_markdown(trace, repo_root))
    findings.extend(_validate_summary(trace, source))
    findings.extend(_validate_chain(trace, repo_root))
    findings.extend(_validate_coverage(trace, source))
    findings.extend(_validate_non_action_flags(trace))
    findings.extend(_validate_owner_r3_blocker_trace(trace, source))
    findings.extend(_validate_blocked_scan(trace, source))
    findings.extend(_validate_steps_and_events(trace))
    findings.extend(_validate_forbidden_outputs(trace, source))
    findings.extend(_validate_handoff(trace))
    findings.extend(_validate_verification(trace))

    forbidden_keys = _find_forbidden_keys(trace)
    if forbidden_keys:
        findings.append(
            "forbidden source-trace/submission/approval/signature/export/customer/secret/final-advice key names "
            f"present: {forbidden_keys}"
        )
    live_true_paths = _find_live_true_keys(trace)
    if live_true_paths:
        findings.append(
            "source-trace/archive/rollback/review-start/submission/refresh/approval/signature/public/export/"
            f"customer/payment/platform/final-advice/live flags must not be true: {live_true_paths}"
        )
    return findings


def _validate_boundaries(trace: dict[str, Any]) -> list[str]:
    boundaries = trace.get("boundaries")
    if not isinstance(boundaries, dict):
        return ["boundaries must be an object"]
    return [f"boundaries.{key} must be true" for key in REQUIRED_BOUNDARIES if boundaries.get(key) is not True]


def _validate_sources(trace: dict[str, Any], repo_root: Path, source: dict[str, Any]) -> list[str]:
    inputs = trace.get("source_inputs")
    if not isinstance(inputs, list):
        return ["source_inputs must be a list"]
    findings: list[str] = []
    source_ids = {item.get("id") for item in inputs if isinstance(item, dict)}
    if SOURCE_AUDIT_PREVIEW_ID not in source_ids:
        findings.append(f"source_inputs missing ids: {[SOURCE_AUDIT_PREVIEW_ID]}")
    for index_num, item in enumerate(inputs):
        if not isinstance(item, dict):
            findings.append(f"source_inputs[{index_num}] must be an object")
            continue
        if item.get("id") == SOURCE_AUDIT_PREVIEW_ID and item.get("path") != SOURCE_AUDIT_PREVIEW_REL:
            findings.append(f"source_inputs[{index_num}].path for {SOURCE_AUDIT_PREVIEW_ID} must be {SOURCE_AUDIT_PREVIEW_REL}")
        try:
            path = _safe_repo_path(repo_root, str(item.get("path", "")))
        except ValueError as exc:
            findings.append(f"source_inputs[{index_num}].path invalid: {exc}")
            continue
        if not path.exists():
            findings.append(f"source_inputs[{index_num}].path missing: {item.get('path')}")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if item.get("sha256") != digest:
            findings.append(f"source_inputs[{index_num}].sha256 mismatch for {item.get('path')}: expected {digest}")
        if item.get("source_status") != source.get("status"):
            findings.append(f"source_inputs[{index_num}].source_status must match source audit preview status")
        if item.get("relationship") != "traces_source_trace_audit_preview_readiness_index_audit_preview":
            findings.append(f"source_inputs[{index_num}].relationship must be traces_source_trace_audit_preview_readiness_index_audit_preview")
    return findings


def _validate_markdown(trace: dict[str, Any], repo_root: Path) -> list[str]:
    markdown = trace.get("companion_markdown")
    if not isinstance(markdown, str):
        return ["companion_markdown must be a string"]
    try:
        path = _safe_repo_path(repo_root, markdown)
    except ValueError as exc:
        return [f"companion_markdown invalid: {exc}"]
    if not path.exists():
        return [f"companion_markdown missing: {markdown}"]
    return []


def _validate_summary(trace: dict[str, Any], source: dict[str, Any]) -> list[str]:
    summary = trace.get("source_trace_summary")
    if not isinstance(summary, dict):
        return ["source_trace_summary must be an object"]
    findings = [
        f"source_trace_summary.{key} must be {expected}"
        for key, expected in REQUIRED_SUMMARY_COUNTS.items()
        if summary.get(key) != expected
    ]
    if summary.get("source_root") != SOURCE_AUDIT_PREVIEW_ID:
        findings.append(f"source_trace_summary.source_root must be {SOURCE_AUDIT_PREVIEW_ID}")
    if summary.get("source_root_status") != source.get("status"):
        findings.append("source_trace_summary.source_root_status must match source audit preview status")
    if summary.get("source_gate_result") != "pass":
        findings.append("source_trace_summary.source_gate_result must be pass")
    if summary.get("gate_result") != "pass":
        findings.append("source_trace_summary.gate_result must be pass")
    if summary.get("stops_at_task_160_source_trace") is not True:
        findings.append("source_trace_summary.stops_at_task_160_source_trace must be true")

    source_summary = source.get("audit_preview_summary")
    if not isinstance(source_summary, dict):
        findings.append("source audit_preview_summary must be an object")
        return findings
    checks = {
        "source_audit_preview_records": len(source.get("audit_preview_records", [])),
        "source_readiness_records": source_summary.get("source_readiness_records"),
        "source_owner_r3_blocker_records": len(source.get("owner_r3_blocker_partition_audit", [])),
        "source_local_next_action_records": len(source.get("local_next_action_partition_audit", [])),
        "source_blocked_action_scan_items": len(source.get("blocked_action_scan", {})),
        "source_forbidden_outputs": len(source.get("forbidden_outputs", [])),
    }
    findings.extend(
        f"source_trace_summary.{key} must be {expected}"
        for key, expected in checks.items()
        if summary.get(key) != expected
    )
    return findings


def _validate_chain(trace: dict[str, Any], repo_root: Path) -> list[str]:
    chain = trace.get("source_chain")
    if not isinstance(chain, list):
        return ["source_chain must be a list"]
    findings: list[str] = []
    if len(chain) != len(TRACE_CHAIN):
        findings.append(f"source_chain must contain {len(TRACE_CHAIN)} records")
    for index_num, expected in enumerate(TRACE_CHAIN):
        if index_num >= len(chain):
            continue
        record = chain[index_num]
        if not isinstance(record, dict):
            findings.append(f"source_chain[{index_num}] must be an object")
            continue
        sequence = index_num + 1
        for key in ("trace_record_id", "artifact_type", "source_id", "path", "status"):
            if record.get(key) != expected[key]:
                findings.append(f"source_chain[{index_num}].{key} must be {expected[key]}")
        if record.get("sequence") != sequence:
            findings.append(f"source_chain[{index_num}].sequence must be {sequence}")
        if record.get("expected_source_input_next_path") != expected["next_path"]:
            findings.append(f"source_chain[{index_num}].expected_source_input_next_path must be {expected['next_path']}")
        if record.get("expected_source_input_relationship") != expected["relationship"]:
            findings.append(
                f"source_chain[{index_num}].expected_source_input_relationship must be {expected['relationship']}"
            )
        for key in ("source_mutated", "external_validation_performed", "action_permitted_now"):
            if record.get(key) is not False:
                findings.append(f"source_chain[{index_num}].{key} must be false")
        try:
            path = _safe_repo_path(repo_root, expected["path"])
        except ValueError as exc:
            findings.append(f"source_chain[{index_num}].path invalid: {exc}")
            continue
        if not path.exists():
            findings.append(f"source_chain[{index_num}].path missing: {expected['path']}")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if record.get("sha256") != digest:
            findings.append(f"source_chain[{index_num}].sha256 mismatch for {expected['path']}: expected {digest}")
        artifact = _load_json(path)
        artifact_status = artifact.get("status")
        if artifact_status is not None and artifact_status != expected["status"]:
            findings.append(f"source_chain[{index_num}].status must match artifact status {artifact_status}")
        artifact_id = artifact.get("id")
        if artifact_id is not None and artifact_id != expected["source_id"]:
            findings.append(f"source_chain[{index_num}].source_id must match artifact id {artifact_id}")
        if expected["next_path"] is not None:
            findings.extend(_validate_chain_source_input(index_num, artifact, expected))
    return findings


def _validate_chain_source_input(index_num: int, artifact: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    source_inputs = artifact.get("source_inputs")
    if not isinstance(source_inputs, list):
        return [f"source_chain[{index_num}] artifact source_inputs must be a list"]
    matches = [
        item
        for item in source_inputs
        if isinstance(item, dict)
        and item.get("path") == expected["next_path"]
        and item.get("relationship") == expected["relationship"]
    ]
    if not matches:
        return [
            "source_chain[{}] artifact source_inputs must include next path {} with relationship {}".format(
                index_num,
                expected["next_path"],
                expected["relationship"],
            )
        ]
    return []


def _validate_coverage(trace: dict[str, Any], source: dict[str, Any]) -> list[str]:
    coverage = trace.get("source_trace_coverage")
    if not isinstance(coverage, dict):
        return ["source_trace_coverage must be an object"]
    source_summary = source.get("audit_preview_summary")
    if not isinstance(source_summary, dict):
        return ["source audit_preview_summary must be an object"]
    checks = {
        "chain_length": len(TRACE_CHAIN),
        "upstream_source_links_verified": len(TRACE_CHAIN) - 1,
        "source_audit_preview_records": len(source.get("audit_preview_records", [])),
        "source_readiness_records": source_summary.get("source_readiness_records"),
        "source_owner_r3_blocker_records": len(source.get("owner_r3_blocker_partition_audit", [])),
        "source_local_next_action_records": len(source.get("local_next_action_partition_audit", [])),
        "source_blocked_action_scan_items": len(source.get("blocked_action_scan", {})),
        "source_forbidden_outputs": len(source.get("forbidden_outputs", [])),
    }
    findings = [
        f"source_trace_coverage.{key} must be {expected}"
        for key, expected in checks.items()
        if coverage.get(key) != expected
    ]
    for key in (
        "source_root_gate_reused",
        "source_hash_recorded",
        "source_reference_coverage_passed",
        "source_chain_hashes_recorded",
        "source_chain_links_followed",
        "owner_r3_blockers_preserved",
        "stops_at_task_160_source_trace",
    ):
        if coverage.get(key) is not True:
            findings.append(f"source_trace_coverage.{key} must be true")
    for key in ("source_mutated", "external_validation_performed"):
        if coverage.get(key) is not False:
            findings.append(f"source_trace_coverage.{key} must be false")
    return findings


def _validate_non_action_flags(trace: dict[str, Any]) -> list[str]:
    flags = trace.get("non_action_flags")
    if not isinstance(flags, dict):
        return ["non_action_flags must be an object"]
    return [f"non_action_flags.{key} must be false" for key in REQUIRED_NON_ACTION_FLAGS if flags.get(key) is not False]


def _validate_owner_r3_blocker_trace(trace: dict[str, Any], source: dict[str, Any]) -> list[str]:
    records = trace.get("owner_r3_blocker_trace")
    if not isinstance(records, list):
        return ["owner_r3_blocker_trace must be a list"]
    findings: list[str] = []
    by_decision = {item.get("decision_type"): item for item in records if isinstance(item, dict)}
    source_by_decision = _by_decision(source.get("audit_preview_records"))
    missing = REQUIRED_DECISION_TYPES - set(by_decision)
    extra = set(by_decision) - REQUIRED_DECISION_TYPES
    if missing:
        findings.append(f"owner_r3_blocker_trace missing decision types: {sorted(missing)}")
    if extra:
        findings.append(f"owner_r3_blocker_trace unexpected decision types: {sorted(extra)}")
    for decision_type, item in sorted(by_decision.items()):
        source_item = source_by_decision.get(decision_type, {})
        if item.get("source_audit_preview_record_id") != source_item.get("audit_preview_record_id"):
            findings.append(f"owner_r3_blocker_trace[{decision_type}].source_audit_preview_record_id must match source")
        if item.get("source_readiness_record_id") != source_item.get("source_readiness_record_id"):
            findings.append(f"owner_r3_blocker_trace[{decision_type}].source_readiness_record_id must match source")
        if item.get("source_origin_readiness_record_id") != source_item.get("source_origin_readiness_record_id"):
            findings.append(f"owner_r3_blocker_trace[{decision_type}].source_origin_readiness_record_id must match source")
        if item.get("blocker_trace_status") != "pass":
            findings.append(f"owner_r3_blocker_trace[{decision_type}].blocker_trace_status must be pass")
        for key in (
            "owner_r3_required_before_submission",
            "owner_r3_required_before_public_use",
            "professional_review_required_before_reliance",
        ):
            if item.get(key) is not True:
                findings.append(f"owner_r3_blocker_trace[{decision_type}].{key} must be true")
        for key in ("public_use_approved", "action_permitted_now"):
            if item.get(key) is not False:
                findings.append(f"owner_r3_blocker_trace[{decision_type}].{key} must be false")
    return findings


def _validate_blocked_scan(trace: dict[str, Any], source: dict[str, Any]) -> list[str]:
    scan = trace.get("blocked_action_scan")
    if scan != source.get("blocked_action_scan"):
        return ["blocked_action_scan must match source audit preview"]
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


def _validate_steps_and_events(trace: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    steps = trace.get("source_trace_steps")
    if not isinstance(steps, list):
        return ["source_trace_steps must be a list"]
    step_ids = {item.get("step_id") for item in steps if isinstance(item, dict)}
    missing_steps = REQUIRED_TRACE_STEPS - step_ids
    if missing_steps:
        findings.append(f"source_trace_steps missing {', '.join(sorted(missing_steps))}")
    for index_num, step in enumerate(steps):
        if not isinstance(step, dict):
            findings.append(f"source_trace_steps[{index_num}] must be an object")
            continue
        if step.get("status") != "pass":
            findings.append(f"source_trace_steps[{index_num}].status must be pass")
        for key in (
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
        ):
            if step.get(key) is not False:
                findings.append(f"source_trace_steps[{index_num}].{key} must be false")

    events = trace.get("source_trace_events")
    if not isinstance(events, list):
        findings.append("source_trace_events must be a list")
        return findings
    event_ids = {item.get("event_id") for item in events if isinstance(item, dict)}
    missing_events = REQUIRED_TRACE_EVENTS - event_ids
    if missing_events:
        findings.append(f"source_trace_events missing {', '.join(sorted(missing_events))}")
    for index_num, event in enumerate(events):
        if not isinstance(event, dict):
            findings.append(f"source_trace_events[{index_num}] must be an object")
            continue
        if event.get("status") != "pass":
            findings.append(f"source_trace_events[{index_num}].status must be pass")
        if event.get("external_action") is not False:
            findings.append(f"source_trace_events[{index_num}].external_action must be false")
    return findings


def _validate_forbidden_outputs(trace: dict[str, Any], source: dict[str, Any]) -> list[str]:
    outputs = trace.get("forbidden_outputs")
    if not isinstance(outputs, list) or not all(isinstance(item, str) for item in outputs):
        return ["forbidden_outputs must be a string list"]
    findings: list[str] = []
    missing_source_outputs = set(source.get("forbidden_outputs", [])) - set(outputs)
    if missing_source_outputs:
        findings.append(f"forbidden_outputs missing source outputs: {sorted(missing_source_outputs)}")
    missing_required = REQUIRED_FORBIDDEN_OUTPUTS - set(outputs)
    if missing_required:
        findings.append(f"forbidden_outputs missing required outputs: {sorted(missing_required)}")
    return findings


def _validate_handoff(trace: dict[str, Any]) -> list[str]:
    handoff = trace.get("taskset_handoff")
    if not isinstance(handoff, dict):
        return ["taskset_handoff must be an object"]
    findings: list[str] = []
    if handoff.get("task_164_source_trace_ready") is not True:
        findings.append("taskset_handoff.task_164_source_trace_ready must be true")
    if handoff.get("taskset_local_scope_complete_when_task_closes") is not True:
        findings.append("taskset_handoff.taskset_local_scope_complete_when_task_closes must be true")
    if handoff.get("next_task_candidate") != "TASK-165":
        findings.append("taskset_handoff.next_task_candidate must be TASK-165")
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
        "final PDF/PPTX export",
        "public URL/upload/SNS/customer/CRM/payment/platform/API use",
    ):
        if item not in required_for:
            findings.append(f"taskset_handoff.owner_r3_required_for missing {item}")
    return findings


def _validate_verification(trace: dict[str, Any]) -> list[str]:
    verification = trace.get("verification")
    if not isinstance(verification, dict):
        return ["verification must be an object"]
    expected = {
        "local_gate": "python scripts/promotion_source_trace_audit_preview_readiness_index_audit_preview_source_trace_gate.py --check",
        "focused_tests": "python -m pytest tests/unit/test_promotion_source_trace_audit_preview_readiness_index_audit_preview_source_trace_gate.py -q",
        "source_gate": "python scripts/promotion_source_trace_audit_preview_readiness_index_audit_preview_gate.py --check",
    }
    return [f"verification.{key} must be {value}" for key, value in expected.items() if verification.get(key) != value]


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"{path} root must be an object")
    return data


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
    parser.add_argument("--trace", type=Path, default=DEFAULT_TRACE)
    parser.add_argument("--check", action="store_true", help="validate and return non-zero on findings")
    args = parser.parse_args()

    trace = load_trace(args.trace)
    findings = validate_trace(trace)
    if findings:
        print("promotion source trace audit preview readiness index audit preview source trace gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"promotion source trace audit preview readiness index audit preview source trace gate: PASS ({args.trace})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
