"""Validate the TASK-142 promotion asset Owner evidence freshness contract.

This gate validates local freshness metadata only. It rejects actual Owner
approval records, actual approval evidence collection, public approval, final
advice, final asset export, live publishing, customer contact, CRM/payment
action, external account action, platform calls, secret fields, and missing
blocked-action or freshness coverage.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = REPO_ROOT / "agents" / "project" / "PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-FRESHNESS-CONTRACT.json"
SOURCE_PREVIEW_PATH = REPO_ROOT / "agents" / "project" / "PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-CHECKLIST-AUDIT-PREVIEW.json"

REQUIRED_SOURCE_IDS = {"promotion_asset_owner_decision_evidence_checklist_audit_preview"}
EXPECTED_SOURCE_PATHS = {
    "promotion_asset_owner_decision_evidence_checklist_audit_preview": "agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-CHECKLIST-AUDIT-PREVIEW.json",
}

REQUIRED_BOUNDARIES = {
    "local_freshness_contract_only",
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

REQUIRED_STATE_IDS = {
    "current_local_evidence_snapshot",
    "refresh_required_before_owner_review",
    "expired_blocked_until_refresh",
    "archived_or_superseded",
    "future_owner_r3_packet_candidate_after_refresh",
}

REQUIRED_REFRESH_TRIGGERS = {
    "source_preview_hash_change",
    "checklist_item_coverage_change",
    "required_evidence_count_change",
    "stale_evidence_trigger_count_change",
    "blocked_action_scan_change",
    "forbidden_field_or_output_change",
    "external_policy_or_platform_rule_change",
    "owner_r3_boundary_change",
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

REQUIRED_BLOCKED_SCAN_KEYS = {
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
    "freshness_records": 9,
    "refresh_states": 5,
    "refresh_state_map_items": 8,
    "total_required_evidence_items": 25,
    "total_stale_evidence_trigger_items": 27,
    "records_with_stale_trigger_map": 9,
    "records_with_invalidating_events": 9,
    "records_with_archive_rollback": 9,
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
        raise ValueError("promotion asset Owner decision evidence freshness contract root must be an object")
    return data


def validate_contract(contract: dict[str, Any], repo_root: Path = REPO_ROOT) -> list[str]:
    findings: list[str] = []

    if contract.get("$schema") != "autofolio.promotion-asset-owner-decision-evidence-freshness-contract/v1":
        findings.append("unexpected or missing promotion asset Owner decision evidence freshness contract schema")

    if contract.get("status") != "local_freshness_contract_not_actual_approval_evidence":
        findings.append("status must be local_freshness_contract_not_actual_approval_evidence")

    boundaries = contract.get("boundaries")
    if not isinstance(boundaries, dict):
        findings.append("boundaries must be an object")
    else:
        for key in REQUIRED_BOUNDARIES:
            if boundaries.get(key) is not True:
                findings.append(f"boundaries.{key} must be true")

    forbidden_keys = _find_forbidden_keys(contract)
    if forbidden_keys:
        findings.append(f"forbidden approval/export/customer/secret/final-advice key names present: {forbidden_keys}")

    live_true_paths = _find_live_true_keys(contract)
    if live_true_paths:
        findings.append(f"approval/public/export/customer/payment/platform/final-advice/live flags must not be true: {live_true_paths}")

    findings.extend(_validate_sources(contract, repo_root))
    findings.extend(_validate_markdown_companion(contract, repo_root))
    findings.extend(_validate_summary(contract))
    findings.extend(_validate_freshness_states(contract))
    findings.extend(_validate_refresh_state_map(contract))
    findings.extend(_validate_freshness_records(contract))
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
        "not actual owner approval",
        "not actual approval evidence",
        "freshness contract",
        "stale-evidence trigger map",
        "invalidating events",
        "blocked action scan",
        "owner/r3",
    ):
        if required not in text:
            findings.append(f"companion_markdown must mention {required}")
    return findings


def _validate_summary(contract: dict[str, Any]) -> list[str]:
    summary = contract.get("freshness_summary")
    if not isinstance(summary, dict):
        return ["freshness_summary must be an object"]
    findings: list[str] = []
    for key, expected in REQUIRED_SUMMARY_COUNTS.items():
        if summary.get(key) != expected:
            findings.append(f"freshness_summary.{key} must be {expected}")
    if summary.get("gate_result") != "pass":
        findings.append("freshness_summary.gate_result must be pass")
    return findings


def _validate_freshness_states(contract: dict[str, Any]) -> list[str]:
    states = contract.get("freshness_states")
    if not isinstance(states, list):
        return ["freshness_states must be a list"]
    findings: list[str] = []
    state_ids = {item.get("state_id") for item in states if isinstance(item, dict)}
    missing = REQUIRED_STATE_IDS - state_ids
    if missing:
        findings.append(f"freshness_states missing state ids: {sorted(missing)}")
    for index, state in enumerate(states):
        if not isinstance(state, dict):
            findings.append(f"freshness_states[{index}] must be an object")
            continue
        prefix = f"freshness_states[{index}]"
        for key in ("live_action", "action_permitted_now", "actual_approval_recorded", "actual_approval_evidence_collected"):
            if state.get(key) is not False:
                findings.append(f"{prefix}.{key} must be false")
        if state.get("owner_r3_required_before_action") is not True:
            findings.append(f"{prefix}.owner_r3_required_before_action must be true")
    return findings


def _validate_refresh_state_map(contract: dict[str, Any]) -> list[str]:
    state_map = contract.get("refresh_state_map")
    if not isinstance(state_map, list):
        return ["refresh_state_map must be a list"]
    findings: list[str] = []
    states = _state_ids(contract)
    trigger_ids = {item.get("trigger_id") for item in state_map if isinstance(item, dict)}
    missing = REQUIRED_REFRESH_TRIGGERS - trigger_ids
    if missing:
        findings.append(f"refresh_state_map missing triggers: {sorted(missing)}")
    for index, item in enumerate(state_map):
        if not isinstance(item, dict):
            findings.append(f"refresh_state_map[{index}] must be an object")
            continue
        prefix = f"refresh_state_map[{index}]"
        if item.get("target_refresh_state") not in states:
            findings.append(f"{prefix}.target_refresh_state must be a known freshness state")
        if item.get("action_permitted_now") is not False:
            findings.append(f"{prefix}.action_permitted_now must be false")
        if item.get("archive_required") is not True:
            findings.append(f"{prefix}.archive_required must be true")
        if not isinstance(item.get("review_role"), str) or not item.get("review_role"):
            findings.append(f"{prefix}.review_role must be a non-empty string")
    return findings


def _validate_freshness_records(contract: dict[str, Any]) -> list[str]:
    records = contract.get("freshness_records")
    if not isinstance(records, list):
        return ["freshness_records must be a list"]
    source = _load_json(SOURCE_PREVIEW_PATH)
    source_items = {
        item.get("decision_type"): item
        for item in source.get("checklist_item_summaries", [])
        if isinstance(item, dict)
    }
    states = _state_ids(contract)
    record_types = {
        item.get("decision_type")
        for item in records
        if isinstance(item, dict) and isinstance(item.get("decision_type"), str)
    }
    findings: list[str] = []
    missing = REQUIRED_DECISION_TYPES - record_types
    if missing:
        findings.append(f"freshness_records missing decision types: {sorted(missing)}")
    for index, item in enumerate(records):
        if not isinstance(item, dict):
            findings.append(f"freshness_records[{index}] must be an object")
            continue
        prefix = f"freshness_records[{index}]"
        source_item = source_items.get(item.get("decision_type"))
        if not isinstance(source_item, dict):
            findings.append(f"{prefix}.decision_type unknown")
            continue
        for key in ("checklist_item_id", "accountable_role", "review_role_count"):
            if item.get(key) != source_item.get(key):
                findings.append(f"{prefix}.{key} must match source preview")
        if item.get("source_required_evidence_count") != source_item.get("required_evidence_count"):
            findings.append(f"{prefix}.source_required_evidence_count must match source preview")
        if item.get("source_stale_evidence_trigger_count") != source_item.get("stale_evidence_trigger_count"):
            findings.append(f"{prefix}.source_stale_evidence_trigger_count must match source preview")
        if item.get("source_forbidden_field_count") != source_item.get("forbidden_field_count"):
            findings.append(f"{prefix}.source_forbidden_field_count must match source preview")
        if item.get("initial_freshness_state") not in states:
            findings.append(f"{prefix}.initial_freshness_state must be a known freshness state")
        if item.get("refresh_required_state") not in states:
            findings.append(f"{prefix}.refresh_required_state must be a known freshness state")
        if item.get("expiry_rule") != "expires_immediately_on_any_invalidating_event":
            findings.append(f"{prefix}.expiry_rule must be expires_immediately_on_any_invalidating_event")
        trigger_map = item.get("stale_trigger_to_refresh_state")
        if not isinstance(trigger_map, list):
            findings.append(f"{prefix}.stale_trigger_to_refresh_state must be a list")
        elif len(trigger_map) != source_item.get("stale_evidence_trigger_count"):
            findings.append(f"{prefix}.stale_trigger_to_refresh_state count must match source preview")
        else:
            for trigger_index, trigger in enumerate(trigger_map):
                if not isinstance(trigger, dict):
                    findings.append(f"{prefix}.stale_trigger_to_refresh_state[{trigger_index}] must be an object")
                    continue
                if trigger.get("target_refresh_state") not in states:
                    findings.append(f"{prefix}.stale_trigger_to_refresh_state[{trigger_index}].target_refresh_state must be a known freshness state")
        invalidating_events = set(_string_list(item.get("invalidating_events")))
        if not invalidating_events:
            findings.append(f"{prefix}.invalidating_events must not be empty")
        if "source_preview_hash_change" not in invalidating_events:
            findings.append(f"{prefix}.invalidating_events must include source_preview_hash_change")
        if not isinstance(item.get("archive_rollback_action"), str) or "Archive stale local evidence" not in item.get("archive_rollback_action", ""):
            findings.append(f"{prefix}.archive_rollback_action must describe stale local evidence archiving")
        if item.get("actual_approval_evidence_collected") is not False:
            findings.append(f"{prefix}.actual_approval_evidence_collected must be false")
        if item.get("actual_approval_recorded") is not False:
            findings.append(f"{prefix}.actual_approval_recorded must be false")
        if item.get("action_permitted_now") is not False:
            findings.append(f"{prefix}.action_permitted_now must be false")
        for key in RECORD_REQUIRED_TRUE_FLAGS:
            if item.get(key) is not True:
                findings.append(f"{prefix}.{key} must be true")
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
        "freshness_contract_generated",
        "stale_trigger_map_recorded",
        "invalidating_events_recorded",
        "blocked_action_scan_passed",
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
    for key in ("task_142_contract_ready", "taskset_local_scope_complete_when_task_closes"):
        if handoff.get(key) is not True:
            findings.append(f"taskset_handoff.{key} must be true")
    r3_items = set(_string_list(handoff.get("owner_r3_required_for")))
    for required in (
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
    if "promotion_asset_owner_decision_evidence_freshness_contract_gate.py --check" not in str(verification.get("local_gate", "")):
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


def _state_ids(contract: dict[str, Any]) -> set[str]:
    states = contract.get("freshness_states")
    if not isinstance(states, list):
        return set()
    return {item.get("state_id") for item in states if isinstance(item, dict) and isinstance(item.get("state_id"), str)}


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
        print("promotion asset Owner decision evidence freshness contract gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"promotion asset Owner decision evidence freshness contract gate: PASS ({args.contract})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
