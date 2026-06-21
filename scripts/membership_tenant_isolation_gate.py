"""Validate the membership tenant-isolation matrix.

This gate checks local JSON only. It must not connect to Supabase, apply SQL,
read secrets, call providers, or deploy anything.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MATRIX = REPO_ROOT / "agents" / "project" / "MEMBERSHIP-TENANT-ISOLATION-MATRIX.json"

REQUIRED_ROUTE_GROUPS = {
    "public_pre_auth",
    "app_user_self_service",
    "app_user_product_read",
    "owner_admin",
    "engine_worker",
}

REQUIRED_SURFACES = {
    "membership_requests",
    "deposit_instructions",
    "approval_events",
    "subscription_grants",
    "integration_records",
    "profiles",
    "acknowledgements",
    "portfolio_accounts",
    "holdings_snapshots",
    "analysis_reports",
    "engine_state",
    "risk_settings",
    "order_intents",
    "audit_events",
    "public_reference_data",
}

REQUIRED_INVARIANTS = {
    "jwt_user_id_source",
    "no_request_body_user_scope",
    "rls_on_tenant_tables",
    "no_client_side_filter_security",
    "owner_cross_tenant_server_audited",
    "service_key_server_only",
    "secrets_write_only",
    "engine_safety_user_scoped",
    "applicant_lookup_non_disclosure",
    "market_reference_data_separated",
}

REQUIRED_TEST_CASES = {
    "anon_no_product_read",
    "guest_no_product_read",
    "member_a_cannot_read_member_b",
    "member_cannot_admin",
    "owner_admin_events_audited",
    "secret_response_redacted",
    "engine_state_scoped",
    "applicant_lookup_requires_contact",
}

TENANT_DATA_CLASSES = {
    "tenant_private",
    "tenant_financial",
    "tenant_product",
    "tenant_control",
    "tenant_secret_metadata",
    "tenant_trading",
    "tenant_audit",
}

FORBIDDEN_TOP_LEVEL_KEYS = {
    "applied_migration",
    "ddl",
    "migration_sql",
    "production_apply_completed",
    "supabase_project_id",
    "service_role_key",
}


def load_matrix(path: Path = DEFAULT_MATRIX) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("matrix root must be an object")
    return data


def validate_matrix(matrix: dict[str, Any]) -> list[str]:
    findings: list[str] = []

    forbidden = FORBIDDEN_TOP_LEVEL_KEYS.intersection(matrix)
    if forbidden:
        findings.append(f"forbidden production/apply keys present: {sorted(forbidden)}")

    if matrix.get("$schema") != "autofolio.membership-tenant-isolation-matrix/v1":
        findings.append("unexpected or missing matrix schema")

    status = str(matrix.get("status", ""))
    if "not_applied" not in status:
        findings.append("matrix status must clearly state it is not applied")

    boundaries = matrix.get("boundaries")
    if not isinstance(boundaries, dict):
        findings.append("boundaries must be an object")
    else:
        for key in (
            "not_applied_to_supabase",
            "no_sql_migration",
            "no_secret_values",
            "no_external_network_action_required",
            "keeps_can_launch_false",
        ):
            if boundaries.get(key) is not True:
                findings.append(f"boundaries.{key} must be true")

    route_groups = matrix.get("route_groups")
    if not isinstance(route_groups, list):
        findings.append("route_groups must be a list")
    else:
        group_ids = {item.get("id") for item in route_groups if isinstance(item, dict)}
        missing = REQUIRED_ROUTE_GROUPS - group_ids
        if missing:
            findings.append(f"missing route groups: {sorted(missing)}")

    surfaces = matrix.get("surfaces")
    if not isinstance(surfaces, list):
        findings.append("surfaces must be a list")
        return findings

    by_id = {item.get("id"): item for item in surfaces if isinstance(item, dict)}
    missing_surfaces = REQUIRED_SURFACES - set(by_id)
    if missing_surfaces:
        findings.append(f"missing surfaces: {sorted(missing_surfaces)}")

    for surface_id, surface in by_id.items():
        data_class = surface.get("data_class")
        is_tenant = data_class in TENANT_DATA_CLASSES
        if is_tenant:
            if not surface.get("production_owner_field"):
                findings.append(f"{surface_id}: tenant surface must define production_owner_field")
            if surface.get("references_auth_users") is not True:
                findings.append(f"{surface_id}: tenant surface must reference auth.users")
            if surface.get("rls_required") is not True:
                findings.append(f"{surface_id}: tenant surface must require RLS")
            member_policy = str(surface.get("member_policy", ""))
            if "auth.uid()" not in member_policy:
                findings.append(f"{surface_id}: member_policy must include auth.uid() ownership")
            current_status = str(surface.get("current_status", ""))
            if current_status == "production_ready":
                findings.append(f"{surface_id}: matrix cannot mark production_ready")

    for surface_id in ("approval_events", "order_intents", "audit_events"):
        surface = by_id.get(surface_id, {})
        if surface.get("append_only") is not True:
            findings.append(f"{surface_id}: append_only must be true")

    integration = by_id.get("integration_records", {})
    if integration.get("raw_secret_response_allowed") is not False:
        findings.append("integration_records.raw_secret_response_allowed must be false")

    public_ref = by_id.get("public_reference_data", {})
    if public_ref.get("rls_required") is not False:
        findings.append("public_reference_data.rls_required must be false")
    if public_ref.get("production_owner_field") is not None:
        findings.append("public_reference_data must not define production_owner_field")

    invariant_ids = {
        item.get("id")
        for item in matrix.get("security_invariants", [])
        if isinstance(item, dict)
    }
    missing_invariants = REQUIRED_INVARIANTS - invariant_ids
    if missing_invariants:
        findings.append(f"missing security invariants: {sorted(missing_invariants)}")

    verification = matrix.get("verification_required")
    if not isinstance(verification, dict):
        findings.append("verification_required must be an object")
    else:
        local_gate = str(verification.get("local_matrix_gate", ""))
        if "membership_tenant_isolation_gate.py --check" not in local_gate:
            findings.append("verification_required.local_matrix_gate must reference this gate")
        test_ids = {
            item.get("id")
            for item in verification.get("required_test_cases", [])
            if isinstance(item, dict)
        }
        missing_tests = REQUIRED_TEST_CASES - test_ids
        if missing_tests:
            findings.append(f"missing required test cases: {sorted(missing_tests)}")

    blockers = matrix.get("launch_blockers_remaining")
    if not _string_list(blockers):
        findings.append("launch_blockers_remaining must list remaining blockers")

    return findings


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--check", action="store_true", help="validate and return non-zero on findings")
    args = parser.parse_args()

    matrix = load_matrix(args.matrix)
    findings = validate_matrix(matrix)
    if findings:
        print("membership tenant isolation gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print(f"membership tenant isolation gate: PASS ({args.matrix})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
