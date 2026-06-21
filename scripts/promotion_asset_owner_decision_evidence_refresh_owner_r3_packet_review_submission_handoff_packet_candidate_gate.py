"""Validate the TASK-154 Owner/R3 packet review submission handoff packet candidate.

This validates local candidate metadata only. It rejects actual Owner/R3
review submission, review start, evidence refresh execution, approval records,
signatures, approval evidence collection, public approval, final exports,
customer/CRM/payment action, external account action, platform calls, secrets,
and drift from the source submission preflight audit preview.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANDIDATE = (
    REPO_ROOT
    / "agents"
    / "project"
    / "PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-REVIEW-SUBMISSION-HANDOFF-PACKET-CANDIDATE.json"
)
SOURCE_PREVIEW_PATH = (
    REPO_ROOT
    / "agents"
    / "project"
    / "PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-REVIEW-SUBMISSION-PREFLIGHT-AUDIT-PREVIEW.json"
)
SOURCE_ID = "promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_preflight_audit_preview"
SOURCE_REL = (
    "agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-REVIEW-SUBMISSION-PREFLIGHT-AUDIT-PREVIEW.json"
)

REQUIRED_DECISION_TYPES = {
    "public_landing_use",
    "final_pdf_export",
    "final_pptx_export",
    "sns_upload",
    "customer_contact",
    "crm_payment_setup",
    "paid_ads",
    "external_account_action",
    "legal_tax_securities_reliance",
}

REQUIRED_BOUNDARIES = {
    "local_owner_r3_packet_review_submission_handoff_packet_candidate_only",
    "handoff_packet_candidate_not_submission",
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
    "source_submission_preflight_record_summaries": 9,
    "handoff_packet_records": 9,
    "owner_r3_required_input_summaries": 9,
    "unresolved_blocker_summaries": 9,
    "invalidating_trigger_summaries": 9,
    "source_preflight_state_safety_scan_items": 6,
    "source_queue_state_safety_scan_items": 6,
    "source_state_reference_summaries": 5,
    "source_trigger_reference_summaries": 8,
    "blocked_action_scan_items": 13,
    "total_source_required_evidence_items": 25,
    "total_source_stale_evidence_trigger_items": 27,
    "total_source_invalidating_event_items": 36,
    "records_requiring_owner_r3": 9,
    "records_with_non_submission_status": 9,
    "records_with_non_approval_status": 9,
    "records_with_owner_review_not_started": 9,
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
    "live_action_states": 0,
}

REQUIRED_BLOCKED_SCAN_KEYS = {
    "actual_refresh_execution",
    "actual_owner_approval_record",
    "owner_signature",
    "approval_evidence_collection",
    "public_use",
    "final_export",
    "sns_upload",
    "external_action",
    "customer_contact",
    "crm_payment",
    "secret_material",
    "final_advice",
    "kis_order_risk_prod_deploy",
}

FORBIDDEN_KEY_NAMES = {
    "approval_signature",
    "approval_secret",
    "approved_by_owner",
    "approval_timestamp",
    "approval_evidence_file",
    "owner_signature_file",
    "owner_signature_value",
    "signature_image",
    "signed_packet_path",
    "owner_review_submission_log",
    "review_submission_receipt",
    "refresh_execution_log",
    "source_refresh_result_file",
    "external_source_result_file",
    "access_token",
    "refresh_token",
    "bot_token",
    "client_secret",
    "api_secret",
    "app_secret",
    "password",
    "cookie",
    "session",
    "customer_email",
    "customer_phone",
    "bank_account_number",
    "public_url",
    "external_upload_id",
    "final_pdf_path",
    "final_pptx_path",
    "pdf_binary_path",
    "pptx_binary_path",
    "payment_request_id",
    "customer_record_id",
    "legal_opinion",
    "tax_advice_final",
    "securities_advice_final",
    "kis_app_secret",
}

LIVE_TRUE_KEYS = {
    "actual_refresh_executed",
    "refresh_execution_allowed",
    "source_refresh_executed",
    "external_source_refresh_enabled",
    "actual_owner_review_started",
    "owner_review_submission_allowed",
    "owner_r3_review_submission_allowed",
    "review_submission_allowed",
    "actual_owner_r3_review_submitted",
    "queue_submitted_to_owner",
    "actual_owner_approval_recorded",
    "actual_owner_signature_collected",
    "owner_signature_collected",
    "owner_signature_allowed",
    "actual_approval_evidence_collected",
    "actual_approval_recorded",
    "action_permitted_now",
    "approval_evidence_collection_enabled",
    "evidence_collection_allowed",
    "review_submission_is_approval",
    "submission_preflight_is_submission",
    "submission_preflight_is_approval",
    "preflight_is_submission",
    "preflight_is_approval",
    "handoff_packet_is_submission",
    "handoff_packet_is_approval",
    "review_queue_is_approval",
    "review_queue_audit_is_approval",
    "packet_is_approval",
    "candidate_is_approval",
    "public_use_approved",
    "publication_approved",
    "claim_approved_for_publication",
    "final_advice_enabled",
    "final_export_enabled",
    "binary_export_enabled",
    "public_export_enabled",
    "external_upload_enabled",
    "customer_contact_enabled",
    "crm_action_enabled",
    "payment_action_enabled",
    "secret_storage_enabled",
    "live_post_enabled",
    "external_network_calls",
    "external_action_enabled",
    "paid_ads_enabled",
    "platform_api_call_enabled",
    "oauth_flow_enabled",
    "live_action",
    "public_action_allowed",
    "external_action_allowed",
}

REQUIRED_FORBIDDEN_OUTPUTS = {
    "actual Owner/R3 review submission",
    "actual Owner/R3 review start",
    "actual evidence refresh execution",
    "actual Owner approval record",
    "actual Owner signature",
    "actual approval evidence file",
    "approval evidence collection",
    "publication approval",
    "legal/tax/securities final advice",
    "final PDF binary",
    "final PPTX binary",
    "public landing page deployment",
    "SNS upload",
    "customer email or direct message",
    "CRM lead or customer record",
    "payment or checkout request",
    "external URL publication",
    "external account action",
    "OAuth flow",
    "platform API call",
    "secret or token material",
    "KIS/order/risk/prod/deploy change",
}


def load_candidate(path: Path = DEFAULT_CANDIDATE) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("promotion asset Owner/R3 handoff packet candidate root must be an object")
    return data


def validate_candidate(candidate: dict[str, Any], repo_root: Path = REPO_ROOT) -> list[str]:
    source = _load_json(SOURCE_PREVIEW_PATH)
    findings: list[str] = []

    if candidate.get("$schema") != (
        "autofolio.promotion-asset-owner-decision-evidence-refresh-owner-r3-packet-review-submission-handoff-packet-candidate/v1"
    ):
        findings.append("unexpected or missing promotion asset Owner/R3 handoff packet candidate schema")
    if candidate.get("status") != "local_owner_r3_packet_review_submission_handoff_packet_candidate_not_actual_submission":
        findings.append("status must be local_owner_r3_packet_review_submission_handoff_packet_candidate_not_actual_submission")

    findings.extend(_validate_boundaries(candidate))
    findings.extend(_validate_sources(candidate, repo_root))
    findings.extend(_validate_markdown(candidate, repo_root))
    findings.extend(_validate_summary(candidate, source))
    findings.extend(_validate_source_copies(candidate, source))
    findings.extend(_validate_records(candidate, source))
    findings.extend(_validate_inputs(candidate, source))
    findings.extend(_validate_blockers(candidate, source))
    findings.extend(_validate_triggers(candidate, source))
    findings.extend(_validate_blocked_scan(candidate, source))
    findings.extend(_validate_steps_and_events(candidate))
    findings.extend(_validate_forbidden_outputs(candidate))
    findings.extend(_validate_handoff(candidate))
    findings.extend(_validate_verification(candidate))

    forbidden_keys = _find_forbidden_keys(candidate)
    if forbidden_keys:
        findings.append(
            "forbidden review-submission/approval/signature/export/customer/secret/final-advice key names "
            f"present: {forbidden_keys}"
        )
    live_true_paths = _find_live_true_keys(candidate)
    if live_true_paths:
        findings.append(
            "review-start/submission/refresh/approval/signature/public/export/customer/payment/platform/"
            f"final-advice/live flags must not be true: {live_true_paths}"
        )
    return findings


def _validate_boundaries(candidate: dict[str, Any]) -> list[str]:
    boundaries = candidate.get("boundaries")
    if not isinstance(boundaries, dict):
        return ["boundaries must be an object"]
    return [f"boundaries.{key} must be true" for key in REQUIRED_BOUNDARIES if boundaries.get(key) is not True]


def _validate_sources(candidate: dict[str, Any], repo_root: Path) -> list[str]:
    inputs = candidate.get("source_inputs")
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


def _validate_markdown(candidate: dict[str, Any], repo_root: Path) -> list[str]:
    try:
        path = _safe_repo_path(repo_root, str(candidate.get("companion_markdown", "")))
    except ValueError as exc:
        return [f"companion_markdown invalid: {exc}"]
    if not path.exists():
        return [f"companion_markdown missing: {candidate.get('companion_markdown')}"]
    text = path.read_text(encoding="utf-8").lower()
    required = (
        "handoff packet candidate",
        "handoff packet candidate not submission",
        "handoff packet candidate not approval",
        "source preflight audit not submission",
        "source preflight audit not approval",
        "not actual owner/r3 review submission",
        "not actual owner/r3 review start",
        "not actual owner approval",
        "not actual owner signature",
        "not actual approval evidence",
        "handoff packet records",
        "owner/r3 required input summaries",
        "unresolved blocker summaries",
        "invalidating trigger summaries",
        "source reference coverage",
        "blocked action scan",
    )
    return [f"companion_markdown must mention {item}" for item in required if item not in text]


def _validate_summary(candidate: dict[str, Any], source: dict[str, Any]) -> list[str]:
    summary = candidate.get("candidate_summary")
    if not isinstance(summary, dict):
        return ["candidate_summary must be an object"]
    findings = [f"candidate_summary.{k} must be {v}" for k, v in REQUIRED_SUMMARY_COUNTS.items() if summary.get(k) != v]
    if summary.get("source_submission_preflight_audit_preview") != source.get("preview_id"):
        findings.append("candidate_summary.source_submission_preflight_audit_preview must match source preview_id")
    if summary.get("gate_result") != "pass":
        findings.append("candidate_summary.gate_result must be pass")
    source_summary = source.get("audit_summary", {})
    for key in (
        "total_source_required_evidence_items",
        "total_source_stale_evidence_trigger_items",
        "total_source_invalidating_event_items",
    ):
        if summary.get(key) != source_summary.get(key):
            findings.append(f"candidate_summary.{key} must match source audit summary")
    return findings


def _validate_source_copies(candidate: dict[str, Any], source: dict[str, Any]) -> list[str]:
    pairs = (
        ("source_preflight_state_safety_scan", "preflight_state_safety_scan"),
        ("source_queue_state_safety_scan", "source_queue_state_safety_scan"),
        ("source_state_reference_safety_scan", "source_state_reference_safety_scan"),
        ("source_trigger_reference_coverage_scan", "source_trigger_reference_coverage_scan"),
    )
    return [f"{key} must match source preview {src}" for key, src in pairs if candidate.get(key) != source.get(src)]


def _validate_records(candidate: dict[str, Any], source: dict[str, Any]) -> list[str]:
    records = candidate.get("handoff_packet_records")
    if not isinstance(records, list):
        return ["handoff_packet_records must be a list"]
    source_by_type = _by_decision(source.get("submission_preflight_record_summaries"))
    findings = _missing_decisions(records, "handoff_packet_records")
    for index, item in enumerate(records):
        if not isinstance(item, dict):
            findings.append(f"handoff_packet_records[{index}] must be an object")
            continue
        prefix = f"handoff_packet_records[{index}]"
        src = source_by_type.get(item.get("decision_type"))
        if not src:
            findings.append(f"{prefix}.decision_type has no source preflight summary")
            continue
        links = {
            "source_submission_preflight_record_id": "submission_preflight_record_id",
            "source_review_queue_record_id": "source_review_queue_record_id",
            "source_packet_candidate_id": "source_packet_candidate_id",
            "source_work_order_id": "source_work_order_id",
            "source_queue_record_id": "source_queue_record_id",
            "source_record_id": "source_record_id",
            "source_preflight_state": "preflight_state",
            "source_preflight_status": "preflight_status",
            "source_submission_status": "submission_status",
            "source_approval_status": "approval_status",
            "source_required_evidence_count": "source_required_evidence_count",
            "source_stale_evidence_trigger_count": "source_stale_evidence_trigger_count",
            "source_invalidating_event_count": "source_invalidating_event_count",
            "source_precondition_count": "source_precondition_count",
            "source_proof_requirement_count": "source_proof_requirement_count",
            "source_expiry_trigger_count": "source_expiry_trigger_count",
            "review_routing_id": "review_routing_id",
            "owner_r3_input_id": "owner_r3_input_id",
            "expiry_invalidating_trigger_id": "expiry_invalidating_trigger_id",
        }
        for key, src_key in links.items():
            if item.get(key) != src.get(src_key):
                findings.append(f"{prefix}.{key} must match source preflight summary")
        expected = {
            "packet_candidate_state": "local_handoff_packet_candidate_draft_not_submitted",
            "handoff_status": "local_candidate_only_not_submitted",
            "review_start_status": "not_started",
            "submission_status": "not_submitted",
            "approval_status": "not_approved",
            "candidate_status": "pass",
        }
        findings.extend(_expect_values(item, expected, prefix))
        false_keys = (
            "handoff_packet_is_submission",
            "handoff_packet_is_approval",
            "actual_owner_review_started",
            "actual_owner_r3_review_submitted",
            "actual_refresh_executed",
            "refresh_execution_allowed",
            "actual_owner_approval_recorded",
            "actual_owner_signature_collected",
            "actual_approval_evidence_collected",
            "public_use_approved",
            "action_permitted_now",
        )
        true_keys = (
            "archive_rollback_required",
            "owner_r3_required_before_submission",
            "owner_r3_required_before_review_start",
            "public_use_blocked",
            "final_export_blocked",
            "external_action_blocked",
            "customer_contact_blocked",
            "crm_payment_blocked",
            "secret_material_blocked",
            "final_advice_blocked",
            "kis_order_risk_prod_deploy_blocked",
        )
        findings.extend(_expect_bools(item, false_keys, False, prefix))
        findings.extend(_expect_bools(item, true_keys, True, prefix))
    return findings


def _validate_inputs(candidate: dict[str, Any], source: dict[str, Any]) -> list[str]:
    records = candidate.get("owner_r3_required_input_summaries")
    if not isinstance(records, list):
        return ["owner_r3_required_input_summaries must be a list"]
    source_by_type = _by_decision(source.get("owner_r3_decision_package_input_summaries"))
    findings = _missing_decisions(records, "owner_r3_required_input_summaries")
    for index, item in enumerate(records):
        if not isinstance(item, dict):
            findings.append(f"owner_r3_required_input_summaries[{index}] must be an object")
            continue
        prefix = f"owner_r3_required_input_summaries[{index}]"
        src = source_by_type.get(item.get("decision_type"))
        if not src:
            findings.append(f"{prefix}.decision_type has no source owner/R3 input summary")
            continue
        if item.get("source_owner_r3_decision_package_input_id") != src.get("owner_r3_decision_package_input_id"):
            findings.append(f"{prefix}.source_owner_r3_decision_package_input_id must match source")
        if item.get("source_owner_r3_input_id") != src.get("source_owner_r3_input_id"):
            findings.append(f"{prefix}.source_owner_r3_input_id must match source")
        if item.get("required_inputs") != src.get("required_inputs"):
            findings.append(f"{prefix}.required_inputs must match source")
        if len(_string_list(item.get("required_inputs"))) < 7:
            findings.append(f"{prefix}.required_inputs must contain at least 7 items")
        findings.extend(_expect_values(item, {"input_status": "missing_required_owner_r3_inputs", "candidate_status": "pass"}, prefix))
        findings.extend(_expect_bools(item, ("owner_r3_required",), True, prefix))
        findings.extend(
            _expect_bools(
                item,
                (
                    "handoff_packet_includes_actual_input_values",
                    "actual_owner_review_started",
                    "actual_owner_r3_review_submitted",
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
    return findings


def _validate_blockers(candidate: dict[str, Any], source: dict[str, Any]) -> list[str]:
    records = candidate.get("unresolved_blocker_summaries")
    if not isinstance(records, list):
        return ["unresolved_blocker_summaries must be a list"]
    source_by_type = _by_decision(source.get("submission_blocker_summaries"))
    findings = _missing_decisions(records, "unresolved_blocker_summaries")
    for index, item in enumerate(records):
        if not isinstance(item, dict):
            findings.append(f"unresolved_blocker_summaries[{index}] must be an object")
            continue
        prefix = f"unresolved_blocker_summaries[{index}]"
        src = source_by_type.get(item.get("decision_type"))
        if not src:
            findings.append(f"{prefix}.decision_type has no source blocker")
            continue
        if item.get("source_submission_blocker_record_id") != src.get("submission_blocker_record_id"):
            findings.append(f"{prefix}.source_submission_blocker_record_id must match source")
        if item.get("blockers") != src.get("blockers"):
            findings.append(f"{prefix}.blockers must match source")
        if len(_string_list(item.get("blockers"))) < 7:
            findings.append(f"{prefix}.blockers must contain at least 7 items")
        findings.extend(_expect_values(item, {"blocker_status": "blocked_pending_owner_r3", "candidate_status": "pass"}, prefix))
        findings.extend(_expect_bools(item, ("owner_r3_required_before_action",), True, prefix))
        findings.extend(
            _expect_bools(
                item,
                (
                    "actual_owner_review_started",
                    "actual_owner_r3_review_submitted",
                    "actual_owner_approval_recorded",
                    "actual_owner_signature_collected",
                    "actual_approval_evidence_collected",
                    "action_permitted_now",
                ),
                False,
                prefix,
            )
        )
    return findings


def _validate_triggers(candidate: dict[str, Any], source: dict[str, Any]) -> list[str]:
    records = candidate.get("invalidating_trigger_summaries")
    if not isinstance(records, list):
        return ["invalidating_trigger_summaries must be a list"]
    source_by_type = _by_decision(source.get("invalidating_trigger_summaries"))
    findings = _missing_decisions(records, "invalidating_trigger_summaries")
    for index, item in enumerate(records):
        if not isinstance(item, dict):
            findings.append(f"invalidating_trigger_summaries[{index}] must be an object")
            continue
        prefix = f"invalidating_trigger_summaries[{index}]"
        src = source_by_type.get(item.get("decision_type"))
        if not src:
            findings.append(f"{prefix}.decision_type has no source trigger")
            continue
        source_key_map = {
            "source_submission_preflight_invalidating_trigger_id": "submission_preflight_invalidating_trigger_id",
            "source_expiry_invalidating_trigger_id": "source_expiry_invalidating_trigger_id",
            "invalidating_triggers": "invalidating_triggers",
        }
        for key, src_key in source_key_map.items():
            if item.get(key) != src.get(src_key):
                findings.append(f"{prefix}.{key} must match source")
        if len(_string_list(item.get("invalidating_triggers"))) < 8:
            findings.append(f"{prefix}.invalidating_triggers must contain at least 8 items")
        findings.extend(_expect_values(item, {"coverage_status": "covered", "candidate_status": "pass"}, prefix))
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
                    "action_permitted_now",
                ),
                False,
                prefix,
            )
        )
    return findings


def _validate_blocked_scan(candidate: dict[str, Any], source: dict[str, Any]) -> list[str]:
    scan = candidate.get("blocked_action_scan")
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


def _validate_steps_and_events(candidate: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    required_steps = {
        "record_source_hash",
        "summarize_preflight_records",
        "summarize_required_owner_r3_inputs",
        "summarize_unresolved_blockers",
        "summarize_invalidating_triggers",
        "copy_source_references",
        "scan_blocked_actions",
    }
    findings.extend(_validate_named_external_items(candidate.get("handoff_packet_assembly_steps"), "step_id", required_steps, "handoff_packet_assembly_steps"))
    required_events = {
        "handoff_packet_candidate_generated",
        "source_preflight_audit_preview_hash_recorded",
        "handoff_packet_records_recorded",
        "owner_r3_required_inputs_summarized",
        "unresolved_blockers_summarized",
        "invalidating_trigger_coverage_recorded",
        "source_reference_coverage_recorded",
        "blocked_action_scan_passed",
    }
    findings.extend(_validate_named_external_items(candidate.get("candidate_events"), "event", required_events, "candidate_events"))
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
        if label == "handoff_packet_assembly_steps" and item.get("owner_r3_required_before_action") is not True:
            findings.append(f"{label}[{index}].owner_r3_required_before_action must be true")
    return findings


def _validate_forbidden_outputs(candidate: dict[str, Any]) -> list[str]:
    outputs = set(_string_list(candidate.get("forbidden_outputs")))
    missing = REQUIRED_FORBIDDEN_OUTPUTS - outputs
    return [f"forbidden_outputs missing: {sorted(missing)}"] if missing else []


def _validate_handoff(candidate: dict[str, Any]) -> list[str]:
    handoff = candidate.get("taskset_handoff")
    if not isinstance(handoff, dict):
        return ["taskset_handoff must be an object"]
    findings: list[str] = []
    for key in ("task_154_candidate_ready", "taskset_local_scope_complete_when_task_closes"):
        if handoff.get(key) is not True:
            findings.append(f"taskset_handoff.{key} must be true")
    if "handoff packet candidate audit/readiness preview" not in str(handoff.get("next_allowed_no_owner_slice", "")).lower():
        findings.append("taskset_handoff.next_allowed_no_owner_slice must describe handoff packet candidate audit/readiness preview")
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


def _validate_verification(candidate: dict[str, Any]) -> list[str]:
    verification = candidate.get("verification")
    if not isinstance(verification, dict):
        return ["verification must be an object"]
    expected = "promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_gate.py --check"
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
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--check", action="store_true", help="validate and return non-zero on findings")
    args = parser.parse_args()

    candidate = load_candidate(args.candidate)
    findings = validate_candidate(candidate)
    if findings:
        print("promotion asset Owner/R3 packet review submission handoff packet candidate gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"promotion asset Owner/R3 packet review submission handoff packet candidate gate: PASS ({args.candidate})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
