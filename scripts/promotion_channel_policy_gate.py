"""Validate the TASK-129 promotion channel policy matrix.

This gate is local-only. It proves that the channel matrix remains a research
packet and does not authorize live publishing, OAuth, external account actions,
secret storage, customer contact, paid ads, or prohibited automation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKET = REPO_ROOT / "agents" / "project" / "PROMOTION-CHANNEL-POLICY-MATRIX.json"

REQUIRED_BOUNDARIES = {
    "research_only",
    "not_publish_ready",
    "no_live_publication",
    "no_external_account_action",
    "no_oauth_flow",
    "no_platform_api_call",
    "no_secret_or_token_storage",
    "no_paid_ads",
    "no_customer_contact",
    "no_scraping_or_lead_harvesting",
    "no_bulk_dm_or_spam",
    "no_viewbots_or_fake_engagement",
    "no_terms_evasion",
    "no_investment_or_performance_claim_publication",
    "owner_approval_required_before_live_action",
}

REQUIRED_CHANNELS = {"owner_blog", "x", "linkedin", "instagram", "naver_blog"}
REQUIRED_NEXT_SLICES = {
    "promotion_publish_state_machine_contract",
    "promotion_dry_run_audit_preview",
    "channel_asset_rendering_requirements",
}
REQUIRED_QUEUE_FIELDS = {
    "campaign_id",
    "channel",
    "copy_surface",
    "source_artifact",
    "source_hash",
    "claim_review_status",
    "compliance_reviewer",
    "owner_approval_required",
    "owner_approval_record",
    "dry_run_preview",
    "scheduled_at",
    "live_action_blocked_by_default",
    "external_post_id_after_live_only",
    "external_url_after_live_only",
    "rollback_or_delete_instruction",
}

REQUIRED_FORBIDDEN_ACTIONS = {
    "public posting",
    "paid campaign",
    "customer email or direct message",
    "external account login",
    "OAuth authorization flow",
    "external API upload",
    "SNS auto-posting",
    "browser automation against social platforms",
    "lead scraping",
    "viewbot or fake engagement",
    "platform manipulation",
    "rate-limit evasion",
    "unauthorized bulk posting",
    "spam",
    "secret or token storage",
    "investment advice claim",
    "performance guarantee",
    "KIS commercial readiness claim",
}

FORBIDDEN_KEY_NAMES = {
    "access_token",
    "refresh_token",
    "client_secret",
    "oauth_client_secret",
    "api_key",
    "api_secret",
    "password",
    "cookie",
    "session",
    "customer_email",
    "customer_phone",
    "kis_app_key",
    "kis_app_secret",
}

FORBIDDEN_READY_VALUES = {
    "approved",
    "publish_ready",
    "ready_to_publish",
    "can_publish_now",
    "auto_publish_enabled",
    "live_enabled",
}


def load_packet(path: Path = DEFAULT_PACKET) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("promotion channel policy matrix root must be an object")
    return data


def validate_packet(packet: dict[str, Any]) -> list[str]:
    findings: list[str] = []

    if packet.get("$schema") != "autofolio.promotion-channel-policy-matrix/v1":
        findings.append("unexpected or missing promotion channel policy schema")

    status = str(packet.get("status", "")).lower()
    if "research" not in status or "not_publish_ready" not in status:
        findings.append("status must clearly remain research and not_publish_ready")

    forbidden_key_paths = _find_forbidden_keys(packet)
    if forbidden_key_paths:
        findings.append(f"forbidden secret/customer key names present: {forbidden_key_paths}")

    findings.extend(_find_ready_values(packet))

    boundaries = packet.get("boundaries")
    if not isinstance(boundaries, dict):
        findings.append("boundaries must be an object")
    else:
        for key in REQUIRED_BOUNDARIES:
            if boundaries.get(key) is not True:
                findings.append(f"boundaries.{key} must be true")

    selection = packet.get("channel_selection")
    if not isinstance(selection, dict):
        findings.append("channel_selection must be an object")
    else:
        if selection.get("live_api_mode") != "blocked_until_owner_r3_approval_and_channel_credentials_policy_review":
            findings.append("channel_selection.live_api_mode must remain blocked until Owner/R3 approval")
        unsupported = set(_string_list(selection.get("unsupported_live_auto_posting")))
        if "naver_blog" not in unsupported:
            findings.append("channel_selection.unsupported_live_auto_posting must include naver_blog")
        if selection.get("defer_paid_ads") is not True:
            findings.append("channel_selection.defer_paid_ads must be true")

    channel_ids: set[str] = set()
    channels = packet.get("channels")
    if not isinstance(channels, list):
        findings.append("channels must be a list")
    else:
        for index, channel in enumerate(channels):
            if not isinstance(channel, dict):
                findings.append(f"channels[{index}] must be an object")
                continue
            channel_id = str(channel.get("id", ""))
            channel_ids.add(channel_id)
            findings.extend(_validate_channel(channel, index))

    missing_channels = REQUIRED_CHANNELS - channel_ids
    if missing_channels:
        findings.append(f"missing required channels: {sorted(missing_channels)}")

    naver = next((item for item in channels or [] if isinstance(item, dict) and item.get("id") == "naver_blog"), None)
    if isinstance(naver, dict) and naver.get("api_posting_possible") != "unsupported_for_auto_posting":
        findings.append("naver_blog.api_posting_possible must be unsupported_for_auto_posting")

    queue_fields = set(_string_list(packet.get("approval_queue_requirements")))
    missing_queue = REQUIRED_QUEUE_FIELDS - queue_fields
    if missing_queue:
        findings.append(f"approval_queue_requirements missing fields: {sorted(missing_queue)}")

    forbidden_actions = set(_string_list(packet.get("forbidden_actions")))
    missing_forbidden = REQUIRED_FORBIDDEN_ACTIONS - forbidden_actions
    if missing_forbidden:
        findings.append(f"forbidden_actions missing entries: {sorted(missing_forbidden)}")

    next_slices = {
        item.get("candidate")
        for item in packet.get("next_local_slices", [])
        if isinstance(item, dict)
    }
    missing_slices = REQUIRED_NEXT_SLICES - next_slices
    if missing_slices:
        findings.append(f"next_local_slices missing candidates: {sorted(missing_slices)}")
    for item in packet.get("next_local_slices", []):
        if isinstance(item, dict) and item.get("safe_without_owner") is not True:
            findings.append(f"next_local_slices.{item.get('candidate')} must be safe_without_owner")

    verification = packet.get("verification")
    if not isinstance(verification, dict):
        findings.append("verification must be an object")
    else:
        if "promotion_channel_policy_gate.py --check" not in str(verification.get("local_gate", "")):
            findings.append("verification.local_gate must reference this gate")

    return findings


def _validate_channel(channel: dict[str, Any], index: int) -> list[str]:
    findings: list[str] = []
    prefix = f"channels[{index}]"

    channel_id = str(channel.get("id", ""))
    if not channel_id:
        findings.append(f"{prefix}.id is required")

    if channel.get("live_action") is not False:
        findings.append(f"{prefix}.live_action must be false")
    if channel.get("owner_r3_required_for_live") is not True:
        findings.append(f"{prefix}.owner_r3_required_for_live must be true")

    publication_status = str(channel.get("publication_status", "")).lower()
    if not publication_status or publication_status in FORBIDDEN_READY_VALUES:
        findings.append(f"{prefix}.publication_status must not be approved")

    official_refs = channel.get("official_refs")
    if not isinstance(official_refs, list) or not official_refs:
        findings.append(f"{prefix}.official_refs must be a non-empty list")
    else:
        for ref_index, ref in enumerate(official_refs):
            if not isinstance(ref, dict):
                findings.append(f"{prefix}.official_refs[{ref_index}] must be an object")
                continue
            if not str(ref.get("authority", "")).strip():
                findings.append(f"{prefix}.official_refs[{ref_index}].authority is required")
            url = str(ref.get("url", ""))
            if not (url.startswith("https://") or url.startswith("agents/")):
                findings.append(f"{prefix}.official_refs[{ref_index}].url must be https or repo-local")

    capabilities = channel.get("capabilities")
    if not isinstance(capabilities, dict):
        findings.append(f"{prefix}.capabilities must be an object")
    else:
        for key in ("create", "update", "delete_or_rollback"):
            if not str(capabilities.get(key, "")).strip():
                findings.append(f"{prefix}.capabilities.{key} is required")

    for key in ("auth_or_access", "policy_risks", "required_before_live", "recommendation"):
        value = channel.get(key)
        if isinstance(value, list):
            if not value:
                findings.append(f"{prefix}.{key} must be non-empty")
        elif not str(value or "").strip():
            findings.append(f"{prefix}.{key} is required")

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


def _find_ready_values(value: Any, prefix: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            findings.extend(_find_ready_values(child, f"{prefix}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(_find_ready_values(child, f"{prefix}[{index}]"))
    elif isinstance(value, str) and value.lower() in FORBIDDEN_READY_VALUES:
        findings.append(f"{prefix} must not be {value!r}")
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
        print("promotion channel policy gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print(f"promotion channel policy gate: PASS ({args.packet})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
