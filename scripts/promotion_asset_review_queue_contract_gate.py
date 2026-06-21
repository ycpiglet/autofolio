"""Validate the TASK-135 promotion asset review queue contract.

This gate validates local review-queue metadata only. It rejects public
approval, final advice, final asset export, live publishing, customer contact,
CRM/payment action, external account action, secret fields, and live-action
state transitions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = REPO_ROOT / "agents" / "project" / "PROMOTION-ASSET-REVIEW-QUEUE-CONTRACT.json"
CLAIM_MATRIX_PATH = REPO_ROOT / "agents" / "project" / "PROMOTION-ASSET-CLAIM-REVIEW-MATRIX.json"
PREVIEW_MANIFEST_PATH = REPO_ROOT / "agents" / "project" / "PROMOTION-ASSET-PREVIEW-MANIFEST.json"
PUBLISHING_STATE_MACHINE_PATH = REPO_ROOT / "agents" / "project" / "PROMOTION-PUBLISHING-STATE-MACHINE.json"

REQUIRED_SOURCE_IDS = {
    "promotion_asset_claim_review_matrix",
    "promotion_asset_preview_manifest",
    "promotion_publishing_state_machine",
}

EXPECTED_SOURCE_PATHS = {
    "promotion_asset_claim_review_matrix": "agents/project/PROMOTION-ASSET-CLAIM-REVIEW-MATRIX.json",
    "promotion_asset_preview_manifest": "agents/project/PROMOTION-ASSET-PREVIEW-MANIFEST.json",
    "promotion_publishing_state_machine": "agents/project/PROMOTION-PUBLISHING-STATE-MACHINE.json",
}

REQUIRED_BOUNDARIES = {
    "local_review_queue_contract_only",
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

REQUIRED_FIELDS = {
    "queue_item_id",
    "target_id",
    "source_asset_id",
    "source_artifact",
    "source_hash",
    "claim_bucket",
    "current_state",
    "assigned_role",
    "blockers",
    "required_evidence",
    "public_use_blocked",
    "final_export_blocked",
    "publication_approval_blocked",
    "rollback_or_archive_instruction",
}

REQUIRED_STATES = {
    "draft_classified",
    "compliance_review_required",
    "owner_review_required",
    "qa_doc_review_required",
    "ready_for_future_owner_review",
    "blocked",
    "withdrawn_or_archived",
}

FORBIDDEN_KEY_NAMES = {
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

TARGET_REQUIRED_TRUE_FLAGS = {
    "public_use_blocked",
    "final_export_blocked",
    "publication_approval_blocked",
    "external_action_blocked",
    "customer_contact_blocked",
    "crm_payment_blocked",
    "secret_material_blocked",
}

TOP_LEVEL_REQUIRED_TRUE_FLAGS = {
    "public_use_blocked",
    "final_advice_blocked",
    "publication_approval_blocked",
}

FORBIDDEN_STATE_TOKENS = {
    "approved_for_publication",
    "approved_for_live",
    "live_post",
    "published",
    "uploaded",
    "sent_to_customer",
}


def load_contract(path: Path = DEFAULT_CONTRACT) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("promotion asset review queue contract root must be an object")
    return data


def validate_contract(contract: dict[str, Any], repo_root: Path = REPO_ROOT) -> list[str]:
    findings: list[str] = []

    if contract.get("$schema") != "autofolio.promotion-asset-review-queue-contract/v1":
        findings.append("unexpected or missing promotion asset review queue contract schema")

    if contract.get("status") != "local_review_queue_contract_not_public_approval":
        findings.append("status must be local_review_queue_contract_not_public_approval")

    for key in TOP_LEVEL_REQUIRED_TRUE_FLAGS:
        if contract.get(key) is not True:
            findings.append(f"{key} must be true")

    boundaries = contract.get("boundaries")
    if not isinstance(boundaries, dict):
        findings.append("boundaries must be an object")
    else:
        for key in REQUIRED_BOUNDARIES:
            if boundaries.get(key) is not True:
                findings.append(f"boundaries.{key} must be true")

    forbidden_keys = _find_forbidden_keys(contract)
    if forbidden_keys:
        findings.append(f"forbidden export/customer/secret/final-advice key names present: {forbidden_keys}")

    live_true_paths = _find_live_true_keys(contract)
    if live_true_paths:
        findings.append(f"public/export/customer/payment/platform/final-advice flags must not be true: {live_true_paths}")

    findings.extend(_validate_sources(contract, repo_root))
    findings.extend(_validate_markdown_companion(contract, repo_root))
    findings.extend(_validate_queue_record_contract(contract))
    findings.extend(_validate_queue_items(contract, repo_root))
    findings.extend(_validate_outputs(contract))
    findings.extend(_validate_handoff(contract))
    findings.extend(_validate_verification(contract))
    return findings


def _validate_sources(contract: dict[str, Any], repo_root: Path) -> list[str]:
    findings: list[str] = []
    inputs = contract.get("source_inputs")
    if not isinstance(inputs, list):
        return ["source_inputs must be a list"]

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
        "not public approval",
        "public_use_blocked=true",
        "final_export_blocked=true",
        "publication_approval_blocked=true",
        "live action",
    ):
        if required not in text:
            findings.append(f"companion_markdown must mention {required}")
    return findings


def _validate_queue_record_contract(contract: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    record_contract = contract.get("queue_record_contract")
    if not isinstance(record_contract, dict):
        return ["queue_record_contract must be an object"]

    required_fields = set(_string_list(record_contract.get("required_fields")))
    missing_fields = REQUIRED_FIELDS - required_fields
    if missing_fields:
        findings.append(f"queue_record_contract.required_fields missing: {sorted(missing_fields)}")

    forbidden_fields = set(_string_list(record_contract.get("forbidden_fields")))
    missing_forbidden = {
        "access_token",
        "client_secret",
        "customer_email",
        "public_url",
        "final_pdf_path",
        "final_pptx_path",
        "payment_request_id",
        "customer_record_id",
        "legal_opinion",
    } - forbidden_fields
    if missing_forbidden:
        findings.append(f"queue_record_contract.forbidden_fields missing: {sorted(missing_forbidden)}")

    states = record_contract.get("allowed_states")
    if not isinstance(states, list):
        return findings + ["queue_record_contract.allowed_states must be a list"]

    state_ids = {item.get("id") for item in states if isinstance(item, dict)}
    missing_states = REQUIRED_STATES - state_ids
    if missing_states:
        findings.append(f"queue_record_contract.allowed_states missing: {sorted(missing_states)}")

    for index, state in enumerate(states):
        if not isinstance(state, dict):
            findings.append(f"queue_record_contract.allowed_states[{index}] must be an object")
            continue
        state_id = str(state.get("id", ""))
        if state.get("live_action") is not False:
            findings.append(f"queue_record_contract.allowed_states[{index}].live_action must be false")
        lowered = state_id.lower()
        if any(token in lowered for token in FORBIDDEN_STATE_TOKENS):
            findings.append(f"queue_record_contract.allowed_states[{index}].id is forbidden live/public state: {state_id}")
        for next_state in _string_list(state.get("allowed_next")):
            if next_state not in REQUIRED_STATES:
                findings.append(f"queue_record_contract.allowed_states[{index}].allowed_next unknown: {next_state}")
    return findings


def _validate_queue_items(contract: dict[str, Any], repo_root: Path) -> list[str]:
    findings: list[str] = []
    queue_items = contract.get("queue_items")
    if not isinstance(queue_items, list):
        return ["queue_items must be a list"]

    claim_matrix = _load_json(CLAIM_MATRIX_PATH)
    expected_targets = {
        item.get("target_id")
        for item in claim_matrix.get("preview_target_reviews", [])
        if isinstance(item, dict) and isinstance(item.get("target_id"), str)
    }
    item_targets = {
        item.get("target_id")
        for item in queue_items
        if isinstance(item, dict) and isinstance(item.get("target_id"), str)
    }
    missing_targets = expected_targets - item_targets
    if missing_targets:
        findings.append(f"queue_items missing targets: {sorted(missing_targets)}")

    allowed_states = _allowed_states(contract)
    for index, item in enumerate(queue_items):
        if not isinstance(item, dict):
            findings.append(f"queue_items[{index}] must be an object")
            continue
        prefix = f"queue_items[{index}]"
        for key in REQUIRED_FIELDS:
            if key not in item:
                findings.append(f"{prefix}.{key} is required")
        if item.get("target_id") not in expected_targets:
            findings.append(f"{prefix}.target_id not found in claim matrix: {item.get('target_id')}")
        if item.get("current_state") not in allowed_states:
            findings.append(f"{prefix}.current_state must be in allowed states")
        for key in TARGET_REQUIRED_TRUE_FLAGS:
            if item.get(key) is not True:
                findings.append(f"{prefix}.{key} must be true")
        if not _string_list(item.get("blockers")):
            findings.append(f"{prefix}.blockers must be a non-empty string list")
        if not _string_list(item.get("required_evidence")):
            findings.append(f"{prefix}.required_evidence must be a non-empty string list")
        rollback = str(item.get("rollback_or_archive_instruction", "")).lower()
        if not rollback or not any(word in rollback for word in ("archive", "withdraw", "delete")):
            findings.append(f"{prefix}.rollback_or_archive_instruction must include archive/withdraw/delete")
        findings.extend(_validate_item_source(item, repo_root, prefix))
    return findings


def _validate_item_source(item: dict[str, Any], repo_root: Path, prefix: str) -> list[str]:
    rel_path = str(item.get("source_artifact", ""))
    try:
        path = _safe_repo_path(repo_root, rel_path)
    except ValueError as exc:
        return [f"{prefix}.source_artifact invalid: {exc}"]
    findings: list[str] = []
    if rel_path != "agents/project/PROMOTION-ASSET-CLAIM-REVIEW-MATRIX.json":
        findings.append(f"{prefix}.source_artifact must be PROMOTION-ASSET-CLAIM-REVIEW-MATRIX.json")
    if not path.exists():
        findings.append(f"{prefix}.source_artifact missing: {rel_path}")
    elif str(item.get("source_hash", "")).lower() != _sha256(path):
        findings.append(f"{prefix}.source_hash mismatch for {rel_path}")
    return findings


def _validate_outputs(contract: dict[str, Any]) -> list[str]:
    outputs = contract.get("queue_outputs")
    if not isinstance(outputs, dict):
        return ["queue_outputs must be an object"]
    expected = {
        "json_contract": "agents/project/PROMOTION-ASSET-REVIEW-QUEUE-CONTRACT.json",
        "markdown_contract": "agents/project/PROMOTION-ASSET-REVIEW-QUEUE-CONTRACT.md",
    }
    findings: list[str] = []
    for key, value in expected.items():
        if outputs.get(key) != value:
            findings.append(f"queue_outputs.{key} must be {value}")
    for key in FORBIDDEN_KEY_NAMES:
        if outputs.get(key) is not None:
            findings.append(f"queue_outputs.{key} must be null")
    return findings


def _validate_handoff(contract: dict[str, Any]) -> list[str]:
    handoff = contract.get("taskset_handoff")
    if not isinstance(handoff, dict):
        return ["taskset_handoff must be an object"]
    findings: list[str] = []
    for key in ("task_135_complete", "taskset_complete"):
        if handoff.get(key) is not True:
            findings.append(f"taskset_handoff.{key} must be true")
    r3_items = set(_string_list(handoff.get("owner_r3_required_for")))
    for required in ("public use of any claim", "final PDF export", "SNS upload", "external account action"):
        if required not in r3_items:
            findings.append(f"taskset_handoff.owner_r3_required_for missing {required}")
    return findings


def _validate_verification(contract: dict[str, Any]) -> list[str]:
    verification = contract.get("verification")
    if not isinstance(verification, dict):
        return ["verification must be an object"]
    if "promotion_asset_review_queue_contract_gate.py --check" not in str(verification.get("local_gate", "")):
        return ["verification.local_gate must reference this gate"]
    return []


def _allowed_states(contract: dict[str, Any]) -> set[str]:
    record_contract = contract.get("queue_record_contract")
    if not isinstance(record_contract, dict):
        return set()
    states = record_contract.get("allowed_states")
    if not isinstance(states, list):
        return set()
    return {item.get("id") for item in states if isinstance(item, dict) and isinstance(item.get("id"), str)}


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
        print("promotion asset review queue contract gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"promotion asset review queue contract gate: PASS ({args.contract})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
