"""Validate the TASK-146 promotion asset Owner evidence refresh work-order contract.

This gate validates local refresh work-order contract metadata only. It rejects
actual evidence refresh execution, actual Owner approval records, actual
approval evidence collection, public approval, final advice, final asset export,
live publishing, customer contact, CRM/payment action, external account action,
platform calls, secret fields, and missing work-order, trigger, state,
precondition, proof-requirement, or blocked-action coverage.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = REPO_ROOT / "agents" / "project" / "PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-WORK-ORDER-CONTRACT.json"
SOURCE_PREVIEW_PATH = REPO_ROOT / "agents" / "project" / "PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-QUEUE-AUDIT-PREVIEW.json"

REQUIRED_SOURCE_IDS = {"promotion_asset_owner_decision_evidence_refresh_queue_audit_preview"}
EXPECTED_SOURCE_PATHS = {
    "promotion_asset_owner_decision_evidence_refresh_queue_audit_preview": "agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-QUEUE-AUDIT-PREVIEW.json",
}

REQUIRED_BOUNDARIES = {
    "local_refresh_work_order_contract_only",
    "not_actual_refresh_execution",
    "not_actual_owner_approval_record",
    "not_actual_approval_evidence_collection",
    "not_publication_approval",
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

RECORD_REQUIRED_TRUE_FLAGS = {
    "public_use_blocked",
    "final_export_blocked",
    "external_action_blocked",
    "customer_contact_blocked",
    "crm_payment_blocked",
    "secret_material_blocked",
    "final_advice_blocked",
    "kis_order_risk_prod_deploy_blocked",
}

RECORD_REQUIRED_FALSE_FLAGS = {
    "actual_refresh_executed",
    "refresh_execution_allowed",
    "actual_approval_evidence_collected",
    "actual_approval_recorded",
    "action_permitted_now",
}

REQUIRED_BLOCKED_SCAN_KEYS = {
    "actual_refresh_execution",
    "actual_approval_record",
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
    "source_refresh_queue_record_summaries": 9,
    "refresh_work_order_records": 9,
    "work_order_states": 5,
    "invalidating_trigger_map_items": 8,
    "source_hash_archive_scans": 9,
    "total_source_required_evidence_items": 25,
    "total_source_stale_evidence_trigger_items": 27,
    "total_source_invalidating_event_items": 36,
    "records_with_preconditions": 9,
    "records_with_proof_requirements": 9,
    "records_with_expiry_triggers": 9,
    "records_with_archive_rollback_required": 9,
    "work_orders_blocked_from_execution": 9,
    "ready_for_future_r3_records": 0,
    "actual_refresh_executions": 0,
    "actual_approval_records": 0,
    "actual_approval_evidence_records": 0,
    "public_use_blocked_records": 9,
    "final_export_blocked_records": 9,
    "external_action_blocked_records": 9,
    "customer_contact_blocked_records": 9,
    "crm_payment_blocked_records": 9,
    "secret_material_blocked_records": 9,
    "final_advice_blocked_records": 9,
    "kis_order_risk_prod_deploy_blocked_records": 9,
    "live_action_states": 0,
    "actual_refresh_states": 0,
    "actual_approval_states": 0,
    "approval_evidence_collection_states": 0,
    "final_export_outputs": 0,
    "public_publication_outputs": 0,
    "customer_or_payment_outputs": 0,
    "secret_or_token_outputs": 0,
    "final_advice_outputs": 0,
}

FORBIDDEN_KEY_NAMES = {
    "approval_signature",
    "approval_secret",
    "approved_by_owner",
    "approval_timestamp",
    "approval_evidence_file",
    "owner_signature_file",
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
    "actual_approval_evidence_collected",
    "actual_approval_recorded",
    "action_permitted_now",
    "approval_evidence_collection_enabled",
    "evidence_collection_allowed",
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


def load_contract(path: Path = DEFAULT_CONTRACT) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("promotion asset Owner decision evidence refresh work-order contract root must be an object")
    return data


def validate_contract(contract: dict[str, Any], repo_root: Path = REPO_ROOT) -> list[str]:
    findings: list[str] = []

    if contract.get("$schema") != "autofolio.promotion-asset-owner-decision-evidence-refresh-work-order-contract/v1":
        findings.append("unexpected or missing promotion asset Owner decision evidence refresh work-order contract schema")

    if contract.get("status") != "local_refresh_work_order_contract_not_actual_refresh_execution":
        findings.append("status must be local_refresh_work_order_contract_not_actual_refresh_execution")

    boundaries = contract.get("boundaries")
    if not isinstance(boundaries, dict):
        findings.append("boundaries must be an object")
    else:
        for key in REQUIRED_BOUNDARIES:
            if boundaries.get(key) is not True:
                findings.append(f"boundaries.{key} must be true")

    forbidden_keys = _find_forbidden_keys(contract)
    if forbidden_keys:
        findings.append(f"forbidden refresh/approval/export/customer/secret/final-advice key names present: {forbidden_keys}")

    live_true_paths = _find_live_true_keys(contract)
    if live_true_paths:
        findings.append(f"refresh/approval/public/export/customer/payment/platform/final-advice/live flags must not be true: {live_true_paths}")

    findings.extend(_validate_sources(contract, repo_root))
    findings.extend(_validate_markdown_companion(contract, repo_root))
    findings.extend(_validate_summary(contract))
    findings.extend(_validate_work_order_states(contract))
    findings.extend(_validate_refresh_work_order_records(contract))
    findings.extend(_validate_trigger_map(contract))
    findings.extend(_validate_blocked_action_scan(contract))
    findings.extend(_validate_events(contract))
    findings.extend(_validate_forbidden_outputs(contract))
    findings.extend(_validate_handoff(contract))
    findings.extend(_validate_verification(contract))
    return findings


def _validate_sources(contract: dict[str, Any], repo_root: Path) -> list[str]:
    inputs = contract.get("source_inputs")
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


def _validate_markdown_companion(contract: dict[str, Any], repo_root: Path) -> list[str]:
    rel_path = str(contract.get("companion_markdown", ""))
    try:
        path = _safe_repo_path(repo_root, rel_path)
    except ValueError as exc:
        return [f"companion_markdown invalid: {exc}"]
    if not path.exists():
        return [f"companion_markdown missing: {rel_path}"]
    text = path.read_text(encoding="utf-8").lower()
    findings: list[str] = []
    for required in (
        "not actual refresh execution",
        "not actual owner approval",
        "not actual approval evidence",
        "refresh work-order record coverage",
        "preconditions and proof requirements",
        "expiry trigger map",
        "blocked action scan",
        "owner/r3",
    ):
        if required not in text:
            findings.append(f"companion_markdown must mention {required}")
    return findings


def _validate_summary(contract: dict[str, Any]) -> list[str]:
    summary = contract.get("contract_summary")
    if not isinstance(summary, dict):
        return ["contract_summary must be an object"]
    findings: list[str] = []
    for key, expected in REQUIRED_SUMMARY_COUNTS.items():
        if summary.get(key) != expected:
            findings.append(f"contract_summary.{key} must be {expected}")
    if summary.get("gate_result") != "pass":
        findings.append("contract_summary.gate_result must be pass")
    return findings


def _validate_work_order_states(contract: dict[str, Any]) -> list[str]:
    states = contract.get("work_order_states")
    if not isinstance(states, list):
        return ["work_order_states must be a list"]
    source = _load_json(SOURCE_PREVIEW_PATH)
    source_states = {
        item.get("state_id"): item
        for item in source.get("queue_state_safety_scan", [])
        if isinstance(item, dict)
    }
    source_state_ids = set(source_states)
    findings: list[str] = []
    mapped_source_ids = {item.get("source_state_id") for item in states if isinstance(item, dict)}
    missing = source_state_ids - mapped_source_ids
    if missing:
        findings.append(f"work_order_states missing source state ids: {sorted(missing)}")
    for index, item in enumerate(states):
        if not isinstance(item, dict):
            findings.append(f"work_order_states[{index}] must be an object")
            continue
        prefix = f"work_order_states[{index}]"
        source_state = source_states.get(item.get("source_state_id"))
        if not isinstance(source_state, dict):
            findings.append(f"{prefix}.source_state_id unknown")
            continue
        for key in (
            "live_action",
            "action_permitted_now",
            "actual_approval_recorded",
            "actual_approval_evidence_collected",
        ):
            if item.get(key) is not False:
                findings.append(f"{prefix}.{key} must be false")
            if item.get(key) != source_state.get(key):
                findings.append(f"{prefix}.{key} must match source preview")
        for key in ("refresh_execution_allowed", "actual_refresh_executed"):
            if item.get(key) is not False:
                findings.append(f"{prefix}.{key} must be false")
        if item.get("owner_r3_required_before_action") is not True:
            findings.append(f"{prefix}.owner_r3_required_before_action must be true")
        if item.get("status") != "pass":
            findings.append(f"{prefix}.status must be pass")
    return findings


def _validate_refresh_work_order_records(contract: dict[str, Any]) -> list[str]:
    records = contract.get("refresh_work_order_records")
    if not isinstance(records, list):
        return ["refresh_work_order_records must be a list"]
    source = _load_json(SOURCE_PREVIEW_PATH)
    source_records = {
        item.get("decision_type"): item
        for item in source.get("refresh_queue_record_summaries", [])
        if isinstance(item, dict)
    }
    work_state_ids = {
        item.get("state_id")
        for item in contract.get("work_order_states", [])
        if isinstance(item, dict)
    }
    record_types = {
        item.get("decision_type")
        for item in records
        if isinstance(item, dict) and isinstance(item.get("decision_type"), str)
    }
    findings: list[str] = []
    missing = REQUIRED_DECISION_TYPES - record_types
    if missing:
        findings.append(f"refresh_work_order_records missing decision types: {sorted(missing)}")
    for index, item in enumerate(records):
        if not isinstance(item, dict):
            findings.append(f"refresh_work_order_records[{index}] must be an object")
            continue
        prefix = f"refresh_work_order_records[{index}]"
        source_record = source_records.get(item.get("decision_type"))
        if not isinstance(source_record, dict):
            findings.append(f"{prefix}.decision_type unknown")
            continue
        if item.get("work_order_id") != f"work-order-{str(source_record.get('queue_record_id', '')).removeprefix('refresh-queue-')}":
            findings.append(f"{prefix}.work_order_id must derive from source queue_record_id")
        for key, source_key in (
            ("source_queue_record_id", "queue_record_id"),
            ("source_record_id", "source_record_id"),
            ("source_current_queue_state", "current_queue_state"),
            ("source_refresh_required_state", "refresh_required_state"),
            ("source_expired_state", "expired_state"),
            ("source_future_candidate_state", "future_candidate_state"),
            ("source_required_evidence_count", "source_required_evidence_count"),
            ("source_stale_evidence_trigger_count", "source_stale_evidence_trigger_count"),
            ("source_invalidating_event_count", "source_invalidating_event_count"),
            ("stale_trigger_to_refresh_state_count", "stale_trigger_to_refresh_state_count"),
            ("source_hash_invalidating_event_present", "source_hash_invalidating_event_present"),
            ("archive_rollback_required", "archive_rollback_required"),
        ):
            if item.get(key) != source_record.get(source_key):
                findings.append(f"{prefix}.{key} must match source preview {source_key}")
        if item.get("current_work_order_state") not in work_state_ids:
            findings.append(f"{prefix}.current_work_order_state must be a known work-order state")
        if item.get("accountable_role") != "Doc Steward":
            findings.append(f"{prefix}.accountable_role must be Doc Steward")
        if set(_string_list(item.get("review_roles"))) != {"QA", "Compliance Officer", "Marketing Growth"}:
            findings.append(f"{prefix}.review_roles must include QA, Compliance Officer, and Marketing Growth")
        if len(_string_list(item.get("preconditions"))) < 3:
            findings.append(f"{prefix}.preconditions must include at least three local preconditions")
        if len(_string_list(item.get("proof_requirements"))) < 3:
            findings.append(f"{prefix}.proof_requirements must include at least three local proof requirements")
        if len(_string_list(item.get("expiry_triggers"))) < 4:
            findings.append(f"{prefix}.expiry_triggers must include at least four local expiry triggers")
        for key in RECORD_REQUIRED_FALSE_FLAGS:
            if item.get(key) is not False:
                findings.append(f"{prefix}.{key} must be false")
        for key in RECORD_REQUIRED_TRUE_FLAGS:
            if item.get(key) is not True:
                findings.append(f"{prefix}.{key} must be true")
        if item.get("work_order_status") != "local_contract_only_not_executed":
            findings.append(f"{prefix}.work_order_status must be local_contract_only_not_executed")
    return findings


def _validate_trigger_map(contract: dict[str, Any]) -> list[str]:
    trigger_map = contract.get("invalidating_trigger_to_work_order_map")
    if not isinstance(trigger_map, list):
        return ["invalidating_trigger_to_work_order_map must be a list"]
    source = _load_json(SOURCE_PREVIEW_PATH)
    source_items = {
        item.get("trigger_id"): item
        for item in source.get("invalidating_trigger_map_coverage_scan", [])
        if isinstance(item, dict)
    }
    work_state_ids = {
        item.get("state_id")
        for item in contract.get("work_order_states", [])
        if isinstance(item, dict)
    }
    findings: list[str] = []
    missing = set(source_items) - {item.get("trigger_id") for item in trigger_map if isinstance(item, dict)}
    if missing:
        findings.append(f"invalidating_trigger_to_work_order_map missing triggers: {sorted(missing)}")
    for index, item in enumerate(trigger_map):
        if not isinstance(item, dict):
            findings.append(f"invalidating_trigger_to_work_order_map[{index}] must be an object")
            continue
        prefix = f"invalidating_trigger_to_work_order_map[{index}]"
        source_item = source_items.get(item.get("trigger_id"))
        if not isinstance(source_item, dict):
            findings.append(f"{prefix}.trigger_id unknown")
            continue
        if item.get("source_target_queue_state") != source_item.get("target_queue_state"):
            findings.append(f"{prefix}.source_target_queue_state must match source target_queue_state")
        if item.get("target_work_order_state") not in work_state_ids:
            findings.append(f"{prefix}.target_work_order_state must be a known work-order state")
        for key in ("archive_required", "action_permitted_now", "owner_r3_required_before_action", "coverage_status"):
            if item.get(key) != source_item.get(key):
                findings.append(f"{prefix}.{key} must match source preview")
        for key in ("refresh_execution_allowed", "actual_refresh_executed"):
            if item.get(key) is not False:
                findings.append(f"{prefix}.{key} must be false")
        if item.get("archive_required") is not True:
            findings.append(f"{prefix}.archive_required must be true")
        if item.get("action_permitted_now") is not False:
            findings.append(f"{prefix}.action_permitted_now must be false")
    return findings


def _validate_blocked_action_scan(contract: dict[str, Any]) -> list[str]:
    scan = contract.get("blocked_action_scan")
    if not isinstance(scan, dict):
        return ["blocked_action_scan must be an object"]
    findings: list[str] = []
    missing = REQUIRED_BLOCKED_SCAN_KEYS - set(scan)
    if missing:
        findings.append(f"blocked_action_scan missing keys: {sorted(missing)}")
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


def _validate_events(contract: dict[str, Any]) -> list[str]:
    events = contract.get("contract_events")
    if not isinstance(events, list):
        return ["contract_events must be a list"]
    findings: list[str] = []
    event_names = {item.get("event") for item in events if isinstance(item, dict)}
    for required in (
        "refresh_work_order_contract_generated",
        "refresh_work_orders_seeded",
        "precondition_and_proof_requirements_recorded",
        "expiry_trigger_map_recorded",
        "blocked_action_scan_recorded",
    ):
        if required not in event_names:
            findings.append(f"contract_events missing {required}")
    for index, event in enumerate(events):
        if isinstance(event, dict) and event.get("external_action") is not False:
            findings.append(f"contract_events[{index}].external_action must be false")
    return findings


def _validate_forbidden_outputs(contract: dict[str, Any]) -> list[str]:
    outputs = set(_string_list(contract.get("forbidden_outputs")))
    missing = REQUIRED_FORBIDDEN_OUTPUTS - outputs
    if missing:
        return [f"forbidden_outputs missing: {sorted(missing)}"]
    return []


def _validate_handoff(contract: dict[str, Any]) -> list[str]:
    handoff = contract.get("taskset_handoff")
    if not isinstance(handoff, dict):
        return ["taskset_handoff must be an object"]
    findings: list[str] = []
    for key in ("task_146_contract_ready", "taskset_local_scope_complete_when_task_closes"):
        if handoff.get(key) is not True:
            findings.append(f"taskset_handoff.{key} must be true")
    r3_items = set(_string_list(handoff.get("owner_r3_required_for")))
    for required in (
        "actual evidence refresh execution",
        "actual Owner approval record",
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


def _validate_verification(contract: dict[str, Any]) -> list[str]:
    verification = contract.get("verification")
    if not isinstance(verification, dict):
        return ["verification must be an object"]
    if "promotion_asset_owner_decision_evidence_refresh_work_order_contract_gate.py --check" not in str(verification.get("local_gate", "")):
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


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--check", action="store_true", help="validate and return non-zero on findings")
    args = parser.parse_args()

    contract = load_contract(args.contract)
    findings = validate_contract(contract)
    if findings:
        print("promotion asset Owner decision evidence refresh work-order contract gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"promotion asset Owner decision evidence refresh work-order contract gate: PASS ({args.contract})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
