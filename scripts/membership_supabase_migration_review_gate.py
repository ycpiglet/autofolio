"""Validate the membership Supabase staging migration/RLS review packet.

This gate checks local review structure only. It must not create migration
files, connect to Supabase, execute SQL, apply schema, edit schema.sql, change
Data API grants, write environment variables, deploy, handle secrets, or touch
production data.
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
    / "MEMBERSHIP-SUPABASE-STAGING-MIGRATION-RLS-REVIEW.json"
)

REQUIRED_BOUNDARIES = {
    "review_packet_only",
    "no_migration_file_created",
    "no_executable_sql",
    "no_supabase_connection",
    "no_supabase_apply",
    "no_schema_sql_change",
    "no_data_api_grant_change",
    "no_external_env_write",
    "no_secret_values",
    "no_production_data",
    "no_public_url_publish",
    "keeps_can_launch_false",
}

REQUIRED_SOURCE_INPUTS = {
    "agents/project/MEMBERSHIP-PRODUCTION-CONTRACT.json",
    "agents/project/MEMBERSHIP-SUPABASE-STAGING-FIELD-MAP.json",
    "agents/project/MEMBERSHIP-STAGING-PERSISTENT-STORAGE-DECISION.json",
    "agents/project/MEMBERSHIP-TENANT-ISOLATION-MATRIX.json",
    "agents/project/MEMBERSHIP-PRODUCTION-SECRET-POLICY.json",
    "agents/project/MEMBERSHIP-PAYMENT-EVIDENCE-POLICY.json",
    "agents/project/MEMBERSHIP-ENGINE-SAFETY-CONTRACT.json",
}

REQUIRED_TABLES = {
    "profiles",
    "membership_requests",
    "deposit_instructions",
    "approval_events",
    "subscription_grants",
    "integration_secret_metadata",
    "payment_evidence",
    "portfolio_accounts",
    "holdings_snapshots",
    "risk_settings",
    "engine_state",
    "engine_run_queue",
    "trade_conditions",
    "order_intents",
    "order_logs",
    "execution_logs",
    "notifications",
    "audit_events",
}

UPDATE_CAPABLE_TABLES = {"profiles", "risk_settings", "trade_conditions"}
APPEND_ONLY_TABLES = {"approval_events", "order_intents", "order_logs", "execution_logs", "audit_events"}

REQUIRED_TESTS = {
    "anon_has_no_tenant_table_access",
    "member_a_cannot_read_member_b",
    "member_a_cannot_update_member_b",
    "member_cannot_reassign_user_id",
    "member_cannot_call_owner_admin",
    "owner_admin_routes_create_audit_events",
    "secret_metadata_never_returns_plaintext",
    "payment_evidence_minimized",
    "engine_queue_user_scope",
    "order_intent_append_only",
}

FORBIDDEN_KEY_NAMES = {
    "migration_sql",
    "ddl",
    "sql_apply_completed",
    "applied_at",
    "supabase_project_ref",
    "database_url",
    "service_role_key",
    "secret_key",
    "schema_sql_updated",
    "data_api_grant_applied",
    "production_apply_completed",
}


def load_packet(path: Path = DEFAULT_PACKET) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("migration/RLS review packet root must be an object")
    return data


def validate_packet(packet: dict[str, Any]) -> list[str]:
    findings: list[str] = []

    forbidden_paths = _find_forbidden_keys(packet)
    if forbidden_paths:
        findings.append(f"forbidden migration/apply/secret keys present: {forbidden_paths}")

    if packet.get("$schema") != "autofolio.membership-supabase-staging-migration-rls-review/v1":
        findings.append("unexpected or missing migration review schema")

    status = str(packet.get("status", ""))
    if "not_migration" not in status or "not_applied" not in status:
        findings.append("packet status must state not migration and not applied")

    boundaries = packet.get("boundaries")
    if not isinstance(boundaries, dict):
        findings.append("boundaries must be an object")
    else:
        for key in REQUIRED_BOUNDARIES:
            if boundaries.get(key) is not True:
                findings.append(f"boundaries.{key} must be true")

    missing_inputs = REQUIRED_SOURCE_INPUTS - set(_string_list(packet.get("source_inputs")))
    if missing_inputs:
        findings.append(f"missing source inputs: {sorted(missing_inputs)}")

    source_text = " ".join(
        item.get("id", "") + " " + item.get("authority", "") + " " + item.get("url", "") + " " + item.get("note", "")
        for item in packet.get("source_basis", [])
        if isinstance(item, dict)
    )
    for marker in ("Supabase", "RLS", "Data API", "advisor", "backup"):
        if marker.lower() not in source_text.lower():
            findings.append(f"source_basis missing marker: {marker}")

    mode = packet.get("review_mode")
    if not isinstance(mode, dict):
        findings.append("review_mode must be an object")
    else:
        if mode.get("artifact_type") != "local_review_packet":
            findings.append("review_mode.artifact_type must be local_review_packet")
        for key in ("migration_artifact_created", "sql_statements_present", "apply_or_push_performed"):
            if mode.get(key) is not False:
                findings.append(f"review_mode.{key} must be false")

    findings.extend(_validate_table_groups(packet.get("table_groups")))
    findings.extend(_validate_table_specs(packet.get("table_review_specs")))

    requirement_text = " ".join(_string_list(packet.get("rls_review_requirements")))
    for marker in ("RLS enabled", "TO authenticated", "WITH CHECK", "Append-only", "Anon", "audit events", "Service role"):
        if marker not in requirement_text:
            findings.append(f"rls_review_requirements missing marker: {marker}")

    order = _string_list(packet.get("data_api_review_order"))
    for marker in ("Confirm anon has no tenant table grants.", "Run security and performance advisors after schema exists.", "Run cross-user tests before any external user staging."):
        if marker not in order:
            findings.append(f"data_api_review_order missing step: {marker}")

    missing_tests = REQUIRED_TESTS - set(_string_list(packet.get("required_cross_user_tests")))
    if missing_tests:
        findings.append(f"missing cross-user tests: {sorted(missing_tests)}")

    rollback = " ".join(_string_list(packet.get("rollback_and_apply_review")))
    for marker in ("staging project", "real migration", "Rollback", "advisor", "Cross-user", "can_launch"):
        if marker.lower() not in rollback.lower():
            findings.append(f"rollback_and_apply_review missing marker: {marker}")

    forbidden_runtime = " ".join(_string_list(packet.get("forbidden_actions")))
    for marker in ("migration file", "execute SQL", "Supabase project", "schema.sql", "environment variables", "secret values", "can_launch"):
        if marker not in forbidden_runtime:
            findings.append(f"forbidden_actions missing marker: {marker}")

    verification = packet.get("verification")
    if not isinstance(verification, dict):
        findings.append("verification must be an object")
    else:
        if "membership_supabase_migration_review_gate.py --check" not in str(
            verification.get("local_review_gate", "")
        ):
            findings.append("verification.local_review_gate must reference this gate")

    return findings


def _validate_table_groups(value: Any) -> list[str]:
    findings: list[str] = []
    if not isinstance(value, list):
        return ["table_groups must be a list"]
    grouped_tables: set[str] = set()
    for group in value:
        if not isinstance(group, dict):
            continue
        tables = set(_string_list(group.get("tables")))
        grouped_tables.update(tables)
        if not group.get("review_focus"):
            findings.append(f"{group.get('id', '<unknown>')}: review_focus is required")
    missing = REQUIRED_TABLES - grouped_tables
    if missing:
        findings.append(f"table_groups missing tables: {sorted(missing)}")
    return findings


def _validate_table_specs(value: Any) -> list[str]:
    findings: list[str] = []
    if not isinstance(value, list):
        return ["table_review_specs must be a list"]
    specs = {item.get("table"): item for item in value if isinstance(item, dict)}
    missing = REQUIRED_TABLES - set(specs)
    if missing:
        findings.append(f"missing table review specs: {sorted(missing)}")
    for table, spec in specs.items():
        if spec.get("rls_required") is not True:
            findings.append(f"{table}: rls_required must be true")
        if spec.get("auth_uid_policy_required") is not True:
            findings.append(f"{table}: auth_uid_policy_required must be true")
        if not _string_list(spec.get("owner_fields")):
            findings.append(f"{table}: owner_fields required")
        grants = set(_string_list(spec.get("authenticated_grants")))
        if not grants:
            findings.append(f"{table}: authenticated_grants required")
        if table in UPDATE_CAPABLE_TABLES and spec.get("update_with_check_required") is not True:
            findings.append(f"{table}: update_with_check_required must be true")
        if table in APPEND_ONLY_TABLES:
            if spec.get("append_only") is not True:
                findings.append(f"{table}: append_only must be true")
            if grants.intersection({"update", "delete"}):
                findings.append(f"{table}: append-only table must not grant authenticated update/delete")
    secret = specs.get("integration_secret_metadata", {})
    if secret.get("plaintext_secret_allowed") is not False:
        findings.append("integration_secret_metadata.plaintext_secret_allowed must be false")
    payment = specs.get("payment_evidence", {})
    if payment.get("raw_source_persisted") is not False:
        findings.append("payment_evidence.raw_source_persisted must be false")
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
        print("membership Supabase migration review gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print(f"membership Supabase migration review gate: PASS ({args.packet})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

