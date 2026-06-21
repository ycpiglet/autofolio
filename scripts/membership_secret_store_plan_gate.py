"""Validate the membership production secret-store implementation plan.

This gate checks local plan structure only. It must not read secrets, call
providers, validate OAuth callbacks, activate KIS credentials, connect to
Supabase, mutate a project, apply migrations, or deploy.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = (
    REPO_ROOT
    / "agents"
    / "project"
    / "MEMBERSHIP-PRODUCTION-SECRET-STORE-IMPLEMENTATION-PLAN.json"
)

REQUIRED_CANDIDATE_STORES = {
    "deployment_runtime_secrets",
    "supabase_edge_function_secrets",
    "supabase_vault_or_equivalent_kms",
    "tenant_secret_metadata_table",
    "external_kms_future_option",
}

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

REQUIRED_API_OPERATIONS = {
    "write_or_replace_secret",
    "rotate_secret",
    "disable_secret",
    "delete_secret",
    "owner_support_metadata_read",
}

REQUIRED_CHECKLIST = {
    "create_metadata_only_response",
    "rotate_replaces_reference_without_readback",
    "disable_blocks_execution_without_delete",
    "delete_removes_payload_and_leaves_tombstone",
    "owner_support_redacted_metadata_only",
    "incident_response_rotation_path",
}

REQUIRED_STAGING_TESTS = {
    "member_a_cannot_read_member_b_secret_metadata",
    "member_a_cannot_update_member_b_secret_metadata",
    "secret_write_returns_metadata_only",
    "secret_rotate_returns_metadata_only",
    "secret_delete_removes_payload_reference",
    "disabled_secret_blocks_worker_execution",
    "owner_support_cannot_read_plaintext",
    "logs_redact_authorization_and_token_fields",
    "vault_decrypted_view_not_exposed_to_anon_or_authenticated_clients",
    "kis_secret_categories_blocked_until_terms_review",
}

REQUIRED_LAUNCH_GATES = {
    "plan_gate_passes",
    "secret_store_selected_by_owner_or_release_council",
    "key_management_access_review_completed",
    "metadata_table_rls_and_update_with_check_reviewed",
    "vault_or_kms_decrypted_access_reviewed",
    "write_rotate_disable_delete_tests_pass",
    "log_redaction_tests_pass",
    "audit_event_schema_reviewed",
    "incident_response_runbook_written",
    "provider_oauth_validation_flow_approved",
    "kis_terms_and_scope_review_completed",
    "can_launch_remains_false_until_r3_evidence",
}

REQUIRED_BOUNDARIES = {
    "not_applied_to_production",
    "no_secret_values",
    "no_secret_read",
    "no_secret_write",
    "no_provider_api_call",
    "no_oauth_callback_validation",
    "no_kis_credential_activation",
    "no_supabase_project_mutation",
    "no_production_db_apply",
    "no_external_network_action_required",
    "keeps_can_launch_false",
}

FORBIDDEN_KEY_NAMES = {
    "secret_value",
    "plaintext_secret",
    "raw_secret",
    "api_key_value",
    "access_token_value",
    "refresh_token_value",
    "app_secret_value",
    "service_role_key_value",
    "supabase_project_id",
    "production_apply_completed",
    "oauth_callback_validated",
    "kis_credential_activated",
}


def load_plan(path: Path = DEFAULT_PLAN) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("plan root must be an object")
    return data


def validate_plan(plan: dict[str, Any]) -> list[str]:
    findings: list[str] = []

    forbidden_paths = list(_find_forbidden_keys(plan))
    if forbidden_paths:
        findings.append(f"forbidden secret/production keys present: {forbidden_paths}")

    if plan.get("$schema") != "autofolio.membership-secret-store-implementation-plan/v1":
        findings.append("unexpected or missing plan schema")

    status = str(plan.get("status", ""))
    if "not_applied" not in status:
        findings.append("plan status must clearly state it is not applied")

    boundaries = plan.get("boundaries")
    if not isinstance(boundaries, dict):
        findings.append("boundaries must be an object")
    else:
        for key in REQUIRED_BOUNDARIES:
            if boundaries.get(key) is not True:
                findings.append(f"boundaries.{key} must be true")

    source_text = " ".join(
        item.get("id", "") + " " + item.get("url", "") + " " + item.get("note", "")
        for item in plan.get("source_basis", [])
        if isinstance(item, dict)
    )
    for marker in ("vault", "Edge Function", "API keys", "secret keys", "browser"):
        if marker.lower() not in source_text.lower():
            findings.append(f"source_basis missing marker: {marker}")

    architecture = plan.get("recommended_architecture")
    if not isinstance(architecture, dict):
        findings.append("recommended_architecture must be an object")
    else:
        if architecture.get("selection_status") == "selected_and_applied":
            findings.append("architecture cannot be marked selected_and_applied")
        for key in ("platform_secret_lane", "tenant_secret_lane", "tenant_metadata_lane"):
            if not architecture.get(key):
                findings.append(f"recommended_architecture.{key} is required")

    candidates = plan.get("candidate_stores")
    if not isinstance(candidates, list):
        findings.append("candidate_stores must be a list")
    else:
        candidate_ids = {item.get("id") for item in candidates if isinstance(item, dict)}
        missing = REQUIRED_CANDIDATE_STORES - candidate_ids
        if missing:
            findings.append(f"missing candidate stores: {sorted(missing)}")
        for item in candidates:
            if not isinstance(item, dict):
                continue
            candidate_id = item.get("id", "<unknown>")
            if item.get("production_status") == "implemented":
                findings.append(f"{candidate_id}: production_status cannot be implemented")
            if item.get("plaintext_browser_access") is not False:
                findings.append(f"{candidate_id}: plaintext_browser_access must be false")
            if item.get("repository_storage_allowed") is not False:
                findings.append(f"{candidate_id}: repository_storage_allowed must be false")
            if item.get("access_review_required") is not True:
                findings.append(f"{candidate_id}: access_review_required must be true")

    providers = plan.get("provider_category_map")
    if not isinstance(providers, list):
        findings.append("provider_category_map must be a list")
    else:
        provider_ids = {item.get("id") for item in providers if isinstance(item, dict)}
        missing = REQUIRED_PROVIDER_CATEGORIES - provider_ids
        if missing:
            findings.append(f"missing provider categories: {sorted(missing)}")
        for item in providers:
            if not isinstance(item, dict):
                continue
            provider_id = item.get("id", "<unknown>")
            if item.get("plaintext_response_allowed") is not False:
                findings.append(f"{provider_id}: plaintext_response_allowed must be false")
            if item.get("target_store") != "supabase_vault_or_equivalent_kms":
                findings.append(f"{provider_id}: target_store must be supabase_vault_or_equivalent_kms")
            if item.get("metadata_table") != "tenant_secret_metadata_table":
                findings.append(f"{provider_id}: metadata_table must be tenant_secret_metadata_table")
            validation = str(item.get("provider_validation", ""))
            if "forbidden" not in validation and "owner" not in validation.lower():
                findings.append(f"{provider_id}: provider_validation must stay blocked until approval")
            if provider_id.startswith("kis_") and item.get("kis_terms_review_required") is not True:
                findings.append(f"{provider_id}: KIS categories require terms review")

    operations = plan.get("future_api_boundary")
    if not isinstance(operations, list):
        findings.append("future_api_boundary must be a list")
    else:
        operation_ids = {item.get("id") for item in operations if isinstance(item, dict)}
        missing = REQUIRED_API_OPERATIONS - operation_ids
        if missing:
            findings.append(f"missing future API operations: {sorted(missing)}")
        for item in operations:
            if not isinstance(item, dict):
                continue
            operation_id = item.get("id", "<unknown>")
            if item.get("response_secret_material") is not False:
                findings.append(f"{operation_id}: response_secret_material must be false")
            if item.get("provider_call_on_write") is not False:
                findings.append(f"{operation_id}: provider_call_on_write must be false")
            if item.get("audit_required") is not True:
                findings.append(f"{operation_id}: audit_required must be true")

    checklist = plan.get("rotation_delete_audit_checklist")
    if not isinstance(checklist, list):
        findings.append("rotation_delete_audit_checklist must be a list")
    else:
        checklist_ids = {item.get("id") for item in checklist if isinstance(item, dict)}
        missing = REQUIRED_CHECKLIST - checklist_ids
        if missing:
            findings.append(f"missing rotation/delete/audit checklist items: {sorted(missing)}")
        for item in checklist:
            if not isinstance(item, dict):
                continue
            item_id = item.get("id", "<unknown>")
            if item.get("plaintext_secret_read_required") is not False:
                findings.append(f"{item_id}: plaintext_secret_read_required must be false")
            if item.get("provider_call_required") is not False:
                findings.append(f"{item_id}: provider_call_required must be false")
            if item.get("audit_required") is not True:
                findings.append(f"{item_id}: audit_required must be true")

    missing_tests = REQUIRED_STAGING_TESTS - set(_string_list(plan.get("required_staging_tests")))
    if missing_tests:
        findings.append(f"missing required staging tests: {sorted(missing_tests)}")

    missing_gates = REQUIRED_LAUNCH_GATES - set(_string_list(plan.get("launch_gates")))
    if missing_gates:
        findings.append(f"missing launch gates: {sorted(missing_gates)}")

    forbidden_runtime = " ".join(_string_list(plan.get("forbidden_actions")))
    for marker in ("secret read", "secret write", "OAuth provider validation", "KIS credential activation", "Supabase project mutation", "deploy"):
        if marker not in forbidden_runtime:
            findings.append(f"forbidden_actions missing marker: {marker}")

    verification = plan.get("verification")
    if not isinstance(verification, dict):
        findings.append("verification must be an object")
    else:
        if "membership_secret_store_plan_gate.py --check" not in str(verification.get("local_plan_gate", "")):
            findings.append("verification.local_plan_gate must reference this gate")

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
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--check", action="store_true", help="validate and return non-zero on findings")
    args = parser.parse_args()

    plan = load_plan(args.plan)
    findings = validate_plan(plan)
    if findings:
        print("membership secret store plan gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print(f"membership secret store plan gate: PASS ({args.plan})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
