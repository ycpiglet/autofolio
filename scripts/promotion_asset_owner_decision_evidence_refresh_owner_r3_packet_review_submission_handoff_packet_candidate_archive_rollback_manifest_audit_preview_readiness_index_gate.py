"""Validate the TASK-158 archive/rollback audit-preview readiness index.

This gate validates local readiness-index metadata only. It rejects actual
Owner/R3 review submission, review start, evidence refresh execution, archive
writes, rollback execution, archive deletion, approval records, signatures,
approval evidence collection, public approval, final exports, customer/CRM/
payment action, external account action, platform calls, secrets, final advice,
and drift from the source TASK-157 audit preview.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX = (
    REPO_ROOT
    / "agents"
    / "project"
    / "PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-REVIEW-SUBMISSION-HANDOFF-PACKET-CANDIDATE-ARCHIVE-ROLLBACK-MANIFEST-AUDIT-PREVIEW-READINESS-INDEX.json"
)
SOURCE_PREVIEW_PATH = (
    REPO_ROOT
    / "agents"
    / "project"
    / "PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-REVIEW-SUBMISSION-HANDOFF-PACKET-CANDIDATE-ARCHIVE-ROLLBACK-MANIFEST-AUDIT-PREVIEW.json"
)
SOURCE_PREVIEW_ID = (
    "promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_"
    "archive_rollback_manifest_audit_preview"
)
SOURCE_PREVIEW_REL = (
    "agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-REVIEW-SUBMISSION-HANDOFF-"
    "PACKET-CANDIDATE-ARCHIVE-ROLLBACK-MANIFEST-AUDIT-PREVIEW.json"
)
SOURCE_PREVIEW_STATUS = (
    "local_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_readiness_"
    "preview_not_actual_submission"
)


def _load_source_gate() -> Any:
    path = (
        REPO_ROOT
        / "scripts"
        / "promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_gate.py"
    )
    spec = importlib.util.spec_from_file_location("archive_rollback_manifest_audit_preview_gate", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import source audit preview gate from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SOURCE_GATE = _load_source_gate()

REQUIRED_DECISION_TYPES = set(SOURCE_GATE.REQUIRED_DECISION_TYPES)
REQUIRED_BLOCKED_SCAN_KEYS = set(SOURCE_GATE.REQUIRED_BLOCKED_SCAN_KEYS)
REQUIRED_FORBIDDEN_OUTPUTS = set(SOURCE_GATE.REQUIRED_FORBIDDEN_OUTPUTS)
FORBIDDEN_KEY_NAMES = set(SOURCE_GATE.FORBIDDEN_KEY_NAMES) | {
    "readiness_submission_id",
    "readiness_approval_id",
    "readiness_public_url",
    "submission_packet_id",
}
LIVE_TRUE_KEYS = set(SOURCE_GATE.LIVE_TRUE_KEYS) | {
    "readiness_index_is_submission",
    "readiness_index_is_approval",
    "readiness_index_is_public_clearance",
    "actual_owner_r3_review_submission_allowed",
    "actual_owner_review_start_allowed",
    "actual_archive_write_allowed",
    "actual_rollback_execution_allowed",
    "actual_archive_delete_allowed",
    "actual_evidence_refresh_allowed",
    "actual_public_use_allowed",
    "final_export_allowed",
    "customer_or_payment_action_allowed",
    "source_mutated",
    "external_validation_performed",
    "public_action",
    "customer_contact",
    "crm_payment",
    "secret_handling",
}

REQUIRED_BOUNDARIES = {
    "local_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_readiness_index_only",
    "readiness_index_not_submission",
    "readiness_index_not_approval",
    "readiness_index_not_publication_clearance",
    "source_audit_preview_not_submission",
    "source_audit_preview_not_approval",
    "source_audit_preview_not_publication_clearance",
    "archive_rollback_manifest_audit_not_submission",
    "archive_rollback_manifest_audit_not_approval",
    "archive_rollback_manifest_audit_not_publication_clearance",
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
    "decision_types": 9,
    "source_coverage_records": 9,
    "readiness_records": 9,
    "owner_r3_blocker_records": 9,
    "local_next_action_records": 9,
    "blocked_action_scan_items": 13,
    "forbidden_outputs": 26,
    "source_audit_preview_boundaries": 35,
    "source_manifest_boundaries": 41,
    "records_requiring_owner_r3": 9,
    "readiness_records_blocked_until_owner_r3": 9,
    "local_only_next_actions": 9,
    "ready_for_owner_r3_submission_records": 0,
    "ready_for_public_use_records": 0,
    "actual_archive_writes": 0,
    "actual_rollback_executions": 0,
    "actual_archive_deletions": 0,
    "actual_review_started_records": 0,
    "actual_review_submissions": 0,
    "actual_refresh_executions": 0,
    "actual_owner_approval_records": 0,
    "actual_owner_signatures": 0,
    "actual_approval_evidence_records": 0,
    "actual_public_approvals": 0,
    "final_export_outputs": 0,
    "public_publication_outputs": 0,
    "customer_or_payment_outputs": 0,
    "secret_or_token_outputs": 0,
    "final_advice_outputs": 0,
    "archive_deletion_outputs": 0,
    "external_archive_outputs": 0,
    "live_action_states": 0,
}

REQUIRED_READINESS_STEPS = {
    "record_source_audit_preview_hash",
    "verify_source_audit_preview_gate",
    "index_source_coverage_records",
    "partition_owner_r3_blockers",
    "partition_local_next_actions",
    "verify_blocked_action_scan",
    "register_audit_preview_handoff",
}

REQUIRED_READINESS_EVENTS = {
    "readiness_index_generated",
    "source_audit_preview_hash_recorded",
    "source_audit_preview_gate_verified",
    "source_coverage_records_indexed",
    "owner_r3_blockers_partitioned",
    "local_next_actions_partitioned",
    "blocked_action_scan_reused",
    "readiness_index_audit_preview_handoff_registered",
}


def load_index(path: Path = DEFAULT_INDEX) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("promotion asset Owner/R3 archive/rollback audit-preview readiness index root must be an object")
    return data


def validate_index(index: dict[str, Any], repo_root: Path = REPO_ROOT) -> list[str]:
    source = _load_json(SOURCE_PREVIEW_PATH)
    findings: list[str] = []

    source_findings = SOURCE_GATE.validate_preview(source, repo_root)
    if source_findings:
        findings.append(f"source audit preview gate must pass: {source_findings}")

    if index.get("$schema") != (
        "autofolio.promotion-asset-owner-decision-evidence-refresh-owner-r3-packet-review-submission-handoff-packet-candidate-archive-rollback-manifest-audit-preview-readiness-index/v1"
    ):
        findings.append("unexpected or missing promotion asset Owner/R3 archive/rollback audit-preview readiness index schema")
    if index.get("status") != (
        "local_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_readiness_index_not_actual_submission"
    ):
        findings.append(
            "status must be local_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_readiness_index_not_actual_submission"
        )

    findings.extend(_validate_boundaries(index))
    findings.extend(_validate_sources(index, repo_root, source))
    findings.extend(_validate_markdown(index, repo_root))
    findings.extend(_validate_summary(index, source))
    findings.extend(_validate_source_reference_coverage(index, source))
    findings.extend(_validate_readiness_records(index, source))
    findings.extend(_validate_owner_r3_blockers(index))
    findings.extend(_validate_local_next_actions(index))
    findings.extend(_validate_blocked_scan(index, source))
    findings.extend(_validate_steps_and_events(index))
    findings.extend(_validate_forbidden_outputs(index, source))
    findings.extend(_validate_handoff(index))
    findings.extend(_validate_verification(index))

    forbidden_keys = _find_forbidden_keys(index)
    if forbidden_keys:
        findings.append(
            "forbidden readiness/review-submission/approval/signature/export/customer/secret/final-advice key names "
            f"present: {forbidden_keys}"
        )
    live_true_paths = _find_live_true_keys(index)
    if live_true_paths:
        findings.append(
            "readiness/archive/rollback/review-start/submission/refresh/approval/signature/public/export/customer/"
            f"payment/platform/final-advice/live flags must not be true: {live_true_paths}"
        )
    return findings


def _validate_boundaries(index: dict[str, Any]) -> list[str]:
    boundaries = index.get("boundaries")
    if not isinstance(boundaries, dict):
        return ["boundaries must be an object"]
    return [f"boundaries.{key} must be true" for key in REQUIRED_BOUNDARIES if boundaries.get(key) is not True]


def _validate_sources(index: dict[str, Any], repo_root: Path, source: dict[str, Any]) -> list[str]:
    inputs = index.get("source_inputs")
    if not isinstance(inputs, list):
        return ["source_inputs must be a list"]
    findings: list[str] = []
    source_ids = {item.get("id") for item in inputs if isinstance(item, dict)}
    if SOURCE_PREVIEW_ID not in source_ids:
        findings.append(f"source_inputs missing ids: {[SOURCE_PREVIEW_ID]}")
    for index_num, item in enumerate(inputs):
        if not isinstance(item, dict):
            findings.append(f"source_inputs[{index_num}] must be an object")
            continue
        if item.get("id") == SOURCE_PREVIEW_ID and item.get("path") != SOURCE_PREVIEW_REL:
            findings.append(f"source_inputs[{index_num}].path for {SOURCE_PREVIEW_ID} must be {SOURCE_PREVIEW_REL}")
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
        if item.get("relationship") != "indexes_source_audit_preview_readiness":
            findings.append(f"source_inputs[{index_num}].relationship must be indexes_source_audit_preview_readiness")
    return findings


def _validate_markdown(index: dict[str, Any], repo_root: Path) -> list[str]:
    markdown = index.get("companion_markdown")
    if not isinstance(markdown, str):
        return ["companion_markdown must be a string"]
    try:
        path = _safe_repo_path(repo_root, markdown)
    except ValueError as exc:
        return [f"companion_markdown invalid: {exc}"]
    if not path.exists():
        return [f"companion_markdown missing: {markdown}"]
    return []


def _validate_summary(index: dict[str, Any], source: dict[str, Any]) -> list[str]:
    summary = index.get("readiness_summary")
    if not isinstance(summary, dict):
        return ["readiness_summary must be an object"]
    findings = [
        f"readiness_summary.{key} must be {expected}"
        for key, expected in REQUIRED_SUMMARY_COUNTS.items()
        if summary.get(key) != expected
    ]
    if summary.get("source_audit_preview") != SOURCE_PREVIEW_ID:
        findings.append(f"readiness_summary.source_audit_preview must be {SOURCE_PREVIEW_ID}")
    if summary.get("source_audit_preview_status") != source.get("status"):
        findings.append("readiness_summary.source_audit_preview_status must match source audit preview status")
    if summary.get("source_gate_result") != "pass":
        findings.append("readiness_summary.source_gate_result must be pass")
    if summary.get("gate_result") != "pass":
        findings.append("readiness_summary.gate_result must be pass")

    source_summary = source.get("audit_summary")
    if not isinstance(source_summary, dict):
        findings.append("source audit_summary must be an object")
        return findings
    if summary.get("source_coverage_records") != len(source.get("coverage_records", [])):
        findings.append("readiness_summary.source_coverage_records must match source coverage_records count")
    if summary.get("blocked_action_scan_items") != len(source.get("blocked_action_scan", {})):
        findings.append("readiness_summary.blocked_action_scan_items must match source blocked_action_scan count")
    if summary.get("forbidden_outputs") != len(source.get("forbidden_outputs", [])):
        findings.append("readiness_summary.forbidden_outputs must match source forbidden_outputs count")
    if summary.get("source_audit_preview_boundaries") != len(source.get("boundaries", {})):
        findings.append("readiness_summary.source_audit_preview_boundaries must match source boundaries count")
    if summary.get("source_manifest_boundaries") != source_summary.get("source_boundaries"):
        findings.append("readiness_summary.source_manifest_boundaries must match source audit_summary.source_boundaries")
    return findings


def _validate_source_reference_coverage(index: dict[str, Any], source: dict[str, Any]) -> list[str]:
    coverage = index.get("source_reference_coverage")
    if not isinstance(coverage, dict):
        return ["source_reference_coverage must be an object"]
    source_coverage = source.get("source_reference_coverage")
    if not isinstance(source_coverage, dict):
        return ["source source_reference_coverage must be an object"]
    checks = {
        "source_preflight_state_safety_scan_count": source_coverage.get("source_preflight_state_safety_scan_count"),
        "source_queue_state_safety_scan_count": source_coverage.get("source_queue_state_safety_scan_count"),
        "source_state_reference_summary_count": source_coverage.get("source_state_reference_summary_count"),
        "source_trigger_reference_summary_count": source_coverage.get("source_trigger_reference_summary_count"),
        "source_handoff_packet_assembly_step_count": source_coverage.get("source_handoff_packet_assembly_step_count"),
        "source_manifest_assembly_step_count": source_coverage.get("source_manifest_assembly_step_count"),
    }
    findings = [f"source_reference_coverage.{key} must be {expected}" for key, expected in checks.items() if coverage.get(key) != expected]
    for key in ("source_reference_coverage_passed", "source_hash_recorded", "source_audit_preview_gate_reused"):
        if coverage.get(key) is not True:
            findings.append(f"source_reference_coverage.{key} must be true")
    for key in ("source_mutated", "external_validation_performed"):
        if coverage.get(key) is not False:
            findings.append(f"source_reference_coverage.{key} must be false")
    return findings


def _validate_readiness_records(index: dict[str, Any], source: dict[str, Any]) -> list[str]:
    records = index.get("readiness_records")
    if not isinstance(records, list):
        return ["readiness_records must be a list"]
    findings: list[str] = []
    by_decision = {item.get("decision_type"): item for item in records if isinstance(item, dict)}
    missing = REQUIRED_DECISION_TYPES - set(by_decision)
    extra = set(by_decision) - REQUIRED_DECISION_TYPES
    if missing:
        findings.append(f"readiness_records missing decision types: {sorted(missing)}")
    if extra:
        findings.append(f"readiness_records unexpected decision types: {sorted(extra)}")

    source_by_decision = _by_decision(source.get("coverage_records"))
    false_keys = {
        "readiness_index_is_submission",
        "readiness_index_is_approval",
        "readiness_index_is_public_clearance",
        "actual_archive_written",
        "actual_rollback_executed",
        "actual_archive_deleted",
        "actual_owner_review_started",
        "actual_owner_r3_review_submitted",
        "actual_refresh_executed",
        "actual_owner_approval_recorded",
        "actual_owner_signature_collected",
        "actual_approval_evidence_collected",
        "public_use_approved",
        "action_permitted_now",
    }
    for decision_type, record in sorted(by_decision.items()):
        source_record = source_by_decision.get(decision_type, {})
        if record.get("source_audit_record_id") != source_record.get("audit_record_id"):
            findings.append(f"readiness_records[{decision_type}].source_audit_record_id must be {source_record.get('audit_record_id')}")
        if record.get("source_archive_manifest_record_id") != source_record.get("source_archive_manifest_record_id"):
            findings.append(
                f"readiness_records[{decision_type}].source_archive_manifest_record_id must be {source_record.get('source_archive_manifest_record_id')}"
            )
        if record.get("source_rollback_trigger_record_id") != source_record.get("source_rollback_trigger_record_id"):
            findings.append(
                f"readiness_records[{decision_type}].source_rollback_trigger_record_id must be {source_record.get('source_rollback_trigger_record_id')}"
            )
        if record.get("source_retention_supersession_record_id") != source_record.get("source_retention_supersession_record_id"):
            findings.append(
                f"readiness_records[{decision_type}].source_retention_supersession_record_id must be {source_record.get('source_retention_supersession_record_id')}"
            )
        if record.get("source_coverage_status") != source_record.get("coverage_status"):
            findings.append(f"readiness_records[{decision_type}].source_coverage_status must match source")
        if record.get("readiness_status") != "blocked_until_owner_r3_and_professional_review_where_required":
            findings.append(f"readiness_records[{decision_type}].readiness_status must be blocked_until_owner_r3_and_professional_review_where_required")
        if record.get("local_work_allowed_now") is not True:
            findings.append(f"readiness_records[{decision_type}].local_work_allowed_now must be true")
        if record.get("local_next_action") != "maintain_local_readiness_index_only":
            findings.append(f"readiness_records[{decision_type}].local_next_action must be maintain_local_readiness_index_only")
        for key in (
            "owner_r3_required_before_submission",
            "owner_r3_required_before_public_use",
            "professional_review_required_before_reliance",
        ):
            if record.get(key) is not True:
                findings.append(f"readiness_records[{decision_type}].{key} must be true")
        for key in false_keys:
            if record.get(key) is not False:
                findings.append(f"readiness_records[{decision_type}].{key} must be false")
    return findings


def _validate_owner_r3_blockers(index: dict[str, Any]) -> list[str]:
    blockers = index.get("owner_r3_blocker_partition")
    if not isinstance(blockers, list):
        return ["owner_r3_blocker_partition must be a list"]
    findings: list[str] = []
    by_decision = {item.get("decision_type"): item for item in blockers if isinstance(item, dict)}
    missing = REQUIRED_DECISION_TYPES - set(by_decision)
    extra = set(by_decision) - REQUIRED_DECISION_TYPES
    if missing:
        findings.append(f"owner_r3_blocker_partition missing decision types: {sorted(missing)}")
    if extra:
        findings.append(f"owner_r3_blocker_partition unexpected decision types: {sorted(extra)}")
    required = {
        "actual Owner/R3 review submission",
        "actual Owner/R3 review start",
        "actual Owner approval evidence collection",
        "professional review where reliance is required",
    }
    false_keys = {
        "actual_owner_r3_review_submitted",
        "actual_owner_review_started",
        "actual_owner_approval_recorded",
        "actual_owner_signature_collected",
        "actual_approval_evidence_collected",
        "public_use_approved",
        "action_permitted_now",
    }
    for decision_type, blocker in sorted(by_decision.items()):
        if blocker.get("blocker_status") != "owner_r3_required_before_live_action":
            findings.append(f"owner_r3_blocker_partition[{decision_type}].blocker_status must be owner_r3_required_before_live_action")
        required_list = set(_string_list(blocker.get("required_before_public_action")))
        missing_required = required - required_list
        if missing_required:
            findings.append(f"owner_r3_blocker_partition[{decision_type}].required_before_public_action missing {sorted(missing_required)}")
        for key in false_keys:
            if blocker.get(key) is not False:
                findings.append(f"owner_r3_blocker_partition[{decision_type}].{key} must be false")
    return findings


def _validate_local_next_actions(index: dict[str, Any]) -> list[str]:
    actions = index.get("local_next_action_partition")
    if not isinstance(actions, list):
        return ["local_next_action_partition must be a list"]
    findings: list[str] = []
    by_decision = {item.get("decision_type"): item for item in actions if isinstance(item, dict)}
    missing = REQUIRED_DECISION_TYPES - set(by_decision)
    extra = set(by_decision) - REQUIRED_DECISION_TYPES
    if missing:
        findings.append(f"local_next_action_partition missing decision types: {sorted(missing)}")
    if extra:
        findings.append(f"local_next_action_partition unexpected decision types: {sorted(extra)}")
    for decision_type, action in sorted(by_decision.items()):
        if action.get("local_only_next_action") != "create_local_readiness_index_audit_preview":
            findings.append(f"local_next_action_partition[{decision_type}].local_only_next_action must be create_local_readiness_index_audit_preview")
        for key in ("external_action", "owner_r3_submission", "public_action", "action_permitted_now"):
            if action.get(key) is not False:
                findings.append(f"local_next_action_partition[{decision_type}].{key} must be false")
    return findings


def _validate_blocked_scan(index: dict[str, Any], source: dict[str, Any]) -> list[str]:
    scan = index.get("blocked_action_scan")
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
                findings.append(f"readiness_steps[{index_num}].{key} must be false")

    events = index.get("readiness_events")
    if not isinstance(events, list):
        findings.append("readiness_events must be a list")
        return findings
    event_ids = {item.get("event") for item in events if isinstance(item, dict)}
    missing_events = REQUIRED_READINESS_EVENTS - event_ids
    if missing_events:
        findings.append(f"readiness_events missing {', '.join(sorted(missing_events))}")
    for index_num, event in enumerate(events):
        if not isinstance(event, dict):
            findings.append(f"readiness_events[{index_num}] must be an object")
            continue
        if event.get("external_action") is not False:
            findings.append(f"readiness_events[{index_num}].external_action must be false")
    return findings


def _validate_forbidden_outputs(index: dict[str, Any], source: dict[str, Any]) -> list[str]:
    outputs = index.get("forbidden_outputs")
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


def _validate_handoff(index: dict[str, Any]) -> list[str]:
    handoff = index.get("taskset_handoff")
    if not isinstance(handoff, dict):
        return ["taskset_handoff must be an object"]
    findings: list[str] = []
    if handoff.get("task_158_readiness_index_ready") is not True:
        findings.append("taskset_handoff.task_158_readiness_index_ready must be true")
    if handoff.get("taskset_local_scope_complete_when_task_closes") is not True:
        findings.append("taskset_handoff.taskset_local_scope_complete_when_task_closes must be true")
    if handoff.get("next_task_candidate") != "TASK-159":
        findings.append("taskset_handoff.next_task_candidate must be TASK-159")
    for key in (
        "actual_owner_r3_review_submission_allowed",
        "actual_owner_review_start_allowed",
        "actual_archive_write_allowed",
        "actual_rollback_execution_allowed",
        "actual_archive_delete_allowed",
        "actual_evidence_refresh_allowed",
        "actual_public_use_allowed",
        "final_export_allowed",
        "customer_or_payment_action_allowed",
    ):
        if handoff.get(key) is not False:
            findings.append(f"taskset_handoff.{key} must be false")
    required_for = _string_list(handoff.get("owner_r3_required_for"))
    for item in (
        "actual Owner/R3 review submission",
        "actual Owner/R3 review start",
        "actual archive write",
        "actual rollback execution",
        "archive deletion",
        "SNS upload",
        "secret or token handling",
    ):
        if item not in required_for:
            findings.append(f"taskset_handoff.owner_r3_required_for missing {item}")
    return findings


def _validate_verification(index: dict[str, Any]) -> list[str]:
    verification = index.get("verification")
    if not isinstance(verification, dict):
        return ["verification must be an object"]
    expected = {
        "local_gate": "python scripts/promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_readiness_index_gate.py --check",
        "focused_tests": "python -m pytest tests/unit/test_promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_readiness_index_gate.py -q",
        "source_gate": "python scripts/promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_gate.py --check",
    }
    return [f"verification.{key} must be {value}" for key, value in expected.items() if verification.get(key) != value]


def _by_decision(value: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(value, list):
        return {}
    return {item.get("decision_type"): item for item in value if isinstance(item, dict)}


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
        print("promotion asset Owner/R3 archive/rollback audit-preview readiness index gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"promotion asset Owner/R3 archive/rollback audit-preview readiness index gate: PASS ({args.index})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
