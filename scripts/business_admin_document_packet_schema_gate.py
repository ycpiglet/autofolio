"""Validate the business admin document packet schema.

This gate checks local document-packet structure only. It must not log in to
official services, generate official submissions, process Owner private data,
or provide final legal, tax, accounting, securities, or regulatory advice.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKET = REPO_ROOT / "agents" / "project" / "BUSINESS-ADMIN-DOCUMENT-PACKET-SCHEMA.json"

REQUIRED_BOUNDARIES = {
    "foundation_only",
    "not_official_form",
    "no_owner_identity_data",
    "no_login_or_authentication",
    "no_signature_or_submission",
    "no_payment_or_fee",
    "no_legal_tax_securities_final_advice",
    "no_hwpx_binary_mutation",
    "no_external_service_action",
    "keeps_task_094_blocked_until_form_selected",
}

REQUIRED_SOURCE_MARKERS = {
    "National Tax Service",
    "Hancom",
    "Financial Services Commission",
    "law.go.kr",
}

REQUIRED_TOP_LEVEL_FIELDS = {
    "packet_id",
    "procedure",
    "jurisdiction",
    "status",
    "source_basis",
    "checked_at",
    "owner_non_sensitive_business_data",
    "owner_private_data_placeholders",
    "agent_drafted_text",
    "required_attachments",
    "generated_artifacts",
    "owner_only_steps",
    "review_gates",
    "forbidden_repo_data",
    "verification",
}

REQUIRED_FIELD_GROUPS = {
    "owner_non_sensitive_business_data",
    "owner_private_data_placeholders",
    "agent_drafted_text",
    "required_attachments",
    "generated_artifacts",
    "owner_only_steps",
    "review_gates",
}

REQUIRED_OWNER_ONLY_MARKERS = {
    "login",
    "authentication",
    "signature",
    "payment",
    "upload",
    "submission",
}

REQUIRED_OWNER_ONLY_STEPS = {
    "official_service_login",
    "certificate_or_identity_authentication",
    "signature_or_electronic_signature",
    "fee_payment_if_any",
    "document_upload",
    "official_submission",
}

REQUIRED_VALIDATION = {
    "business_admin_document_packet_schema_gate_passes",
    "no_forbidden_key_names_present",
    "owner_only_steps_cover_login_auth_signature_payment_submission",
    "future_hwpx_policy_requires_template_fixture_and_xml_diff",
    "task_094_remains_blocked_until_target_form_and_owner_data_path",
}

FORBIDDEN_KEY_NAMES = {
    "resident_registration_number",
    "rrn",
    "certificate_password",
    "private_key",
    "bank_account_number",
    "full_bank_account_number",
    "kis_app_key",
    "kis_app_secret",
    "api_key",
    "client_secret",
    "oauth_client_secret",
    "production_secret",
    "signed_submission_file",
    "hometax_password",
}


def load_packet(path: Path = DEFAULT_PACKET) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("document packet schema root must be an object")
    return data


def validate_packet(packet: dict[str, Any]) -> list[str]:
    findings: list[str] = []

    forbidden_paths = list(_find_forbidden_keys(packet))
    if forbidden_paths:
        findings.append(f"forbidden private/secret keys present: {forbidden_paths}")

    if packet.get("$schema") != "autofolio.business-admin-document-packet-schema/v1":
        findings.append("unexpected or missing document packet schema")

    status = str(packet.get("status", ""))
    if "foundation" not in status or "not_submission" not in status:
        findings.append("status must clearly state foundation-only and not submission-ready")

    boundaries = packet.get("boundaries")
    if not isinstance(boundaries, dict):
        findings.append("boundaries must be an object")
    else:
        for key in REQUIRED_BOUNDARIES:
            if boundaries.get(key) is not True:
                findings.append(f"boundaries.{key} must be true")

    source_text = " ".join(
        item.get("authority", "") + " " + item.get("url", "") + " " + item.get("note", "")
        for item in packet.get("source_basis", [])
        if isinstance(item, dict)
    )
    for marker in REQUIRED_SOURCE_MARKERS:
        if marker.lower() not in source_text.lower():
            findings.append(f"source_basis missing marker: {marker}")

    contract = packet.get("document_packet_contract")
    if not isinstance(contract, dict):
        findings.append("document_packet_contract must be an object")
    else:
        missing_fields = REQUIRED_TOP_LEVEL_FIELDS - set(_string_list(contract.get("required_top_level_fields")))
        if missing_fields:
            findings.append(f"missing required packet fields: {sorted(missing_fields)}")

        group_ids = {
            item.get("id")
            for item in contract.get("packet_field_groups", [])
            if isinstance(item, dict)
        }
        missing_groups = REQUIRED_FIELD_GROUPS - group_ids
        if missing_groups:
            findings.append(f"missing packet field groups: {sorted(missing_groups)}")

    hwpx_policy = packet.get("future_hwpx_policy")
    if not isinstance(hwpx_policy, dict):
        findings.append("future_hwpx_policy must be an object")
    else:
        for key in (
            "markdown_first",
            "structured_data_source_required",
            "template_fixture_required",
            "xml_diff_required",
            "human_review_required",
            "no_auto_submit",
            "target_form_required_before_generation",
        ):
            if hwpx_policy.get(key) is not True:
                findings.append(f"future_hwpx_policy.{key} must be true")

    owner_only_steps = set(_string_list(packet.get("owner_only_steps")))
    missing_owner_steps = REQUIRED_OWNER_ONLY_STEPS - owner_only_steps
    if missing_owner_steps:
        findings.append(f"missing required owner-only steps: {sorted(missing_owner_steps)}")

    owner_only_text = " ".join(owner_only_steps).lower()
    for marker in REQUIRED_OWNER_ONLY_MARKERS:
        if marker not in owner_only_text:
            findings.append(f"owner_only_steps missing marker: {marker}")

    forbidden_actions = " ".join(_string_list(packet.get("forbidden_actions"))).lower()
    for marker in ("log in", "authenticate", "sign", "pay", "upload", "submit", "private identity", "final advice"):
        if marker not in forbidden_actions:
            findings.append(f"forbidden_actions missing marker: {marker}")

    missing_validation = REQUIRED_VALIDATION - set(_string_list(packet.get("required_validation")))
    if missing_validation:
        findings.append(f"missing required validation entries: {sorted(missing_validation)}")

    verification = packet.get("verification")
    if not isinstance(verification, dict):
        findings.append("verification must be an object")
    else:
        if "business_admin_document_packet_schema_gate.py --check" not in str(
            verification.get("local_schema_gate", "")
        ):
            findings.append("verification.local_schema_gate must reference this gate")

    return findings


def _find_forbidden_keys(value: Any, prefix: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}"
            if key in FORBIDDEN_KEY_NAMES:
                findings.append(path)
            findings.extend(_find_forbidden_keys(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(_find_forbidden_keys(child, f"{prefix}[{index}]"))
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
        print("business admin document packet schema gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print(f"business admin document packet schema gate: PASS ({args.packet})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
