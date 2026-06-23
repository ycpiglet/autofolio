"""Validate the TASK-168 promotion asset generator readiness map.

This gate validates local readiness metadata only. It rejects final PDF/PPTX
exports, public URLs, SNS uploads, customer contact, CRM/payment action,
platform OAuth/API work, secret fields, and unreviewed public-claim shortcuts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAP = REPO_ROOT / "agents" / "project" / "PROMOTION-ASSET-GENERATOR-READINESS-MAP.json"

REQUIRED_SOURCE_IDS = {
    "marketing_materials_v1",
    "promotion_campaign_backlog_calendar_v1",
    "promotion_asset_rendering_contract",
    "promotion_asset_preview_manifest",
    "marketing_brief",
    "promotion_channel_policy_matrix",
}

REQUIRED_BOUNDARIES = {
    "local_readiness_map_only",
    "not_renderer_implementation",
    "not_asset_export",
    "not_publication_approval",
    "no_final_pdf_export",
    "no_final_pptx_export",
    "no_binary_asset_generation",
    "no_public_destination_or_upload",
    "no_sns_upload",
    "no_external_account_action",
    "no_oauth_flow",
    "no_platform_api_call",
    "no_browser_automation_against_social_platform",
    "no_customer_contact",
    "no_customer_private_data",
    "no_crm_or_payment_action",
    "no_secret_or_token_storage",
    "no_sales_revenue_activation",
    "no_kis_order_risk_prod_deploy_change",
    "owner_approval_required_before_final_export",
    "compliance_review_required_before_public_claim_use",
}

REQUIRED_SURFACES = {
    "landing_page_source",
    "pdf_one_pager_source",
    "pptx_deck_source",
    "sns_draft_bundle_source",
}

REQUIRED_TOOLING_STAGES = {
    "source_parse",
    "hash_manifest",
    "template_mapping",
    "preview_manifest",
    "claim_review_link",
    "export_blocker",
    "rollback_manifest",
}

REQUIRED_SURFACE_TRUE_FLAGS = {
    "owner_r3_required_for_final",
    "claim_review_required",
    "public_export_blocked",
    "final_export_blocked",
    "binary_export_blocked",
    "external_action_blocked",
    "customer_contact_blocked",
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
    "OAuth flow or platform API call",
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
    "oauth_flow_enabled",
    "platform_api_call_enabled",
    "browser_automation_enabled",
    "sales_revenue_activation_enabled",
}


def load_readiness_map(path: Path = DEFAULT_MAP) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("promotion asset generator readiness map root must be an object")
    return data


def validate_readiness_map(readiness_map: dict[str, Any], repo_root: Path = REPO_ROOT) -> list[str]:
    findings: list[str] = []

    if readiness_map.get("$schema") != "autofolio.promotion-asset-generator-readiness-map/v1":
        findings.append("unexpected or missing promotion asset generator readiness map schema")

    status = str(readiness_map.get("status", "")).lower()
    if "readiness_map" not in status or "not_asset_export" not in status:
        findings.append("status must clearly remain readiness_map and not_asset_export")

    forbidden_keys = _find_forbidden_keys(readiness_map)
    if forbidden_keys:
        findings.append(f"forbidden export/customer/secret key names present: {forbidden_keys}")

    live_true_paths = _find_live_true_keys(readiness_map)
    if live_true_paths:
        findings.append(f"export/public/customer/payment/platform flags must not be true: {live_true_paths}")

    boundaries = readiness_map.get("boundaries")
    if not isinstance(boundaries, dict):
        findings.append("boundaries must be an object")
    else:
        for key in REQUIRED_BOUNDARIES:
            if boundaries.get(key) is not True:
                findings.append(f"boundaries.{key} must be true")

    source_lookup, source_findings = _validate_sources(readiness_map, repo_root)
    findings.extend(source_findings)
    findings.extend(_validate_asset_surfaces(readiness_map, source_lookup, repo_root))
    findings.extend(_validate_tooling_readiness(readiness_map))
    findings.extend(_validate_future_tasks(readiness_map))
    findings.extend(_validate_handoff(readiness_map))

    forbidden_outputs = set(_string_list(readiness_map.get("forbidden_outputs")))
    missing_outputs = REQUIRED_FORBIDDEN_OUTPUTS - forbidden_outputs
    if missing_outputs:
        findings.append(f"forbidden_outputs missing: {sorted(missing_outputs)}")

    verification = readiness_map.get("verification")
    if not isinstance(verification, dict):
        findings.append("verification must be an object")
    elif "promotion_asset_generator_readiness_map_gate.py --check" not in str(
        verification.get("local_gate", "")
    ):
        findings.append("verification.local_gate must reference this gate")

    return findings


def _validate_sources(readiness_map: dict[str, Any], repo_root: Path) -> tuple[dict[str, dict[str, Any]], list[str]]:
    findings: list[str] = []
    inputs = readiness_map.get("source_inputs")
    if not isinstance(inputs, list):
        return {}, ["source_inputs must be a list"]

    source_lookup: dict[str, dict[str, Any]] = {}
    source_ids = {item.get("id") for item in inputs if isinstance(item, dict)}
    missing = REQUIRED_SOURCE_IDS - source_ids
    if missing:
        findings.append(f"source_inputs missing ids: {sorted(missing)}")

    for index, item in enumerate(inputs):
        if not isinstance(item, dict):
            findings.append(f"source_inputs[{index}] must be an object")
            continue
        source_id = str(item.get("id", ""))
        source_lookup[source_id] = item
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
    return source_lookup, findings


def _validate_asset_surfaces(
    readiness_map: dict[str, Any],
    source_lookup: dict[str, dict[str, Any]],
    repo_root: Path,
) -> list[str]:
    findings: list[str] = []
    surfaces = readiness_map.get("asset_surfaces")
    if not isinstance(surfaces, list):
        return ["asset_surfaces must be a list"]

    target_ids = {item.get("target_id") for item in surfaces if isinstance(item, dict)}
    missing = REQUIRED_SURFACES - target_ids
    if missing:
        findings.append(f"asset_surfaces missing: {sorted(missing)}")

    for index, surface in enumerate(surfaces):
        if not isinstance(surface, dict):
            findings.append(f"asset_surfaces[{index}] must be an object")
            continue
        prefix = f"asset_surfaces[{index}]"
        if surface.get("output_mode") != "local_source_or_preview_only":
            findings.append(f"{prefix}.output_mode must be local_source_or_preview_only")
        for key in REQUIRED_SURFACE_TRUE_FLAGS:
            if surface.get(key) is not True:
                findings.append(f"{prefix}.{key} must be true")
        for key in ("final_export_enabled", "binary_export_enabled", "public_export_enabled"):
            if surface.get(key) is not False:
                findings.append(f"{prefix}.{key} must be false")

        source_id = str(surface.get("source_input_id", ""))
        source = source_lookup.get(source_id)
        if not isinstance(source, dict):
            findings.append(f"{prefix}.source_input_id missing from source_inputs: {source_id}")
        else:
            if surface.get("source_artifact") != source.get("path"):
                findings.append(f"{prefix}.source_artifact must match source input path")
            if surface.get("source_sha256") != source.get("sha256"):
                findings.append(f"{prefix}.source_sha256 must match source input sha256")
            rel_path = str(surface.get("source_artifact", ""))
            try:
                path = _safe_repo_path(repo_root, rel_path)
            except ValueError as exc:
                findings.append(f"{prefix}.source_artifact invalid: {exc}")
            else:
                if not path.exists():
                    findings.append(f"{prefix}.source_artifact missing: {rel_path}")
                elif str(surface.get("source_sha256", "")).lower() != _sha256(path):
                    findings.append(f"{prefix}.source_sha256 mismatch for {rel_path}")

        renderer = surface.get("renderer_candidate")
        if not isinstance(renderer, dict):
            findings.append(f"{prefix}.renderer_candidate must be an object")
        else:
            if renderer.get("stage") != "candidate_not_implementation":
                findings.append(f"{prefix}.renderer_candidate.stage must be candidate_not_implementation")
            if renderer.get("implementation_started") is not False:
                findings.append(f"{prefix}.renderer_candidate.implementation_started must be false")

        reviews = set(_string_list(surface.get("required_reviews")))
        if "Compliance Officer" not in reviews:
            findings.append(f"{prefix}.required_reviews must include Compliance Officer")
        if "Owner/R3 before final or public use" not in reviews:
            findings.append(f"{prefix}.required_reviews must include Owner/R3 before final or public use")
        rollback = str(surface.get("rollback_or_delete_requirement", "")).lower()
        if not rollback or not any(word in rollback for word in ("delete", "archive", "withdraw")):
            findings.append(f"{prefix}.rollback_or_delete_requirement must include delete/archive/withdraw")
    return findings


def _validate_tooling_readiness(readiness_map: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    stages = readiness_map.get("tooling_readiness")
    if not isinstance(stages, list):
        return ["tooling_readiness must be a list"]
    stage_ids = {item.get("stage_id") for item in stages if isinstance(item, dict)}
    missing = REQUIRED_TOOLING_STAGES - stage_ids
    if missing:
        findings.append(f"tooling_readiness missing stages: {sorted(missing)}")
    for index, stage in enumerate(stages):
        if not isinstance(stage, dict):
            findings.append(f"tooling_readiness[{index}] must be an object")
            continue
        prefix = f"tooling_readiness[{index}]"
        if stage.get("local_only") is not True:
            findings.append(f"{prefix}.local_only must be true")
        if stage.get("owner_r3_required_for_output") is not True:
            findings.append(f"{prefix}.owner_r3_required_for_output must be true")
        for key in (
            "external_action_enabled",
            "final_export_enabled",
            "binary_export_enabled",
            "public_export_enabled",
            "platform_api_call_enabled",
            "oauth_flow_enabled",
        ):
            if stage.get(key) is not False:
                findings.append(f"{prefix}.{key} must be false")
    return findings


def _validate_future_tasks(readiness_map: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    tasks = readiness_map.get("future_implementation_tasks")
    if not isinstance(tasks, list) or not tasks:
        return ["future_implementation_tasks must be a non-empty list"]
    levels = {item.get("reversibility_level") for item in tasks if isinstance(item, dict)}
    if "R2" not in levels:
        findings.append("future_implementation_tasks must include at least one R2 local implementation candidate")
    if "R3" not in levels:
        findings.append("future_implementation_tasks must include at least one R3 Owner-approval candidate")
    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            findings.append(f"future_implementation_tasks[{index}] must be an object")
            continue
        prefix = f"future_implementation_tasks[{index}]"
        if task.get("reversibility_level") not in {"R2", "R3"}:
            findings.append(f"{prefix}.reversibility_level must be R2 or R3")
        if task.get("external_action_enabled") is not False:
            findings.append(f"{prefix}.external_action_enabled must be false")
        level = task.get("reversibility_level")
        if level == "R3" and task.get("owner_approval_required_before_execution") is not True:
            findings.append(f"{prefix}.owner_approval_required_before_execution must be true for R3")
        if level == "R2":
            if task.get("safe_without_owner") is not True:
                findings.append(f"{prefix}.safe_without_owner must be true for R2")
            if task.get("owner_approval_required_before_execution") is not False:
                findings.append(f"{prefix}.owner_approval_required_before_execution must be false for R2")
    return findings


def _validate_handoff(readiness_map: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    handoff = readiness_map.get("taskset_handoff")
    if not isinstance(handoff, dict):
        return ["taskset_handoff must be an object"]
    expected = {
        "task_168_complete": True,
        "task_169_next": True,
        "taskset_complete": False,
        "final_asset_export_approved": False,
        "live_publication_approved": False,
        "customer_contact_enabled": False,
        "sales_revenue_activation_enabled": False,
    }
    for key, value in expected.items():
        if handoff.get(key) is not value:
            findings.append(f"taskset_handoff.{key} must be {str(value).lower()}")
    r3_items = set(_string_list(handoff.get("owner_r3_required_for")))
    for required in ("final PDF export", "final PPTX export", "SNS upload", "customer contact"):
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
    parser.add_argument("--map", type=Path, default=DEFAULT_MAP)
    parser.add_argument("--check", action="store_true", help="validate and return non-zero on findings")
    args = parser.parse_args()

    readiness_map = load_readiness_map(args.map)
    findings = validate_readiness_map(readiness_map)
    if findings:
        print("promotion asset generator readiness map gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"promotion asset generator readiness map gate: PASS ({args.map})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
