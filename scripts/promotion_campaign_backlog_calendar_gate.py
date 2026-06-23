"""Validate the TASK-167 promotion campaign backlog and content calendar.

This packet is draft planning only. It must keep campaign copy separated from
review-required or forbidden claims, and it must not enable publication,
customer contact, external platform action, final asset export, CRM/payment,
Sales/Revenue activation, secrets, or KIS/order/risk/prod/deploy changes.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKET = REPO_ROOT / "agents" / "project" / "PROMOTION-CAMPAIGN-BACKLOG-CALENDAR-V1.json"

REQUIRED_SOURCE_KEYS = {
    "business_plan",
    "marketing_brief",
    "marketing_materials_v1",
    "marketing_team_operating_model",
    "promotion_channel_policy_matrix",
    "promotion_publishing_state_machine",
}

REQUIRED_BOUNDARIES = {
    "draft_planning_only",
    "not_publication_approval",
    "no_public_posting",
    "no_paid_ads",
    "no_customer_contact",
    "no_customer_records",
    "no_crm_activation",
    "no_payment_request",
    "no_sales_revenue_activation",
    "no_external_account_action",
    "no_oauth_flow",
    "no_platform_api_call",
    "no_browser_automation_against_social_platform",
    "no_secret_or_token_handling",
    "no_final_asset_export",
    "no_public_url_publication",
    "no_investment_advice_publication",
    "no_kis_order_risk_prod_deploy_change",
}

REQUIRED_CAMPAIGN_IDS = {
    "private_pilot_explainer",
    "owner_blog_devlog",
    "landing_page_source",
    "pdf_pptx_source_bundle",
    "sns_draft_bundle",
}

REQUIRED_CLAIM_GROUPS = {"allowed_draft", "needs_review", "do_not_use"}

REQUIRED_REVIEW_QUEUES = {
    "compliance_review_required",
    "owner_r3_required",
    "business_planner_review_required",
}

REQUIRED_FORBIDDEN_ACTIONS = {
    "public posting",
    "SNS upload",
    "paid ads",
    "customer contact",
    "CRM activation",
    "customer record storage",
    "payment request",
    "billing setup",
    "Sales/Revenue role activation",
    "OAuth flow",
    "token handling",
    "platform API call",
    "browser automation against social platforms",
    "final PDF export",
    "final PPTX export",
    "public URL publication",
    "secret storage",
    "KIS/order/risk/prod/deploy change",
}

FORBIDDEN_KEY_NAMES = {
    "access_token",
    "refresh_token",
    "client_secret",
    "api_secret",
    "app_secret",
    "password",
    "cookie",
    "session",
    "customer_email",
    "customer_phone",
    "customer_name",
    "bank_account_number",
    "card_number",
    "payment_provider_secret",
    "crm_api_key",
    "ad_account_id",
    "kis_app_secret",
}

LIVE_TRUE_KEYS = {
    "public_posting_enabled",
    "public_post_enabled",
    "sns_upload_enabled",
    "paid_ads_enabled",
    "customer_contact_enabled",
    "customer_records_enabled",
    "crm_enabled",
    "crm_activation_enabled",
    "payment_request_enabled",
    "sales_revenue_lane_active",
    "oauth_flow_enabled",
    "platform_api_call_enabled",
    "browser_automation_enabled",
    "final_asset_export_approved",
    "live_publication_approved",
    "public_url_publication_enabled",
    "secret_storage_enabled",
    "kis_order_risk_prod_deploy_enabled",
    "live_action_enabled",
    "publish_ready",
}


def load_packet(path: Path = DEFAULT_PACKET) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("promotion campaign backlog calendar root must be an object")
    return data


def validate_packet(packet: dict[str, Any]) -> list[str]:
    findings: list[str] = []

    if packet.get("$schema") != "autofolio.promotion-campaign-backlog-calendar-v1/v1":
        findings.append("unexpected or missing promotion campaign backlog calendar schema")

    status = str(packet.get("status", "")).lower()
    if "draft" not in status or "not_publication" not in status:
        findings.append("status must clearly remain draft and not_publication")

    forbidden_keys = _find_forbidden_keys(packet)
    if forbidden_keys:
        findings.append(f"forbidden secret/customer/payment key names present: {forbidden_keys}")

    live_true_paths = _find_live_true_keys(packet)
    if live_true_paths:
        findings.append(f"live or external action flags must not be true: {live_true_paths}")

    source = packet.get("source_of_truth")
    if not isinstance(source, dict):
        findings.append("source_of_truth must be an object")
    else:
        missing_sources = REQUIRED_SOURCE_KEYS - set(source)
        if missing_sources:
            findings.append(f"source_of_truth missing keys: {sorted(missing_sources)}")
        for key, raw_path in source.items():
            if not isinstance(raw_path, str) or not raw_path:
                findings.append(f"source_of_truth.{key} must be a path")
                continue
            if not (REPO_ROOT / raw_path).exists():
                findings.append(f"source_of_truth.{key} path missing: {raw_path}")

    boundaries = packet.get("boundaries")
    if not isinstance(boundaries, dict):
        findings.append("boundaries must be an object")
    else:
        for key in REQUIRED_BOUNDARIES:
            if boundaries.get(key) is not True:
                findings.append(f"boundaries.{key} must be true")

    claim_policy = packet.get("claim_policy")
    allowed_claims: set[str] = set()
    needs_review_claims: set[str] = set()
    do_not_use_claims: set[str] = set()
    if not isinstance(claim_policy, dict):
        findings.append("claim_policy must be an object")
    else:
        missing_groups = REQUIRED_CLAIM_GROUPS - set(claim_policy)
        if missing_groups:
            findings.append(f"claim_policy missing groups: {sorted(missing_groups)}")
        for item in claim_policy.get("allowed_draft", []):
            if not isinstance(item, dict) or item.get("status") != "allowed_draft":
                findings.append("claim_policy.allowed_draft claims must have status allowed_draft")
                continue
            claim = str(item.get("claim", "")).strip()
            if claim:
                allowed_claims.add(claim)
        for item in claim_policy.get("needs_review", []):
            if not isinstance(item, dict) or item.get("status") not in {"compliance_review", "owner_review"}:
                findings.append("claim_policy.needs_review claims must have compliance_review or owner_review status")
                continue
            claim = str(item.get("claim", "")).strip()
            if claim:
                needs_review_claims.add(claim)
        do_not_use_claims = {item for item in _string_list(claim_policy.get("do_not_use")) if item.strip()}
        if not allowed_claims:
            findings.append("claim_policy.allowed_draft must be non-empty")
        if not needs_review_claims:
            findings.append("claim_policy.needs_review must be non-empty")
        if not do_not_use_claims:
            findings.append("claim_policy.do_not_use must be non-empty")

    campaign_ids: set[str] = set()
    campaigns = packet.get("campaign_backlog")
    if not isinstance(campaigns, list) or not campaigns:
        findings.append("campaign_backlog must be a non-empty list")
    else:
        for index, campaign in enumerate(campaigns):
            if not isinstance(campaign, dict):
                findings.append(f"campaign_backlog[{index}] must be an object")
                continue
            campaign_id = str(campaign.get("id", ""))
            campaign_ids.add(campaign_id)
            findings.extend(_validate_campaign(campaign, index, allowed_claims, needs_review_claims, do_not_use_claims))
    missing_campaigns = REQUIRED_CAMPAIGN_IDS - campaign_ids
    if missing_campaigns:
        findings.append(f"campaign_backlog missing ids: {sorted(missing_campaigns)}")

    calendar = packet.get("content_calendar")
    if not isinstance(calendar, list) or not calendar:
        findings.append("content_calendar must be a non-empty list")
    else:
        weeks = set()
        for index, item in enumerate(calendar):
            if not isinstance(item, dict):
                findings.append(f"content_calendar[{index}] must be an object")
                continue
            weeks.add(item.get("week_index"))
            findings.extend(_validate_calendar_item(item, index, campaign_ids))
        if len(weeks) < 4:
            findings.append("content_calendar must cover at least 4 distinct week_index values")

    review_queues = packet.get("review_queues")
    if not isinstance(review_queues, dict):
        findings.append("review_queues must be an object")
    else:
        missing_queues = REQUIRED_REVIEW_QUEUES - set(review_queues)
        if missing_queues:
            findings.append(f"review_queues missing: {sorted(missing_queues)}")
        for key in REQUIRED_REVIEW_QUEUES:
            if not _string_list(review_queues.get(key)):
                findings.append(f"review_queues.{key} must be non-empty")

    separation = packet.get("claim_separation")
    if not isinstance(separation, dict):
        findings.append("claim_separation must be an object")
    else:
        for key in (
            "campaign_copy_uses_allowed_draft_claims_only",
            "review_required_claims_are_not_copy_seed",
            "do_not_use_claims_are_not_copy_seed",
        ):
            if separation.get(key) is not True:
                findings.append(f"claim_separation.{key} must be true")
        if not str(separation.get("quarantine_owner", "")).strip():
            findings.append("claim_separation.quarantine_owner is required")

    forbidden_actions = set(_string_list(packet.get("forbidden_actions")))
    missing_forbidden = REQUIRED_FORBIDDEN_ACTIONS - forbidden_actions
    if missing_forbidden:
        findings.append(f"forbidden_actions missing: {sorted(missing_forbidden)}")

    handoff = packet.get("taskset_handoff")
    if not isinstance(handoff, dict):
        findings.append("taskset_handoff must be an object")
    else:
        if handoff.get("task_167_complete") is not True:
            findings.append("taskset_handoff.task_167_complete must be true")
        if handoff.get("taskset_remains_active") is not True:
            findings.append("taskset_handoff.taskset_remains_active must be true")
        next_tasks = set(_string_list(handoff.get("next_task_candidates")))
        for task_id in ("TASK-168", "TASK-169", "TASK-170"):
            if task_id not in next_tasks:
                findings.append(f"taskset_handoff.next_task_candidates missing {task_id}")
        for blocked_key in (
            "sales_revenue_lane_active",
            "live_publication_approved",
            "final_asset_export_approved",
        ):
            if handoff.get(blocked_key) is not False:
                findings.append(f"taskset_handoff.{blocked_key} must be false")

    verification = packet.get("verification")
    if not isinstance(verification, dict):
        findings.append("verification must be an object")
    elif "promotion_campaign_backlog_calendar_gate.py --check" not in str(verification.get("local_gate", "")):
        findings.append("verification.local_gate must reference this gate")

    return findings


def _validate_campaign(
    campaign: dict[str, Any],
    index: int,
    allowed_claims: set[str],
    needs_review_claims: set[str],
    do_not_use_claims: set[str],
) -> list[str]:
    findings: list[str] = []
    prefix = f"campaign_backlog[{index}]"

    if not str(campaign.get("id", "")).strip():
        findings.append(f"{prefix}.id is required")
    if campaign.get("publication_status") != "draft_only":
        findings.append(f"{prefix}.publication_status must be draft_only")
    if campaign.get("customer_contact_status") != "no_contact":
        findings.append(f"{prefix}.customer_contact_status must be no_contact")
    if campaign.get("claim_status") != "allowed_draft":
        findings.append(f"{prefix}.claim_status must remain allowed_draft")
    if "approved" in str(campaign.get("review_status", "")).lower():
        findings.append(f"{prefix}.review_status must not be approved")

    source_artifacts = _string_list(campaign.get("source_artifacts"))
    if not source_artifacts:
        findings.append(f"{prefix}.source_artifacts must be non-empty")
    for raw_path in source_artifacts:
        if not (REPO_ROOT / raw_path).exists():
            findings.append(f"{prefix}.source_artifacts path missing: {raw_path}")

    source_claims = _string_list(campaign.get("source_claims"))
    if not source_claims:
        findings.append(f"{prefix}.source_claims must be non-empty")
    for claim in source_claims:
        if claim not in allowed_claims:
            findings.append(f"{prefix}.source_claims must use allowed_draft claims only: {claim}")

    copy_seed = str(campaign.get("copy_seed", ""))
    if not copy_seed.strip():
        findings.append(f"{prefix}.copy_seed is required")
    findings.extend(_copy_claim_findings(copy_seed, needs_review_claims, do_not_use_claims, f"{prefix}.copy_seed"))

    approvals = _string_list(campaign.get("required_approval"))
    if not approvals:
        findings.append(f"{prefix}.required_approval must be non-empty")
    elif not any("Owner/R3" in item for item in approvals):
        findings.append(f"{prefix}.required_approval must include Owner/R3 for live or external action")

    blocked = set(_string_list(campaign.get("blocked_actions")))
    if not blocked:
        findings.append(f"{prefix}.blocked_actions must be non-empty")

    return findings


def _validate_calendar_item(item: dict[str, Any], index: int, campaign_ids: set[str]) -> list[str]:
    findings: list[str] = []
    prefix = f"content_calendar[{index}]"

    if not str(item.get("id", "")).strip():
        findings.append(f"{prefix}.id is required")
    if item.get("campaign_item_id") not in campaign_ids:
        findings.append(f"{prefix}.campaign_item_id must reference campaign_backlog")
    if item.get("status") not in {"draft_only", "review_gate"}:
        findings.append(f"{prefix}.status must be draft_only or review_gate")
    if item.get("claim_status") != "allowed_draft":
        findings.append(f"{prefix}.claim_status must be allowed_draft")
    source_artifact = item.get("source_artifact")
    if not isinstance(source_artifact, str) or not source_artifact:
        findings.append(f"{prefix}.source_artifact is required")
    elif not (REPO_ROOT / source_artifact).exists():
        findings.append(f"{prefix}.source_artifact path missing: {source_artifact}")
    if not _string_list(item.get("required_review")):
        findings.append(f"{prefix}.required_review must be non-empty")
    if not str(item.get("approval_gate", "")).strip():
        findings.append(f"{prefix}.approval_gate is required")
    if item.get("live_action_enabled") is not False:
        findings.append(f"{prefix}.live_action_enabled must be false")
    if item.get("publish_ready") is not False:
        findings.append(f"{prefix}.publish_ready must be false")

    return findings


def _copy_claim_findings(
    text: str,
    needs_review_claims: set[str],
    do_not_use_claims: set[str],
    path: str,
) -> list[str]:
    findings: list[str] = []
    lowered = text.lower()
    for claim in sorted(needs_review_claims | do_not_use_claims):
        if claim.lower() in lowered:
            findings.append(f"{path} contains review-required or forbidden claim: {claim}")
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


def _find_live_true_keys(value: Any, prefix: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}"
            if key in LIVE_TRUE_KEYS and child is True:
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
        print("promotion-campaign-backlog-calendar-gate: fail")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("promotion-campaign-backlog-calendar-gate: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
