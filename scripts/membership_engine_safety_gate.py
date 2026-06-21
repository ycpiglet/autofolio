"""Validate the membership per-user engine safety contract.

This gate checks local contract structure only. It must not change OrderFlow,
SafetyChecker, KIS brokers, risk gates, production DB, secrets, deployments, or
runtime engine behavior.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = REPO_ROOT / "agents" / "project" / "MEMBERSHIP-ENGINE-SAFETY-CONTRACT.json"

REQUIRED_SURFACES = {
    "engine_state",
    "engine_run_queue",
    "trade_conditions",
    "safety_flags",
    "risk_limits",
    "circuit_breakers",
    "order_intents",
    "order_logs",
    "execution_logs",
    "notifications",
}

APPEND_ONLY_SURFACES = {
    "order_intents",
    "order_logs",
    "execution_logs",
}

REQUIRED_INVARIANTS = {
    "user_id_required_on_runtime_rows",
    "no_global_auto_for_members",
    "per_user_kill_switch",
    "per_user_risk_limits",
    "per_user_engine_queue",
    "order_intent_append_only",
    "order_flow_requires_user_context",
    "kis_credentials_user_scoped",
    "safety_checker_reads_user_scope",
    "circuit_breaker_user_scoped",
    "audit_events_for_admin_override",
    "no_live_execution_before_r3",
}

REQUIRED_CONTEXT_FIELDS = {
    "user_id",
    "broker_context_id",
    "risk_profile_id",
    "engine_queue_item_id",
    "order_intent_id",
    "audit_event_id",
}

REQUIRED_FORBIDDEN_FALLBACKS = {
    "implicit owner user",
    "global auto flag for member execution",
    "global risk limit for member execution",
    "global KIS credential for member execution",
    "request body user_id as authority",
    "client-side tenant filter as security boundary",
}

REQUIRED_FAILURE_BEHAVIOR = {
    "missing user_id blocks execution",
    "missing user-owned KIS credential blocks execution",
    "missing per-user risk limit blocks execution",
    "missing append-only order intent blocks execution",
    "any cross-user mismatch blocks execution and creates audit evidence",
}

REQUIRED_LAUNCH_GATES = {
    "contract_gate_passes",
    "production_schema_user_id_fields",
    "per_user_engine_queue_tests_pass",
    "member_cannot_run_other_user_engine",
    "per_user_kill_switch_tests_pass",
    "risk_limit_isolation_tests_pass",
    "order_intent_append_only_tests_pass",
    "kis_credentials_user_scoped",
    "live_execution_r3_approval_recorded",
    "staging_engine_dry_run_smoke_passed",
}

FORBIDDEN_TOP_LEVEL_KEYS = {
    "order_flow_patch_applied",
    "safety_checker_patch_applied",
    "kis_broker_enabled",
    "risk_gate_relaxed",
    "production_apply_completed",
    "migration_sql",
    "supabase_project_id",
    "secret_value",
}


def load_contract(path: Path = DEFAULT_CONTRACT) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("contract root must be an object")
    return data


def validate_contract(contract: dict[str, Any]) -> list[str]:
    findings: list[str] = []

    forbidden = FORBIDDEN_TOP_LEVEL_KEYS.intersection(contract)
    if forbidden:
        findings.append(f"forbidden runtime/production keys present: {sorted(forbidden)}")

    if contract.get("$schema") != "autofolio.membership-engine-safety-contract/v1":
        findings.append("unexpected or missing contract schema")

    status = str(contract.get("status", ""))
    if "not_applied" not in status:
        findings.append("contract status must clearly state it is not applied")

    boundaries = contract.get("boundaries")
    if not isinstance(boundaries, dict):
        findings.append("boundaries must be an object")
    else:
        for key in (
            "not_applied_to_runtime",
            "no_order_path_change",
            "no_risk_gate_change",
            "no_kis_broker_change",
            "no_schema_migration",
            "no_secret_values",
            "keeps_can_launch_false",
        ):
            if boundaries.get(key) is not True:
                findings.append(f"boundaries.{key} must be true")

    surfaces = contract.get("runtime_surfaces")
    if not isinstance(surfaces, list):
        findings.append("runtime_surfaces must be a list")
    else:
        by_id = {item.get("id"): item for item in surfaces if isinstance(item, dict)}
        missing_surfaces = REQUIRED_SURFACES - set(by_id)
        if missing_surfaces:
            findings.append(f"missing runtime surfaces: {sorted(missing_surfaces)}")
        for surface_id, surface in by_id.items():
            if surface.get("tenant_owned") is not True:
                findings.append(f"{surface_id}: tenant_owned must be true")
            if surface.get("production_owner_field") != "user_id":
                findings.append(f"{surface_id}: production_owner_field must be user_id")
            if surface.get("live_execution_allowed") is not False:
                findings.append(f"{surface_id}: live_execution_allowed must be false")
            if str(surface.get("current_status", "")) == "production_ready":
                findings.append(f"{surface_id}: contract cannot mark production_ready")
            worker_policy = str(surface.get("worker_policy", ""))
            if "user" not in worker_policy.lower() and "user_id" not in worker_policy:
                findings.append(f"{surface_id}: worker_policy must include user context")
        for surface_id in APPEND_ONLY_SURFACES:
            surface = by_id.get(surface_id, {})
            if surface.get("append_only") is not True:
                findings.append(f"{surface_id}: append_only must be true")

    invariant_ids = {
        item.get("id")
        for item in contract.get("safety_invariants", [])
        if isinstance(item, dict)
    }
    missing_invariants = REQUIRED_INVARIANTS - invariant_ids
    if missing_invariants:
        findings.append(f"missing safety invariants: {sorted(missing_invariants)}")

    worker = contract.get("worker_contract")
    if not isinstance(worker, dict):
        findings.append("worker_contract must be an object")
    else:
        missing_context = REQUIRED_CONTEXT_FIELDS - set(_string_list(worker.get("required_context_fields")))
        if missing_context:
            findings.append(f"missing worker context fields: {sorted(missing_context)}")
        missing_fallbacks = REQUIRED_FORBIDDEN_FALLBACKS - set(_string_list(worker.get("forbidden_fallbacks")))
        if missing_fallbacks:
            findings.append(f"missing forbidden fallbacks: {sorted(missing_fallbacks)}")
        missing_failure = REQUIRED_FAILURE_BEHAVIOR - set(_string_list(worker.get("failure_behavior")))
        if missing_failure:
            findings.append(f"missing failure behavior entries: {sorted(missing_failure)}")

    missing_gates = REQUIRED_LAUNCH_GATES - set(_string_list(contract.get("launch_gates")))
    if missing_gates:
        findings.append(f"missing launch gates: {sorted(missing_gates)}")

    verification = contract.get("verification")
    if not isinstance(verification, dict):
        findings.append("verification must be an object")
    else:
        local_gate = str(verification.get("local_contract_gate", ""))
        if "membership_engine_safety_gate.py --check" not in local_gate:
            findings.append("verification.local_contract_gate must reference this gate")

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
        print("membership engine safety gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print(f"membership engine safety gate: PASS ({args.contract})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
