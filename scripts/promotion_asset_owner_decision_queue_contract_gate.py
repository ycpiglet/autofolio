"""Validate the TASK-138 promotion asset Owner decision queue contract.

This gate validates local decision queue contract metadata only. It rejects
actual Owner approval records, public approval, final advice, final asset
export, live publishing, customer contact, CRM/payment action, external account
action, platform calls, secret fields, and missing blocked-action coverage.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = REPO_ROOT / "agents" / "project" / "PROMOTION-ASSET-OWNER-DECISION-QUEUE-CONTRACT.json"
SOURCE_PACKET_PATH = REPO_ROOT / "agents" / "project" / "PROMOTION-ASSET-OWNER-REVIEW-PACKET.json"

REQUIRED_SOURCE_IDS = {"promotion_asset_owner_review_packet"}
EXPECTED_SOURCE_PATHS = {
    "promotion_asset_owner_review_packet": "agents/project/PROMOTION-ASSET-OWNER-REVIEW-PACKET.json",
}

REQUIRED_BOUNDARIES = {
    "local_decision_queue_contract_only",
    "not_actual_owner_approval_record",
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

REQUIRED_RECORD_FIELDS = {
    "decision_record_id",
    "decision_type",
    "source_packet_id",
    "source_hash",
    "current_state",
    "required_evidence",
    "blockers",
    "actual_approval_recorded",
    "public_use_blocked",
    "final_export_blocked",
    "external_action_blocked",
    "customer_contact_blocked",
    "crm_payment_blocked",
    "secret_material_blocked",
    "final_advice_blocked",
    "kis_order_risk_prod_deploy_blocked",
    "rollback_or_archive_instruction",
}

REQUIRED_STATES = {
    "pending_local_review",
    "evidence_required",
    "owner_decision_needed",
    "approved_record_ready_for_future_r3",
    "rejected",
    "blocked",
    "withdrawn_or_archived",
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

FORBIDDEN_KEY_NAMES = {
    "approval_signature",
    "approval_secret",
    "approved_by_owner",
    "approval_timestamp",
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
    "actual_approval_recorded",
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
}

FORBIDDEN_OUTPUTS = {
    "actual Owner approval record",
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

REQUIRED_SUMMARY_COUNTS = {
    "decision_types": 9,
    "queue_record_required_fields": 17,
    "allowed_states": 7,
    "seed_records": 9,
    "actual_approval_records": 0,
    "public_use_approved_records": 0,
    "final_export_approved_records": 0,
    "external_action_approved_records": 0,
    "customer_contact_approved_records": 0,
    "crm_payment_approved_records": 0,
    "secret_material_records": 0,
    "final_advice_records": 0,
}


def load_contract(path: Path = DEFAULT_CONTRACT) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("promotion asset Owner decision queue contract root must be an object")
    return data


def validate_contract(contract: dict[str, Any], repo_root: Path = REPO_ROOT) -> list[str]:
    findings: list[str] = []

    if contract.get("$schema") != "autofolio.promotion-asset-owner-decision-queue-contract/v1":
        findings.append("unexpected or missing promotion asset Owner decision queue contract schema")

    if contract.get("status") != "local_decision_queue_contract_not_actual_approval":
        findings.append("status must be local_decision_queue_contract_not_actual_approval")

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
        findings.append(f"approval/public/export/customer/payment/platform/final-advice flags must not be true: {live_true_paths}")

    findings.extend(_validate_sources(contract, repo_root))
    findings.extend(_validate_markdown_companion(contract, repo_root))
    findings.extend(_validate_summary(contract))
    findings.extend(_validate_queue_contract(contract))
    findings.extend(_validate_decision_types(contract))
    findings.extend(_validate_seed_records(contract))
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
    for required in ("not actual owner approval", "decision queue states", "blocked action flags", "owner/r3"):
        if required not in text:
            findings.append(f"companion_markdown must mention {required}")
    return findings


def _validate_summary(contract: dict[str, Any]) -> list[str]:
    summary = contract.get("queue_summary")
    if not isinstance(summary, dict):
        return ["queue_summary must be an object"]
    findings: list[str] = []
    for key, expected in REQUIRED_SUMMARY_COUNTS.items():
        if summary.get(key) != expected:
            findings.append(f"queue_summary.{key} must be {expected}")
    if summary.get("gate_result") != "pass":
        findings.append("queue_summary.gate_result must be pass")
    return findings


def _validate_queue_contract(contract: dict[str, Any]) -> list[str]:
    queue_contract = contract.get("decision_queue_contract")
    if not isinstance(queue_contract, dict):
        return ["decision_queue_contract must be an object"]
    findings: list[str] = []

    required_fields = set(_string_list(queue_contract.get("required_fields")))
    missing_fields = REQUIRED_RECORD_FIELDS - required_fields
    if missing_fields:
        findings.append(f"decision_queue_contract.required_fields missing: {sorted(missing_fields)}")

    forbidden_fields = set(_string_list(queue_contract.get("forbidden_fields")))
    missing_forbidden = {"approval_signature", "approved_by_owner", "access_token", "customer_email", "final_pdf_path", "payment_request_id", "tax_advice_final"} - forbidden_fields
    if missing_forbidden:
        findings.append(f"decision_queue_contract.forbidden_fields missing: {sorted(missing_forbidden)}")

    states = queue_contract.get("allowed_states")
    if not isinstance(states, list):
        findings.append("decision_queue_contract.allowed_states must be a list")
        return findings
    state_ids = {item.get("id") for item in states if isinstance(item, dict)}
    missing_states = REQUIRED_STATES - state_ids
    if missing_states:
        findings.append(f"decision_queue_contract.allowed_states missing: {sorted(missing_states)}")
    for index, state in enumerate(states):
        if not isinstance(state, dict):
            findings.append(f"decision_queue_contract.allowed_states[{index}] must be an object")
            continue
        prefix = f"decision_queue_contract.allowed_states[{index}]"
        if state.get("live_action") is not False:
            findings.append(f"{prefix}.live_action must be false")
        if state.get("actual_approval_recorded") is not False:
            findings.append(f"{prefix}.actual_approval_recorded must be false")
        if not isinstance(state.get("allowed_next"), list):
            findings.append(f"{prefix}.allowed_next must be a list")
    return findings


def _validate_decision_types(contract: dict[str, Any]) -> list[str]:
    decision_types = contract.get("decision_types")
    if not isinstance(decision_types, list):
        return ["decision_types must be a list"]
    findings: list[str] = []
    ids = {item.get("decision_type") for item in decision_types if isinstance(item, dict)}
    missing = REQUIRED_DECISION_TYPES - ids
    if missing:
        findings.append(f"decision_types missing: {sorted(missing)}")
    source_packet = _load_json(SOURCE_PACKET_PATH)
    source_decisions = {
        item.get("decision_id")
        for item in source_packet.get("owner_decision_list", [])
        if isinstance(item, dict)
    }
    for index, item in enumerate(decision_types):
        if not isinstance(item, dict):
            findings.append(f"decision_types[{index}] must be an object")
            continue
        prefix = f"decision_types[{index}]"
        if item.get("owner_r3_required") is not True:
            findings.append(f"{prefix}.owner_r3_required must be true")
        if item.get("source_decision") not in source_decisions:
            findings.append(f"{prefix}.source_decision must match source packet owner_decision_list")
        if not _string_list(item.get("required_evidence")):
            findings.append(f"{prefix}.required_evidence must be a non-empty list")
        if not _string_list(item.get("blocked_actions")):
            findings.append(f"{prefix}.blocked_actions must be a non-empty list")
    return findings


def _validate_seed_records(contract: dict[str, Any]) -> list[str]:
    records = contract.get("seed_decision_records")
    if not isinstance(records, list):
        return ["seed_decision_records must be a list"]
    findings: list[str] = []
    ids = {item.get("decision_type") for item in records if isinstance(item, dict)}
    missing = REQUIRED_DECISION_TYPES - ids
    if missing:
        findings.append(f"seed_decision_records missing decision types: {sorted(missing)}")
    source_hash = _sha256(SOURCE_PACKET_PATH)
    for index, item in enumerate(records):
        if not isinstance(item, dict):
            findings.append(f"seed_decision_records[{index}] must be an object")
            continue
        prefix = f"seed_decision_records[{index}]"
        for field in REQUIRED_RECORD_FIELDS:
            if field not in item:
                findings.append(f"{prefix}.{field} is required")
        if item.get("decision_type") not in REQUIRED_DECISION_TYPES:
            findings.append(f"{prefix}.decision_type unknown")
        if item.get("source_packet_id") != "PROMOTION-ASSET-OWNER-REVIEW-PACKET-2026-06-20-001":
            findings.append(f"{prefix}.source_packet_id must reference source packet")
        if str(item.get("source_hash", "")).lower() != source_hash:
            findings.append(f"{prefix}.source_hash must match source packet")
        if item.get("current_state") not in REQUIRED_STATES:
            findings.append(f"{prefix}.current_state must be an allowed state")
        if item.get("actual_approval_recorded") is not False:
            findings.append(f"{prefix}.actual_approval_recorded must be false")
        for flag in RECORD_REQUIRED_TRUE_FLAGS:
            if item.get(flag) is not True:
                findings.append(f"{prefix}.{flag} must be true")
        if not _string_list(item.get("required_evidence")):
            findings.append(f"{prefix}.required_evidence must be a non-empty list")
        if not _string_list(item.get("blockers")):
            findings.append(f"{prefix}.blockers must be a non-empty list")
    return findings


def _validate_forbidden_outputs(contract: dict[str, Any]) -> list[str]:
    outputs = set(_string_list(contract.get("forbidden_outputs")))
    missing = FORBIDDEN_OUTPUTS - outputs
    if missing:
        return [f"forbidden_outputs missing: {sorted(missing)}"]
    return []


def _validate_handoff(contract: dict[str, Any]) -> list[str]:
    handoff = contract.get("taskset_handoff")
    if not isinstance(handoff, dict):
        return ["taskset_handoff must be an object"]
    findings: list[str] = []
    for key in ("task_138_contract_ready", "taskset_local_scope_complete_when_task_closes"):
        if handoff.get(key) is not True:
            findings.append(f"taskset_handoff.{key} must be true")
    r3_items = set(_string_list(handoff.get("owner_r3_required_for")))
    for required in ("actual Owner approval record", "public use of any claim", "final PDF export", "SNS upload", "OAuth flow or platform API call"):
        if required not in r3_items:
            findings.append(f"taskset_handoff.owner_r3_required_for missing {required}")
    return findings


def _validate_verification(contract: dict[str, Any]) -> list[str]:
    verification = contract.get("verification")
    if not isinstance(verification, dict):
        return ["verification must be an object"]
    if "promotion_asset_owner_decision_queue_contract_gate.py --check" not in str(verification.get("local_gate", "")):
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
        print("promotion asset Owner decision queue contract gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"promotion asset Owner decision queue contract gate: PASS ({args.contract})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
