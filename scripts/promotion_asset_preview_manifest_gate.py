"""Validate the TASK-133 promotion asset preview manifest.

This gate validates local preview metadata only. It rejects final asset export,
public URLs, uploads, customer contact, CRM/payment action, secret fields, and
unreviewed public-claim shortcuts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "agents" / "project" / "PROMOTION-ASSET-PREVIEW-MANIFEST.json"
CONTRACT_PATH = REPO_ROOT / "agents" / "project" / "PROMOTION-ASSET-RENDERING-CONTRACT.json"
MARKETING_MATERIALS_PATH = REPO_ROOT / "agents" / "project" / "MARKETING-MATERIALS-V1.json"

REQUIRED_SOURCE_IDS = {
    "promotion_asset_rendering_contract",
    "marketing_materials_v1",
}

REQUIRED_BOUNDARIES = {
    "local_markdown_preview_manifest_only",
    "not_renderer_implementation",
    "not_publication_approval",
    "no_final_pdf_export",
    "no_final_pptx_export",
    "no_binary_asset_generation",
    "no_public_url_or_upload",
    "no_sns_upload",
    "no_external_account_action",
    "no_customer_contact",
    "no_customer_private_data",
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

REQUIRED_PREVIEW_FLAGS_TRUE = {
    "owner_approval_required",
    "public_export_blocked",
    "final_export_blocked",
    "binary_export_blocked",
    "external_upload_blocked",
    "customer_contact_blocked",
    "crm_payment_blocked",
    "secret_material_blocked",
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
    "customer_record_id",
    "payment_request_id",
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
    "live_post_enabled",
    "external_network_calls",
    "external_action_enabled",
}

FORBIDDEN_COPY_PHRASES = {
    "guaranteed returns",
    "guaranteed return",
    "risk-free",
    "safe returns",
    "investment advice",
    "paid signal",
    "model portfolio",
    "performance guarantee",
    "kis commercial integration cleared",
}


def load_manifest(path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("promotion asset preview manifest root must be an object")
    return data


def validate_manifest(manifest: dict[str, Any], repo_root: Path = REPO_ROOT) -> list[str]:
    findings: list[str] = []

    if manifest.get("$schema") != "autofolio.promotion-asset-preview-manifest/v1":
        findings.append("unexpected or missing promotion asset preview manifest schema")

    status = str(manifest.get("status", "")).lower()
    if "local_preview_manifest" not in status or "not_asset_export" not in status:
        findings.append("status must clearly remain local_preview_manifest and not_asset_export")

    boundaries = manifest.get("boundaries")
    if not isinstance(boundaries, dict):
        findings.append("boundaries must be an object")
    else:
        for key in REQUIRED_BOUNDARIES:
            if boundaries.get(key) is not True:
                findings.append(f"boundaries.{key} must be true")

    forbidden_keys = _find_forbidden_keys(manifest)
    if forbidden_keys:
        findings.append(f"forbidden export/customer/secret key names present: {forbidden_keys}")

    live_true_paths = _find_live_true_keys(manifest)
    if live_true_paths:
        findings.append(f"export/public/customer/payment flags must not be true: {live_true_paths}")

    findings.extend(_validate_sources(manifest, repo_root))
    findings.extend(_validate_markdown_companion(manifest, repo_root))
    findings.extend(_validate_asset_previews(manifest, repo_root))
    findings.extend(_validate_outputs(manifest))
    findings.extend(_validate_handoff(manifest))

    forbidden_outputs = set(_string_list(manifest.get("forbidden_outputs")))
    missing_outputs = REQUIRED_FORBIDDEN_OUTPUTS - forbidden_outputs
    if missing_outputs:
        findings.append(f"forbidden_outputs missing: {sorted(missing_outputs)}")

    verification = manifest.get("verification")
    if not isinstance(verification, dict):
        findings.append("verification must be an object")
    elif "promotion_asset_preview_manifest_gate.py --check" not in str(verification.get("local_gate", "")):
        findings.append("verification.local_gate must reference this gate")

    return findings


def _validate_sources(manifest: dict[str, Any], repo_root: Path) -> list[str]:
    findings: list[str] = []
    inputs = manifest.get("source_inputs")
    if not isinstance(inputs, list):
        return ["source_inputs must be a list"]

    source_ids = {item.get("id") for item in inputs if isinstance(item, dict)}
    missing = REQUIRED_SOURCE_IDS - source_ids
    if missing:
        findings.append(f"source_inputs missing ids: {sorted(missing)}")

    expected_paths = {
        "promotion_asset_rendering_contract": "agents/project/PROMOTION-ASSET-RENDERING-CONTRACT.json",
        "marketing_materials_v1": "agents/project/MARKETING-MATERIALS-V1.json",
    }
    for index, item in enumerate(inputs):
        if not isinstance(item, dict):
            findings.append(f"source_inputs[{index}] must be an object")
            continue
        source_id = str(item.get("id", ""))
        rel_path = str(item.get("path", ""))
        expected = expected_paths.get(source_id)
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


def _validate_markdown_companion(manifest: dict[str, Any], repo_root: Path) -> list[str]:
    findings: list[str] = []
    rel_path = str(manifest.get("companion_markdown", ""))
    try:
        path = _safe_repo_path(repo_root, rel_path)
    except ValueError as exc:
        return [f"companion_markdown invalid: {exc}"]
    if not path.exists():
        return [f"companion_markdown missing: {rel_path}"]
    text = path.read_text(encoding="utf-8").lower()
    for required in ("not asset export", "final_export_blocked=true", "public_export_blocked=true"):
        if required not in text:
            findings.append(f"companion_markdown must mention {required}")
    return findings


def _validate_asset_previews(manifest: dict[str, Any], repo_root: Path) -> list[str]:
    findings: list[str] = []
    previews = manifest.get("asset_previews")
    if not isinstance(previews, list):
        return ["asset_previews must be a list"]

    contract = _load_json(CONTRACT_PATH)
    materials = _load_json(MARKETING_MATERIALS_PATH)
    contract_targets = {
        item.get("target_id"): item
        for item in contract.get("render_targets", [])
        if isinstance(item, dict)
    }

    target_ids = {item.get("target_id") for item in previews if isinstance(item, dict)}
    missing = REQUIRED_TARGETS - target_ids
    if missing:
        findings.append(f"asset_previews missing: {sorted(missing)}")

    for index, preview in enumerate(previews):
        if not isinstance(preview, dict):
            findings.append(f"asset_previews[{index}] must be an object")
            continue
        prefix = f"asset_previews[{index}]"
        target_id = preview.get("target_id")
        contract_target = contract_targets.get(target_id)
        if not isinstance(contract_target, dict):
            findings.append(f"{prefix}.target_id not found in rendering contract: {target_id}")
        else:
            if preview.get("source_section") != contract_target.get("source_section"):
                findings.append(f"{prefix}.source_section must match rendering contract")
            if contract_target.get("render_mode") != "local_preview_source_only":
                findings.append(f"contract target {target_id} must remain local_preview_source_only")

        if preview.get("render_mode") != "local_preview_source_only":
            findings.append(f"{prefix}.render_mode must be local_preview_source_only")
        if preview.get("local_preview_kind") != "manifest_embedded_markdown_source":
            findings.append(f"{prefix}.local_preview_kind must be manifest_embedded_markdown_source")
        for key in REQUIRED_PREVIEW_FLAGS_TRUE:
            if preview.get(key) is not True:
                findings.append(f"{prefix}.{key} must be true")
        for key in ("final_export_enabled", "binary_export_enabled", "public_export_enabled"):
            if preview.get(key) is not False:
                findings.append(f"{prefix}.{key} must be false")
        if preview.get("claim_review_status") not in {"draft", "compliance_review_required"}:
            findings.append(f"{prefix}.claim_review_status must not be approved")
        if not _is_required_status(preview.get("compliance_review_status")):
            findings.append(f"{prefix}.compliance_review_status must require review")
        if not _is_required_status(preview.get("owner_approval_status")):
            findings.append(f"{prefix}.owner_approval_status must require Owner approval")
        rollback = str(preview.get("rollback_or_delete_instruction", "")).lower()
        if not rollback or not any(word in rollback for word in ("delete", "archive", "withdraw")):
            findings.append(f"{prefix}.rollback_or_delete_instruction must include delete/archive/withdraw")
        if not _string_list(preview.get("preview_snapshot")):
            findings.append(f"{prefix}.preview_snapshot must be a non-empty string list")

        findings.extend(_validate_preview_source(preview, repo_root, prefix))
        findings.extend(_validate_source_section_exists(materials, str(preview.get("source_section", "")), prefix))

        text = " ".join(_collect_strings(preview)).lower()
        for phrase in sorted(FORBIDDEN_COPY_PHRASES):
            if phrase in text:
                findings.append(f"{prefix} contains forbidden phrase: {phrase}")
    return findings


def _validate_preview_source(preview: dict[str, Any], repo_root: Path, prefix: str) -> list[str]:
    findings: list[str] = []
    rel_path = str(preview.get("source_artifact", ""))
    try:
        path = _safe_repo_path(repo_root, rel_path)
    except ValueError as exc:
        return [f"{prefix}.source_artifact invalid: {exc}"]
    if not path.exists():
        return [f"{prefix}.source_artifact missing: {rel_path}"]
    if rel_path != "agents/project/MARKETING-MATERIALS-V1.json":
        findings.append(f"{prefix}.source_artifact must be MARKETING-MATERIALS-V1.json")
    if str(preview.get("source_hash", "")).lower() != _sha256(path):
        findings.append(f"{prefix}.source_hash mismatch for {rel_path}")
    return findings


def _validate_source_section_exists(materials: dict[str, Any], dotted: str, prefix: str) -> list[str]:
    current: Any = materials
    if "." not in dotted and isinstance(materials.get("assets"), dict) and dotted in materials["assets"]:
        return []
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            return [f"{prefix}.source_section does not exist in MARKETING-MATERIALS-V1: {dotted}"]
        current = current[part]
    return []


def _validate_outputs(manifest: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    outputs = manifest.get("manifest_outputs")
    if not isinstance(outputs, dict):
        return ["manifest_outputs must be an object"]
    for key in (
        "final_pdf_path",
        "final_pptx_path",
        "public_url",
        "external_upload_id",
        "customer_record_id",
        "payment_request_id",
    ):
        if outputs.get(key) is not None:
            findings.append(f"manifest_outputs.{key} must be null")
    return findings


def _validate_handoff(manifest: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    handoff = manifest.get("taskset_handoff")
    if not isinstance(handoff, dict):
        return ["taskset_handoff must be an object"]
    for key in ("task_132_complete", "task_133_complete", "taskset_complete"):
        if handoff.get(key) is not True:
            findings.append(f"taskset_handoff.{key} must be true")
    r3_items = set(_string_list(handoff.get("owner_r3_required_for")))
    for required in ("final PDF export", "SNS upload", "CRM/customer-record activation"):
        if required not in r3_items:
            findings.append(f"taskset_handoff.owner_r3_required_for missing {required}")
    return findings


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


def _collect_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend(_collect_strings(item))
        return result
    if isinstance(value, dict):
        result: list[str] = []
        for child in value.values():
            result.extend(_collect_strings(child))
        return result
    return []


def _is_required_status(value: Any) -> bool:
    lowered = str(value or "").strip().lower().replace("-", "_")
    if not lowered:
        return False
    if lowered in {"not_required", "none_required", "unrequired"}:
        return False
    if "not required" in lowered or "no review required" in lowered:
        return False
    return "required" in lowered


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--check", action="store_true", help="validate and return non-zero on findings")
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    findings = validate_manifest(manifest)
    if findings:
        print("promotion asset preview manifest gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"promotion asset preview manifest gate: PASS ({args.manifest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
