"""Validate the TASK-129 promotion publishing policy packet.

This gate keeps TASK-096 at policy/dry-run design level. It must reject any
packet that enables live posting, OAuth/token handling, external account action,
customer contact, paid ads, spam, engagement manipulation, or public financial
claims without the required Owner and Compliance boundaries.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKET = REPO_ROOT / "agents" / "project" / "PROMOTION-PUBLISHING-POLICY-PACKET.json"

REQUIRED_BOUNDARIES = {
    "policy_foundation_only",
    "not_publication_approval",
    "no_live_posting",
    "no_external_account_action",
    "no_external_api_upload",
    "no_oauth_flow",
    "no_secret_or_token_storage",
    "no_customer_contact",
    "no_paid_ads",
    "no_bulk_messaging",
    "no_scraping",
    "no_engagement_manipulation",
    "owner_approval_required_for_live_post",
    "compliance_review_required_for_financial_claims",
    "keeps_task_096_live_posting_blocked",
}

REQUIRED_SOURCE_IDS = {
    "telegram_bot_api",
    "telegram_bots_faq",
    "x_api_intro",
    "x_create_post",
    "x_auth_scopes",
    "linkedin_share",
    "google_business_profile_local_posts",
    "kakao_message_rest",
    "naver_share",
    "naver_cafe_write",
}

REQUIRED_CHANNEL_IDS = {
    "owner_blog_manual",
    "telegram_bot",
    "x_api",
    "linkedin_share",
    "naver_share",
    "naver_cafe_write",
    "kakao_message",
    "google_business_profile",
}

REQUIRED_WORKFLOW_STATES = {
    "draft_source",
    "preview_rendered",
    "claim_review_required",
    "owner_approval_required",
    "dry_run_audit_preview",
    "live_post_blocked",
    "rollback_instruction_recorded",
}

REQUIRED_FORBIDDEN_ACTIONS = {
    "live posting without Owner approval",
    "public posting",
    "paid ads",
    "customer email or direct message",
    "external account login",
    "external API upload",
    "OAuth callback validation",
    "token or credential storage",
    "bulk messaging",
    "spam",
    "viewbot or fake engagement",
    "platform manipulation",
    "terms-of-service evasion",
    "unsourced lead scraping",
    "investment advice claim",
    "paid signal claim",
    "model portfolio claim",
    "performance guarantee",
    "KIS commercial clearance claim",
}

FORBIDDEN_KEY_NAMES = {
    "access_token",
    "refresh_token",
    "bot_token",
    "telegram_token",
    "client_secret",
    "api_secret",
    "app_secret",
    "consumer_secret",
    "password",
    "customer_email",
    "customer_phone",
    "ad_account_id",
    "external_post_id",
    "live_campaign_id",
}

LIVE_TRUE_KEYS = {
    "can_publish",
    "live_post_enabled",
    "external_action_enabled",
    "external_network_calls",
    "oauth_flow_enabled",
    "stores_tokens",
    "publication_approved",
}

BAD_STATUS_FRAGMENTS = {
    "publication_approved",
    "live_enabled",
    "ready_for_live_posting",
    "ready_to_publish",
}


def load_packet(path: Path = DEFAULT_PACKET) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("promotion publishing policy packet root must be an object")
    return data


def validate_packet(packet: dict[str, Any]) -> list[str]:
    findings: list[str] = []

    if packet.get("$schema") != "autofolio.promotion-publishing-policy-packet/v1":
        findings.append("unexpected or missing promotion publishing policy schema")

    status = str(packet.get("status", "")).lower()
    if "policy" not in status or "not_live" not in status:
        findings.append("status must clearly remain policy foundation and not live")
    if any(fragment in status for fragment in BAD_STATUS_FRAGMENTS):
        findings.append("status must not imply publication approval or live readiness")

    boundaries = packet.get("boundaries")
    if not isinstance(boundaries, dict):
        findings.append("boundaries must be an object")
    else:
        for key in REQUIRED_BOUNDARIES:
            if boundaries.get(key) is not True:
                findings.append(f"boundaries.{key} must be true")

    forbidden_keys = _find_forbidden_keys(packet)
    if forbidden_keys:
        findings.append(f"forbidden secret/customer/live key names present: {forbidden_keys}")

    live_true_paths = _find_live_true_keys(packet)
    allowed_live_false_keys = {"$.dry_run_contract.external_network_calls"}
    live_true_paths = [path for path in live_true_paths if path not in allowed_live_false_keys]
    if live_true_paths:
        findings.append(f"live/external action flags must not be true: {live_true_paths}")

    sources = packet.get("official_sources")
    if not isinstance(sources, list):
        findings.append("official_sources must be a list")
    else:
        source_ids = {item.get("id") for item in sources if isinstance(item, dict)}
        missing = REQUIRED_SOURCE_IDS - source_ids
        if missing:
            findings.append(f"official_sources missing ids: {sorted(missing)}")
        for item in sources:
            if not isinstance(item, dict):
                findings.append("official_sources entries must be objects")
                continue
            if item.get("official") is not True:
                findings.append(f"official source {item.get('id')} must be marked official")
            if not str(item.get("url", "")).startswith("https://"):
                findings.append(f"official source {item.get('id')} must use https URL")

    states = packet.get("workflow_state_model")
    if not isinstance(states, list):
        findings.append("workflow_state_model must be a list")
    else:
        state_ids = {item.get("state") for item in states if isinstance(item, dict)}
        missing_states = REQUIRED_WORKFLOW_STATES - state_ids
        if missing_states:
            findings.append(f"workflow_state_model missing states: {sorted(missing_states)}")
        for item in states:
            if isinstance(item, dict) and item.get("external_action_enabled") is not False:
                findings.append(f"workflow state {item.get('state')} must keep external_action_enabled false")

    dry_run = packet.get("dry_run_contract")
    if not isinstance(dry_run, dict):
        findings.append("dry_run_contract must be an object")
    else:
        if dry_run.get("external_network_calls") is not False:
            findings.append("dry_run_contract.external_network_calls must be false")
        if dry_run.get("writes_only_preview_record") is not True:
            findings.append("dry_run_contract.writes_only_preview_record must be true")
        for required in ("campaign_id", "channel_id", "source_hash", "blocked_reason"):
            if required not in dry_run.get("output_fields", []):
                findings.append(f"dry_run_contract.output_fields missing {required}")

    channels = packet.get("channel_policies")
    if not isinstance(channels, list):
        findings.append("channel_policies must be a list")
    else:
        channel_ids = {item.get("channel_id") for item in channels if isinstance(item, dict)}
        missing_channels = REQUIRED_CHANNEL_IDS - channel_ids
        if missing_channels:
            findings.append(f"channel_policies missing channels: {sorted(missing_channels)}")
        for item in channels:
            if not isinstance(item, dict):
                findings.append("channel_policies entries must be objects")
                continue
            channel_id = item.get("channel_id")
            if item.get("external_action_enabled") is not False:
                findings.append(f"channel {channel_id} must keep external_action_enabled false")
            if item.get("owner_approval_required") is not True:
                findings.append(f"channel {channel_id} must require Owner approval")
            if item.get("compliance_review_required") is not True:
                findings.append(f"channel {channel_id} must require Compliance review")
            if "live" in str(item.get("current_mode", "")).lower():
                findings.append(f"channel {channel_id} current_mode must not imply live mode")
            if not item.get("rollback_instruction"):
                findings.append(f"channel {channel_id} must include rollback_instruction")

    forbidden_actions = set(_string_list(packet.get("forbidden_actions")))
    missing_actions = REQUIRED_FORBIDDEN_ACTIONS - forbidden_actions
    if missing_actions:
        findings.append(f"forbidden_actions missing: {sorted(missing_actions)}")

    handoff = packet.get("task_096_handoff")
    if not isinstance(handoff, dict):
        findings.append("task_096_handoff must be an object")
    else:
        if handoff.get("r2_foundation_done") is not True:
            findings.append("task_096_handoff.r2_foundation_done must be true")
        if handoff.get("live_pipeline_still_blocked") is not True:
            findings.append("task_096_handoff.live_pipeline_still_blocked must be true")
        r3_items = set(_string_list(handoff.get("owner_r3_required_for")))
        for required in ("posting, scheduling, editing, or deleting live content", "storing tokens or channel ids"):
            if required not in r3_items:
                findings.append(f"task_096_handoff.owner_r3_required_for missing {required}")

    verification = packet.get("verification")
    if not isinstance(verification, dict):
        findings.append("verification must be an object")
    elif "promotion_publishing_policy_gate.py --check" not in str(verification.get("local_gate", "")):
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
        print("promotion publishing policy gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"promotion publishing policy gate: PASS ({args.packet})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
