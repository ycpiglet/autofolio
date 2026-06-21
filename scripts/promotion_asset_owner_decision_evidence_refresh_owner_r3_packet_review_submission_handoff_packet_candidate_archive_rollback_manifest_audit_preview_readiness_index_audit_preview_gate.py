"""Validate the TASK-159 readiness-index audit preview.

This gate validates local audit-preview metadata only. It rejects actual
Owner/R3 review submission, review start, evidence refresh execution, archive
writes, rollback execution, archive deletion, approval records, signatures,
approval evidence collection, public approval, final exports, customer/CRM/
payment action, external account action, platform calls, secrets, final advice,
and drift from the source TASK-158 readiness index.
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
    / "PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-REVIEW-SUBMISSION-HANDOFF-PACKET-CANDIDATE-ARCHIVE-ROLLBACK-MANIFEST-AUDIT-PREVIEW-READINESS-INDEX-AUDIT-PREVIEW.json"
)
SOURCE_READINESS_INDEX_PATH = (
    REPO_ROOT
    / "agents"
    / "project"
    / "PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-REVIEW-SUBMISSION-HANDOFF-PACKET-CANDIDATE-ARCHIVE-ROLLBACK-MANIFEST-AUDIT-PREVIEW-READINESS-INDEX.json"
)
SOURCE_READINESS_INDEX_ID = (
    "promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_"
    "archive_rollback_manifest_audit_preview_readiness_index"
)
SOURCE_READINESS_INDEX_REL = (
    "agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-REVIEW-SUBMISSION-HANDOFF-"
    "PACKET-CANDIDATE-ARCHIVE-ROLLBACK-MANIFEST-AUDIT-PREVIEW-READINESS-INDEX.json"
)
SOURCE_READINESS_INDEX_STATUS = (
    "local_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_"
    "readiness_index_not_actual_submission"
)


def _load_source_gate() -> Any:
    path = (
        REPO_ROOT
        / "scripts"
        / "promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_readiness_index_gate.py"
    )
    spec = importlib.util.spec_from_file_location("archive_rollback_manifest_audit_preview_readiness_index_gate", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import source readiness index gate from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SOURCE_GATE = _load_source_gate()

REQUIRED_DECISION_TYPES = set(SOURCE_GATE.REQUIRED_DECISION_TYPES)
REQUIRED_BLOCKED_SCAN_KEYS = set(SOURCE_GATE.REQUIRED_BLOCKED_SCAN_KEYS)
REQUIRED_FORBIDDEN_OUTPUTS = set(SOURCE_GATE.REQUIRED_FORBIDDEN_OUTPUTS)
FORBIDDEN_KEY_NAMES = set(SOURCE_GATE.FORBIDDEN_KEY_NAMES) | {
    "readiness_audit_submission_id",
    "readiness_audit_approval_id",
    "readiness_audit_public_url",
    "source_trace_public_url",
}
LIVE_TRUE_KEYS = set(SOURCE_GATE.LIVE_TRUE_KEYS) | {
    "audit_preview_is_submission",
    "audit_preview_is_approval",
    "audit_preview_is_public_clearance",
    "readiness_index_audit_preview_is_submission",
    "readiness_index_audit_preview_is_approval",
    "readiness_index_audit_preview_is_public_clearance",
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
    "local_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_readiness_index_audit_preview_only",
    "readiness_index_audit_preview_not_submission",
    "readiness_index_audit_preview_not_approval",
    "readiness_index_audit_preview_not_publication_clearance",
    "source_readiness_index_not_submission",
    "source_readiness_index_not_approval",
    "source_readiness_index_not_publication_clearance",
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
    "source_readiness_records": 9,
    "source_owner_r3_blocker_records": 9,
    "source_local_next_action_records": 9,
    "audit_preview_records": 9,
    "owner_r3_blocker_records": 9,
    "local_next_action_records": 9,
    "blocked_action_scan_items": 13,
    "forbidden_outputs": 26,
    "source_readiness_index_boundaries": 37,
    "source_audit_preview_boundaries": 35,
    "source_manifest_boundaries": 41,
    "records_requiring_owner_r3": 9,
    "audit_preview_records_passed": 9,
    "records_with_source_hash_recorded": 9,
    "records_with_non_submission_status": 9,
    "records_with_non_approval_status": 9,
    "records_with_public_use_blocked": 9,
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

REQUIRED_AUDIT_STEPS = {
    "record_source_readiness_index_hash",
    "verify_source_readiness_index_gate",
    "audit_source_readiness_records",
    "audit_owner_r3_blocker_partition",
    "audit_local_next_action_partition",
    "audit_source_reference_coverage",
    "audit_blocked_action_scan",
    "register_source_trace_handoff",
}

REQUIRED_AUDIT_EVENTS = {
    "readiness_index_audit_preview_generated",
    "source_readiness_index_hash_recorded",
    "source_readiness_index_gate_verified",
    "source_readiness_records_audited",
    "owner_r3_blockers_audited",
    "local_next_actions_audited",
    "blocked_action_scan_reused",
    "source_trace_handoff_registered",
}


def load_preview(path: Path = DEFAULT_PREVIEW) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("promotion asset readiness-index audit preview root must be an object")
    return data


def validate_preview(preview: dict[str, Any], repo_root: Path = REPO_ROOT) -> list[str]:
    source = _load_json(SOURCE_READINESS_INDEX_PATH)
    findings: list[str] = []

    source_findings = SOURCE_GATE.validate_index(source, repo_root)
    if source_findings:
        findings.append(f"source readiness index gate must pass: {source_findings}")

    if preview.get("$schema") != (
        "autofolio.promotion-asset-owner-decision-evidence-refresh-owner-r3-packet-review-submission-handoff-packet-candidate-archive-rollback-manifest-audit-preview-readiness-index-audit-preview/v1"
    ):
        findings.append("unexpected or missing promotion asset readiness-index audit preview schema")
    if preview.get("status") != (
        "local_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_readiness_index_audit_preview_not_actual_submission"
    ):
        findings.append(
            "status must be local_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_readiness_index_audit_preview_not_actual_submission"
        )

    findings.extend(_validate_boundaries(preview))
    findings.extend(_validate_sources(preview, repo_root, source))
    findings.extend(_validate_markdown(preview, repo_root))
    findings.extend(_validate_summary(preview, source))
    findings.extend(_validate_source_reference_coverage(preview, source))
    findings.extend(_validate_audit_preview_records(preview, source))
    findings.extend(_validate_owner_r3_blocker_audit(preview, source))
    findings.extend(_validate_local_next_action_audit(preview, source))
    findings.extend(_validate_blocked_scan(preview, source))
    findings.extend(_validate_steps_and_events(preview))
    findings.extend(_validate_forbidden_outputs(preview, source))
    findings.extend(_validate_handoff(preview))
    findings.extend(_validate_verification(preview))

    forbidden_keys = _find_forbidden_keys(preview)
    if forbidden_keys:
        findings.append(
            "forbidden readiness-audit/submission/approval/signature/export/customer/secret/final-advice key names "
            f"present: {forbidden_keys}"
        )
    live_true_paths = _find_live_true_keys(preview)
    if live_true_paths:
        findings.append(
            "readiness-audit/archive/rollback/review-start/submission/refresh/approval/signature/public/export/"
            f"customer/payment/platform/final-advice/live flags must not be true: {live_true_paths}"
        )
    return findings


def _validate_boundaries(preview: dict[str, Any]) -> list[str]:
    boundaries = preview.get("boundaries")
    if not isinstance(boundaries, dict):
        return ["boundaries must be an object"]
    return [f"boundaries.{key} must be true" for key in REQUIRED_BOUNDARIES if boundaries.get(key) is not True]


def _validate_sources(preview: dict[str, Any], repo_root: Path, source: dict[str, Any]) -> list[str]:
    inputs = preview.get("source_inputs")
    if not isinstance(inputs, list):
        return ["source_inputs must be a list"]
    findings: list[str] = []
    source_ids = {item.get("id") for item in inputs if isinstance(item, dict)}
    if SOURCE_READINESS_INDEX_ID not in source_ids:
        findings.append(f"source_inputs missing ids: {[SOURCE_READINESS_INDEX_ID]}")
    for index_num, item in enumerate(inputs):
        if not isinstance(item, dict):
            findings.append(f"source_inputs[{index_num}] must be an object")
            continue
        if item.get("id") == SOURCE_READINESS_INDEX_ID and item.get("path") != SOURCE_READINESS_INDEX_REL:
            findings.append(
                f"source_inputs[{index_num}].path for {SOURCE_READINESS_INDEX_ID} must be {SOURCE_READINESS_INDEX_REL}"
            )
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
            findings.append(f"source_inputs[{index_num}].source_status must match source readiness index status")
        if item.get("relationship") != "audits_source_readiness_index":
            findings.append(f"source_inputs[{index_num}].relationship must be audits_source_readiness_index")
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
    summary = preview.get("audit_preview_summary")
    if not isinstance(summary, dict):
        return ["audit_preview_summary must be an object"]
    findings = [
        f"audit_preview_summary.{key} must be {expected}"
        for key, expected in REQUIRED_SUMMARY_COUNTS.items()
        if summary.get(key) != expected
    ]
    if summary.get("source_readiness_index") != SOURCE_READINESS_INDEX_ID:
        findings.append(f"audit_preview_summary.source_readiness_index must be {SOURCE_READINESS_INDEX_ID}")
    if summary.get("source_readiness_index_status") != source.get("status"):
        findings.append("audit_preview_summary.source_readiness_index_status must match source readiness index status")
    if summary.get("source_gate_result") != "pass":
        findings.append("audit_preview_summary.source_gate_result must be pass")
    if summary.get("gate_result") != "pass":
        findings.append("audit_preview_summary.gate_result must be pass")

    source_summary = source.get("readiness_summary")
    if not isinstance(source_summary, dict):
        findings.append("source readiness_summary must be an object")
        return findings
    checks = {
        "source_readiness_records": len(source.get("readiness_records", [])),
        "source_owner_r3_blocker_records": len(source.get("owner_r3_blocker_partition", [])),
        "source_local_next_action_records": len(source.get("local_next_action_partition", [])),
        "blocked_action_scan_items": len(source.get("blocked_action_scan", {})),
        "forbidden_outputs": len(source.get("forbidden_outputs", [])),
        "source_readiness_index_boundaries": len(source.get("boundaries", {})),
        "source_audit_preview_boundaries": source_summary.get("source_audit_preview_boundaries"),
        "source_manifest_boundaries": source_summary.get("source_manifest_boundaries"),
    }
    findings.extend(
        f"audit_preview_summary.{key} must be {expected}"
        for key, expected in checks.items()
        if summary.get(key) != expected
    )
    return findings


def _validate_source_reference_coverage(preview: dict[str, Any], source: dict[str, Any]) -> list[str]:
    coverage = preview.get("source_reference_coverage")
    if not isinstance(coverage, dict):
        return ["source_reference_coverage must be an object"]
    source_coverage = source.get("source_reference_coverage")
    source_summary = source.get("readiness_summary")
    if not isinstance(source_coverage, dict):
        return ["source source_reference_coverage must be an object"]
    if not isinstance(source_summary, dict):
        return ["source readiness_summary must be an object"]
    checks = {
        "source_readiness_index_records": len(source.get("readiness_records", [])),
        "source_owner_r3_blocker_records": len(source.get("owner_r3_blocker_partition", [])),
        "source_local_next_action_records": len(source.get("local_next_action_partition", [])),
        "source_blocked_action_scan_items": len(source.get("blocked_action_scan", {})),
        "source_forbidden_outputs": len(source.get("forbidden_outputs", [])),
        "source_readiness_index_boundaries": len(source.get("boundaries", {})),
        "source_audit_preview_boundaries": source_summary.get("source_audit_preview_boundaries"),
        "source_manifest_boundaries": source_summary.get("source_manifest_boundaries"),
        "source_preflight_state_safety_scan_count": source_coverage.get("source_preflight_state_safety_scan_count"),
        "source_queue_state_safety_scan_count": source_coverage.get("source_queue_state_safety_scan_count"),
        "source_state_reference_summary_count": source_coverage.get("source_state_reference_summary_count"),
        "source_trigger_reference_summary_count": source_coverage.get("source_trigger_reference_summary_count"),
        "source_handoff_packet_assembly_step_count": source_coverage.get("source_handoff_packet_assembly_step_count"),
        "source_manifest_assembly_step_count": source_coverage.get("source_manifest_assembly_step_count"),
    }
    findings = [
        f"source_reference_coverage.{key} must be {expected}"
        for key, expected in checks.items()
        if coverage.get(key) != expected
    ]
    for key in ("source_readiness_index_gate_reused", "source_reference_coverage_passed", "source_hash_recorded"):
        if coverage.get(key) is not True:
            findings.append(f"source_reference_coverage.{key} must be true")
    for key in ("source_mutated", "external_validation_performed"):
        if coverage.get(key) is not False:
            findings.append(f"source_reference_coverage.{key} must be false")
    return findings


def _validate_audit_preview_records(preview: dict[str, Any], source: dict[str, Any]) -> list[str]:
    records = preview.get("audit_preview_records")
    if not isinstance(records, list):
        return ["audit_preview_records must be a list"]
    findings: list[str] = []
    by_decision = {item.get("decision_type"): item for item in records if isinstance(item, dict)}
    missing = REQUIRED_DECISION_TYPES - set(by_decision)
    extra = set(by_decision) - REQUIRED_DECISION_TYPES
    if missing:
        findings.append(f"audit_preview_records missing decision types: {sorted(missing)}")
    if extra:
        findings.append(f"audit_preview_records unexpected decision types: {sorted(extra)}")

    source_by_decision = _by_decision(source.get("readiness_records"))
    false_keys = {
        "audit_preview_is_submission",
        "audit_preview_is_approval",
        "audit_preview_is_public_clearance",
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
        comparisons = {
            "source_readiness_record_id": source_record.get("readiness_record_id"),
            "source_audit_record_id": source_record.get("source_audit_record_id"),
            "source_archive_manifest_record_id": source_record.get("source_archive_manifest_record_id"),
            "source_rollback_trigger_record_id": source_record.get("source_rollback_trigger_record_id"),
            "source_retention_supersession_record_id": source_record.get("source_retention_supersession_record_id"),
            "source_readiness_status": source_record.get("readiness_status"),
            "source_coverage_status": source_record.get("source_coverage_status"),
        }
        for key, expected in comparisons.items():
            if record.get(key) != expected:
                findings.append(f"audit_preview_records[{decision_type}].{key} must be {expected}")
        if record.get("audit_preview_status") != "pass":
            findings.append(f"audit_preview_records[{decision_type}].audit_preview_status must be pass")
        for key in (
            "source_owner_r3_required_before_submission",
            "source_owner_r3_required_before_public_use",
            "source_professional_review_required_before_reliance",
        ):
            if record.get(key) is not True:
                findings.append(f"audit_preview_records[{decision_type}].{key} must be true")
        for key in false_keys:
            if record.get(key) is not False:
                findings.append(f"audit_preview_records[{decision_type}].{key} must be false")
    return findings


def _validate_owner_r3_blocker_audit(preview: dict[str, Any], source: dict[str, Any]) -> list[str]:
    audit = preview.get("owner_r3_blocker_partition_audit")
    if not isinstance(audit, list):
        return ["owner_r3_blocker_partition_audit must be a list"]
    findings: list[str] = []
    by_decision = {item.get("decision_type"): item for item in audit if isinstance(item, dict)}
    source_by_decision = _by_decision(source.get("owner_r3_blocker_partition"))
    missing = REQUIRED_DECISION_TYPES - set(by_decision)
    extra = set(by_decision) - REQUIRED_DECISION_TYPES
    if missing:
        findings.append(f"owner_r3_blocker_partition_audit missing decision types: {sorted(missing)}")
    if extra:
        findings.append(f"owner_r3_blocker_partition_audit unexpected decision types: {sorted(extra)}")
    false_keys = {
        "actual_owner_r3_review_submitted",
        "actual_owner_review_started",
        "actual_owner_approval_recorded",
        "actual_owner_signature_collected",
        "actual_approval_evidence_collected",
        "public_use_approved",
        "action_permitted_now",
    }
    for decision_type, item in sorted(by_decision.items()):
        source_item = source_by_decision.get(decision_type, {})
        if item.get("source_blocker_status") != source_item.get("blocker_status"):
            findings.append(f"owner_r3_blocker_partition_audit[{decision_type}].source_blocker_status must match source")
        if item.get("audit_status") != "pass":
            findings.append(f"owner_r3_blocker_partition_audit[{decision_type}].audit_status must be pass")
        if item.get("required_before_public_action_count") != len(_string_list(source_item.get("required_before_public_action"))):
            findings.append(
                f"owner_r3_blocker_partition_audit[{decision_type}].required_before_public_action_count must match source"
            )
        if item.get("blocker_partition_preserved") is not True:
            findings.append(f"owner_r3_blocker_partition_audit[{decision_type}].blocker_partition_preserved must be true")
        for key in false_keys:
            if item.get(key) is not False:
                findings.append(f"owner_r3_blocker_partition_audit[{decision_type}].{key} must be false")
    return findings


def _validate_local_next_action_audit(preview: dict[str, Any], source: dict[str, Any]) -> list[str]:
    audit = preview.get("local_next_action_partition_audit")
    if not isinstance(audit, list):
        return ["local_next_action_partition_audit must be a list"]
    findings: list[str] = []
    by_decision = {item.get("decision_type"): item for item in audit if isinstance(item, dict)}
    source_by_decision = _by_decision(source.get("local_next_action_partition"))
    missing = REQUIRED_DECISION_TYPES - set(by_decision)
    extra = set(by_decision) - REQUIRED_DECISION_TYPES
    if missing:
        findings.append(f"local_next_action_partition_audit missing decision types: {sorted(missing)}")
    if extra:
        findings.append(f"local_next_action_partition_audit unexpected decision types: {sorted(extra)}")
    for decision_type, item in sorted(by_decision.items()):
        source_item = source_by_decision.get(decision_type, {})
        if item.get("source_local_only_next_action") != source_item.get("local_only_next_action"):
            findings.append(
                f"local_next_action_partition_audit[{decision_type}].source_local_only_next_action must match source"
            )
        if item.get("audit_status") != "pass":
            findings.append(f"local_next_action_partition_audit[{decision_type}].audit_status must be pass")
        if item.get("local_action_preserved") is not True:
            findings.append(f"local_next_action_partition_audit[{decision_type}].local_action_preserved must be true")
        for key in ("external_action", "owner_r3_submission", "public_action", "action_permitted_now"):
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
                findings.append(f"audit_preview_steps[{index_num}].{key} must be false")

    events = preview.get("audit_preview_events")
    if not isinstance(events, list):
        findings.append("audit_preview_events must be a list")
        return findings
    event_ids = {item.get("event") for item in events if isinstance(item, dict)}
    missing_events = REQUIRED_AUDIT_EVENTS - event_ids
    if missing_events:
        findings.append(f"audit_preview_events missing {', '.join(sorted(missing_events))}")
    for index_num, event in enumerate(events):
        if not isinstance(event, dict):
            findings.append(f"audit_preview_events[{index_num}] must be an object")
            continue
        if event.get("external_action") is not False:
            findings.append(f"audit_preview_events[{index_num}].external_action must be false")
    return findings


def _validate_forbidden_outputs(preview: dict[str, Any], source: dict[str, Any]) -> list[str]:
    outputs = preview.get("forbidden_outputs")
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


def _validate_handoff(preview: dict[str, Any]) -> list[str]:
    handoff = preview.get("taskset_handoff")
    if not isinstance(handoff, dict):
        return ["taskset_handoff must be an object"]
    findings: list[str] = []
    if handoff.get("task_159_audit_preview_ready") is not True:
        findings.append("taskset_handoff.task_159_audit_preview_ready must be true")
    if handoff.get("taskset_local_scope_complete_when_task_closes") is not True:
        findings.append("taskset_handoff.taskset_local_scope_complete_when_task_closes must be true")
    if handoff.get("next_task_candidate") != "TASK-160":
        findings.append("taskset_handoff.next_task_candidate must be TASK-160")
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


def _validate_verification(preview: dict[str, Any]) -> list[str]:
    verification = preview.get("verification")
    if not isinstance(verification, dict):
        return ["verification must be an object"]
    expected = {
        "local_gate": "python scripts/promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_readiness_index_audit_preview_gate.py --check",
        "focused_tests": "python -m pytest tests/unit/test_promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_readiness_index_audit_preview_gate.py -q",
        "source_gate": "python scripts/promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_readiness_index_gate.py --check",
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
    parser.add_argument("--preview", type=Path, default=DEFAULT_PREVIEW)
    parser.add_argument("--check", action="store_true", help="validate and return non-zero on findings")
    args = parser.parse_args()

    preview = load_preview(args.preview)
    findings = validate_preview(preview)
    if findings:
        print("promotion asset Owner/R3 readiness-index audit preview gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"promotion asset Owner/R3 readiness-index audit preview gate: PASS ({args.preview})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
