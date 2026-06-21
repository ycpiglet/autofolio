"""Validate the TASK-169 SNS publishing automation readiness backlog.

This gate validates local readiness metadata only. It rejects OAuth flows,
token handling, platform API calls, live or scheduled posts, browser automation
against social platforms, paid ads, customer contact, scraping, fake engagement,
and any shortcut that turns a readiness backlog into publication approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BACKLOG = REPO_ROOT / "agents" / "project" / "SNS-PUBLISHING-AUTOMATION-READINESS-BACKLOG.json"

REQUIRED_SOURCE_IDS = {
    "promotion_channel_policy_matrix",
    "promotion_publishing_policy_packet",
    "promotion_publishing_state_machine",
    "promotion_dry_run_audit_preview",
    "promotion_asset_generator_readiness_map",
    "marketing_materials_v1",
    "marketing_brief",
}

REQUIRED_BOUNDARIES = {
    "local_readiness_backlog_only",
    "not_live_publishing_implementation",
    "not_publication_approval",
    "no_oauth_flow",
    "no_token_acquisition",
    "no_token_storage",
    "no_platform_api_call",
    "no_live_post",
    "no_scheduled_post",
    "no_external_account_action",
    "no_browser_automation_against_social_platform",
    "no_paid_ads",
    "no_customer_contact",
    "no_lead_scraping",
    "no_bulk_messaging_or_spam",
    "no_viewbot_or_fake_engagement",
    "no_platform_manipulation_or_terms_evasion",
    "no_public_investment_or_performance_claim",
    "no_secret_or_private_data",
    "no_sales_revenue_activation",
    "no_kis_order_risk_prod_deploy_change",
    "owner_r3_required_before_live_action",
    "compliance_review_required_before_public_claim_use",
}

REQUIRED_CHANNEL_IDS = {
    "owner_blog_manual",
    "telegram_bot",
    "x_api",
    "linkedin_share",
    "instagram",
    "naver_share",
    "naver_blog",
    "naver_cafe_write",
    "kakao_message",
    "google_business_profile",
}

ALLOWED_CLASSIFICATIONS = {"manual_only", "future_approval_queue", "defer", "rejected"}

REQUIRED_QUEUE_FIELDS = {
    "campaign_id",
    "channel_id",
    "channel_classification",
    "copy_surface",
    "source_artifact",
    "source_hash",
    "draft_text",
    "claim_review_status",
    "compliance_reviewer",
    "owner_approval_required",
    "owner_approval_record",
    "required_scopes",
    "dry_run_preview",
    "scheduled_at",
    "live_action_blocked_by_default",
    "external_post_id_after_live_only",
    "external_url_after_live_only",
    "rollback_or_delete_instruction",
    "blocked_reason",
    "audit_events",
}

REQUIRED_DRY_RUN_FIELDS = {
    "campaign_id",
    "channel_id",
    "source_hash",
    "claim_review_status",
    "owner_approval_status",
    "planned_visibility",
    "scheduled_at",
    "external_network_calls",
    "external_action_enabled",
    "live_action_blocked_by_default",
    "rollback_instruction",
    "blocked_reason",
}

REQUIRED_TEST_IDS = {
    "source_hash_required",
    "queue_record_has_no_secret_fields",
    "dry_run_has_no_network_or_external_action",
    "channel_classification_complete",
    "rollback_delete_evidence_required",
    "record_only_after_owner_external_action",
    "forbidden_automation_terms_blocked",
}

REQUIRED_BACKLOG_IDS = {
    "manual_export_packet",
    "approval_queue_storage_contract",
    "no_network_dry_run_adapter",
    "record_only_after_owner_external_action",
    "unsupported_channel_registry",
    "policy_refresh_check",
}

REQUIRED_FORBIDDEN_ACTIONS = {
    "public posting",
    "scheduled live post",
    "OAuth authorization flow",
    "token or credential storage",
    "external API upload",
    "external account login",
    "browser automation against social platforms",
    "paid ads",
    "customer email or direct message",
    "bulk messaging",
    "spam",
    "lead scraping",
    "viewbot or fake engagement",
    "platform manipulation",
    "terms-of-service evasion",
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
    "customer_record_id",
    "payment_request_id",
    "external_post_id",
    "external_url",
    "kis_app_secret",
}

LIVE_TRUE_KEYS = {
    "live_post_enabled",
    "scheduled_post_enabled",
    "external_network_calls",
    "external_action_enabled",
    "external_api_upload_enabled",
    "oauth_flow_enabled",
    "token_acquisition_enabled",
    "token_storage_enabled",
    "platform_api_call_enabled",
    "browser_automation_enabled",
    "paid_ads_enabled",
    "customer_contact_enabled",
    "lead_scraping_enabled",
    "bulk_messaging_enabled",
    "fake_engagement_enabled",
    "sales_revenue_activation_enabled",
}


def load_backlog(path: Path = DEFAULT_BACKLOG) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("SNS publishing automation readiness backlog root must be an object")
    return data


def validate_backlog(backlog: dict[str, Any], repo_root: Path = REPO_ROOT) -> list[str]:
    findings: list[str] = []

    if backlog.get("$schema") != "autofolio.sns-publishing-automation-readiness-backlog/v1":
        findings.append("unexpected or missing SNS publishing automation readiness backlog schema")

    status = str(backlog.get("status", "")).lower()
    if "local_readiness_backlog" not in status or "not_live_publication" not in status:
        findings.append("status must clearly remain local_readiness_backlog and not_live_publication")

    forbidden_keys = _find_forbidden_keys(backlog)
    if forbidden_keys:
        findings.append(f"forbidden live/customer/secret key names present: {forbidden_keys}")

    live_true_paths = _find_live_true_keys(backlog)
    if live_true_paths:
        findings.append(f"live/external/customer/platform flags must not be true: {live_true_paths}")

    boundaries = backlog.get("boundaries")
    if not isinstance(boundaries, dict):
        findings.append("boundaries must be an object")
    else:
        for key in REQUIRED_BOUNDARIES:
            if boundaries.get(key) is not True:
                findings.append(f"boundaries.{key} must be true")

    findings.extend(_validate_sources(backlog, repo_root))
    findings.extend(_validate_queue_contract(backlog))
    findings.extend(_validate_dry_run_contract(backlog))
    findings.extend(_validate_channel_readiness(backlog))
    findings.extend(_validate_no_network_tests(backlog))
    findings.extend(_validate_implementation_backlog(backlog))
    findings.extend(_validate_handoff(backlog))

    forbidden_actions = set(_string_list(backlog.get("forbidden_actions")))
    missing_actions = REQUIRED_FORBIDDEN_ACTIONS - forbidden_actions
    if missing_actions:
        findings.append(f"forbidden_actions missing: {sorted(missing_actions)}")

    verification = backlog.get("verification")
    if not isinstance(verification, dict):
        findings.append("verification must be an object")
    elif "sns_publishing_automation_readiness_backlog_gate.py --check" not in str(
        verification.get("local_gate", "")
    ):
        findings.append("verification.local_gate must reference this gate")

    return findings


def _validate_sources(backlog: dict[str, Any], repo_root: Path) -> list[str]:
    findings: list[str] = []
    inputs = backlog.get("source_inputs")
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
        if str(item.get("sha256", "")).lower() != _sha256(path):
            findings.append(f"source_inputs[{index}].sha256 mismatch for {rel_path}")
    return findings


def _validate_queue_contract(backlog: dict[str, Any]) -> list[str]:
    queue = backlog.get("local_queue_contract")
    if not isinstance(queue, dict):
        return ["local_queue_contract must be an object"]
    findings: list[str] = []
    missing_fields = REQUIRED_QUEUE_FIELDS - set(_string_list(queue.get("required_fields")))
    if missing_fields:
        findings.append(f"local_queue_contract.required_fields missing: {sorted(missing_fields)}")
    forbidden_fields = set(_string_list(queue.get("forbidden_fields")))
    for required in ("access_token", "refresh_token", "bot_token", "client_secret", "customer_email"):
        if required not in forbidden_fields:
            findings.append(f"local_queue_contract.forbidden_fields missing {required}")
    if queue.get("append_only_events") is not True:
        findings.append("local_queue_contract.append_only_events must be true")
    if queue.get("live_action_blocked_by_default") is not True:
        findings.append("local_queue_contract.live_action_blocked_by_default must be true")
    return findings


def _validate_dry_run_contract(backlog: dict[str, Any]) -> list[str]:
    dry_run = backlog.get("no_network_dry_run_contract")
    if not isinstance(dry_run, dict):
        return ["no_network_dry_run_contract must be an object"]
    findings: list[str] = []
    missing_fields = REQUIRED_DRY_RUN_FIELDS - set(_string_list(dry_run.get("required_fields")))
    if missing_fields:
        findings.append(f"no_network_dry_run_contract.required_fields missing: {sorted(missing_fields)}")
    for key in ("external_network_calls", "external_action_enabled", "platform_api_call_enabled"):
        if dry_run.get(key) is not False:
            findings.append(f"no_network_dry_run_contract.{key} must be false")
    if dry_run.get("writes_only_local_preview_record") is not True:
        findings.append("no_network_dry_run_contract.writes_only_local_preview_record must be true")
    if dry_run.get("live_action_blocked_by_default") is not True:
        findings.append("no_network_dry_run_contract.live_action_blocked_by_default must be true")
    return findings


def _validate_channel_readiness(backlog: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    channels = backlog.get("channel_readiness")
    if not isinstance(channels, list):
        return ["channel_readiness must be a list"]
    channel_ids = {item.get("channel_id") for item in channels if isinstance(item, dict)}
    missing = REQUIRED_CHANNEL_IDS - channel_ids
    if missing:
        findings.append(f"channel_readiness missing channel ids: {sorted(missing)}")
    for index, item in enumerate(channels):
        if not isinstance(item, dict):
            findings.append(f"channel_readiness[{index}] must be an object")
            continue
        prefix = f"channel_readiness[{index}]"
        if item.get("classification") not in ALLOWED_CLASSIFICATIONS:
            findings.append(f"{prefix}.classification must be one of {sorted(ALLOWED_CLASSIFICATIONS)}")
        if item.get("owner_r3_required_for_live") is not True:
            findings.append(f"{prefix}.owner_r3_required_for_live must be true")
        for key in (
            "external_action_enabled",
            "live_post_enabled",
            "scheduled_post_enabled",
            "platform_api_call_enabled",
            "oauth_flow_enabled",
            "token_storage_enabled",
            "browser_automation_enabled",
            "paid_ads_enabled",
            "customer_contact_enabled",
        ):
            if item.get(key) is not False:
                findings.append(f"{prefix}.{key} must be false")
        connector = item.get("connector_candidate")
        if not isinstance(connector, dict):
            findings.append(f"{prefix}.connector_candidate must be an object")
        else:
            if connector.get("stage") != "candidate_not_implementation":
                findings.append(f"{prefix}.connector_candidate.stage must be candidate_not_implementation")
            if connector.get("implementation_started") is not False:
                findings.append(f"{prefix}.connector_candidate.implementation_started must be false")
        if not isinstance(item.get("required_scopes"), list):
            findings.append(f"{prefix}.required_scopes must be a list")
        if not _has_required_subset(item.get("queue_fields"), REQUIRED_QUEUE_FIELDS):
            findings.append(f"{prefix}.queue_fields must include required queue fields")
        if not _has_required_subset(item.get("dry_run_fields"), REQUIRED_DRY_RUN_FIELDS):
            findings.append(f"{prefix}.dry_run_fields must include required dry-run fields")
        rollback = str(item.get("rollback_delete_evidence", "")).lower()
        if not rollback or not any(word in rollback for word in ("delete", "edit", "archive", "withdraw")):
            findings.append(f"{prefix}.rollback_delete_evidence must include delete/edit/archive/withdraw")
        if not _string_list(item.get("no_network_test_ids")):
            findings.append(f"{prefix}.no_network_test_ids must be a non-empty string list")
    return findings


def _validate_no_network_tests(backlog: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    tests = backlog.get("no_network_test_plan")
    if not isinstance(tests, list):
        return ["no_network_test_plan must be a list"]
    test_ids = {item.get("test_id") for item in tests if isinstance(item, dict)}
    missing = REQUIRED_TEST_IDS - test_ids
    if missing:
        findings.append(f"no_network_test_plan missing test ids: {sorted(missing)}")
    for index, item in enumerate(tests):
        if not isinstance(item, dict):
            findings.append(f"no_network_test_plan[{index}] must be an object")
            continue
        prefix = f"no_network_test_plan[{index}]"
        if item.get("external_network_calls") is not False:
            findings.append(f"{prefix}.external_network_calls must be false")
        if item.get("external_action_enabled") is not False:
            findings.append(f"{prefix}.external_action_enabled must be false")
        if item.get("owner_r3_required_for_live") is not True:
            findings.append(f"{prefix}.owner_r3_required_for_live must be true")
    return findings


def _validate_implementation_backlog(backlog: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    items = backlog.get("implementation_backlog")
    if not isinstance(items, list):
        return ["implementation_backlog must be a list"]
    item_ids = {item.get("backlog_id") for item in items if isinstance(item, dict)}
    missing = REQUIRED_BACKLOG_IDS - item_ids
    if missing:
        findings.append(f"implementation_backlog missing ids: {sorted(missing)}")
    levels = {item.get("reversibility_level") for item in items if isinstance(item, dict)}
    if "R2" not in levels:
        findings.append("implementation_backlog must include R2 local candidates")
    if "R3" not in levels:
        findings.append("implementation_backlog must include R3 live candidates")
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            findings.append(f"implementation_backlog[{index}] must be an object")
            continue
        prefix = f"implementation_backlog[{index}]"
        if item.get("reversibility_level") not in {"R2", "R3"}:
            findings.append(f"{prefix}.reversibility_level must be R2 or R3")
        if item.get("external_action_enabled") is not False:
            findings.append(f"{prefix}.external_action_enabled must be false")
        if item.get("reversibility_level") == "R2":
            if item.get("safe_without_owner") is not True:
                findings.append(f"{prefix}.safe_without_owner must be true for R2")
            if item.get("owner_approval_required_before_execution") is not False:
                findings.append(f"{prefix}.owner_approval_required_before_execution must be false for R2")
        if item.get("reversibility_level") == "R3":
            if item.get("safe_without_owner") is not False:
                findings.append(f"{prefix}.safe_without_owner must be false for R3")
            if item.get("owner_approval_required_before_execution") is not True:
                findings.append(f"{prefix}.owner_approval_required_before_execution must be true for R3")
    return findings


def _validate_handoff(backlog: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    handoff = backlog.get("taskset_handoff")
    if not isinstance(handoff, dict):
        return ["taskset_handoff must be an object"]
    expected = {
        "task_166_complete": True,
        "task_167_complete": True,
        "task_168_complete": True,
        "task_169_complete": True,
        "task_170_complete": True,
        "taskset_complete": True,
        "live_publication_approved": False,
        "oauth_or_platform_api_enabled": False,
        "customer_contact_enabled": False,
        "sales_revenue_activation_enabled": False,
    }
    for key, value in expected.items():
        if handoff.get(key) is not value:
            findings.append(f"taskset_handoff.{key} must be {str(value).lower()}")
    r3_items = set(_string_list(handoff.get("owner_r3_required_for")))
    for required in ("SNS upload", "OAuth or platform API posting", "token handling", "customer contact"):
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


def _has_required_subset(value: Any, required: set[str]) -> bool:
    return required <= set(_string_list(value))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backlog", type=Path, default=DEFAULT_BACKLOG)
    parser.add_argument("--check", action="store_true", help="validate and return non-zero on findings")
    args = parser.parse_args()

    backlog = load_backlog(args.backlog)
    findings = validate_backlog(backlog)
    if findings:
        print("SNS publishing automation readiness backlog gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"SNS publishing automation readiness backlog gate: PASS ({args.backlog})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
