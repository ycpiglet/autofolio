"""Validate the TASK-149 promotion asset Owner/R3 packet candidate audit preview.

This gate validates local audit/readiness preview metadata only. It rejects
actual evidence refresh execution, actual Owner approval records, Owner
signatures, approval evidence collection, public approval, final advice, final
asset export, live publishing, customer contact, CRM/payment action, external
account action, platform calls, secret fields, and missing packet-candidate,
evidence-bundle, Owner-prompt, unresolved-blocker, state/trigger-reference, or
blocked-action coverage.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PREVIEW = (
    REPO_ROOT
    / "agents"
    / "project"
    / "PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-CANDIDATE-AUDIT-PREVIEW.json"
)
SOURCE_CONTRACT_PATH = (
    REPO_ROOT
    / "agents"
    / "project"
    / "PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-CANDIDATE.json"
)

REQUIRED_SOURCE_IDS = {"promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_candidate_contract"}
EXPECTED_SOURCE_PATHS = {
    "promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_candidate_contract": (
        "agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-CANDIDATE.json"
    ),
}

REQUIRED_BOUNDARIES = {
    "local_owner_r3_packet_candidate_audit_readiness_preview_only",
    "packet_candidate_audit_not_approval",
    "packet_candidate_not_approval",
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

PACKET_REQUIRED_FALSE_FLAGS = {
    "actual_refresh_executed",
    "refresh_execution_allowed",
    "actual_owner_approval_recorded",
    "actual_owner_signature_collected",
    "actual_approval_evidence_collected",
    "packet_is_approval",
    "public_use_approved",
    "action_permitted_now",
}

PACKET_REQUIRED_TRUE_FLAGS = {
    "owner_r3_required_before_decision",
    "public_use_blocked",
    "final_export_blocked",
    "external_action_blocked",
    "customer_contact_blocked",
    "crm_payment_blocked",
    "secret_material_blocked",
    "final_advice_blocked",
    "kis_order_risk_prod_deploy_blocked",
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

REQUIRED_SUMMARY_COUNTS = {
    "decision_types": 9,
    "source_packet_candidate_records": 9,
    "packet_candidate_record_summaries": 9,
    "evidence_bundle_reference_summaries": 9,
    "owner_decision_prompt_summaries": 9,
    "unresolved_blocker_summaries": 9,
    "source_state_reference_summaries": 5,
    "source_trigger_reference_summaries": 8,
    "source_blocked_action_scan_items": 13,
    "total_source_required_evidence_items": 25,
    "total_source_stale_evidence_trigger_items": 27,
    "total_source_invalidating_event_items": 36,
    "records_requiring_owner_r3": 9,
    "records_with_non_approval_status": 9,
    "prompts_with_draft_candidate_status": 9,
    "unresolved_blocker_records": 9,
    "states_with_safe_flags": 5,
    "triggers_blocked_from_refresh": 8,
    "blocked_scan_items_passed": 13,
    "ready_for_public_use_records": 0,
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
    "actual_owner_approval_recorded",
    "actual_owner_signature_collected",
    "owner_signature_collected",
    "owner_signature_allowed",
    "actual_approval_evidence_collected",
    "actual_approval_recorded",
    "action_permitted_now",
    "approval_evidence_collection_enabled",
    "evidence_collection_allowed",
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
}

REQUIRED_FORBIDDEN_OUTPUTS = {
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


def load_preview(path: Path = DEFAULT_PREVIEW) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("promotion asset Owner/R3 packet candidate audit preview root must be an object")
    return data


def validate_preview(preview: dict[str, Any], repo_root: Path = REPO_ROOT) -> list[str]:
    findings: list[str] = []

    if preview.get("$schema") != (
        "autofolio.promotion-asset-owner-decision-evidence-refresh-owner-r3-packet-candidate-audit-preview/v1"
    ):
        findings.append("unexpected or missing promotion asset Owner/R3 packet candidate audit preview schema")

    if preview.get("status") != "local_owner_r3_packet_candidate_audit_readiness_preview_not_actual_approval":
        findings.append("status must be local_owner_r3_packet_candidate_audit_readiness_preview_not_actual_approval")

    boundaries = preview.get("boundaries")
    if not isinstance(boundaries, dict):
        findings.append("boundaries must be an object")
    else:
        for key in REQUIRED_BOUNDARIES:
            if boundaries.get(key) is not True:
                findings.append(f"boundaries.{key} must be true")

    forbidden_keys = _find_forbidden_keys(preview)
    if forbidden_keys:
        findings.append(
            "forbidden refresh/approval/signature/export/customer/secret/final-advice key names present: "
            f"{forbidden_keys}"
        )

    live_true_paths = _find_live_true_keys(preview)
    if live_true_paths:
        findings.append(
            "refresh/approval/signature/public/export/customer/payment/platform/final-advice/live flags must not "
            f"be true: {live_true_paths}"
        )

    findings.extend(_validate_sources(preview, repo_root))
    findings.extend(_validate_markdown_companion(preview, repo_root))
    findings.extend(_validate_summary(preview))
    findings.extend(_validate_packet_candidate_record_summaries(preview))
    findings.extend(_validate_evidence_bundle_reference_summaries(preview))
    findings.extend(_validate_owner_decision_prompt_summaries(preview))
    findings.extend(_validate_unresolved_blocker_summaries(preview))
    findings.extend(_validate_state_reference_safety_scan(preview))
    findings.extend(_validate_trigger_reference_coverage_scan(preview))
    findings.extend(_validate_blocked_action_scan(preview))
    findings.extend(_validate_events(preview))
    findings.extend(_validate_forbidden_outputs(preview))
    findings.extend(_validate_handoff(preview))
    findings.extend(_validate_verification(preview))
    return findings


def _validate_sources(preview: dict[str, Any], repo_root: Path) -> list[str]:
    inputs = preview.get("source_inputs")
    if not isinstance(inputs, list):
        return ["source_inputs must be a list"]
    findings: list[str] = []
    source_ids = {item.get("id") for item in inputs if isinstance(item, dict)}
    missing = REQUIRED_SOURCE_IDS - source_ids
    if missing:
        findings.append(f"source_inputs missing ids: {sorted(missing)}")
    for index, item in enumerate(inputs):
        if not isinstance(item, dict):
            findings.append(f"source_inputs[{index}] must be an object")
            continue
        source_id = str(item.get("id", ""))
        rel_path = str(item.get("path", ""))
        expected = EXPECTED_SOURCE_PATHS.get(source_id)
        if expected and rel_path != expected:
            findings.append(f"source_inputs[{index}].path for {source_id} must be {expected}")
        try:
            path = _safe_repo_path(repo_root, rel_path)
        except ValueError as exc:
            findings.append(f"source_inputs[{index}].path invalid: {exc}")
            continue
        if not path.exists():
            findings.append(f"source_inputs[{index}].path missing: {rel_path}")
            continue
        if str(item.get("sha256", "")).lower() != _sha256(path):
            findings.append(f"source_inputs[{index}].sha256 mismatch for {rel_path}")
    return findings


def _validate_markdown_companion(preview: dict[str, Any], repo_root: Path) -> list[str]:
    rel_path = str(preview.get("companion_markdown", ""))
    try:
        path = _safe_repo_path(repo_root, rel_path)
    except ValueError as exc:
        return [f"companion_markdown invalid: {exc}"]
    if not path.exists():
        return [f"companion_markdown missing: {rel_path}"]
    text = path.read_text(encoding="utf-8").lower()
    findings: list[str] = []
    for required in (
        "packet candidate audit/readiness preview",
        "packet candidate not approval",
        "not actual owner approval",
        "not actual owner signature",
        "not actual approval evidence",
        "packet candidate record summaries",
        "evidence bundle reference summaries",
        "owner decision prompt summaries",
        "unresolved blocker summaries",
        "blocked action scan",
        "owner/r3",
    ):
        if required not in text:
            findings.append(f"companion_markdown must mention {required}")
    return findings


def _validate_summary(preview: dict[str, Any]) -> list[str]:
    summary = preview.get("audit_summary")
    if not isinstance(summary, dict):
        return ["audit_summary must be an object"]
    findings: list[str] = []
    for key, expected in REQUIRED_SUMMARY_COUNTS.items():
        if summary.get(key) != expected:
            findings.append(f"audit_summary.{key} must be {expected}")
    if summary.get("gate_result") != "pass":
        findings.append("audit_summary.gate_result must be pass")
    return findings


def _validate_packet_candidate_record_summaries(preview: dict[str, Any]) -> list[str]:
    summaries = preview.get("packet_candidate_record_summaries")
    if not isinstance(summaries, list):
        return ["packet_candidate_record_summaries must be a list"]
    source = _load_json(SOURCE_CONTRACT_PATH)
    source_records = _records_by_decision_type(source.get("packet_candidate_records"))
    findings: list[str] = []
    missing = REQUIRED_DECISION_TYPES - {item.get("decision_type") for item in summaries if isinstance(item, dict)}
    if missing:
        findings.append(f"packet_candidate_record_summaries missing decision types: {sorted(missing)}")
    for index, item in enumerate(summaries):
        if not isinstance(item, dict):
            findings.append(f"packet_candidate_record_summaries[{index}] must be an object")
            continue
        prefix = f"packet_candidate_record_summaries[{index}]"
        source_record = source_records.get(item.get("decision_type"))
        if not isinstance(source_record, dict):
            findings.append(f"{prefix}.decision_type unknown")
            continue
        for key in (
            "packet_candidate_id",
            "source_work_order_id",
            "source_queue_record_id",
            "source_record_id",
            "source_current_work_order_state",
            "source_required_evidence_count",
            "source_stale_evidence_trigger_count",
            "source_invalidating_event_count",
            "precondition_count",
            "proof_requirement_count",
            "expiry_trigger_count",
            "archive_rollback_required",
            "source_work_order_status",
            "candidate_status",
            "approval_status",
        ):
            if item.get(key) != source_record.get(key):
                findings.append(f"{prefix}.{key} must match source packet candidate")
        for key in PACKET_REQUIRED_FALSE_FLAGS:
            if item.get(key) != source_record.get(key):
                findings.append(f"{prefix}.{key} must match source packet candidate")
            if item.get(key) is not False:
                findings.append(f"{prefix}.{key} must be false")
        for key in PACKET_REQUIRED_TRUE_FLAGS:
            if item.get(key) != source_record.get(key):
                findings.append(f"{prefix}.{key} must match source packet candidate")
            if item.get(key) is not True:
                findings.append(f"{prefix}.{key} must be true")
        if item.get("source_audit_status") != source_record.get("audit_status"):
            findings.append(f"{prefix}.source_audit_status must match source audit_status")
        if item.get("audit_status") != "pass":
            findings.append(f"{prefix}.audit_status must be pass")
    return findings


def _validate_evidence_bundle_reference_summaries(preview: dict[str, Any]) -> list[str]:
    summaries = preview.get("evidence_bundle_reference_summaries")
    if not isinstance(summaries, list):
        return ["evidence_bundle_reference_summaries must be a list"]
    source = _load_json(SOURCE_CONTRACT_PATH)
    source_records = _records_by_decision_type(source.get("evidence_bundle_references"))
    findings: list[str] = []
    missing = REQUIRED_DECISION_TYPES - {item.get("decision_type") for item in summaries if isinstance(item, dict)}
    if missing:
        findings.append(f"evidence_bundle_reference_summaries missing decision types: {sorted(missing)}")
    for index, item in enumerate(summaries):
        if not isinstance(item, dict):
            findings.append(f"evidence_bundle_reference_summaries[{index}] must be an object")
            continue
        prefix = f"evidence_bundle_reference_summaries[{index}]"
        source_record = source_records.get(item.get("decision_type"))
        if not isinstance(source_record, dict):
            findings.append(f"{prefix}.decision_type unknown")
            continue
        for key in (
            "evidence_bundle_reference_id",
            "source_work_order_id",
            "required_evidence_count",
            "stale_evidence_trigger_count",
            "invalidating_event_count",
            "precondition_count",
            "proof_requirement_count",
            "expiry_trigger_count",
            "archive_rollback_required",
            "source_hash_required",
            "collection_status",
            "actual_approval_evidence_collected",
            "status",
        ):
            if item.get(key) != source_record.get(key):
                findings.append(f"{prefix}.{key} must match source evidence bundle reference")
        if item.get("collection_status") != "not_collected_candidate_reference_only":
            findings.append(f"{prefix}.collection_status must be not_collected_candidate_reference_only")
        if item.get("actual_approval_evidence_collected") is not False:
            findings.append(f"{prefix}.actual_approval_evidence_collected must be false")
        if item.get("audit_status") != "pass":
            findings.append(f"{prefix}.audit_status must be pass")
    return findings


def _validate_owner_decision_prompt_summaries(preview: dict[str, Any]) -> list[str]:
    summaries = preview.get("owner_decision_prompt_summaries")
    if not isinstance(summaries, list):
        return ["owner_decision_prompt_summaries must be a list"]
    source = _load_json(SOURCE_CONTRACT_PATH)
    source_records = _records_by_decision_type(source.get("owner_decision_prompt_map"))
    findings: list[str] = []
    missing = REQUIRED_DECISION_TYPES - {item.get("decision_type") for item in summaries if isinstance(item, dict)}
    if missing:
        findings.append(f"owner_decision_prompt_summaries missing decision types: {sorted(missing)}")
    for index, item in enumerate(summaries):
        if not isinstance(item, dict):
            findings.append(f"owner_decision_prompt_summaries[{index}] must be an object")
            continue
        prefix = f"owner_decision_prompt_summaries[{index}]"
        source_record = source_records.get(item.get("decision_type"))
        if not isinstance(source_record, dict):
            findings.append(f"{prefix}.decision_type unknown")
            continue
        for key in (
            "owner_decision_prompt_id",
            "decision_required",
            "candidate_is_approval",
            "actual_owner_approval_recorded",
            "actual_owner_signature_collected",
            "public_use_approved",
            "action_permitted_now",
            "professional_review_required",
            "prompt_status",
            "status",
        ):
            if item.get(key) != source_record.get(key):
                findings.append(f"{prefix}.{key} must match source Owner decision prompt")
        for key in ("candidate_is_approval", "actual_owner_approval_recorded", "actual_owner_signature_collected", "public_use_approved", "action_permitted_now"):
            if item.get(key) is not False:
                findings.append(f"{prefix}.{key} must be false")
        if item.get("decision_required") is not True:
            findings.append(f"{prefix}.decision_required must be true")
        if item.get("prompt_status") != "draft_candidate_only":
            findings.append(f"{prefix}.prompt_status must be draft_candidate_only")
        if item.get("audit_status") != "pass":
            findings.append(f"{prefix}.audit_status must be pass")
    return findings


def _validate_unresolved_blocker_summaries(preview: dict[str, Any]) -> list[str]:
    summaries = preview.get("unresolved_blocker_summaries")
    if not isinstance(summaries, list):
        return ["unresolved_blocker_summaries must be a list"]
    source = _load_json(SOURCE_CONTRACT_PATH)
    source_records = _records_by_decision_type(source.get("unresolved_blocker_map"))
    findings: list[str] = []
    missing = REQUIRED_DECISION_TYPES - {item.get("decision_type") for item in summaries if isinstance(item, dict)}
    if missing:
        findings.append(f"unresolved_blocker_summaries missing decision types: {sorted(missing)}")
    for index, item in enumerate(summaries):
        if not isinstance(item, dict):
            findings.append(f"unresolved_blocker_summaries[{index}] must be an object")
            continue
        prefix = f"unresolved_blocker_summaries[{index}]"
        source_record = source_records.get(item.get("decision_type"))
        if not isinstance(source_record, dict):
            findings.append(f"{prefix}.decision_type unknown")
            continue
        for key in (
            "blocker_id",
            "unresolved_blocker_count",
            "owner_r3_required",
            "action_permitted_now",
            "public_use_blocked",
            "final_export_blocked",
            "status",
        ):
            if item.get(key) != source_record.get(key):
                findings.append(f"{prefix}.{key} must match source unresolved blocker")
        if item.get("blockers") != source_record.get("blockers"):
            findings.append(f"{prefix}.blockers must match source unresolved blocker")
        if item.get("owner_r3_required") is not True:
            findings.append(f"{prefix}.owner_r3_required must be true")
        if item.get("action_permitted_now") is not False:
            findings.append(f"{prefix}.action_permitted_now must be false")
        if item.get("status") != "blocked_pending_owner_r3":
            findings.append(f"{prefix}.status must be blocked_pending_owner_r3")
        if item.get("audit_status") != "pass":
            findings.append(f"{prefix}.audit_status must be pass")
    return findings


def _validate_state_reference_safety_scan(preview: dict[str, Any]) -> list[str]:
    summaries = preview.get("source_state_reference_safety_scan")
    if not isinstance(summaries, list):
        return ["source_state_reference_safety_scan must be a list"]
    source = _load_json(SOURCE_CONTRACT_PATH)
    source_records = {
        item.get("state_id"): item
        for item in source.get("source_state_safety_references", [])
        if isinstance(item, dict)
    }
    findings: list[str] = []
    missing = set(source_records) - {item.get("state_id") for item in summaries if isinstance(item, dict)}
    if missing:
        findings.append(f"source_state_reference_safety_scan missing state ids: {sorted(missing)}")
    for index, item in enumerate(summaries):
        if not isinstance(item, dict):
            findings.append(f"source_state_reference_safety_scan[{index}] must be an object")
            continue
        prefix = f"source_state_reference_safety_scan[{index}]"
        source_record = source_records.get(item.get("state_id"))
        if not isinstance(source_record, dict):
            findings.append(f"{prefix}.state_id unknown")
            continue
        for key in (
            "live_action",
            "refresh_execution_allowed",
            "actual_refresh_executed",
            "action_permitted_now",
            "actual_approval_recorded",
            "actual_approval_evidence_collected",
            "owner_r3_required_before_action",
            "status",
        ):
            if item.get(key) != source_record.get(key):
                findings.append(f"{prefix}.{key} must match source state reference")
        for key in ("live_action", "refresh_execution_allowed", "actual_refresh_executed", "action_permitted_now", "actual_approval_recorded", "actual_approval_evidence_collected"):
            if item.get(key) is not False:
                findings.append(f"{prefix}.{key} must be false")
        if item.get("audit_status") != "pass":
            findings.append(f"{prefix}.audit_status must be pass")
    return findings


def _validate_trigger_reference_coverage_scan(preview: dict[str, Any]) -> list[str]:
    summaries = preview.get("source_trigger_reference_coverage_scan")
    if not isinstance(summaries, list):
        return ["source_trigger_reference_coverage_scan must be a list"]
    source = _load_json(SOURCE_CONTRACT_PATH)
    source_records = {
        item.get("trigger_id"): item
        for item in source.get("source_trigger_references", [])
        if isinstance(item, dict)
    }
    findings: list[str] = []
    missing = set(source_records) - {item.get("trigger_id") for item in summaries if isinstance(item, dict)}
    if missing:
        findings.append(f"source_trigger_reference_coverage_scan missing trigger ids: {sorted(missing)}")
    for index, item in enumerate(summaries):
        if not isinstance(item, dict):
            findings.append(f"source_trigger_reference_coverage_scan[{index}] must be an object")
            continue
        prefix = f"source_trigger_reference_coverage_scan[{index}]"
        source_record = source_records.get(item.get("trigger_id"))
        if not isinstance(source_record, dict):
            findings.append(f"{prefix}.trigger_id unknown")
            continue
        for key in (
            "target_work_order_state",
            "archive_required",
            "refresh_execution_allowed",
            "actual_refresh_executed",
            "action_permitted_now",
            "owner_r3_required_before_action",
            "coverage_status",
            "status",
        ):
            if item.get(key) != source_record.get(key):
                findings.append(f"{prefix}.{key} must match source trigger reference")
        for key in ("refresh_execution_allowed", "actual_refresh_executed", "action_permitted_now"):
            if item.get(key) is not False:
                findings.append(f"{prefix}.{key} must be false")
        if item.get("audit_status") != "pass":
            findings.append(f"{prefix}.audit_status must be pass")
    return findings


def _validate_blocked_action_scan(preview: dict[str, Any]) -> list[str]:
    scan = preview.get("blocked_action_scan")
    if not isinstance(scan, dict):
        return ["blocked_action_scan must be an object"]
    source = _load_json(SOURCE_CONTRACT_PATH)
    source_scan = source.get("blocked_action_scan")
    if not isinstance(source_scan, dict):
        source_scan = {}
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


def _validate_events(preview: dict[str, Any]) -> list[str]:
    events = preview.get("audit_events")
    if not isinstance(events, list):
        return ["audit_events must be a list"]
    findings: list[str] = []
    event_names = {item.get("event") for item in events if isinstance(item, dict)}
    for required in (
        "owner_r3_packet_candidate_audit_preview_generated",
        "packet_candidate_record_summaries_recorded",
        "evidence_bundle_reference_coverage_recorded",
        "owner_decision_prompt_coverage_recorded",
        "unresolved_blocker_coverage_recorded",
        "source_state_trigger_reference_coverage_recorded",
        "blocked_action_scan_passed",
    ):
        if required not in event_names:
            findings.append(f"audit_events missing {required}")
    for index, event in enumerate(events):
        if isinstance(event, dict) and event.get("external_action") is not False:
            findings.append(f"audit_events[{index}].external_action must be false")
    return findings


def _validate_forbidden_outputs(preview: dict[str, Any]) -> list[str]:
    outputs = set(_string_list(preview.get("forbidden_outputs")))
    missing = REQUIRED_FORBIDDEN_OUTPUTS - outputs
    if missing:
        return [f"forbidden_outputs missing: {sorted(missing)}"]
    return []


def _validate_handoff(preview: dict[str, Any]) -> list[str]:
    handoff = preview.get("taskset_handoff")
    if not isinstance(handoff, dict):
        return ["taskset_handoff must be an object"]
    findings: list[str] = []
    for key in ("task_149_preview_ready", "taskset_local_scope_complete_when_task_closes"):
        if handoff.get(key) is not True:
            findings.append(f"taskset_handoff.{key} must be true")
    r3_items = set(_string_list(handoff.get("owner_r3_required_for")))
    for required in (
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


def _validate_verification(preview: dict[str, Any]) -> list[str]:
    verification = preview.get("verification")
    if not isinstance(verification, dict):
        return ["verification must be an object"]
    if "promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_candidate_audit_preview_gate.py --check" not in str(
        verification.get("local_gate", "")
    ):
        return ["verification.local_gate must reference this gate"]
    return []


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


def _records_by_decision_type(value: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(value, list):
        return {}
    return {
        item.get("decision_type"): item
        for item in value
        if isinstance(item, dict) and isinstance(item.get("decision_type"), str)
    }


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
        print("promotion asset Owner/R3 packet candidate audit preview gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"promotion asset Owner/R3 packet candidate audit preview gate: PASS ({args.preview})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
