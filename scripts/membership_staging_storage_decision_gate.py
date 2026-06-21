"""Validate the membership staging persistent-storage decision packet.

This gate checks local decision structure only. It must not create or mutate
Supabase, Railway, Vercel, database, storage bucket, or volume resources; write
environment variables; create or apply migrations; read or write secrets; use
production data; publish URLs; or mark launch readiness true.
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
    / "MEMBERSHIP-STAGING-PERSISTENT-STORAGE-DECISION.json"
)

REQUIRED_BOUNDARIES = {
    "not_applied_to_staging",
    "no_database_migration_created",
    "no_supabase_apply",
    "no_external_project_mutation",
    "no_external_env_write",
    "no_railway_volume_created",
    "no_secret_values",
    "no_production_data",
    "no_public_url_publish",
    "keeps_can_launch_false",
}

REQUIRED_OPTIONS = {
    "local_encrypted_vault",
    "sqlite_file",
    "railway_volume",
    "supabase_postgres_auth_rls",
    "supabase_storage_buckets",
}

REQUIRED_SURFACES = {
    "auth_identity_and_profile",
    "membership_requests",
    "subscription_grants",
    "payment_evidence",
    "integration_secret_metadata",
    "portfolio_engine_trading_state",
    "audit_events",
}

REQUIRED_STAGING_TESTS = {
    "storage_decision_gate_passes",
    "local_vault_not_external_staging_source_of_truth",
    "railway_volume_not_tenant_data_source_of_truth",
    "supabase_migration_review_packet_exists",
    "rls_enabled_on_membership_and_secret_metadata_tables",
    "cross_user_membership_request_read_blocked",
    "cross_user_integration_metadata_read_blocked",
    "applicant_lookup_requires_request_id_and_contact",
    "service_role_or_secret_key_server_only",
    "backup_restore_plan_owner_reviewed",
    "no_external_users_until_supabase_apply_and_tests_pass",
    "can_launch_false_until_r3_evidence",
}

REQUIRED_LAUNCH_GATES = {
    "storage_decision_gate_passes",
    "membership_supabase_field_map_gate_passes",
    "membership_secret_store_plan_gate_passes",
    "migration_review_packet_exists",
    "owner_selected_supabase_staging_project",
    "supabase_migration_rls_advisors_and_cross_user_tests_pass",
    "backup_restore_plan_reviewed",
    "local_vault_and_sqlite_limited_to_internal_smoke_or_replaced",
    "railway_volume_not_tenant_source_of_truth",
    "external_env_values_written_by_owner_outside_repo",
    "no_real_secrets_or_customer_data_in_repo",
    "can_launch_remains_false_until_r3_evidence",
}

FORBIDDEN_KEY_NAMES = {
    "database_url",
    "supabase_project_ref",
    "supabase_service_role_key",
    "service_role_key",
    "vault_key",
    "raw_token",
    "secret_value",
    "api_key",
    "production_apply_completed",
    "railway_volume_id",
    "mount_path_value",
    "public_url",
    "deployment_url",
    "customer_record",
}


def load_packet(path: Path = DEFAULT_PACKET) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("storage decision packet root must be an object")
    return data


def validate_packet(packet: dict[str, Any]) -> list[str]:
    findings: list[str] = []

    forbidden_paths = _find_forbidden_keys(packet)
    if forbidden_paths:
        findings.append(f"forbidden deploy/storage/secret keys present: {forbidden_paths}")

    if packet.get("$schema") != "autofolio.membership-staging-persistent-storage-decision/v1":
        findings.append("unexpected or missing storage decision schema")

    status = str(packet.get("status", ""))
    if "not_applied" not in status:
        findings.append("packet status must clearly state it is not applied")

    boundaries = packet.get("boundaries")
    if not isinstance(boundaries, dict):
        findings.append("boundaries must be an object")
    else:
        for key in REQUIRED_BOUNDARIES:
            if boundaries.get(key) is not True:
                findings.append(f"boundaries.{key} must be true")

    source_text = " ".join(
        item.get("id", "") + " " + item.get("authority", "") + " " + item.get("url", "") + " " + item.get("note", "")
        for item in packet.get("source_basis", [])
        if isinstance(item, dict)
    )
    for marker in ("Supabase", "Postgres", "RLS", "backup", "Storage", "Railway", "volume"):
        if marker.lower() not in source_text.lower():
            findings.append(f"source_basis missing marker: {marker}")

    summary = packet.get("decision_summary")
    if not isinstance(summary, dict):
        findings.append("decision_summary must be an object")
    else:
        if summary.get("selected_external_staging_source_of_truth") != "supabase_postgres_auth_rls":
            findings.append("decision_summary must select supabase_postgres_auth_rls")
        smoke_limit = str(summary.get("internal_smoke_limit", ""))
        if "no_external_users" not in smoke_limit or "can_launch_false" not in smoke_limit:
            findings.append("decision_summary.internal_smoke_limit must forbid external users and keep can_launch false")
        not_selected = str(summary.get("not_selected_for_tenant_source_of_truth", ""))
        for marker in ("local_encrypted_vault", "sqlite_file", "railway_volume"):
            if marker not in not_selected:
                findings.append(f"decision_summary.not_selected missing {marker}")

    options = packet.get("options")
    option_map: dict[str, dict[str, Any]] = {}
    if not isinstance(options, list):
        findings.append("options must be a list")
    else:
        option_map = {item.get("id"): item for item in options if isinstance(item, dict)}
        missing = REQUIRED_OPTIONS - set(option_map)
        if missing:
            findings.append(f"missing storage options: {sorted(missing)}")
        for option_id, item in option_map.items():
            findings.extend(_validate_option(option_id, item))

    selected = option_map.get("supabase_postgres_auth_rls")
    if selected:
        if selected.get("decision") != "selected_external_staging_source_of_truth":
            findings.append("supabase_postgres_auth_rls must be selected")
        if selected.get("tenant_source_of_truth") is not True:
            findings.append("supabase_postgres_auth_rls must be the tenant source of truth")
        if selected.get("rls_available") is not True:
            findings.append("supabase_postgres_auth_rls must have RLS available")

    local = option_map.get("local_encrypted_vault")
    if local and local.get("tenant_source_of_truth") is not False:
        findings.append("local_encrypted_vault cannot be tenant source of truth")

    railway = option_map.get("railway_volume")
    if railway:
        if railway.get("tenant_source_of_truth") is not False:
            findings.append("railway_volume cannot be tenant source of truth")
        if railway.get("external_action_required") is not True:
            findings.append("railway_volume must require external action")

    surfaces = packet.get("storage_surfaces")
    if not isinstance(surfaces, list):
        findings.append("storage_surfaces must be a list")
    else:
        surface_map = {item.get("id"): item for item in surfaces if isinstance(item, dict)}
        missing = REQUIRED_SURFACES - set(surface_map)
        if missing:
            findings.append(f"missing storage surfaces: {sorted(missing)}")
        for surface_id, item in surface_map.items():
            target = str(item.get("selected_target", ""))
            if "supabase" not in target.lower():
                findings.append(f"{surface_id}: selected_target must be Supabase-backed")
            if not item.get("required_before_external_users"):
                findings.append(f"{surface_id}: required_before_external_users is required")

    missing_tests = REQUIRED_STAGING_TESTS - set(_string_list(packet.get("required_staging_tests")))
    if missing_tests:
        findings.append(f"missing required staging tests: {sorted(missing_tests)}")

    missing_gates = REQUIRED_LAUNCH_GATES - set(_string_list(packet.get("launch_gates")))
    if missing_gates:
        findings.append(f"missing launch gates: {sorted(missing_gates)}")

    forbidden_runtime = " ".join(_string_list(packet.get("forbidden_actions")))
    for marker in ("Supabase", "Railway", "migrations", "environment variables", "real customer data", "can_launch"):
        if marker not in forbidden_runtime:
            findings.append(f"forbidden_actions missing marker: {marker}")

    verification = packet.get("verification")
    if not isinstance(verification, dict):
        findings.append("verification must be an object")
    else:
        if "membership_staging_storage_decision_gate.py --check" not in str(
            verification.get("local_decision_gate", "")
        ):
            findings.append("verification.local_decision_gate must reference this gate")

    return findings


def _validate_option(option_id: str, item: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    if "decision" not in item:
        findings.append(f"{option_id}: decision is required")
    if "allowed_scope" not in item:
        findings.append(f"{option_id}: allowed_scope is required")
    if item.get("tenant_source_of_truth") is True and option_id != "supabase_postgres_auth_rls":
        findings.append(f"{option_id}: only supabase_postgres_auth_rls may be tenant source of truth")
    if option_id != "supabase_postgres_auth_rls":
        if "selected_external_staging_source_of_truth" in str(item.get("decision", "")):
            findings.append(f"{option_id}: cannot be selected as external staging source of truth")
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
        print("membership staging storage decision gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print(f"membership staging storage decision gate: PASS ({args.packet})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

