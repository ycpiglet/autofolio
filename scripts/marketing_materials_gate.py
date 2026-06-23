"""Validate the TASK-095 marketing materials draft packet.

The packet is source material only. This gate must keep it separate from public
publication approval, external account actions, customer contact, secret
handling, performance claims, and investment-advice claims.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKET = REPO_ROOT / "agents" / "project" / "MARKETING-MATERIALS-V1.json"

REQUIRED_BOUNDARIES = {
    "draft_source_only",
    "not_publication_approval",
    "no_public_posting",
    "no_paid_ads",
    "no_customer_contact",
    "no_external_account_action",
    "no_external_api_upload",
    "no_secret_or_private_data",
    "no_bank_account_values",
    "no_customer_records",
    "no_performance_guarantee",
    "no_investment_advice_claim",
    "no_kis_commercial_clearance_claim",
    "keeps_sales_lane_inactive",
}

REQUIRED_ASSETS = {
    "landing_page",
    "pdf_one_pager",
    "pptx_deck",
    "sns_draft_bundle",
    "support_faq",
    "disclaimer",
}

REQUIRED_CLAIM_GROUPS = {"allowed_draft", "needs_review", "do_not_use"}

FORBIDDEN_KEY_NAMES = {
    "kis_app_key",
    "kis_app_secret",
    "kis_account_number",
    "account_number",
    "bank_account",
    "resident_registration_number",
    "rrn",
    "certificate",
    "private_key",
    "access_token",
    "refresh_token",
    "client_secret",
    "api_secret",
    "password",
    "customer_email",
    "customer_phone",
}

FORBIDDEN_COPY_PHRASES = {
    "guaranteed return",
    "guaranteed returns",
    "risk-free",
    "safe return",
    "safe returns",
    "winning stocks",
    "hands-free wealth",
    "investment advice",
    "paid signal",
    "model portfolio",
    "asset manager",
    "robo-advisor",
    "kis commercial integration cleared",
}


def load_packet(path: Path = DEFAULT_PACKET) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("marketing materials packet root must be an object")
    return data


def validate_packet(packet: dict[str, Any]) -> list[str]:
    findings: list[str] = []

    if packet.get("$schema") != "autofolio.marketing-materials-v1/v1":
        findings.append("unexpected or missing marketing materials schema")
    if "draft" not in str(packet.get("status", "")).lower():
        findings.append("status must clearly remain draft")
    if "not_publication" not in str(packet.get("status", "")).lower():
        findings.append("status must clearly state this is not publication approval")

    forbidden_keys = _find_forbidden_keys(packet)
    if forbidden_keys:
        findings.append(f"forbidden secret/private key names present: {forbidden_keys}")

    boundaries = packet.get("boundaries")
    if not isinstance(boundaries, dict):
        findings.append("boundaries must be an object")
    else:
        for key in REQUIRED_BOUNDARIES:
            if boundaries.get(key) is not True:
                findings.append(f"boundaries.{key} must be true")

    campaign = packet.get("campaign_brief")
    if not isinstance(campaign, dict):
        findings.append("campaign_brief must be an object")
    else:
        if campaign.get("claim_review") not in {"draft", "compliance_review", "owner_review"}:
            findings.append("campaign_brief.claim_review must not be approved")
        if campaign.get("publishing_mode") != "manual_export_review_only":
            findings.append("campaign_brief.publishing_mode must remain manual_export_review_only")
        if "verified membership" not in str(campaign.get("cta", "")).lower():
            findings.append("campaign_brief.cta must use verified membership review")

    claim_review = packet.get("claim_review_map")
    if not isinstance(claim_review, dict):
        findings.append("claim_review_map must be an object")
    else:
        missing = REQUIRED_CLAIM_GROUPS - set(claim_review)
        if missing:
            findings.append(f"claim_review_map missing groups: {sorted(missing)}")
        for item in claim_review.get("allowed_draft", []):
            if not isinstance(item, dict) or item.get("status") != "allowed_draft":
                findings.append("allowed_draft claims must have status allowed_draft")
        for item in claim_review.get("needs_review", []):
            if not isinstance(item, dict) or item.get("status") not in {"compliance_review", "owner_review"}:
                findings.append("needs_review claims must have compliance_review or owner_review status")

    assets = packet.get("assets")
    if not isinstance(assets, dict):
        findings.append("assets must be an object")
    else:
        missing_assets = REQUIRED_ASSETS - set(assets)
        if missing_assets:
            findings.append(f"missing required assets: {sorted(missing_assets)}")
        sns = assets.get("sns_draft_bundle")
        if not isinstance(sns, dict):
            findings.append("assets.sns_draft_bundle must be an object")
        elif sns.get("status") != "draft_only":
            findings.append("assets.sns_draft_bundle.status must remain draft_only")
        elif len([item for item in sns.get("channels", []) if isinstance(item, dict)]) < 3:
            findings.append("assets.sns_draft_bundle must include at least 3 channel drafts")

    copy_inventory = packet.get("copy_inventory")
    if not isinstance(copy_inventory, list) or not copy_inventory:
        findings.append("copy_inventory must be a non-empty list")
    else:
        for index, item in enumerate(copy_inventory):
            if not isinstance(item, dict):
                findings.append(f"copy_inventory[{index}] must be an object")
                continue
            if item.get("publication_status") != "draft_only":
                findings.append(f"copy_inventory[{index}].publication_status must be draft_only")
            if item.get("claim_status") not in {"allowed_draft", "compliance_review", "owner_review"}:
                findings.append(f"copy_inventory[{index}].claim_status is invalid")
            findings.extend(_forbidden_copy_findings(str(item.get("text", "")), f"copy_inventory[{index}].text"))

    for surface, text in _asset_texts(packet.get("assets")).items():
        findings.extend(_forbidden_copy_findings(text, f"assets.{surface}"))

    forbidden_actions = set(_string_list(packet.get("forbidden_actions")))
    for required in ("public posting", "SNS auto-posting", "secret or credential storage", "investment advice claim", "performance guarantee"):
        if required not in forbidden_actions:
            findings.append(f"forbidden_actions missing: {required}")

    verification = packet.get("verification")
    if not isinstance(verification, dict):
        findings.append("verification must be an object")
    elif "marketing_materials_gate.py --check" not in str(verification.get("local_gate", "")):
        findings.append("verification.local_gate must reference this gate")

    return findings


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


def _asset_texts(assets: Any) -> dict[str, str]:
    if not isinstance(assets, dict):
        return {}
    texts: dict[str, str] = {}
    for key, value in assets.items():
        if key in {"disclaimer"}:
            continue
        texts[key] = " ".join(_collect_strings(value))
    return texts


def _collect_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend(_collect_strings(item))
        return result
    if isinstance(value, dict):
        result = []
        for child in value.values():
            result.extend(_collect_strings(child))
        return result
    return []


def _forbidden_copy_findings(text: str, path: str) -> list[str]:
    lowered = text.lower()
    return [
        f"{path} contains forbidden phrase: {phrase}"
        for phrase in sorted(FORBIDDEN_COPY_PHRASES)
        if phrase in lowered
    ]


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
        print("marketing materials gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"marketing materials gate: PASS ({args.packet})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
