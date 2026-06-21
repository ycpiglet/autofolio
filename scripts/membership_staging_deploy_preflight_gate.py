"""Validate the membership staging deploy preflight checklist.

This gate checks local checklist structure only. It must not deploy, create or
mutate external platform projects, write environment variables, read secrets,
apply Supabase migrations, publish URLs, or activate KIS/payment providers.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHECKLIST = (
    REPO_ROOT
    / "agents"
    / "project"
    / "MEMBERSHIP-STAGING-DEPLOY-PREFLIGHT-CHECKLIST.json"
)

REQUIRED_BOUNDARIES = {
    "not_deployed",
    "no_external_project_mutation",
    "no_env_var_write",
    "no_public_url_publish",
    "no_supabase_project_mutation",
    "no_migration_apply",
    "no_secret_read_or_write",
    "no_kis_credential_activation",
    "no_bank_or_payment_api",
    "keeps_can_launch_false",
}

REQUIRED_SOURCE_MARKERS = {
    "Vercel",
    "Railway",
    "Supabase",
    "KIS",
    "environment",
    "healthcheck",
    "RLS",
}

REQUIRED_REPO_FINDINGS = {
    "env_inventory_template_created_external_env_write_blocked",
    "railway_backend_port_binding_ready_external_deploy_blocked",
    "supabase_migration_review_packet_recorded_apply_blocked",
    "persistent_storage_decision_recorded_implementation_blocked",
    "kis_terms_review_packet_recorded_clearance_blocked",
    "payment_external_boundaries_blocked",
}

REQUIRED_SERVICES = {
    "vercel_frontend",
    "railway_backend",
    "supabase_staging",
}

REQUIRED_LOCAL_CHECKS = {
    "python scripts/membership_staging_deploy_preflight_gate.py --check",
    "python scripts/membership_staging_env_inventory_gate.py --check",
    "python scripts/membership_railway_backend_readiness_gate.py --check",
    "python scripts/membership_staging_storage_decision_gate.py --check",
    "python scripts/membership_supabase_migration_review_gate.py --check",
    "python scripts/membership_supabase_apply_evidence_gate.py --check",
    "python scripts/membership_kis_terms_review_gate.py --check",
    "python scripts/membership_contract_gate.py --check",
    "python scripts/membership_supabase_field_map_gate.py --check",
    "python scripts/membership_secret_store_plan_gate.py --check",
    "python scripts/membership_payment_recognition_decision_gate.py --check",
    "python scripts/check_agent_docs.py",
}

REQUIRED_SMOKE_TESTS = {
    "frontend_loads_login",
    "frontend_proxy_health",
    "public_signup_intake_safe",
    "guest_and_autoregister_fail_closed",
    "readiness_can_launch_false",
    "no_order_or_kis_activation",
    "no_secret_or_payment_disclosure",
    "persistent_storage_source_of_truth",
}

REQUIRED_ROLLBACK = {
    "vercel_preview_only",
    "railway_healthcheck_blocks_bad_release",
    "no_db_migration_without_rollback",
    "env_change_reversal",
    "kill_switch_and_mock_default",
}

REQUIRED_LAUNCH_GATES = {
    "preflight_gate_passes",
    "repo_state_blockers_resolved_or_waived_by_owner",
    "local_backend_health_passes",
    "web_lint_and_build_pass",
    "vercel_preview_or_custom_staging_target_selected",
    "railway_backend_port_and_healthcheck_reviewed",
    "persistent_storage_decision_gate_passes",
    "migration_rls_review_packet_gate_passes",
    "apply_evidence_checklist_gate_passes",
    "kis_terms_review_packet_gate_passes",
    "supabase_staging_project_and_migration_reviewed",
    "secret_store_not_plaintext_and_not_repo",
    "payment_and_kis_external_boundaries_remain_blocked",
    "staging_smoke_plan_passes",
    "rollback_plan_recorded",
    "can_launch_remains_false_until_r3_evidence",
}

FORBIDDEN_KEY_NAMES = {
    "vercel_token",
    "railway_token",
    "supabase_access_token",
    "supabase_service_role_key",
    "kis_app_key",
    "kis_app_secret",
    "bank_account_number",
    "secret_value",
    "plaintext_secret",
    "production_apply_completed",
    "deployment_url",
    "public_url",
    "environment_value",
}


def load_checklist(path: Path = DEFAULT_CHECKLIST) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("preflight checklist root must be an object")
    return data


def validate_checklist(checklist: dict[str, Any]) -> list[str]:
    findings: list[str] = []

    forbidden_paths = list(_find_forbidden_keys(checklist))
    if forbidden_paths:
        findings.append(f"forbidden deploy/secret/value keys present: {forbidden_paths}")

    if checklist.get("$schema") != "autofolio.membership-staging-deploy-preflight-checklist/v1":
        findings.append("unexpected or missing preflight checklist schema")

    status = str(checklist.get("status", ""))
    if "not_deployed" not in status:
        findings.append("checklist status must clearly state it is not deployed")

    boundaries = checklist.get("boundaries")
    if not isinstance(boundaries, dict):
        findings.append("boundaries must be an object")
    else:
        for key in REQUIRED_BOUNDARIES:
            if boundaries.get(key) is not True:
                findings.append(f"boundaries.{key} must be true")

    source_text = " ".join(
        item.get("id", "") + " " + item.get("authority", "") + " " + item.get("url", "") + " " + item.get("note", "")
        for item in checklist.get("source_basis", [])
        if isinstance(item, dict)
    )
    for marker in REQUIRED_SOURCE_MARKERS:
        if marker.lower() not in source_text.lower():
            findings.append(f"source_basis missing marker: {marker}")

    findings.extend(_validate_repo_findings(checklist.get("repo_state_findings")))
    findings.extend(_validate_services(checklist.get("services")))
    findings.extend(_validate_environment_inventory(checklist.get("environment_inventory_placeholders")))

    missing_local_checks = REQUIRED_LOCAL_CHECKS - set(_string_list(checklist.get("required_local_checks")))
    if missing_local_checks:
        findings.append(f"missing required local checks: {sorted(missing_local_checks)}")

    smoke_ids = {
        item.get("id")
        for item in checklist.get("required_staging_smoke_plan", [])
        if isinstance(item, dict)
    }
    missing_smoke = REQUIRED_SMOKE_TESTS - smoke_ids
    if missing_smoke:
        findings.append(f"missing staging smoke tests: {sorted(missing_smoke)}")

    rollback_ids = {
        item.get("id")
        for item in checklist.get("rollback_plan", [])
        if isinstance(item, dict)
    }
    missing_rollback = REQUIRED_ROLLBACK - rollback_ids
    if missing_rollback:
        findings.append(f"missing rollback plan items: {sorted(missing_rollback)}")

    missing_gates = REQUIRED_LAUNCH_GATES - set(_string_list(checklist.get("launch_gates")))
    if missing_gates:
        findings.append(f"missing launch gates: {sorted(missing_gates)}")

    forbidden_runtime = " ".join(_string_list(checklist.get("forbidden_actions")))
    for marker in ("deploy", "environment variable", "Supabase migrations", "secrets", "KIS", "can_launch"):
        if marker not in forbidden_runtime:
            findings.append(f"forbidden_actions missing marker: {marker}")

    verification = checklist.get("verification")
    if not isinstance(verification, dict):
        findings.append("verification must be an object")
    else:
        if "membership_staging_deploy_preflight_gate.py --check" not in str(
            verification.get("local_preflight_gate", "")
        ):
            findings.append("verification.local_preflight_gate must reference this gate")

    return findings


def _validate_repo_findings(value: Any) -> list[str]:
    findings: list[str] = []
    if not isinstance(value, list):
        return ["repo_state_findings must be a list"]
    finding_map = {item.get("id"): item for item in value if isinstance(item, dict)}
    missing = REQUIRED_REPO_FINDINGS - set(finding_map)
    if missing:
        findings.append(f"missing repo state findings: {sorted(missing)}")
    for finding_id, item in finding_map.items():
        if item.get("state") not in {"block_actual_deploy", "block_external_user_launch"}:
            findings.append(f"{finding_id}: state must block actual deploy or external user launch")
        if not item.get("required_before_deploy"):
            findings.append(f"{finding_id}: required_before_deploy is required")
    return findings


def _validate_services(value: Any) -> list[str]:
    findings: list[str] = []
    if not isinstance(value, list):
        return ["services must be a list"]
    service_map = {item.get("id"): item for item in value if isinstance(item, dict)}
    missing = REQUIRED_SERVICES - set(service_map)
    if missing:
        findings.append(f"missing services: {sorted(missing)}")
    for service_id, service in service_map.items():
        status = str(service.get("deploy_status", ""))
        if "not" not in status and "not_deployed" not in status:
            findings.append(f"{service_id}: deploy_status must remain not deployed/not mutated")
        checks = set(_string_list(service.get("preflight_checks")))
        if not checks:
            findings.append(f"{service_id}: preflight_checks are required")
    railway = service_map.get("railway_backend")
    if railway:
        if railway.get("healthcheck_path") != "/api/health":
            findings.append("railway_backend.healthcheck_path must be /api/health")
        if "PORT" not in _string_list(railway.get("required_env_placeholders")):
            findings.append("railway_backend must include PORT placeholder")
    return findings


def _validate_environment_inventory(value: Any) -> list[str]:
    findings: list[str] = []
    if not isinstance(value, list):
        return ["environment_inventory_placeholders must be a list"]
    for item in value:
        if not isinstance(item, dict):
            continue
        item_id = item.get("id", "<unknown>")
        if item.get("value_allowed_in_repo") is not False:
            findings.append(f"{item_id}: value_allowed_in_repo must be false")
        if item.get("id") == "backend_kis_env" and item.get("required_staging_value") != "mock":
            findings.append("backend_kis_env.required_staging_value must be mock")
        if item.get("id") == "backend_membership_bank_placeholders" and item.get("secret") is not True:
            findings.append("backend_membership_bank_placeholders must be secret")
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
    parser.add_argument("--checklist", type=Path, default=DEFAULT_CHECKLIST)
    parser.add_argument("--check", action="store_true", help="validate and return non-zero on findings")
    args = parser.parse_args()

    checklist = load_checklist(args.checklist)
    findings = validate_checklist(checklist)
    if findings:
        print("membership staging deploy preflight gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print(f"membership staging deploy preflight gate: PASS ({args.checklist})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
