"""Validate the TASK-132 promotion asset rendering contract.

This gate allows only a local rendering contract. It rejects final PDF/PPTX
export, binary generation, public uploads, customer contact, CRM/payment action,
secret fields, and unreviewed public claim shortcuts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = REPO_ROOT / "agents" / "project" / "PROMOTION-ASSET-RENDERING-CONTRACT.json"

REQUIRED_SOURCE_IDS = {
    "marketing_materials_v1",
    "marketing_brief",
    "sales_revenue_lane_decision",
}

REQUIRED_BOUNDARIES = {
    "contract_only",
    "not_renderer_implementation",
    "not_publication_approval",
    "no_final_pdf_export",
    "no_final_pptx_export",
    "no_binary_asset_generation",
    "no_public_url_or_upload",
    "no_external_account_action",
    "no_customer_contact",
    "no_customer_private_data",
    "no_paid_ads",
    "no_crm_or_payment_action",
    "no_secret_or_token_storage",
    "no_kis_order_risk_prod_deploy_change",
    "owner_approval_required_before_public_export",
    "compliance_review_required_before_public_claim_use",
}

REQUIRED_TARGETS = {
    "landing_page_source",
    "pdf_one_pager_source",
    "pptx_deck_source",
    "sns_text_bundle_source",
}

REQUIRED_QUEUE_FIELDS = {
    "asset_id",
    "target_id",
    "source_artifact",
    "source_hash",
    "source_section",
    "render_mode",
    "claim_review_status",
    "owner_approval_required",
    "public_export_blocked",
    "final_export_blocked",
    "rollback_or_delete_instruction",
}

REQUIRED_FORBIDDEN_OUTPUTS = {
    "final PDF binary",
    "final PPTX binary",
    "public landing page deployment",
    "SNS upload",
    "customer email or direct message",
    "paid ad creative upload",
    "CRM lead or customer record",
    "payment or checkout request",
    "external URL publication",
    "investment advice claim",
    "paid signal claim",
    "model portfolio claim",
    "performance guarantee",
    "KIS commercial clearance claim",
    "secret or token material",
}

FORBIDDEN_KEY_NAMES = {
    "access_token",
    "refresh_token",
    "client_secret",
    "api_secret",
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
    "kis_app_secret",
}

LIVE_TRUE_KEYS = {
    "final_export_enabled",
    "binary_export_enabled",
    "public_export_enabled",
    "external_upload_enabled",
    "customer_contact_enabled",
    "crm_action_enabled",
    "payment_action_enabled",
    "secret_storage_enabled",
}


def load_contract(path: Path = DEFAULT_CONTRACT) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("promotion asset rendering contract root must be an object")
    return data


def validate_contract(contract: dict[str, Any], repo_root: Path = REPO_ROOT) -> list[str]:
    findings: list[str] = []

    if contract.get("$schema") != "autofolio.promotion-asset-rendering-contract/v1":
        findings.append("unexpected or missing promotion asset rendering contract schema")

    status = str(contract.get("status", "")).lower()
    if "local_contract" not in status or "not_asset_export" not in status:
        findings.append("status must clearly remain local_contract and not_asset_export")

    forbidden_keys = _find_forbidden_keys(contract)
    if forbidden_keys:
        findings.append(f"forbidden export/customer/secret key names present: {forbidden_keys}")

    live_true_paths = _find_live_true_keys(contract)
    if live_true_paths:
        findings.append(f"export/public/customer/payment flags must not be true: {live_true_paths}")

    boundaries = contract.get("boundaries")
    if not isinstance(boundaries, dict):
        findings.append("boundaries must be an object")
    else:
        for key in REQUIRED_BOUNDARIES:
            if boundaries.get(key) is not True:
                findings.append(f"boundaries.{key} must be true")

    findings.extend(_validate_sources(contract, repo_root))
    findings.extend(_validate_targets(contract))
    findings.extend(_validate_queue_contract(contract))

    forbidden_outputs = set(_string_list(contract.get("forbidden_outputs")))
    missing_outputs = REQUIRED_FORBIDDEN_OUTPUTS - forbidden_outputs
    if missing_outputs:
        findings.append(f"forbidden_outputs missing: {sorted(missing_outputs)}")

    next_slices = contract.get("allowed_next_local_slices")
    if not isinstance(next_slices, list) or not next_slices:
        findings.append("allowed_next_local_slices must be a non-empty list")
    else:
        candidates = {item.get("candidate") for item in next_slices if isinstance(item, dict)}
        if "TASK-133-promotion-asset-preview-manifest" not in candidates:
            findings.append("allowed_next_local_slices must include TASK-133-promotion-asset-preview-manifest")
        for index, item in enumerate(next_slices):
            if isinstance(item, dict) and item.get("safe_without_owner") is not True:
                findings.append(f"allowed_next_local_slices[{index}].safe_without_owner must be true")

    handoff = contract.get("taskset_handoff")
    if not isinstance(handoff, dict):
        findings.append("taskset_handoff must be an object")
    else:
        if handoff.get("task_132_complete") is not True:
            findings.append("taskset_handoff.task_132_complete must be true")
        if handoff.get("task_133_next") is not True:
            findings.append("taskset_handoff.task_133_next must be true")
        if handoff.get("taskset_complete") is not False:
            findings.append("taskset_handoff.taskset_complete must be false")

    verification = contract.get("verification")
    if not isinstance(verification, dict):
        findings.append("verification must be an object")
    elif "promotion_asset_rendering_contract_gate.py --check" not in str(verification.get("local_gate", "")):
        findings.append("verification.local_gate must reference this gate")

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
        rel_path = str(item.get("path", ""))
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


def _validate_targets(contract: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    targets = contract.get("render_targets")
    if not isinstance(targets, list):
        return ["render_targets must be a list"]
    target_ids = {item.get("target_id") for item in targets if isinstance(item, dict)}
    missing = REQUIRED_TARGETS - target_ids
    if missing:
        findings.append(f"render_targets missing: {sorted(missing)}")
    for index, target in enumerate(targets):
        if not isinstance(target, dict):
            findings.append(f"render_targets[{index}] must be an object")
            continue
        prefix = f"render_targets[{index}]"
        if target.get("render_mode") != "local_preview_source_only":
            findings.append(f"{prefix}.render_mode must be local_preview_source_only")
        if target.get("allowed_intermediate") != "md":
            findings.append(f"{prefix}.allowed_intermediate must be md")
        for key in ("final_export_enabled", "binary_export_enabled", "public_export_enabled"):
            if target.get(key) is not False:
                findings.append(f"{prefix}.{key} must be false")
        reviews = set(_string_list(target.get("review_required")))
        if not any("Compliance Officer" in item for item in reviews):
            findings.append(f"{prefix}.review_required must include Compliance Officer")
        if not any("Owner before" in item for item in reviews):
            findings.append(f"{prefix}.review_required must include Owner before public/export use")
    return findings


def _validate_queue_contract(contract: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    queue = contract.get("render_queue_contract")
    if not isinstance(queue, dict):
        return ["render_queue_contract must be an object"]
    missing_fields = REQUIRED_QUEUE_FIELDS - set(_string_list(queue.get("required_fields")))
    if missing_fields:
        findings.append(f"render_queue_contract.required_fields missing: {sorted(missing_fields)}")
    forbidden_fields = set(_string_list(queue.get("forbidden_fields")))
    for required in ("final_pdf_path", "final_pptx_path", "public_url", "customer_email", "access_token"):
        if required not in forbidden_fields:
            findings.append(f"render_queue_contract.forbidden_fields missing {required}")
    return findings


def _safe_repo_path(repo_root: Path, rel_path: str) -> Path:
    if not rel_path or Path(rel_path).is_absolute():
        raise ValueError("path must be a non-empty relative path")
    resolved = (repo_root / rel_path).resolve()
    root = repo_root.resolve()
    if root not in resolved.parents and resolved != root:
        raise ValueError("path must stay inside repository")
    return resolved


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
        print("promotion asset rendering contract gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"promotion asset rendering contract gate: PASS ({args.contract})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
