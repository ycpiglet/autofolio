"""Validate the KIS commercial terms review packet.

This gate validates local review artifacts only. It must not log into KIS,
contact KIS, collect credentials, enable KIS production, or change order/risk
behavior.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKET = (
    REPO_ROOT
    / "agents"
    / "project"
    / "MEMBERSHIP-KIS-COMMERCIAL-TERMS-REVIEW-PACKET.json"
)

REQUIRED_BOUNDARIES = {
    "review_packet_only",
    "not_legal_advice",
    "not_kis_clearance",
    "no_kis_login",
    "no_kis_account_access",
    "no_kis_credential_collection",
    "no_external_contact",
    "no_order_path_change",
    "no_real_market_data_redistribution",
    "no_production_kis_activation",
    "keeps_kis_env_mock_for_external_staging",
    "keeps_can_launch_false",
}

REQUIRED_SOURCE_IDS = {
    "kis_developers_provider_guide",
    "kis_developers_provider_api_start",
    "kis_open_api_affiliate_user_terms_pdf",
    "kis_open_api_terms_revision_notice",
    "efriend_expert_open_api_service",
    "fsc_robo_advisor_interpretation",
}

REQUIRED_FINDINGS = {
    "self_owned_account_open_api_is_not_third_party_clearance",
    "third_party_service_points_to_partner_surface",
    "market_data_contract_required_for_partner_brand_use",
    "order_api_requires_regulatory_process_review",
    "affiliate_user_terms_assume_approved_institution",
    "load_and_service_suspension_terms_affect_operations",
}

REQUIRED_QUESTIONS = {
    "third_party_service_boundary",
    "software_only_vs_hosted_service",
    "market_data_display_rights",
    "order_api_user_approval_model",
    "credential_storage_and_token_handling",
    "investment_advice_and_discretionary_boundary",
    "rate_limit_and_load_controls",
    "terms_revision_monitoring",
}

REQUIRED_NEXT_EVIDENCE = {
    "owner_kis_terms_review_completed",
    "kis_or_legal_answer_on_third_party_service_boundary",
    "market_data_rights_answer",
    "order_api_user_approval_model_answer",
    "credential_storage_requirements_answer",
    "investment_advice_boundary_answer",
    "rate_limit_and_service_suspension_controls",
}

FORBIDDEN_KEY_NAMES = {
    "kis_app_key",
    "kis_app_secret",
    "kis_account_number",
    "account_number",
    "access_token",
    "refresh_token",
    "approval_key",
    "partner_contract_id",
    "production_kis_enabled",
    "legal_clearance_complete",
    "kis_clearance_complete",
}


def load_packet(path: Path = DEFAULT_PACKET) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("KIS terms review packet root must be an object")
    return data


def validate_packet(packet: dict[str, Any]) -> list[str]:
    findings: list[str] = []

    forbidden_paths = _find_forbidden_keys(packet)
    if forbidden_paths:
        findings.append(f"forbidden KIS credential/clearance keys present: {forbidden_paths}")

    if packet.get("$schema") != "autofolio.membership-kis-commercial-terms-review-packet/v1":
        findings.append("unexpected or missing KIS terms review packet schema")
    if "not_clearance" not in str(packet.get("status", "")):
        findings.append("status must clearly state this is not clearance")

    boundaries = packet.get("boundaries")
    if not isinstance(boundaries, dict):
        findings.append("boundaries must be an object")
    else:
        for key in REQUIRED_BOUNDARIES:
            if boundaries.get(key) is not True:
                findings.append(f"boundaries.{key} must be true")

    source_ids = {
        item.get("id")
        for item in packet.get("source_basis", [])
        if isinstance(item, dict)
    }
    missing_sources = REQUIRED_SOURCE_IDS - source_ids
    if missing_sources:
        findings.append(f"missing source ids: {sorted(missing_sources)}")

    source_text = " ".join(
        item.get("authority", "") + " " + item.get("url", "") + " " + item.get("finding", "")
        for item in packet.get("source_basis", [])
        if isinstance(item, dict)
    )
    for marker in ("Korea Investment", "KIS", "Open API", "FSC"):
        if marker.lower() not in source_text.lower():
            findings.append(f"source_basis missing marker: {marker}")

    classification = packet.get("classification")
    if not isinstance(classification, dict):
        findings.append("classification must be an object")
    else:
        for key in ("commercial_clearance", "third_party_service_clearance", "market_data_redistribution_clearance", "order_api_clearance"):
            if classification.get(key) != "missing":
                findings.append(f"classification.{key} must remain missing")
        if classification.get("professional_review_required") is not True:
            findings.append("classification.professional_review_required must be true")

    finding_ids = {
        item.get("id")
        for item in packet.get("findings", [])
        if isinstance(item, dict)
    }
    missing_findings = REQUIRED_FINDINGS - finding_ids
    if missing_findings:
        findings.append(f"missing finding ids: {sorted(missing_findings)}")
    for item in packet.get("findings", []):
        if isinstance(item, dict) and item.get("state") not in {"watch", "block_launch"}:
            findings.append(f"{item.get('id', '<unknown>')}: state must be watch or block_launch")

    question_ids = {
        item.get("id")
        for item in packet.get("owner_kis_legal_question_set", [])
        if isinstance(item, dict)
    }
    missing_questions = REQUIRED_QUESTIONS - question_ids
    if missing_questions:
        findings.append(f"missing question ids: {sorted(missing_questions)}")

    next_evidence = set(_string_list(packet.get("required_next_evidence")))
    missing_evidence = REQUIRED_NEXT_EVIDENCE - next_evidence
    if missing_evidence:
        findings.append(f"missing required next evidence: {sorted(missing_evidence)}")

    launch_policy = packet.get("launch_policy")
    if not isinstance(launch_policy, dict):
        findings.append("launch_policy must be an object")
    else:
        policy_text = " ".join(str(value) for value in launch_policy.values())
        for marker in ("KIS_ENV", "mock", "KIS", "can_launch"):
            if marker not in policy_text:
                findings.append(f"launch_policy missing marker: {marker}")

    forbidden_runtime = " ".join(_string_list(packet.get("forbidden_actions")))
    for marker in ("KIS", "credentials", "OrderFlow", "can_launch"):
        if marker not in forbidden_runtime:
            findings.append(f"forbidden_actions missing marker: {marker}")

    verification = packet.get("verification")
    if not isinstance(verification, dict):
        findings.append("verification must be an object")
    elif "membership_kis_terms_review_gate.py --check" not in str(verification.get("local_gate", "")):
        findings.append("verification.local_gate must reference this gate")

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
        print("membership KIS terms review gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"membership KIS terms review gate: PASS ({args.packet})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
