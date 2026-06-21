"""Validate the TASK-157 archive/rollback manifest audit preview.

This gate validates local audit/readiness preview metadata only. It rejects
actual Owner/R3 review submission, review start, evidence refresh execution,
archive writes, rollback execution, archive deletion, approval records,
signatures, approval evidence collection, public approval, final exports,
customer/CRM/payment action, external account action, platform calls, secrets,
and drift from the source archive/rollback manifest.
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
    / "PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-REVIEW-SUBMISSION-HANDOFF-PACKET-CANDIDATE-ARCHIVE-ROLLBACK-MANIFEST-AUDIT-PREVIEW.json"
)
SOURCE_MANIFEST_PATH = (
    REPO_ROOT
    / "agents"
    / "project"
    / "PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-REVIEW-SUBMISSION-HANDOFF-PACKET-CANDIDATE-ARCHIVE-ROLLBACK-MANIFEST.json"
)
SOURCE_ID = "promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest"
SOURCE_REL = (
    "agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-REVIEW-SUBMISSION-HANDOFF-PACKET-CANDIDATE-ARCHIVE-ROLLBACK-MANIFEST.json"
)


def _load_source_gate() -> Any:
    path = (
        REPO_ROOT
        / "scripts"
        / "promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_gate.py"
    )
    spec = importlib.util.spec_from_file_location("archive_rollback_manifest_gate", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import source archive/rollback manifest gate from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SOURCE_GATE = _load_source_gate()

REQUIRED_DECISION_TYPES = set(SOURCE_GATE.REQUIRED_DECISION_TYPES)
REQUIRED_BLOCKED_SCAN_KEYS = set(SOURCE_GATE.REQUIRED_BLOCKED_SCAN_KEYS)
REQUIRED_FORBIDDEN_OUTPUTS = set(SOURCE_GATE.REQUIRED_FORBIDDEN_OUTPUTS)
FORBIDDEN_KEY_NAMES = set(SOURCE_GATE.FORBIDDEN_KEY_NAMES) | {
    "audit_submission_id",
    "audit_approval_id",
    "archive_audit_public_url",
    "rollback_audit_execution_log",
}
LIVE_TRUE_KEYS = set(SOURCE_GATE.LIVE_TRUE_KEYS) | {
    "audit_preview_is_submission",
    "audit_preview_is_approval",
    "audit_preview_is_public_clearance",
    "actual_owner_r3_review_submission_allowed",
    "actual_archive_write_allowed",
    "actual_rollback_execution_allowed",
    "actual_archive_delete_allowed",
    "source_mutated",
    "external_validation_performed",
}

REQUIRED_BOUNDARIES = {
    "local_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_readiness_preview_only",
    "archive_rollback_manifest_audit_not_submission",
    "archive_rollback_manifest_audit_not_approval",
    "archive_rollback_manifest_audit_not_publication_clearance",
    "source_archive_rollback_manifest_not_submission",
    "source_archive_rollback_manifest_not_approval",
    "archive_manifest_not_publication_clearance",
    "rollback_manifest_not_execution",
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
    "source_archive_manifest_records": 9,
    "source_rollback_trigger_records": 9,
    "source_retention_supersession_records": 9,
    "audit_coverage_records": 9,
    "source_preflight_state_safety_scan_items": 6,
    "source_queue_state_safety_scan_items": 6,
    "source_state_reference_summaries": 5,
    "source_trigger_reference_summaries": 8,
    "source_handoff_packet_assembly_steps": 7,
    "source_manifest_assembly_steps": 8,
    "blocked_action_scan_items": 13,
    "forbidden_outputs": 26,
    "source_boundaries": 41,
    "coverage_records_passed": 9,
    "records_requiring_owner_r3": 9,
    "records_with_non_submission_status": 9,
    "records_with_non_approval_status": 9,
    "records_with_archive_required": 9,
    "records_with_rollback_covered": 9,
    "records_with_retention_supersession_covered": 9,
    "records_with_public_use_blocked": 9,
    "records_with_final_export_blocked": 9,
    "records_with_customer_contact_blocked": 9,
    "records_with_crm_payment_blocked": 9,
    "records_with_secret_material_blocked": 9,
    "records_with_final_advice_blocked": 9,
    "records_with_kis_order_risk_prod_deploy_blocked": 9,
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
    "record_source_manifest_hash",
    "verify_source_manifest_gate",
    "audit_archive_manifest_records",
    "audit_rollback_trigger_records",
    "audit_retention_supersession_records",
    "audit_source_reference_coverage",
    "audit_blocked_action_scan",
    "register_readiness_index_handoff",
}

REQUIRED_AUDIT_EVENTS = {
    "archive_rollback_manifest_audit_preview_generated",
    "source_archive_rollback_manifest_hash_recorded",
    "source_manifest_gate_verified",
    "archive_manifest_record_coverage_audited",
    "rollback_trigger_coverage_audited",
    "retention_supersession_coverage_audited",
    "blocked_action_scan_passed",
    "readiness_index_handoff_registered",
}


def load_preview(path: Path = DEFAULT_PREVIEW) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("promotion asset Owner/R3 archive/rollback manifest audit preview root must be an object")
    return data


def validate_preview(preview: dict[str, Any], repo_root: Path = REPO_ROOT) -> list[str]:
    source = _load_json(SOURCE_MANIFEST_PATH)
    findings: list[str] = []

    source_findings = SOURCE_GATE.validate_manifest(source, repo_root)
    if source_findings:
        findings.append(f"source archive/rollback manifest gate must pass: {source_findings}")

    if preview.get("$schema") != (
        "autofolio.promotion-asset-owner-decision-evidence-refresh-owner-r3-packet-review-submission-handoff-packet-candidate-archive-rollback-manifest-audit-preview/v1"
    ):
        findings.append("unexpected or missing promotion asset Owner/R3 archive/rollback manifest audit preview schema")
    if preview.get("status") != (
        "local_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_readiness_preview_not_actual_submission"
    ):
        findings.append(
            "status must be local_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_readiness_preview_not_actual_submission"
        )

    findings.extend(_validate_boundaries(preview))
    findings.extend(_validate_sources(preview, repo_root))
    findings.extend(_validate_markdown(preview, repo_root))
    findings.extend(_validate_summary(preview, source))
    findings.extend(_validate_source_reference_coverage(preview, source))
    findings.extend(_validate_coverage_records(preview, source))
    findings.extend(_validate_blocked_scan(preview, source))
    findings.extend(_validate_steps_and_events(preview))
    findings.extend(_validate_forbidden_outputs(preview, source))
    findings.extend(_validate_handoff(preview))
    findings.extend(_validate_verification(preview))

    forbidden_keys = _find_forbidden_keys(preview)
    if forbidden_keys:
        findings.append(
            "forbidden archive-audit/review-submission/approval/signature/export/customer/secret/final-advice key names "
            f"present: {forbidden_keys}"
        )
    live_true_paths = _find_live_true_keys(preview)
    if live_true_paths:
        findings.append(
            "archive-audit/archive/rollback/review-start/submission/refresh/approval/signature/public/export/customer/"
            f"payment/platform/final-advice/live flags must not be true: {live_true_paths}"
        )
    return findings


def _validate_boundaries(preview: dict[str, Any]) -> list[str]:
    boundaries = preview.get("boundaries")
    if not isinstance(boundaries, dict):
        return ["boundaries must be an object"]
    return [f"boundaries.{key} must be true" for key in REQUIRED_BOUNDARIES if boundaries.get(key) is not True]


def _validate_sources(preview: dict[str, Any], repo_root: Path) -> list[str]:
    inputs = preview.get("source_inputs")
    if not isinstance(inputs, list):
        return ["source_inputs must be a list"]
    findings: list[str] = []
    source_ids = {item.get("id") for item in inputs if isinstance(item, dict)}
    if SOURCE_ID not in source_ids:
        findings.append(f"source_inputs missing ids: {[SOURCE_ID]}")
    for index, item in enumerate(inputs):
        if not isinstance(item, dict):
            findings.append(f"source_inputs[{index}] must be an object")
            continue
        if item.get("id") == SOURCE_ID and item.get("path") != SOURCE_REL:
            findings.append(f"source_inputs[{index}].path for {SOURCE_ID} must be {SOURCE_REL}")
        try:
            path = _safe_repo_path(repo_root, str(item.get("path", "")))
        except ValueError as exc:
            findings.append(f"source_inputs[{index}].path invalid: {exc}")
            continue
        if not path.exists():
            findings.append(f"source_inputs[{index}].path missing: {item.get('path')}")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if item.get("sha256") != digest:
            findings.append(f"source_inputs[{index}].sha256 mismatch for {item.get('path')}: expected {digest}")
        if item.get("source_status") != "local_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_not_actual_submission":
            findings.append(f"source_inputs[{index}].source_status must match the source manifest non-submission status")
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
    summary = preview.get("audit_summary")
    if not isinstance(summary, dict):
        return ["audit_summary must be an object"]
    findings = [
        f"audit_summary.{key} must be {expected}"
        for key, expected in REQUIRED_SUMMARY_COUNTS.items()
        if summary.get(key) != expected
    ]
    if summary.get("source_archive_rollback_manifest") != SOURCE_ID:
        findings.append(f"audit_summary.source_archive_rollback_manifest must be {SOURCE_ID}")
    if summary.get("source_manifest_status") != source.get("status"):
        findings.append("audit_summary.source_manifest_status must match source manifest status")
    if summary.get("source_gate_result") != "pass":
        findings.append("audit_summary.source_gate_result must be pass")

    source_summary = source.get("manifest_summary")
    if not isinstance(source_summary, dict):
        findings.append("source manifest_summary must be an object")
        return findings
    source_count_map = {
        "source_archive_manifest_records": source_summary.get("archive_manifest_records"),
        "source_rollback_trigger_records": source_summary.get("rollback_trigger_records"),
        "source_retention_supersession_records": source_summary.get("retention_supersession_records"),
        "source_preflight_state_safety_scan_items": source_summary.get("source_preflight_state_safety_scan_items"),
        "source_queue_state_safety_scan_items": source_summary.get("source_queue_state_safety_scan_items"),
        "source_state_reference_summaries": source_summary.get("source_state_reference_summaries"),
        "source_trigger_reference_summaries": source_summary.get("source_trigger_reference_summaries"),
        "source_handoff_packet_assembly_steps": source_summary.get("source_handoff_packet_assembly_steps"),
        "source_manifest_assembly_steps": source_summary.get("manifest_assembly_steps"),
        "blocked_action_scan_items": source_summary.get("blocked_action_scan_items"),
        "ready_for_owner_r3_submission_records": source_summary.get("ready_for_owner_r3_submission_records"),
        "ready_for_public_use_records": source_summary.get("ready_for_public_use_records"),
        "actual_archive_writes": source_summary.get("actual_archive_writes"),
        "actual_rollback_executions": source_summary.get("actual_rollback_executions"),
        "actual_archive_deletions": source_summary.get("actual_archive_deletions"),
        "actual_review_started_records": source_summary.get("actual_review_started_records"),
        "actual_review_submissions": source_summary.get("actual_review_submissions"),
        "actual_refresh_executions": source_summary.get("actual_refresh_executions"),
        "actual_owner_approval_records": source_summary.get("actual_owner_approval_records"),
        "actual_owner_signatures": source_summary.get("actual_owner_signatures"),
        "actual_approval_evidence_records": source_summary.get("actual_approval_evidence_records"),
        "actual_public_approvals": source_summary.get("actual_public_approvals"),
        "final_export_outputs": source_summary.get("final_export_outputs"),
        "public_publication_outputs": source_summary.get("public_publication_outputs"),
        "customer_or_payment_outputs": source_summary.get("customer_or_payment_outputs"),
        "secret_or_token_outputs": source_summary.get("secret_or_token_outputs"),
        "final_advice_outputs": source_summary.get("final_advice_outputs"),
        "archive_deletion_outputs": source_summary.get("archive_deletion_outputs"),
        "external_archive_outputs": source_summary.get("external_archive_outputs"),
        "live_action_states": source_summary.get("live_action_states"),
    }
    for key, expected in source_count_map.items():
        if summary.get(key) != expected:
            findings.append(f"audit_summary.{key} must match source manifest_summary value {expected}")
    if summary.get("source_boundaries") != len(source.get("boundaries", {})):
        findings.append("audit_summary.source_boundaries must match source boundaries count")
    if summary.get("forbidden_outputs") != len(source.get("forbidden_outputs", [])):
        findings.append("audit_summary.forbidden_outputs must match source forbidden_outputs count")
    return findings


def _validate_source_reference_coverage(preview: dict[str, Any], source: dict[str, Any]) -> list[str]:
    coverage = preview.get("source_reference_coverage")
    if not isinstance(coverage, dict):
        return ["source_reference_coverage must be an object"]
    summary = source.get("manifest_summary", {})
    checks = {
        "source_preflight_state_safety_scan_count": summary.get("source_preflight_state_safety_scan_items"),
        "source_queue_state_safety_scan_count": summary.get("source_queue_state_safety_scan_items"),
        "source_state_reference_summary_count": summary.get("source_state_reference_summaries"),
        "source_trigger_reference_summary_count": summary.get("source_trigger_reference_summaries"),
        "source_handoff_packet_assembly_step_count": summary.get("source_handoff_packet_assembly_steps"),
        "source_manifest_assembly_step_count": summary.get("manifest_assembly_steps"),
    }
    findings = [f"source_reference_coverage.{key} must be {expected}" for key, expected in checks.items() if coverage.get(key) != expected]
    for key in ("source_reference_coverage_passed", "source_hash_recorded", "source_manifest_gate_reused"):
        if coverage.get(key) is not True:
            findings.append(f"source_reference_coverage.{key} must be true")
    for key in ("source_mutated", "external_validation_performed"):
        if coverage.get(key) is not False:
            findings.append(f"source_reference_coverage.{key} must be false")
    return findings


def _validate_coverage_records(preview: dict[str, Any], source: dict[str, Any]) -> list[str]:
    records = preview.get("coverage_records")
    if not isinstance(records, list):
        return ["coverage_records must be a list"]
    findings: list[str] = []
    by_decision = {item.get("decision_type"): item for item in records if isinstance(item, dict)}
    missing = REQUIRED_DECISION_TYPES - set(by_decision)
    extra = set(by_decision) - REQUIRED_DECISION_TYPES
    if missing:
        findings.append(f"coverage_records missing decision types: {sorted(missing)}")
    if extra:
        findings.append(f"coverage_records unexpected decision types: {sorted(extra)}")

    archive_by_decision = _by_decision(source.get("archive_manifest_records"))
    rollback_by_decision = _by_decision(source.get("rollback_trigger_records"))
    retention_by_decision = _by_decision(source.get("retention_supersession_records"))

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
        archive = archive_by_decision.get(decision_type, {})
        rollback = rollback_by_decision.get(decision_type, {})
        retention = retention_by_decision.get(decision_type, {})
        if record.get("source_archive_manifest_record_id") != archive.get("archive_manifest_record_id"):
            findings.append(
                f"coverage_records[{decision_type}].source_archive_manifest_record_id must be {archive.get('archive_manifest_record_id')}"
            )
        if record.get("source_rollback_trigger_record_id") != rollback.get("rollback_trigger_record_id"):
            findings.append(
                f"coverage_records[{decision_type}].source_rollback_trigger_record_id must be {rollback.get('rollback_trigger_record_id')}"
            )
        if record.get("source_retention_supersession_record_id") != retention.get("retention_supersession_record_id"):
            findings.append(
                f"coverage_records[{decision_type}].source_retention_supersession_record_id must be {retention.get('retention_supersession_record_id')}"
            )
        if record.get("archive_manifest_record_status") != archive.get("manifest_status"):
            findings.append(f"coverage_records[{decision_type}].archive_manifest_record_status must match source")
        if record.get("rollback_trigger_coverage_status") != rollback.get("coverage_status"):
            findings.append(f"coverage_records[{decision_type}].rollback_trigger_coverage_status must match source")
        if record.get("retention_supersession_status") != "covered":
            findings.append(f"coverage_records[{decision_type}].retention_supersession_status must be covered")
        if record.get("coverage_status") != "pass":
            findings.append(f"coverage_records[{decision_type}].coverage_status must be pass")
        if record.get("owner_r3_required_before_action") is not True:
            findings.append(f"coverage_records[{decision_type}].owner_r3_required_before_action must be true")
        if record.get("public_use_blocked") is not True:
            findings.append(f"coverage_records[{decision_type}].public_use_blocked must be true")
        for key in false_keys:
            if record.get(key) is not False:
                findings.append(f"coverage_records[{decision_type}].{key} must be false")
    return findings


def _validate_blocked_scan(preview: dict[str, Any], source: dict[str, Any]) -> list[str]:
    scan = preview.get("blocked_action_scan")
    if scan != source.get("blocked_action_scan"):
        return ["blocked_action_scan must match source archive/rollback manifest"]
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
    steps = preview.get("audit_steps")
    if not isinstance(steps, list):
        return ["audit_steps must be a list"]
    step_ids = {item.get("step_id") for item in steps if isinstance(item, dict)}
    missing_steps = REQUIRED_AUDIT_STEPS - step_ids
    if missing_steps:
        findings.append(f"audit_steps missing {', '.join(sorted(missing_steps))}")
    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            findings.append(f"audit_steps[{index}] must be an object")
            continue
        if step.get("status") != "pass":
            findings.append(f"audit_steps[{index}].status must be pass")
        for key in ("external_action", "owner_r3_submission", "archive_write", "rollback_execution", "archive_delete"):
            if step.get(key) is not False:
                findings.append(f"audit_steps[{index}].{key} must be false")

    events = preview.get("audit_events")
    if not isinstance(events, list):
        findings.append("audit_events must be a list")
        return findings
    event_ids = {item.get("event") for item in events if isinstance(item, dict)}
    missing_events = REQUIRED_AUDIT_EVENTS - event_ids
    if missing_events:
        findings.append(f"audit_events missing {', '.join(sorted(missing_events))}")
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            findings.append(f"audit_events[{index}] must be an object")
            continue
        if event.get("external_action") is not False:
            findings.append(f"audit_events[{index}].external_action must be false")
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
    if handoff.get("task_157_audit_preview_ready") is not True:
        findings.append("taskset_handoff.task_157_audit_preview_ready must be true")
    if handoff.get("taskset_local_scope_complete_when_task_closes") is not True:
        findings.append("taskset_handoff.taskset_local_scope_complete_when_task_closes must be true")
    if handoff.get("next_task_candidate") != "TASK-158":
        findings.append("taskset_handoff.next_task_candidate must be TASK-158")
    for key in (
        "actual_owner_r3_review_submission_allowed",
        "actual_archive_write_allowed",
        "actual_rollback_execution_allowed",
        "actual_archive_delete_allowed",
    ):
        if handoff.get(key) is not False:
            findings.append(f"taskset_handoff.{key} must be false")
    required_for = _string_list(handoff.get("owner_r3_required_for"))
    for item in (
        "actual Owner/R3 review submission",
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
        "local_gate": "python scripts/promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_gate.py --check",
        "focused_tests": "python -m pytest tests/unit/test_promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_audit_preview_gate.py -q",
        "source_gate": "python scripts/promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_gate.py --check",
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
        for index, child in enumerate(value):
            findings.extend(_find_forbidden_keys(child, f"{prefix}[{index}]"))
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
        for index, child in enumerate(value):
            findings.extend(_find_live_true_keys(child, f"{prefix}[{index}]"))
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
        print("promotion asset Owner/R3 archive/rollback manifest audit preview gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"promotion asset Owner/R3 archive/rollback manifest audit preview gate: PASS ({args.preview})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
