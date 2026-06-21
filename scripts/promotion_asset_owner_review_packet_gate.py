"""Validate the TASK-137 promotion asset Owner review packet.

This gate validates local Owner-review packet metadata only. It rejects public
approval, final advice, final asset export, live publishing, customer contact,
CRM/payment action, external account action, platform calls, secret fields, and
missing Owner/R3 blocked-action coverage.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKET = REPO_ROOT / "agents" / "project" / "PROMOTION-ASSET-OWNER-REVIEW-PACKET.json"
AUDIT_PREVIEW_PATH = REPO_ROOT / "agents" / "project" / "PROMOTION-ASSET-REVIEW-QUEUE-AUDIT-PREVIEW.json"

REQUIRED_SOURCE_IDS = {"promotion_asset_review_queue_audit_preview"}
EXPECTED_SOURCE_PATHS = {
    "promotion_asset_review_queue_audit_preview": "agents/project/PROMOTION-ASSET-REVIEW-QUEUE-AUDIT-PREVIEW.json",
}

REQUIRED_BOUNDARIES = {
    "local_owner_review_packet_only",
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

REQUIRED_DECISIONS = {
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

REQUIRED_BLOCKED_ACTIONS = {
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
    "review_items": 4,
    "owner_decisions_required": 9,
    "blocked_actions": 9,
    "public_use_blocked_items": 4,
    "final_export_blocked_items": 4,
    "external_action_blocked_items": 4,
    "customer_contact_blocked_items": 4,
    "crm_payment_blocked_items": 4,
    "secret_material_blocked_items": 4,
}

ITEM_REQUIRED_TRUE_FLAGS = {
    "owner_decision_required",
    "professional_review_required",
    "public_use_blocked",
    "final_export_blocked",
    "publication_approval_blocked",
    "external_action_blocked",
    "customer_contact_blocked",
    "crm_payment_blocked",
    "secret_material_blocked",
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
    "paid_ads_enabled",
    "platform_api_call_enabled",
    "oauth_flow_enabled",
}

FORBIDDEN_OUTPUTS = {
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


def load_packet(path: Path = DEFAULT_PACKET) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("promotion asset Owner review packet root must be an object")
    return data


def validate_packet(packet: dict[str, Any], repo_root: Path = REPO_ROOT) -> list[str]:
    findings: list[str] = []

    if packet.get("$schema") != "autofolio.promotion-asset-owner-review-packet/v1":
        findings.append("unexpected or missing promotion asset Owner review packet schema")

    if packet.get("status") != "local_owner_review_packet_not_public_approval":
        findings.append("status must be local_owner_review_packet_not_public_approval")

    boundaries = packet.get("boundaries")
    if not isinstance(boundaries, dict):
        findings.append("boundaries must be an object")
    else:
        for key in REQUIRED_BOUNDARIES:
            if boundaries.get(key) is not True:
                findings.append(f"boundaries.{key} must be true")

    forbidden_keys = _find_forbidden_keys(packet)
    if forbidden_keys:
        findings.append(f"forbidden export/customer/secret/final-advice key names present: {forbidden_keys}")

    live_true_paths = _find_live_true_keys(packet)
    if live_true_paths:
        findings.append(f"public/export/customer/payment/platform/final-advice flags must not be true: {live_true_paths}")

    findings.extend(_validate_sources(packet, repo_root))
    findings.extend(_validate_markdown_companion(packet, repo_root))
    findings.extend(_validate_summary(packet))
    findings.extend(_validate_review_items(packet))
    findings.extend(_validate_owner_decisions(packet))
    findings.extend(_validate_evidence_map(packet))
    findings.extend(_validate_blocked_actions(packet))
    findings.extend(_validate_forbidden_outputs(packet))
    findings.extend(_validate_handoff(packet))
    findings.extend(_validate_verification(packet))
    return findings


def _validate_sources(packet: dict[str, Any], repo_root: Path) -> list[str]:
    inputs = packet.get("source_inputs")
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


def _validate_markdown_companion(packet: dict[str, Any], repo_root: Path) -> list[str]:
    rel_path = str(packet.get("companion_markdown", ""))
    try:
        path = _safe_repo_path(repo_root, rel_path)
    except ValueError as exc:
        return [f"companion_markdown invalid: {exc}"]
    if not path.exists():
        return [f"companion_markdown missing: {rel_path}"]
    text = path.read_text(encoding="utf-8").lower()
    findings: list[str] = []
    for required in ("not public approval", "owner decisions", "blocked action list", "sns upload"):
        if required not in text:
            findings.append(f"companion_markdown must mention {required}")
    return findings


def _validate_summary(packet: dict[str, Any]) -> list[str]:
    summary = packet.get("packet_summary")
    if not isinstance(summary, dict):
        return ["packet_summary must be an object"]
    findings: list[str] = []
    for key, expected in REQUIRED_SUMMARY_COUNTS.items():
        if summary.get(key) != expected:
            findings.append(f"packet_summary.{key} must be {expected}")
    if summary.get("ready_for_owner_review") is not True:
        findings.append("packet_summary.ready_for_owner_review must be true")
    if summary.get("publication_approved") is not False:
        findings.append("packet_summary.publication_approved must be false")
    if summary.get("external_action_enabled") is not False:
        findings.append("packet_summary.external_action_enabled must be false")
    if summary.get("gate_result") != "pass":
        findings.append("packet_summary.gate_result must be pass")
    return findings


def _validate_review_items(packet: dict[str, Any]) -> list[str]:
    review_items = packet.get("review_items")
    if not isinstance(review_items, list):
        return ["review_items must be a list"]
    source = _load_json(AUDIT_PREVIEW_PATH)
    source_items = source.get("queue_item_summaries", [])
    expected_ids = {
        item.get("queue_item_id")
        for item in source_items
        if isinstance(item, dict) and isinstance(item.get("queue_item_id"), str)
    }
    item_ids = {
        item.get("queue_item_id")
        for item in review_items
        if isinstance(item, dict) and isinstance(item.get("queue_item_id"), str)
    }
    findings: list[str] = []
    missing = expected_ids - item_ids
    if missing:
        findings.append(f"review_items missing queue items: {sorted(missing)}")

    source_by_id = {
        item.get("queue_item_id"): item
        for item in source_items
        if isinstance(item, dict)
    }
    for index, item in enumerate(review_items):
        if not isinstance(item, dict):
            findings.append(f"review_items[{index}] must be an object")
            continue
        prefix = f"review_items[{index}]"
        source_item = source_by_id.get(item.get("queue_item_id"))
        if not isinstance(source_item, dict):
            findings.append(f"{prefix}.queue_item_id not found in source audit preview")
            continue
        for key in ("target_id", "current_state", "assigned_role"):
            if item.get(key) != source_item.get(key):
                findings.append(f"{prefix}.{key} must match source audit preview")
        for key in ITEM_REQUIRED_TRUE_FLAGS:
            if item.get(key) is not True:
                findings.append(f"{prefix}.{key} must be true")
        if not _string_list(item.get("required_evidence_refs")):
            findings.append(f"{prefix}.required_evidence_refs must be a non-empty list")
    return findings


def _validate_owner_decisions(packet: dict[str, Any]) -> list[str]:
    decisions = packet.get("owner_decision_list")
    if not isinstance(decisions, list):
        return ["owner_decision_list must be a list"]
    findings: list[str] = []
    ids = {item.get("decision_id") for item in decisions if isinstance(item, dict)}
    missing = REQUIRED_DECISIONS - ids
    if missing:
        findings.append(f"owner_decision_list missing decisions: {sorted(missing)}")
    for index, item in enumerate(decisions):
        if not isinstance(item, dict):
            findings.append(f"owner_decision_list[{index}] must be an object")
            continue
        prefix = f"owner_decision_list[{index}]"
        if item.get("status") != "requires_owner_r3":
            findings.append(f"{prefix}.status must be requires_owner_r3")
        if item.get("action_permitted_now") is not False:
            findings.append(f"{prefix}.action_permitted_now must be false")
        if item.get("external_action") is not False:
            findings.append(f"{prefix}.external_action must be false")
        if not _string_list(item.get("required_evidence")):
            findings.append(f"{prefix}.required_evidence must be a non-empty list")
    return findings


def _validate_evidence_map(packet: dict[str, Any]) -> list[str]:
    evidence = packet.get("evidence_map")
    if not isinstance(evidence, list):
        return ["evidence_map must be a list"]
    ids = {item.get("evidence_id") for item in evidence if isinstance(item, dict)}
    required = {"source_audit_preview_hash", "review_queue_contract", "claim_matrix", "channel_policy", "professional_review", "focused_gate_tests"}
    missing = required - ids
    findings: list[str] = []
    if missing:
        findings.append(f"evidence_map missing evidence ids: {sorted(missing)}")
    for index, item in enumerate(evidence):
        if not isinstance(item, dict):
            findings.append(f"evidence_map[{index}] must be an object")
            continue
        if not item.get("source") or not item.get("status") or not item.get("proves"):
            findings.append(f"evidence_map[{index}] must include source, status, and proves")
    return findings


def _validate_blocked_actions(packet: dict[str, Any]) -> list[str]:
    actions = packet.get("blocked_action_list")
    if not isinstance(actions, list):
        return ["blocked_action_list must be a list"]
    findings: list[str] = []
    ids = {item.get("action_id") for item in actions if isinstance(item, dict)}
    missing = REQUIRED_BLOCKED_ACTIONS - ids
    if missing:
        findings.append(f"blocked_action_list missing actions: {sorted(missing)}")
    for index, item in enumerate(actions):
        if not isinstance(item, dict):
            findings.append(f"blocked_action_list[{index}] must be an object")
            continue
        prefix = f"blocked_action_list[{index}]"
        if item.get("blocked") is not True:
            findings.append(f"{prefix}.blocked must be true")
        if item.get("owner_r3_required") is not True:
            findings.append(f"{prefix}.owner_r3_required must be true")
        if not isinstance(item.get("reason"), str) or not item.get("reason"):
            findings.append(f"{prefix}.reason must be a non-empty string")
    return findings


def _validate_forbidden_outputs(packet: dict[str, Any]) -> list[str]:
    outputs = set(_string_list(packet.get("forbidden_outputs")))
    missing = FORBIDDEN_OUTPUTS - outputs
    if missing:
        return [f"forbidden_outputs missing: {sorted(missing)}"]
    return []


def _validate_handoff(packet: dict[str, Any]) -> list[str]:
    handoff = packet.get("taskset_handoff")
    if not isinstance(handoff, dict):
        return ["taskset_handoff must be an object"]
    findings: list[str] = []
    for key in ("task_137_packet_ready", "taskset_local_scope_complete_when_task_closes"):
        if handoff.get(key) is not True:
            findings.append(f"taskset_handoff.{key} must be true")
    r3_items = set(_string_list(handoff.get("owner_r3_required_for")))
    for required in ("public use of any claim", "final PDF export", "SNS upload", "OAuth flow or platform API call"):
        if required not in r3_items:
            findings.append(f"taskset_handoff.owner_r3_required_for missing {required}")
    return findings


def _validate_verification(packet: dict[str, Any]) -> list[str]:
    verification = packet.get("verification")
    if not isinstance(verification, dict):
        return ["verification must be an object"]
    if "promotion_asset_owner_review_packet_gate.py --check" not in str(verification.get("local_gate", "")):
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
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--check", action="store_true", help="validate and return non-zero on findings")
    args = parser.parse_args()

    packet = load_packet(args.packet)
    findings = validate_packet(packet)
    if findings:
        print("promotion asset Owner review packet gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"promotion asset Owner review packet gate: PASS ({args.packet})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
