"""Validate the TASK-131 promotion dry-run audit preview.

This gate validates a local preview artifact only. It recalculates source file
hashes and rejects any live publication, OAuth/token, external account action,
customer contact, paid ad, scraping, engagement manipulation, or public-claim
shortcut.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PREVIEW = REPO_ROOT / "agents" / "project" / "PROMOTION-DRY-RUN-AUDIT-PREVIEW.json"
POLICY_PACKET = REPO_ROOT / "agents" / "project" / "PROMOTION-PUBLISHING-POLICY-PACKET.json"
STATE_MACHINE = REPO_ROOT / "agents" / "project" / "PROMOTION-PUBLISHING-STATE-MACHINE.json"

REQUIRED_SOURCE_IDS = {
    "marketing_materials_v1",
    "channel_policy_matrix",
    "publishing_policy_packet",
    "state_machine_contract",
}

REQUIRED_BOUNDARIES = {
    "local_preview_only",
    "not_publication_approval",
    "no_live_posting",
    "no_external_network_calls",
    "no_external_api_upload",
    "no_external_account_action",
    "no_oauth_flow",
    "no_secret_or_token_storage",
    "no_customer_contact",
    "no_paid_ads",
    "no_browser_automation",
    "no_scraping",
    "no_engagement_manipulation",
    "live_action_blocked_by_default",
    "owner_approval_required_for_live_use",
    "compliance_review_required_before_public_use",
}

REQUIRED_FORBIDDEN_ACTIONS = {
    "public posting",
    "scheduled live post",
    "external account login",
    "OAuth authorization flow",
    "external API upload",
    "token or credential storage",
    "customer email or direct message",
    "paid ads",
    "browser automation",
    "lead scraping",
    "bulk messaging",
    "viewbot or fake engagement",
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
    "client_secret",
    "api_secret",
    "app_secret",
    "password",
    "cookie",
    "session",
    "customer_email",
    "customer_phone",
    "bank_account_number",
    "ad_account_id",
    "external_post_id",
    "external_url",
    "kis_app_secret",
}

LIVE_TRUE_KEYS = {
    "live_post_enabled",
    "external_network_calls",
    "external_action_enabled",
    "external_api_upload_enabled",
    "oauth_flow_enabled",
    "stores_tokens",
    "customer_contact_enabled",
    "paid_ads_enabled",
    "browser_automation_enabled",
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


def load_preview(path: Path = DEFAULT_PREVIEW) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("promotion dry-run preview root must be an object")
    return data


def validate_preview(preview: dict[str, Any], repo_root: Path = REPO_ROOT) -> list[str]:
    findings: list[str] = []

    if preview.get("$schema") != "autofolio.promotion-dry-run-audit-preview/v1":
        findings.append("unexpected or missing promotion dry-run preview schema")

    status = str(preview.get("status", "")).lower()
    if "local_preview" not in status or "not_live" not in status:
        findings.append("status must clearly remain local_preview and not live")

    boundaries = preview.get("boundaries")
    if not isinstance(boundaries, dict):
        findings.append("boundaries must be an object")
    else:
        for key in REQUIRED_BOUNDARIES:
            if boundaries.get(key) is not True:
                findings.append(f"boundaries.{key} must be true")

    forbidden_keys = _find_forbidden_keys(preview)
    if forbidden_keys:
        findings.append(f"forbidden secret/customer/live key names present: {forbidden_keys}")

    live_true_paths = _find_live_true_keys(preview)
    if live_true_paths:
        findings.append(f"live or external action flags must not be true: {live_true_paths}")

    findings.extend(_validate_sources(preview, repo_root))
    findings.extend(_validate_preview_record(preview, repo_root))
    findings.extend(_validate_review_scan(preview))

    events = preview.get("audit_events")
    event_names = {item.get("event") for item in events if isinstance(item, dict)} if isinstance(events, list) else set()
    for required in ("dry_run_generated", "live_action_blocked"):
        if required not in event_names:
            findings.append(f"audit_events missing {required}")
    if isinstance(events, list):
        for index, event in enumerate(events):
            if isinstance(event, dict) and event.get("external_action") is not False:
                findings.append(f"audit_events[{index}].external_action must be false")

    forbidden_actions = set(_string_list(preview.get("forbidden_actions")))
    missing_actions = REQUIRED_FORBIDDEN_ACTIONS - forbidden_actions
    if missing_actions:
        findings.append(f"forbidden_actions missing: {sorted(missing_actions)}")

    handoff = preview.get("task_096_handoff")
    if not isinstance(handoff, dict):
        findings.append("task_096_handoff must be an object")
    else:
        if handoff.get("dry_run_preview_done") is not True:
            findings.append("task_096_handoff.dry_run_preview_done must be true")
        if handoff.get("live_pipeline_still_blocked") is not True:
            findings.append("task_096_handoff.live_pipeline_still_blocked must be true")
        r3_items = set(_string_list(handoff.get("owner_r3_required_for")))
        for required in ("posting, scheduling, editing, or deleting live content", "storing tokens or channel ids"):
            if required not in r3_items:
                findings.append(f"task_096_handoff.owner_r3_required_for missing {required}")

    verification = preview.get("verification")
    if not isinstance(verification, dict):
        findings.append("verification must be an object")
    elif "promotion_dry_run_audit_preview_gate.py --check" not in str(verification.get("local_gate", "")):
        findings.append("verification.local_gate must reference this gate")

    return findings


def _validate_sources(preview: dict[str, Any], repo_root: Path) -> list[str]:
    findings: list[str] = []
    inputs = preview.get("source_inputs")
    if not isinstance(inputs, list):
        return ["source_inputs must be a list"]

    source_ids = {item.get("id") for item in inputs if isinstance(item, dict)}
    missing = REQUIRED_SOURCE_IDS - source_ids
    if missing:
        findings.append(f"source_inputs missing ids: {sorted(missing)}")

    for index, item in enumerate(inputs):
        if not isinstance(item, dict):
            findings.append(f"source_inputs[{index}] must be an object")
            continue
        rel_path = str(item.get("path", ""))
        try:
            path = _safe_repo_path(repo_root, rel_path)
        except ValueError as exc:
            findings.append(f"source_inputs[{index}].path invalid: {exc}")
            continue
        if not path.exists():
            findings.append(f"source_inputs[{index}].path missing: {rel_path}")
            continue
        actual = _sha256(path)
        recorded = str(item.get("sha256", "")).lower()
        if recorded != actual:
            findings.append(f"source_inputs[{index}].sha256 mismatch for {rel_path}")
    return findings


def _validate_preview_record(preview: dict[str, Any], repo_root: Path) -> list[str]:
    findings: list[str] = []
    record = preview.get("preview_record")
    if not isinstance(record, dict):
        return ["preview_record must be an object"]

    required_fields = {
        "campaign_id",
        "channel_id",
        "state",
        "source_artifact",
        "source_hash",
        "copy_surface",
        "preview_text",
        "claim_review_status",
        "compliance_review_status",
        "owner_approval_status",
        "planned_visibility",
        "scheduled_at",
        "rollback_instruction",
        "blocked_reason",
    }
    missing = {field for field in required_fields if not str(record.get(field, "")).strip()}
    if missing:
        findings.append(f"preview_record missing fields: {sorted(missing)}")

    if record.get("state") not in {"dry_run_scheduled", "blocked"}:
        findings.append("preview_record.state must be dry_run_scheduled or blocked")
    if record.get("planned_visibility") != "local_preview_only":
        findings.append("preview_record.planned_visibility must be local_preview_only")
    if record.get("scheduled_at") != "not_scheduled":
        findings.append("preview_record.scheduled_at must remain not_scheduled")
    if record.get("live_action_blocked_by_default") is not True:
        findings.append("preview_record.live_action_blocked_by_default must be true")
    if record.get("owner_approval_required_for_live") is not True:
        findings.append("preview_record.owner_approval_required_for_live must be true")
    if record.get("external_network_calls") is not False:
        findings.append("preview_record.external_network_calls must be false")
    if record.get("external_action_enabled") is not False:
        findings.append("preview_record.external_action_enabled must be false")
    if "required" not in str(record.get("owner_approval_status", "")).lower():
        findings.append("preview_record.owner_approval_status must require Owner before live use")
    if "required" not in str(record.get("compliance_review_status", "")).lower():
        findings.append("preview_record.compliance_review_status must require review before public use")

    try:
        source_path = _safe_repo_path(repo_root, str(record.get("source_artifact", "")))
    except ValueError as exc:
        findings.append(f"preview_record.source_artifact invalid: {exc}")
    else:
        if not source_path.exists():
            findings.append("preview_record.source_artifact missing")
        elif str(record.get("source_hash", "")).lower() != _sha256(source_path):
            findings.append("preview_record.source_hash does not match source_artifact")

    findings.extend(_validate_channel_and_state(record, repo_root))

    text = str(record.get("preview_text", "")).lower()
    for phrase in sorted(FORBIDDEN_COPY_PHRASES):
        if phrase in text:
            findings.append(f"preview_record.preview_text contains forbidden phrase: {phrase}")
    return findings


def _validate_channel_and_state(record: dict[str, Any], repo_root: Path) -> list[str]:
    findings: list[str] = []
    channel_id = record.get("channel_id")
    policy_path = repo_root / "agents" / "project" / "PROMOTION-PUBLISHING-POLICY-PACKET.json"
    state_path = repo_root / "agents" / "project" / "PROMOTION-PUBLISHING-STATE-MACHINE.json"

    policy = _load_json(policy_path)
    channels = policy.get("channel_policies", []) if isinstance(policy, dict) else []
    channel = next((item for item in channels if isinstance(item, dict) and item.get("channel_id") == channel_id), None)
    if not isinstance(channel, dict):
        findings.append(f"preview_record.channel_id not found in policy packet: {channel_id}")
    else:
        if channel.get("external_action_enabled") is not False:
            findings.append(f"policy channel {channel_id} must keep external_action_enabled false")
        if channel.get("owner_approval_required") is not True:
            findings.append(f"policy channel {channel_id} must require Owner approval")

    state_machine = _load_json(state_path)
    states = state_machine.get("states", []) if isinstance(state_machine, dict) else []
    state = next((item for item in states if isinstance(item, dict) and item.get("id") == record.get("state")), None)
    if not isinstance(state, dict):
        findings.append(f"preview_record.state not found in state machine: {record.get('state')}")
    elif state.get("live_action") is not False:
        findings.append(f"state {record.get('state')} must keep live_action false")
    return findings


def _validate_review_scan(preview: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    scan = preview.get("review_scan")
    if not isinstance(scan, dict):
        return ["review_scan must be an object"]
    for key in ("forbidden_automation", "forbidden_public_claims", "secret_or_customer_data"):
        item = scan.get(key)
        if not isinstance(item, dict):
            findings.append(f"review_scan.{key} must be an object")
            continue
        if item.get("status") != "pass":
            findings.append(f"review_scan.{key}.status must be pass")
        if item.get("matches") != []:
            findings.append(f"review_scan.{key}.matches must be empty")
    return findings


def _safe_repo_path(repo_root: Path, rel_path: str) -> Path:
    if not rel_path or Path(rel_path).is_absolute():
        raise ValueError("path must be a non-empty relative path")
    resolved = (repo_root / rel_path).resolve()
    if repo_root.resolve() not in resolved.parents and resolved != repo_root.resolve():
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
    parser.add_argument("--preview", type=Path, default=DEFAULT_PREVIEW)
    parser.add_argument("--check", action="store_true", help="validate and return non-zero on findings")
    args = parser.parse_args()

    preview = load_preview(args.preview)
    findings = validate_preview(preview)
    if findings:
        print("promotion dry-run audit preview gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"promotion dry-run audit preview gate: PASS ({args.preview})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
