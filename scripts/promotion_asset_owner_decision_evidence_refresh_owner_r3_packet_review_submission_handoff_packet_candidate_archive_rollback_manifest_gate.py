"""Validate the TASK-156 handoff packet archive/rollback manifest.

This gate validates local manifest metadata only. It rejects actual Owner/R3
review submission, review start, evidence refresh execution, archive writes,
rollback execution, approval records, signatures, approval evidence collection,
public approval, final exports, customer/CRM/payment action, external account
action, platform calls, secrets, and drift from the source audit preview.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = (
    REPO_ROOT
    / "agents"
    / "project"
    / "PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-REVIEW-SUBMISSION-HANDOFF-PACKET-CANDIDATE-ARCHIVE-ROLLBACK-MANIFEST.json"
)
SOURCE_PREVIEW_PATH = (
    REPO_ROOT
    / "agents"
    / "project"
    / "PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-REVIEW-SUBMISSION-HANDOFF-PACKET-CANDIDATE-AUDIT-PREVIEW.json"
)
SOURCE_ID = "promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_audit_preview"
SOURCE_REL = (
    "agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-REVIEW-SUBMISSION-HANDOFF-PACKET-CANDIDATE-AUDIT-PREVIEW.json"
)


def _load_source_gate() -> Any:
    path = (
        REPO_ROOT
        / "scripts"
        / "promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_audit_preview_gate.py"
    )
    spec = importlib.util.spec_from_file_location("handoff_packet_candidate_audit_preview_gate", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import source audit preview gate from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SOURCE_GATE = _load_source_gate()

REQUIRED_DECISION_TYPES = set(SOURCE_GATE.REQUIRED_DECISION_TYPES)
REQUIRED_BLOCKED_SCAN_KEYS = set(SOURCE_GATE.REQUIRED_BLOCKED_SCAN_KEYS)
REQUIRED_FORBIDDEN_OUTPUTS = set(SOURCE_GATE.REQUIRED_FORBIDDEN_OUTPUTS) | {
    "actual archive write",
    "actual rollback execution",
    "archive deletion",
    "external archive upload",
}
FORBIDDEN_KEY_NAMES = set(SOURCE_GATE.FORBIDDEN_KEY_NAMES) | {
    "archive_file_path",
    "archive_storage_path",
    "rollback_execution_log",
    "archive_delete_log",
    "external_archive_upload_id",
}
LIVE_TRUE_KEYS = set(SOURCE_GATE.LIVE_TRUE_KEYS) | {
    "archive_record_is_submission",
    "archive_record_is_approval",
    "archive_manifest_is_public_clearance",
    "actual_archive_written",
    "actual_rollback_executed",
    "actual_archive_deleted",
    "external_archive_upload_enabled",
    "customer_private_data_retained",
    "secret_material_retained",
    "rollback_execution_enabled",
    "archive_write_enabled",
    "archive_delete_enabled",
    "archive_manifest_is_submission",
    "archive_manifest_is_approval",
    "rollback_manifest_is_execution",
}

REQUIRED_BOUNDARIES = {
    "local_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_only",
    "archive_rollback_manifest_not_submission",
    "archive_rollback_manifest_not_approval",
    "archive_manifest_not_publication_clearance",
    "rollback_manifest_not_execution",
    "handoff_packet_candidate_audit_not_submission",
    "handoff_packet_candidate_not_submission",
    "handoff_packet_candidate_audit_not_approval",
    "handoff_packet_candidate_not_approval",
    "source_preflight_audit_not_submission",
    "source_preflight_audit_not_approval",
    "source_preflight_not_submission",
    "source_preflight_not_approval",
    "review_queue_audit_not_approval",
    "review_queue_not_approval",
    "not_actual_owner_r3_review_submission",
    "not_actual_owner_review_started",
    "not_actual_refresh_execution",
    "not_actual_archive_write",
    "not_actual_rollback_execution",
    "not_archive_deletion",
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
    "source_handoff_packet_record_summaries": 9,
    "archive_manifest_records": 9,
    "rollback_trigger_records": 9,
    "retention_supersession_records": 9,
    "owner_r3_required_input_summaries": 9,
    "unresolved_blocker_summaries": 9,
    "invalidating_trigger_summaries": 9,
    "source_preflight_state_safety_scan_items": 6,
    "source_queue_state_safety_scan_items": 6,
    "source_state_reference_summaries": 5,
    "source_trigger_reference_summaries": 8,
    "source_handoff_packet_assembly_steps": 7,
    "manifest_assembly_steps": 8,
    "blocked_action_scan_items": 13,
    "total_source_required_evidence_items": 25,
    "total_source_stale_evidence_trigger_items": 27,
    "total_source_invalidating_event_items": 36,
    "records_requiring_owner_r3": 9,
    "records_with_non_submission_status": 9,
    "records_with_non_approval_status": 9,
    "records_with_owner_review_not_started": 9,
    "records_with_archive_required": 9,
    "rollback_triggers_covered": 9,
    "retention_supersession_records_without_private_data": 9,
    "records_with_public_use_blocked": 9,
    "records_with_final_export_blocked": 9,
    "records_with_external_action_blocked": 9,
    "records_with_customer_contact_blocked": 9,
    "records_with_crm_payment_blocked": 9,
    "records_with_secret_material_blocked": 9,
    "records_with_final_advice_blocked": 9,
    "records_with_kis_order_risk_prod_deploy_blocked": 9,
    "owner_r3_inputs_missing": 9,
    "unresolved_blockers_active": 9,
    "invalidating_triggers_blocked_from_refresh_or_submission": 9,
    "blocked_scan_items_passed": 13,
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

REQUIRED_MANIFEST_STEPS = {
    "record_source_hash",
    "summarize_archive_records",
    "map_rollback_triggers",
    "map_retention_supersession",
    "copy_source_references",
    "preserve_blocked_actions",
    "validate_no_live_action",
    "register_audit_preview_handoff",
}

REQUIRED_MANIFEST_EVENTS = {
    "archive_rollback_manifest_generated",
    "source_handoff_packet_candidate_audit_preview_hash_recorded",
    "archive_manifest_records_recorded",
    "rollback_triggers_mapped",
    "retention_supersession_coverage_recorded",
    "source_reference_coverage_recorded",
    "blocked_action_scan_passed",
    "audit_preview_handoff_registered",
}


def load_manifest(path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("promotion asset Owner/R3 archive/rollback manifest root must be an object")
    return data


def validate_manifest(manifest: dict[str, Any], repo_root: Path = REPO_ROOT) -> list[str]:
    source = _load_json(SOURCE_PREVIEW_PATH)
    findings: list[str] = []

    source_findings = SOURCE_GATE.validate_preview(source, repo_root)
    if source_findings:
        findings.append(f"source handoff packet candidate audit preview gate must pass: {source_findings}")

    if manifest.get("$schema") != (
        "autofolio.promotion-asset-owner-decision-evidence-refresh-owner-r3-packet-review-submission-handoff-packet-candidate-archive-rollback-manifest/v1"
    ):
        findings.append("unexpected or missing promotion asset Owner/R3 archive/rollback manifest schema")
    if manifest.get("status") != "local_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_not_actual_submission":
        findings.append(
            "status must be local_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_not_actual_submission"
        )

    findings.extend(_validate_boundaries(manifest))
    findings.extend(_validate_sources(manifest, repo_root))
    findings.extend(_validate_markdown(manifest, repo_root))
    findings.extend(_validate_summary(manifest, source))
    findings.extend(_validate_source_copies(manifest, source))
    findings.extend(_validate_archive_records(manifest, source))
    findings.extend(_validate_rollback_records(manifest, source))
    findings.extend(_validate_retention_records(manifest))
    findings.extend(_validate_blocked_scan(manifest, source))
    findings.extend(_validate_steps_and_events(manifest))
    findings.extend(_validate_forbidden_outputs(manifest))
    findings.extend(_validate_handoff(manifest))
    findings.extend(_validate_verification(manifest))

    forbidden_keys = _find_forbidden_keys(manifest)
    if forbidden_keys:
        findings.append(
            "forbidden archive/review-submission/approval/signature/export/customer/secret/final-advice key names "
            f"present: {forbidden_keys}"
        )
    live_true_paths = _find_live_true_keys(manifest)
    if live_true_paths:
        findings.append(
            "archive/rollback/review-start/submission/refresh/approval/signature/public/export/customer/payment/platform/"
            f"final-advice/live flags must not be true: {live_true_paths}"
        )
    return findings


def _validate_boundaries(manifest: dict[str, Any]) -> list[str]:
    boundaries = manifest.get("boundaries")
    if not isinstance(boundaries, dict):
        return ["boundaries must be an object"]
    return [f"boundaries.{key} must be true" for key in REQUIRED_BOUNDARIES if boundaries.get(key) is not True]


def _validate_sources(manifest: dict[str, Any], repo_root: Path) -> list[str]:
    inputs = manifest.get("source_inputs")
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
        if str(item.get("sha256", "")).lower() != _sha256(path):
            findings.append(f"source_inputs[{index}].sha256 mismatch for {item.get('path')}")
    return findings


def _validate_markdown(manifest: dict[str, Any], repo_root: Path) -> list[str]:
    try:
        path = _safe_repo_path(repo_root, str(manifest.get("companion_markdown", "")))
    except ValueError as exc:
        return [f"companion_markdown invalid: {exc}"]
    if not path.exists():
        return [f"companion_markdown missing: {manifest.get('companion_markdown')}"]
    text = path.read_text(encoding="utf-8").lower()
    required = (
        "archive/rollback manifest",
        "archive rollback manifest not submission",
        "archive rollback manifest not approval",
        "archive manifest not publication clearance",
        "rollback manifest not execution",
        "not actual owner/r3 review submission",
        "not actual owner/r3 review start",
        "not actual archive write",
        "not actual rollback execution",
        "not actual owner approval",
        "not actual owner signature",
        "not actual approval evidence",
        "archive manifest records",
        "rollback trigger records",
        "retention supersession records",
        "source reference coverage",
        "blocked action scan",
    )
    return [f"companion_markdown must mention {item}" for item in required if item not in text]


def _validate_summary(manifest: dict[str, Any], source: dict[str, Any]) -> list[str]:
    summary = manifest.get("manifest_summary")
    if not isinstance(summary, dict):
        return ["manifest_summary must be an object"]
    findings = [f"manifest_summary.{key} must be {value}" for key, value in REQUIRED_SUMMARY_COUNTS.items() if summary.get(key) != value]
    if summary.get("source_handoff_packet_candidate_audit_preview") != source.get("preview_id"):
        findings.append("manifest_summary.source_handoff_packet_candidate_audit_preview must match source preview_id")
    if summary.get("source_preview_status") != source.get("status"):
        findings.append("manifest_summary.source_preview_status must match source status")
    if summary.get("gate_result") != "pass":
        findings.append("manifest_summary.gate_result must be pass")
    source_summary = source.get("audit_summary", {})
    for key in (
        "total_source_required_evidence_items",
        "total_source_stale_evidence_trigger_items",
        "total_source_invalidating_event_items",
        "actual_review_started_records",
        "actual_review_submissions",
        "actual_refresh_executions",
        "actual_owner_approval_records",
        "actual_owner_signatures",
        "actual_approval_evidence_records",
        "actual_public_approvals",
        "final_export_outputs",
        "public_publication_outputs",
        "customer_or_payment_outputs",
        "secret_or_token_outputs",
        "final_advice_outputs",
        "live_action_states",
    ):
        if summary.get(key) != source_summary.get(key):
            findings.append(f"manifest_summary.{key} must match source audit summary")
    return findings


def _validate_source_copies(manifest: dict[str, Any], source: dict[str, Any]) -> list[str]:
    pairs = (
        ("source_audit_preview_summary", "audit_summary"),
        ("source_candidate_summary", "source_candidate_summary"),
        ("source_handoff_packet_record_summaries", "handoff_packet_record_summaries"),
        ("source_owner_r3_required_input_summaries", "owner_r3_required_input_summaries"),
        ("source_unresolved_blocker_summaries", "unresolved_blocker_summaries"),
        ("source_invalidating_trigger_summaries", "invalidating_trigger_summaries"),
        ("source_preflight_state_safety_scan", "source_preflight_state_safety_scan"),
        ("source_queue_state_safety_scan", "source_queue_state_safety_scan"),
        ("source_state_reference_safety_scan", "source_state_reference_safety_scan"),
        ("source_trigger_reference_coverage_scan", "source_trigger_reference_coverage_scan"),
        ("source_handoff_packet_assembly_step_summaries", "handoff_packet_assembly_step_summaries"),
    )
    return [f"{key} must match source audit preview {src}" for key, src in pairs if manifest.get(key) != source.get(src)]


def _validate_archive_records(manifest: dict[str, Any], source: dict[str, Any]) -> list[str]:
    records = manifest.get("archive_manifest_records")
    if not isinstance(records, list):
        return ["archive_manifest_records must be a list"]
    findings = _missing_decisions(records, "archive_manifest_records")
    source_records = _by_decision(source.get("handoff_packet_record_summaries"))
    source_inputs = _by_decision(source.get("owner_r3_required_input_summaries"))
    source_blockers = _by_decision(source.get("unresolved_blocker_summaries"))
    source_triggers = _by_decision(source.get("invalidating_trigger_summaries"))
    for index, item in enumerate(records):
        if not isinstance(item, dict):
            findings.append(f"archive_manifest_records[{index}] must be an object")
            continue
        prefix = f"archive_manifest_records[{index}]"
        decision = item.get("decision_type")
        src = source_records.get(decision)
        src_input = source_inputs.get(decision)
        src_blocker = source_blockers.get(decision)
        src_trigger = source_triggers.get(decision)
        if not src or not src_input or not src_blocker or not src_trigger:
            findings.append(f"{prefix}.decision_type has incomplete source references")
            continue
        expected_links = {
            "source_handoff_packet_record_id": src.get("handoff_packet_record_id"),
            "source_owner_r3_input_summary_id": src_input.get("handoff_owner_r3_input_summary_id"),
            "source_unresolved_blocker_summary_id": src_blocker.get("handoff_unresolved_blocker_summary_id"),
            "source_invalidating_trigger_summary_id": src_trigger.get("handoff_invalidating_trigger_summary_id"),
            "source_review_routing_id": src.get("review_routing_id"),
            "source_owner_r3_input_id": src.get("owner_r3_input_id"),
            "source_expiry_invalidating_trigger_id": src.get("expiry_invalidating_trigger_id"),
            "source_handoff_status": src.get("handoff_status"),
            "source_review_start_status": src.get("review_start_status"),
            "source_submission_status": src.get("submission_status"),
            "source_approval_status": src.get("approval_status"),
            "source_required_evidence_count": src.get("source_required_evidence_count"),
            "source_stale_evidence_trigger_count": src.get("source_stale_evidence_trigger_count"),
            "source_invalidating_event_count": src.get("source_invalidating_event_count"),
        }
        findings.extend(_expect_values(item, expected_links, prefix))
        findings.extend(
            _expect_values(
                item,
                {
                    "archive_state": "local_archive_rollback_manifest_draft_not_archived_externally",
                    "archive_status": "local_manifest_only_no_archive_write",
                    "retention_status": "local_metadata_only_no_private_customer_or_secret_data",
                    "supersession_status": "supersession_required_before_any_future_submission",
                    "rollback_status": "rollback_required_before_refresh_review_start_or_submission",
                    "manifest_status": "pass",
                },
                prefix,
            )
        )
        findings.extend(
            _expect_bools(
                item,
                (
                    "archive_record_is_submission",
                    "archive_record_is_approval",
                    "archive_manifest_is_public_clearance",
                    "actual_archive_written",
                    "actual_rollback_executed",
                    "actual_archive_deleted",
                    "actual_owner_review_started",
                    "actual_owner_r3_review_submitted",
                    "actual_refresh_executed",
                    "refresh_execution_allowed",
                    "actual_owner_approval_recorded",
                    "actual_owner_signature_collected",
                    "actual_approval_evidence_collected",
                    "public_use_approved",
                    "action_permitted_now",
                ),
                False,
                prefix,
            )
        )
        findings.extend(
            _expect_bools(
                item,
                (
                    "owner_r3_required_before_submission",
                    "owner_r3_required_before_review_start",
                    "archive_required_before_future_submission",
                    "rollback_required_on_invalidating_trigger",
                    "supersession_required_on_source_drift",
                    "public_use_blocked",
                    "final_export_blocked",
                    "external_action_blocked",
                    "customer_contact_blocked",
                    "crm_payment_blocked",
                    "secret_material_blocked",
                    "final_advice_blocked",
                    "kis_order_risk_prod_deploy_blocked",
                ),
                True,
                prefix,
            )
        )
    return findings


def _validate_rollback_records(manifest: dict[str, Any], source: dict[str, Any]) -> list[str]:
    records = manifest.get("rollback_trigger_records")
    if not isinstance(records, list):
        return ["rollback_trigger_records must be a list"]
    findings = _missing_decisions(records, "rollback_trigger_records")
    source_triggers = _by_decision(source.get("invalidating_trigger_summaries"))
    for index, item in enumerate(records):
        if not isinstance(item, dict):
            findings.append(f"rollback_trigger_records[{index}] must be an object")
            continue
        prefix = f"rollback_trigger_records[{index}]"
        src = source_triggers.get(item.get("decision_type"))
        if not src:
            findings.append(f"{prefix}.decision_type has no source trigger")
            continue
        findings.extend(
            _expect_values(
                item,
                {
                    "source_handoff_invalidating_trigger_summary_id": src.get("handoff_invalidating_trigger_summary_id"),
                    "source_submission_preflight_invalidating_trigger_id": src.get("source_submission_preflight_invalidating_trigger_id"),
                    "source_expiry_invalidating_trigger_id": src.get("source_expiry_invalidating_trigger_id"),
                    "invalidating_triggers": src.get("invalidating_triggers"),
                    "trigger_status": "covered",
                    "rollback_status": "required_before_future_submission_or_refresh",
                    "coverage_status": "covered",
                    "manifest_status": "pass",
                },
                prefix,
            )
        )
        if len(_string_list(item.get("invalidating_triggers"))) < 8:
            findings.append(f"{prefix}.invalidating_triggers must contain at least 8 items")
        findings.extend(_expect_bools(item, ("archive_rollback_required", "owner_r3_required_before_action"), True, prefix))
        findings.extend(
            _expect_bools(
                item,
                (
                    "refresh_execution_allowed",
                    "actual_refresh_executed",
                    "owner_r3_review_submission_allowed",
                    "actual_owner_review_started",
                    "actual_owner_r3_review_submitted",
                    "actual_archive_written",
                    "actual_rollback_executed",
                    "actual_archive_deleted",
                    "action_permitted_now",
                ),
                False,
                prefix,
            )
        )
    return findings


def _validate_retention_records(manifest: dict[str, Any]) -> list[str]:
    records = manifest.get("retention_supersession_records")
    if not isinstance(records, list):
        return ["retention_supersession_records must be a list"]
    findings = _missing_decisions(records, "retention_supersession_records")
    archive_ids = {
        item.get("archive_manifest_record_id")
        for item in manifest.get("archive_manifest_records", [])
        if isinstance(item, dict)
    }
    rollback_ids = {
        item.get("rollback_trigger_record_id")
        for item in manifest.get("rollback_trigger_records", [])
        if isinstance(item, dict)
    }
    for index, item in enumerate(records):
        if not isinstance(item, dict):
            findings.append(f"retention_supersession_records[{index}] must be an object")
            continue
        prefix = f"retention_supersession_records[{index}]"
        if item.get("source_archive_manifest_record_id") not in archive_ids:
            findings.append(f"{prefix}.source_archive_manifest_record_id must reference an archive record")
        if item.get("source_rollback_trigger_record_id") not in rollback_ids:
            findings.append(f"{prefix}.source_rollback_trigger_record_id must reference a rollback record")
        if len(_string_list(item.get("retention_requirements"))) < 7:
            findings.append(f"{prefix}.retention_requirements must contain at least 7 items")
        if len(_string_list(item.get("supersession_triggers"))) < 8:
            findings.append(f"{prefix}.supersession_triggers must contain at least 8 items")
        findings.extend(
            _expect_values(
                item,
                {
                    "retention_status": "local_metadata_only_no_private_customer_or_secret_data",
                    "supersession_status": "required_before_any_future_submission",
                    "manifest_status": "pass",
                },
                prefix,
            )
        )
        findings.extend(_expect_bools(item, ("owner_r3_required_before_action",), True, prefix))
        findings.extend(
            _expect_bools(
                item,
                (
                    "actual_archive_written",
                    "actual_rollback_executed",
                    "actual_archive_deleted",
                    "customer_private_data_retained",
                    "secret_material_retained",
                    "external_archive_upload_enabled",
                    "action_permitted_now",
                ),
                False,
                prefix,
            )
        )
    return findings


def _validate_blocked_scan(manifest: dict[str, Any], source: dict[str, Any]) -> list[str]:
    scan = manifest.get("blocked_action_scan")
    if not isinstance(scan, dict):
        return ["blocked_action_scan must be an object"]
    source_scan = source.get("blocked_action_scan", {})
    findings: list[str] = []
    missing = REQUIRED_BLOCKED_SCAN_KEYS - set(scan)
    if missing:
        findings.append(f"blocked_action_scan missing keys: {sorted(missing)}")
    for key in REQUIRED_BLOCKED_SCAN_KEYS:
        item = scan.get(key)
        if not isinstance(item, dict):
            findings.append(f"blocked_action_scan.{key} must be an object")
            continue
        if item != source_scan.get(key):
            findings.append(f"blocked_action_scan.{key} must match source blocked action scan")
        if item.get("status") != "pass":
            findings.append(f"blocked_action_scan.{key}.status must be pass")
        if item.get("blocked_all") is not True:
            findings.append(f"blocked_action_scan.{key}.blocked_all must be true")
        if item.get("matches") != []:
            findings.append(f"blocked_action_scan.{key}.matches must be empty")
    return findings


def _validate_steps_and_events(manifest: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    findings.extend(
        _validate_named_external_items(
            manifest.get("manifest_assembly_steps"),
            "step_id",
            REQUIRED_MANIFEST_STEPS,
            "manifest_assembly_steps",
        )
    )
    findings.extend(
        _validate_named_external_items(
            manifest.get("manifest_events"),
            "event",
            REQUIRED_MANIFEST_EVENTS,
            "manifest_events",
        )
    )
    return findings


def _validate_named_external_items(value: Any, id_key: str, required: set[str], label: str) -> list[str]:
    if not isinstance(value, list):
        return [f"{label} must be a list"]
    findings: list[str] = []
    ids = {item.get(id_key) for item in value if isinstance(item, dict)}
    for required_id in required - ids:
        findings.append(f"{label} missing {required_id}")
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            findings.append(f"{label}[{index}] must be an object")
            continue
        if item.get("external_action") is not False:
            findings.append(f"{label}[{index}].external_action must be false")
        if label == "manifest_assembly_steps" and item.get("owner_r3_required_before_action") is not True:
            findings.append(f"{label}[{index}].owner_r3_required_before_action must be true")
    return findings


def _validate_forbidden_outputs(manifest: dict[str, Any]) -> list[str]:
    outputs = set(_string_list(manifest.get("forbidden_outputs")))
    missing = REQUIRED_FORBIDDEN_OUTPUTS - outputs
    return [f"forbidden_outputs missing: {sorted(missing)}"] if missing else []


def _validate_handoff(manifest: dict[str, Any]) -> list[str]:
    handoff = manifest.get("taskset_handoff")
    if not isinstance(handoff, dict):
        return ["taskset_handoff must be an object"]
    findings: list[str] = []
    for key in ("task_156_manifest_ready", "taskset_local_scope_complete_when_task_closes"):
        if handoff.get(key) is not True:
            findings.append(f"taskset_handoff.{key} must be true")
    if "archive/rollback manifest audit/readiness preview" not in str(handoff.get("next_allowed_no_owner_slice", "")).lower():
        findings.append("taskset_handoff.next_allowed_no_owner_slice must describe archive/rollback manifest audit/readiness preview")
    r3_items = set(_string_list(handoff.get("owner_r3_required_for")))
    for required in (
        "actual Owner/R3 review submission",
        "actual Owner/R3 review start",
        "actual evidence refresh execution",
        "actual Owner approval record",
        "actual Owner signature",
        "actual approval evidence collection",
        "public use of any claim",
        "final PDF export",
        "SNS upload",
        "OAuth flow or platform API call",
        "secret or token handling",
    ):
        if required not in r3_items:
            findings.append(f"taskset_handoff.owner_r3_required_for missing {required}")
    return findings


def _validate_verification(manifest: dict[str, Any]) -> list[str]:
    verification = manifest.get("verification")
    if not isinstance(verification, dict):
        return ["verification must be an object"]
    expected = "promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_archive_rollback_manifest_gate.py --check"
    if expected not in str(verification.get("local_gate", "")):
        return ["verification.local_gate must reference this gate"]
    return []


def _by_decision(value: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(value, list):
        return {}
    return {item.get("decision_type"): item for item in value if isinstance(item, dict)}


def _missing_decisions(records: list[Any], label: str) -> list[str]:
    found = {item.get("decision_type") for item in records if isinstance(item, dict)}
    missing = REQUIRED_DECISION_TYPES - found
    return [f"{label} missing decision types: {sorted(missing)}"] if missing else []


def _expect_values(item: dict[str, Any], expected: dict[str, Any], prefix: str) -> list[str]:
    return [f"{prefix}.{key} must be {value}" for key, value in expected.items() if item.get(key) != value]


def _expect_bools(item: dict[str, Any], keys: tuple[str, ...], expected: bool, prefix: str) -> list[str]:
    return [f"{prefix}.{key} must be {str(expected).lower()}" for key in keys if item.get(key) is not expected]


def _safe_repo_path(repo_root: Path, rel_path: str) -> Path:
    if not rel_path or Path(rel_path).is_absolute():
        raise ValueError("path must be a non-empty relative path")
    resolved = (repo_root / rel_path).resolve()
    root = repo_root.resolve()
    if root not in resolved.parents and resolved != root:
        raise ValueError("path must stay inside repository")
    return resolved


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, dict) else {}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--check", action="store_true", help="validate and return non-zero on findings")
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    findings = validate_manifest(manifest)
    if findings:
        print("promotion asset Owner/R3 archive/rollback manifest gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"promotion asset Owner/R3 archive/rollback manifest gate: PASS ({args.manifest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
