"""Validate the membership production contract asset.

This gate checks the local design contract only. It must not connect to
Supabase, apply migrations, read secrets, or deploy anything.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = REPO_ROOT / "agents" / "project" / "MEMBERSHIP-PRODUCTION-CONTRACT.json"

REQUIRED_ENTITIES = {
    "profiles",
    "membership_requests",
    "deposit_instructions",
    "approval_events",
    "subscription_grants",
    "integration_secrets",
    "portfolio_accounts",
    "holdings_snapshots",
    "risk_settings",
    "engine_state",
    "order_intents",
    "audit_events",
}

REQUIRED_INVARIANTS = {
    "tenant_rows_have_user_id",
    "rls_enabled_for_tenant_tables",
    "self_access_uses_auth_uid",
    "owner_admin_is_server_audited",
    "secret_values_never_return",
    "service_key_never_client",
    "payment_evidence_minimized",
    "engine_state_is_user_scoped",
    "recommendation_claims_are_compliance_gated",
}

REQUIRED_LAUNCH_GATES = {
    "staging_supabase_project_created",
    "schema_migration_reviewed_and_applied_in_staging",
    "rls_enabled_on_all_tenant_owned_tables",
    "tenant_isolation_tests_pass",
    "service_or_secret_key_server_only",
    "secret_rotation_and_deletion_policy_verified",
    "payment_evidence_retention_policy_approved",
    "per_user_engine_safety_contract_implemented",
    "kis_terms_and_compliance_review_recorded",
    "staging_deploy_smoke_passed",
}

FORBIDDEN_TOP_LEVEL_KEYS = {
    "applied_migration",
    "ddl",
    "migration_sql",
    "production_apply_completed",
    "supabase_project_id",
}


def load_contract(path: Path = DEFAULT_CONTRACT) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("contract root must be an object")
    return data


def validate_contract(contract: dict[str, Any]) -> list[str]:
    findings: list[str] = []

    missing_top_level = FORBIDDEN_TOP_LEVEL_KEYS.intersection(contract)
    if missing_top_level:
        findings.append(f"forbidden production-apply keys present: {sorted(missing_top_level)}")

    if contract.get("$schema") != "autofolio.membership-production-contract/v1":
        findings.append("unexpected or missing contract schema")

    status = str(contract.get("status", ""))
    if "not_applied" not in status:
        findings.append("contract status must clearly state it is not applied")

    launch_gate = contract.get("launch_gate")
    if not isinstance(launch_gate, dict):
        findings.append("launch_gate must be an object")
    else:
        if launch_gate.get("can_launch_without_all_passed") is not False:
            findings.append("launch_gate.can_launch_without_all_passed must be false")
        gates = set(_string_list(launch_gate.get("required_before_external_users")))
        missing = REQUIRED_LAUNCH_GATES - gates
        if missing:
            findings.append(f"missing launch gates: {sorted(missing)}")

    client_exposure = contract.get("client_exposure")
    if not isinstance(client_exposure, dict):
        findings.append("client_exposure must be an object")
    else:
        if client_exposure.get("service_role_or_secret_key") != "forbidden":
            findings.append("service role or secret key must be forbidden in browser/client exposure")
        if client_exposure.get("raw_provider_tokens") != "forbidden":
            findings.append("raw provider tokens must be forbidden in client exposure")

    admin_ops = contract.get("admin_operations")
    if not isinstance(admin_ops, dict):
        findings.append("admin_operations must be an object")
    else:
        if admin_ops.get("server_only") is not True:
            findings.append("admin operations must be server_only")
        if admin_ops.get("audited") is not True:
            findings.append("admin operations must be audited")

    invariant_ids = {
        item.get("id")
        for item in contract.get("security_invariants", [])
        if isinstance(item, dict)
    }
    missing_invariants = REQUIRED_INVARIANTS - invariant_ids
    if missing_invariants:
        findings.append(f"missing security invariants: {sorted(missing_invariants)}")

    entities = contract.get("entities")
    if not isinstance(entities, list):
        findings.append("entities must be a list")
        return findings

    by_name = {entity.get("name"): entity for entity in entities if isinstance(entity, dict)}
    missing_entities = REQUIRED_ENTITIES - set(by_name)
    if missing_entities:
        findings.append(f"missing entities: {sorted(missing_entities)}")

    for name, entity in by_name.items():
        if entity.get("tenant_owned") is True:
            if not entity.get("user_id_field"):
                findings.append(f"{name}: tenant-owned entity must define user_id_field")
            if entity.get("references_auth_users") is not True:
                findings.append(f"{name}: tenant-owned entity must reference auth.users")
            if entity.get("rls_required") is not True:
                findings.append(f"{name}: tenant-owned entity must require RLS")
            policies = _string_list(entity.get("member_policies"))
            if not any("auth.uid()" in policy for policy in policies):
                findings.append(f"{name}: member policies must include auth.uid() ownership check")

    for name in ("approval_events", "order_intents", "audit_events"):
        entity = by_name.get(name, {})
        if entity.get("append_only") is not True:
            findings.append(f"{name}: append_only must be true")

    secrets = by_name.get("integration_secrets", {})
    if secrets.get("plaintext_allowed") is not False:
        findings.append("integration_secrets.plaintext_allowed must be false")
    if secrets.get("response_redaction_required") is not True:
        findings.append("integration_secrets.response_redaction_required must be true")

    deposit = by_name.get("deposit_instructions", {})
    if deposit.get("plaintext_bank_account_allowed_in_repo") is not False:
        findings.append("deposit_instructions must forbid plaintext bank account data in repo")

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
        print("membership contract gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print(f"membership contract gate: PASS ({args.contract})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
