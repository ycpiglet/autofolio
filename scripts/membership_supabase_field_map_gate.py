"""Validate the membership Supabase staging field map.

This gate checks local JSON only. It must not connect to Supabase, create
migrations, edit schema.sql, read secrets, call payment/bank APIs, or deploy.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIELD_MAP = REPO_ROOT / "agents" / "project" / "MEMBERSHIP-SUPABASE-STAGING-FIELD-MAP.json"

REQUIRED_SOURCE_CONTRACTS = {
    "agents/project/MEMBERSHIP-PRODUCTION-CONTRACT.json",
    "agents/project/MEMBERSHIP-TENANT-ISOLATION-MATRIX.json",
    "agents/project/MEMBERSHIP-PAYMENT-EVIDENCE-POLICY.json",
    "agents/project/MEMBERSHIP-PRODUCTION-SECRET-POLICY.json",
    "agents/project/MEMBERSHIP-ENGINE-SAFETY-CONTRACT.json",
}

REQUIRED_ENTITIES = {
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

FORBIDDEN_TOP_LEVEL_KEYS = {
    "applied_migration",
    "ddl",
    "migration_sql",
    "production_apply_completed",
    "schema_sql_updated",
    "supabase_project_id",
    "service_role_key",
    "secret_key",
}


def load_field_map(path: Path = DEFAULT_FIELD_MAP) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("field map root must be an object")
    return data


def validate_field_map(field_map: dict[str, Any]) -> list[str]:
    findings: list[str] = []

    forbidden = FORBIDDEN_TOP_LEVEL_KEYS.intersection(field_map)
    if forbidden:
        findings.append(f"forbidden migration/apply keys present: {sorted(forbidden)}")

    if field_map.get("$schema") != "autofolio.membership-supabase-staging-field-map/v1":
        findings.append("unexpected or missing field map schema")

    status = str(field_map.get("status", ""))
    if "not_applied" not in status:
        findings.append("field map status must clearly state it is not applied")

    non_goals = " ".join(_string_list(field_map.get("non_goals")))
    for required in ("No SQL migration", "No app/database/schema.sql", "No Supabase project"):
        if required not in non_goals:
            findings.append(f"non_goals must include boundary: {required}")

    sources = set(_string_list(field_map.get("source_contracts")))
    missing_sources = REQUIRED_SOURCE_CONTRACTS - sources
    if missing_sources:
        findings.append(f"missing source contracts: {sorted(missing_sources)}")

    docs_checked = field_map.get("supabase_docs_checked")
    if not isinstance(docs_checked, dict):
        findings.append("supabase_docs_checked must be an object")
    else:
        items = " ".join(_string_list(docs_checked.get("changelog_items")))
        for marker in ("Data/API exposure", "TO authenticated", "auth.uid()", "WITH CHECK", "service key", "user_metadata"):
            if marker not in items:
                findings.append(f"supabase_docs_checked missing marker: {marker}")

    invariants = " ".join(_string_list(field_map.get("global_invariants")))
    for marker in ("RLS enabled", "TO authenticated", "auth.uid()", "WITH CHECK", "user_metadata", "service keys", "Data API"):
        if marker not in invariants:
            findings.append(f"global_invariants missing marker: {marker}")

    data_api = field_map.get("data_api_access_model")
    if not isinstance(data_api, dict):
        findings.append("data_api_access_model must be an object")
    else:
        if data_api.get("anon") != "no tenant table grants; public pre-auth routes use backend APIs only":
            findings.append("data_api_access_model.anon must forbid tenant table grants")
        if data_api.get("default_for_tenant_tables") != "not_exposed_until_rls_and_grants_reviewed":
            findings.append("tenant tables must not be exposed before RLS/grant review")
        order = _string_list(data_api.get("grant_order"))
        if "enable RLS" not in order or "run security and performance advisors" not in order:
            findings.append("grant_order must include RLS before advisor review")

    entities = field_map.get("entities")
    if not isinstance(entities, list):
        findings.append("entities must be a list")
        return findings

    by_table = {entity.get("table"): entity for entity in entities if isinstance(entity, dict)}
    missing_entities = REQUIRED_ENTITIES - set(by_table)
    if missing_entities:
        findings.append(f"missing entities: {sorted(missing_entities)}")

    for table, entity in by_table.items():
        if entity.get("rls_required") is not True:
            findings.append(f"{table}: rls_required must be true")
        if not entity.get("owner_field"):
            findings.append(f"{table}: owner_field is required")
        if "auth.users" not in str(entity.get("auth_reference", "")):
            findings.append(f"{table}: auth_reference must reference auth.users")

        table_data_api = entity.get("data_api")
        if not isinstance(table_data_api, dict):
            findings.append(f"{table}: data_api must be an object")
        else:
            if table_data_api.get("anon") != "none":
                findings.append(f"{table}: anon Data API access must be none")
            if not _string_list(table_data_api.get("authenticated")):
                findings.append(f"{table}: authenticated grants must be explicit")

        policies = entity.get("policies")
        if not isinstance(policies, list) or not policies:
            findings.append(f"{table}: policies must be a non-empty list")
            continue

        for policy in policies:
            if not isinstance(policy, dict):
                findings.append(f"{table}: policy entries must be objects")
                continue
            name = str(policy.get("name", ""))
            operation = str(policy.get("operation", ""))
            if not name.startswith(f"{table}_"):
                findings.append(f"{table}: policy name must start with table name")
            if policy.get("to") != "authenticated":
                findings.append(f"{table}.{name}: policy must use TO authenticated")
            if operation in {"select", "update", "delete"} and "auth.uid()" not in str(policy.get("using", "")):
                findings.append(f"{table}.{name}: {operation} policy must use auth.uid() ownership")
            if operation in {"insert", "update"} and "auth.uid()" not in str(policy.get("with_check", "")):
                findings.append(f"{table}.{name}: {operation} policy must include WITH CHECK auth.uid() ownership")
            if operation == "update" and not policy.get("using"):
                findings.append(f"{table}.{name}: update policy must include USING")

    for table in ("approval_events", "order_intents", "order_logs", "execution_logs", "audit_events"):
        entity = by_table.get(table, {})
        if entity.get("append_only") is not True:
            findings.append(f"{table}: append_only must be true")
        data_api = entity.get("data_api", {})
        if isinstance(data_api, dict) and any(op in _string_list(data_api.get("authenticated")) for op in ("update", "delete")):
            findings.append(f"{table}: append-only table must not grant authenticated update/delete")

    secret = by_table.get("integration_secret_metadata", {})
    if secret.get("plaintext_secret_allowed") is not False:
        findings.append("integration_secret_metadata.plaintext_secret_allowed must be false")

    payment = by_table.get("payment_evidence", {})
    if payment.get("raw_source_persisted") is not False:
        findings.append("payment_evidence.raw_source_persisted must be false")

    tests = field_map.get("required_staging_tests")
    if not isinstance(tests, list):
        findings.append("required_staging_tests must be a list")
    else:
        test_ids = {item.get("id") for item in tests if isinstance(item, dict)}
        missing_tests = REQUIRED_TESTS - test_ids
        if missing_tests:
            findings.append(f"missing staging tests: {sorted(missing_tests)}")

    checklist = " ".join(_string_list(field_map.get("advisor_checklist")))
    for marker in ("security advisors", "performance advisors", "Data API table exposure"):
        if marker not in checklist:
            findings.append(f"advisor_checklist missing marker: {marker}")

    blockers = " ".join(_string_list(field_map.get("launch_blockers_remaining")))
    for marker in ("No staging migration", "No staging Supabase schema/RLS apply", "No advisor output"):
        if marker not in blockers:
            findings.append(f"launch_blockers_remaining missing marker: {marker}")

    return findings


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--field-map", type=Path, default=DEFAULT_FIELD_MAP)
    parser.add_argument("--check", action="store_true", help="validate and return non-zero on findings")
    args = parser.parse_args()

    field_map = load_field_map(args.field_map)
    findings = validate_field_map(field_map)
    if findings:
        print("membership Supabase field map gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print(f"membership Supabase field map gate: PASS ({args.field_map})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
