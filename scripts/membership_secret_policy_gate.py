"""Validate the membership production secret policy asset.

This gate checks local policy structure only. It must not read secrets, call
providers, validate OAuth callbacks, activate KIS credentials, connect to
Supabase, apply migrations, or deploy anything.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = REPO_ROOT / "agents" / "project" / "MEMBERSHIP-PRODUCTION-SECRET-POLICY.json"

REQUIRED_PROVIDER_CATEGORIES = {
    "openai_api_key",
    "anthropic_api_key",
    "telegram_bot_token",
    "google_oauth_token",
    "naver_oauth_token",
    "kakao_oauth_token",
    "x_oauth_token",
    "kis_app_key",
    "kis_app_secret",
    "kis_access_token",
}

REQUIRED_METADATA_FIELDS = {
    "user_id",
    "provider_id",
    "provider_kind",
    "auth_type",
    "account_label",
    "scopes",
    "enabled",
    "secret_set",
    "secret_hint",
    "created_at",
    "updated_at",
    "last_checked_at",
    "status",
    "rotation_due_at",
    "deletion_requested_at",
    "audit_event_id",
}

REQUIRED_FORBIDDEN_EXPOSURE = {
    "plaintext_secret_response",
    "secret_value_in_url",
    "secret_value_in_log",
    "secret_value_in_task_record",
    "secret_value_in_report",
    "secret_value_in_browser_storage",
    "service_key_in_browser_bundle",
    "raw_oauth_token_event",
    "committed_env_file",
    "provider_validation_without_owner_approval",
    "kis_credential_activation_without_owner_approval",
}

REQUIRED_REDACTION_RULES = {
    "mask_secret_to_suffix",
    "bound_account_label",
    "allowed_scope_names_only",
    "no_plaintext_last_checked_error",
}

REQUIRED_LIFECYCLE_ACTIONS = {
    "write_or_replace_secret",
    "disable_without_delete",
    "delete_secret",
    "rotate_secret",
    "owner_support_redacted_metadata_read",
}

REQUIRED_AUDIT_INVARIANTS = {
    "server_side_only_storage",
    "write_only_api_boundary",
    "response_metadata_only",
    "delete_removes_secret_material",
    "rotation_replaces_and_audits",
    "no_provider_call_during_policy_gate",
    "no_secret_in_repo_or_logs",
    "user_scope_from_auth_session",
    "owner_admin_plaintext_read_forbidden",
}

REQUIRED_LAUNCH_GATES = {
    "policy_gate_passes",
    "production_secret_store_selected",
    "encryption_key_management_reviewed",
    "write_redaction_delete_tests_pass",
    "rotation_path_tested",
    "audit_event_schema_reviewed",
    "provider_oauth_flows_reviewed",
    "kis_credential_scope_reviewed",
    "incident_response_runbook_written",
}

FORBIDDEN_TOP_LEVEL_KEYS = {
    "secret_value",
    "plaintext_secret",
    "api_key",
    "access_token",
    "refresh_token",
    "app_secret",
    "service_role_key",
    "kis_app_key",
    "kis_app_secret",
    "oauth_callback_validated",
    "production_apply_completed",
    "supabase_project_id",
}

FORBIDDEN_RESPONSE_FIELDS = {
    "secret_value",
    "plaintext_secret",
    "access_token",
    "refresh_token",
    "api_key",
    "app_secret",
}


def load_policy(path: Path = DEFAULT_POLICY) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("policy root must be an object")
    return data


def validate_policy(policy: dict[str, Any]) -> list[str]:
    findings: list[str] = []

    forbidden_present = FORBIDDEN_TOP_LEVEL_KEYS.intersection(policy)
    if forbidden_present:
        findings.append(f"forbidden secret/production keys present: {sorted(forbidden_present)}")

    if policy.get("$schema") != "autofolio.membership-production-secret-policy/v1":
        findings.append("unexpected or missing policy schema")

    status = str(policy.get("status", ""))
    if "not_applied" not in status:
        findings.append("policy status must clearly state it is not applied")

    boundaries = policy.get("boundaries")
    if not isinstance(boundaries, dict):
        findings.append("boundaries must be an object")
    else:
        for key in (
            "not_applied_to_production",
            "no_secret_values",
            "no_provider_api_call",
            "no_oauth_callback_validation",
            "no_kis_credential_activation",
            "no_external_network_action_required",
            "keeps_can_launch_false",
        ):
            if boundaries.get(key) is not True:
                findings.append(f"boundaries.{key} must be true")

    categories = policy.get("provider_categories")
    if not isinstance(categories, list):
        findings.append("provider_categories must be a list")
    else:
        category_ids = {item.get("id") for item in categories if isinstance(item, dict)}
        missing = REQUIRED_PROVIDER_CATEGORIES - category_ids
        if missing:
            findings.append(f"missing provider categories: {sorted(missing)}")
        for item in categories:
            if not isinstance(item, dict):
                continue
            category_id = item.get("id", "<unknown>")
            if item.get("user_owned") is not True:
                findings.append(f"{category_id}: user_owned must be true")
            if item.get("production_storage_status") == "implemented":
                findings.append(f"{category_id}: policy cannot mark production storage implemented")
            if item.get("raw_secret_response_allowed") is not False:
                findings.append(f"{category_id}: raw_secret_response_allowed must be false")
            response_fields = set(_string_list(item.get("response_allowed_fields")))
            leaked = FORBIDDEN_RESPONSE_FIELDS.intersection(response_fields)
            if leaked:
                findings.append(f"{category_id}: forbidden response fields present: {sorted(leaked)}")
            for required in ("provider_id", "auth_type", "secret_set", "secret_hint", "status"):
                if required not in response_fields:
                    findings.append(f"{category_id}: response_allowed_fields missing {required}")

    metadata_fields = set(_string_list(policy.get("retained_metadata_fields")))
    missing_metadata = REQUIRED_METADATA_FIELDS - metadata_fields
    if missing_metadata:
        findings.append(f"missing retained metadata fields: {sorted(missing_metadata)}")
    leaked_metadata = FORBIDDEN_RESPONSE_FIELDS.intersection(metadata_fields)
    if leaked_metadata:
        findings.append(f"retained_metadata_fields include raw secret fields: {sorted(leaked_metadata)}")

    missing_forbidden = REQUIRED_FORBIDDEN_EXPOSURE - set(_string_list(policy.get("forbidden_exposure")))
    if missing_forbidden:
        findings.append(f"missing forbidden exposure entries: {sorted(missing_forbidden)}")

    redaction_ids = {
        item.get("id")
        for item in policy.get("redaction_rules", [])
        if isinstance(item, dict)
    }
    missing_redaction = REQUIRED_REDACTION_RULES - redaction_ids
    if missing_redaction:
        findings.append(f"missing redaction rules: {sorted(missing_redaction)}")

    lifecycle = policy.get("lifecycle_actions")
    if not isinstance(lifecycle, list):
        findings.append("lifecycle_actions must be a list")
    else:
        lifecycle_ids = {item.get("id") for item in lifecycle if isinstance(item, dict)}
        missing_lifecycle = REQUIRED_LIFECYCLE_ACTIONS - lifecycle_ids
        if missing_lifecycle:
            findings.append(f"missing lifecycle actions: {sorted(missing_lifecycle)}")
        for item in lifecycle:
            if not isinstance(item, dict):
                continue
            action_id = item.get("id", "<unknown>")
            if item.get("plaintext_returned") is not False:
                findings.append(f"{action_id}: plaintext_returned must be false")
            if item.get("provider_called") is not False:
                findings.append(f"{action_id}: provider_called must be false")
            if item.get("audit_required") is not True:
                findings.append(f"{action_id}: audit_required must be true")

    invariant_ids = {
        item.get("id")
        for item in policy.get("audit_invariants", [])
        if isinstance(item, dict)
    }
    missing_invariants = REQUIRED_AUDIT_INVARIANTS - invariant_ids
    if missing_invariants:
        findings.append(f"missing audit invariants: {sorted(missing_invariants)}")

    missing_gates = REQUIRED_LAUNCH_GATES - set(_string_list(policy.get("launch_gates")))
    if missing_gates:
        findings.append(f"missing launch gates: {sorted(missing_gates)}")

    verification = policy.get("verification")
    if not isinstance(verification, dict):
        findings.append("verification must be an object")
    else:
        local_gate = str(verification.get("local_policy_gate", ""))
        if "membership_secret_policy_gate.py --check" not in local_gate:
            findings.append("verification.local_policy_gate must reference this gate")

    return findings


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--check", action="store_true", help="validate and return non-zero on findings")
    args = parser.parse_args()

    policy = load_policy(args.policy)
    findings = validate_policy(policy)
    if findings:
        print("membership secret policy gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print(f"membership secret policy gate: PASS ({args.policy})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
