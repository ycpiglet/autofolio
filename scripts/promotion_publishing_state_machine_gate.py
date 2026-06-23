"""Validate the TASK-130 promotion publishing state-machine contract.

This gate verifies a local approval queue contract only. It must not create any
live publishing path, OAuth flow, platform API call, secret storage, paid ad,
customer contact, browser automation, or scraping behavior.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = REPO_ROOT / "agents" / "project" / "PROMOTION-PUBLISHING-STATE-MACHINE.json"

REQUIRED_BOUNDARIES = {
    "contract_only",
    "not_live_publish_implementation",
    "no_external_account_action",
    "no_oauth_flow",
    "no_platform_api_call",
    "no_secret_or_token_storage",
    "no_customer_contact",
    "no_paid_ads",
    "no_browser_automation",
    "no_scraping_or_lead_harvesting",
    "no_auto_publish_transition",
    "owner_approval_required_before_any_live_record",
    "compliance_review_required_for_public_financial_claims",
    "live_action_disabled_by_default",
}

REQUIRED_STATES = {
    "draft_created",
    "copy_review",
    "compliance_review_required",
    "owner_review_required",
    "approved_for_manual_export",
    "dry_run_scheduled",
    "live_recorded_after_owner_action",
    "blocked",
    "withdrawn_or_archived",
}

REQUIRED_FORBIDDEN_TRANSITIONS = {
    "auto_publish",
    "skip_owner_approval",
    "skip_compliance_review",
    "schedule_live_without_owner_approval",
    "external_api_upload",
    "oauth_authorization",
    "token_storage",
    "customer_contact",
    "paid_ad_purchase",
    "browser_automation_publish",
    "lead_scraping",
    "bulk_dm",
    "viewbot_or_fake_engagement",
    "investment_advice_publication",
    "performance_guarantee_publication",
    "kis_commercial_clearance_publication",
}

REQUIRED_QUEUE_FIELDS = {
    "campaign_id",
    "state",
    "channel",
    "copy_surface",
    "source_artifact",
    "source_hash",
    "draft_text",
    "claim_review_status",
    "compliance_reviewer",
    "owner_approval_required",
    "owner_approval_record",
    "dry_run_preview",
    "scheduled_at",
    "live_action_blocked_by_default",
    "external_post_id_after_live_only",
    "external_url_after_live_only",
    "posted_at_after_live_only",
    "rollback_or_delete_instruction",
    "blocked_reason",
    "audit_events",
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
    "kis_app_secret",
}

FORBIDDEN_ACTION_TEXT = {
    "post_to_platform",
    "publish_now",
    "oauth_authorize",
    "call_external_api",
    "send_customer_email",
    "buy_ad",
    "scrape_leads",
}


def load_contract(path: Path = DEFAULT_CONTRACT) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("promotion publishing state-machine root must be an object")
    return data


def validate_contract(contract: dict[str, Any]) -> list[str]:
    findings: list[str] = []

    if contract.get("$schema") != "autofolio.promotion-publishing-state-machine/v1":
        findings.append("unexpected or missing promotion publishing state-machine schema")

    status = str(contract.get("status", "")).lower()
    if "local_contract" not in status or "not_live_publish" not in status:
        findings.append("status must clearly remain local_contract and not_live_publish")

    forbidden_keys = _find_forbidden_keys(contract)
    if forbidden_keys:
        findings.append(f"forbidden secret/customer key names present: {forbidden_keys}")

    forbidden_text = _find_forbidden_action_text(contract)
    if forbidden_text:
        findings.append(f"forbidden action-like text present: {forbidden_text}")

    boundaries = contract.get("boundaries")
    if not isinstance(boundaries, dict):
        findings.append("boundaries must be an object")
    else:
        for key in REQUIRED_BOUNDARIES:
            if boundaries.get(key) is not True:
                findings.append(f"boundaries.{key} must be true")

    states = contract.get("states")
    state_ids: set[str] = set()
    if not isinstance(states, list):
        findings.append("states must be a list")
    else:
        for index, state in enumerate(states):
            if not isinstance(state, dict):
                findings.append(f"states[{index}] must be an object")
                continue
            state_id = str(state.get("id", ""))
            state_ids.add(state_id)
            if state.get("live_action") is not False:
                findings.append(f"states[{index}].live_action must be false")
            if not isinstance(state.get("required_fields"), list) or not state.get("required_fields"):
                findings.append(f"states[{index}].required_fields must be non-empty")
            if state_id == "live_recorded_after_owner_action":
                if state.get("action_type") != "record_only_after_external_owner_action":
                    findings.append("live_recorded_after_owner_action must be record-only")
                if state.get("terminal") is not True:
                    findings.append("live_recorded_after_owner_action must be terminal")

    missing_states = REQUIRED_STATES - state_ids
    if missing_states:
        findings.append(f"missing required states: {sorted(missing_states)}")

    transitions = contract.get("transitions")
    if not isinstance(transitions, list) or not transitions:
        findings.append("transitions must be a non-empty list")
    else:
        for index, transition in enumerate(transitions):
            if not isinstance(transition, dict):
                findings.append(f"transitions[{index}] must be an object")
                continue
            if transition.get("live_action") is not False:
                findings.append(f"transitions[{index}].live_action must be false")
            if transition.get("from") not in state_ids:
                findings.append(f"transitions[{index}].from references unknown state")
            if transition.get("to") not in state_ids:
                findings.append(f"transitions[{index}].to references unknown state")
            if not isinstance(transition.get("guards"), list) or not transition.get("guards"):
                findings.append(f"transitions[{index}].guards must be non-empty")

    forbidden_transitions = set(_string_list(contract.get("forbidden_transitions")))
    missing_forbidden = REQUIRED_FORBIDDEN_TRANSITIONS - forbidden_transitions
    if missing_forbidden:
        findings.append(f"forbidden_transitions missing entries: {sorted(missing_forbidden)}")

    queue = contract.get("queue_record_contract")
    if not isinstance(queue, dict):
        findings.append("queue_record_contract must be an object")
    else:
        missing_queue = REQUIRED_QUEUE_FIELDS - set(_string_list(queue.get("required_fields")))
        if missing_queue:
            findings.append(f"queue_record_contract.required_fields missing: {sorted(missing_queue)}")
        forbidden_fields = set(_string_list(queue.get("forbidden_fields")))
        required_forbidden_fields = FORBIDDEN_KEY_NAMES & {
            "access_token",
            "refresh_token",
            "client_secret",
            "password",
            "cookie",
            "customer_email",
            "customer_phone",
            "bank_account_number",
            "kis_app_secret",
        }
        missing_forbidden_fields = required_forbidden_fields - forbidden_fields
        if missing_forbidden_fields:
            findings.append(f"queue_record_contract.forbidden_fields missing: {sorted(missing_forbidden_fields)}")

    invariants = " ".join(_string_list(contract.get("invariants"))).lower()
    for marker in ("live_action false", "record-only", "owner approval", "compliance officer", "naver blog"):
        if marker not in invariants:
            findings.append(f"invariants missing marker: {marker}")

    verification = contract.get("verification")
    if not isinstance(verification, dict):
        findings.append("verification must be an object")
    elif "promotion_publishing_state_machine_gate.py --check" not in str(verification.get("local_gate", "")):
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


def _find_forbidden_action_text(value: Any, prefix: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            findings.extend(_find_forbidden_action_text(child, f"{prefix}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(_find_forbidden_action_text(child, f"{prefix}[{index}]"))
    elif isinstance(value, str) and value in FORBIDDEN_ACTION_TEXT:
        findings.append(f"{prefix}={value}")
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
        print("promotion publishing state-machine gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print(f"promotion publishing state-machine gate: PASS ({args.contract})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
