"""Validate the membership Supabase staging apply-evidence checklist."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHECKLIST = REPO_ROOT / "agents" / "project" / "MEMBERSHIP-SUPABASE-STAGING-APPLY-EVIDENCE-CHECKLIST.json"

REQUIRED_BOUNDARIES = {
    "checklist_only",
    "no_supabase_connection",
    "no_project_selection_or_mutation",
    "no_migration_file_created",
    "no_sql_apply",
    "no_backup_download_or_restore",
    "no_advisor_execution",
    "no_data_api_grant_change",
    "no_external_env_write",
    "no_secret_values",
    "no_production_data",
    "no_deploy_or_public_url",
    "keeps_can_launch_false",
}

REQUIRED_STAGES = {
    "pre_apply_review",
    "apply_execution",
    "post_apply_security",
    "post_apply_isolation",
    "deploy_smoke_prerequisite",
}

REQUIRED_EVIDENCE_IDS = {
    "owner_selected_staging_project",
    "backup_restore_plan_reviewed",
    "migration_rls_review_packet_passed",
    "rollback_notes_reviewed",
    "external_env_values_ready_outside_repo",
    "approved_migration_created_in_r3_lane",
    "migration_apply_log_captured",
    "migration_status_captured",
    "can_launch_still_false_after_apply",
    "security_advisor_output_captured",
    "performance_advisor_output_captured",
    "data_api_grant_review_captured",
    "service_role_server_only_reviewed",
    "cross_user_membership_request_test_passed",
    "cross_user_integration_metadata_test_passed",
    "anon_tenant_access_test_passed",
    "append_only_order_audit_test_passed",
    "railway_env_written_by_owner",
    "vercel_env_written_by_owner",
    "backend_health_smoke_ready",
    "frontend_proxy_health_smoke_ready",
    "no_real_kis_or_payment_activation",
}

FORBIDDEN_KEY_NAMES = {
    "supabase_project_ref",
    "database_url",
    "migration_sql",
    "apply_completed",
    "backup_file",
    "restore_completed",
    "advisor_output",
    "service_role_key",
    "secret_key",
    "public_url",
    "deployment_url",
}


def load_checklist(path: Path = DEFAULT_CHECKLIST) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("apply evidence checklist root must be an object")
    return data


def validate_checklist(checklist: dict[str, Any]) -> list[str]:
    findings: list[str] = []

    forbidden_paths = _find_forbidden_keys(checklist)
    if forbidden_paths:
        findings.append(f"forbidden apply/backup/secret keys present: {forbidden_paths}")

    if checklist.get("$schema") != "autofolio.membership-supabase-staging-apply-evidence-checklist/v1":
        findings.append("unexpected or missing apply evidence checklist schema")
    if "not_applied" not in str(checklist.get("status", "")):
        findings.append("status must clearly state not applied")

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
    for marker in ("Supabase", "backup", "restore", "advisor"):
        if marker.lower() not in source_text.lower():
            findings.append(f"source_basis missing marker: {marker}")

    stages = checklist.get("evidence_stages")
    stage_ids: set[str] = set()
    stage_evidence: set[str] = set()
    if not isinstance(stages, list):
        findings.append("evidence_stages must be a list")
    else:
        for stage in stages:
            if not isinstance(stage, dict):
                continue
            stage_ids.add(str(stage.get("id", "")))
            evidence = set(_string_list(stage.get("required_evidence_ids")))
            stage_evidence.update(evidence)
            if stage.get("blocks_without_evidence") is not True:
                findings.append(f"{stage.get('id', '<unknown>')}: blocks_without_evidence must be true")
    missing_stages = REQUIRED_STAGES - stage_ids
    if missing_stages:
        findings.append(f"missing evidence stages: {sorted(missing_stages)}")

    required_ids = set(_string_list(checklist.get("required_evidence_ids")))
    missing_ids = REQUIRED_EVIDENCE_IDS - required_ids
    if missing_ids:
        findings.append(f"missing required evidence ids: {sorted(missing_ids)}")
    missing_from_stages = REQUIRED_EVIDENCE_IDS - stage_evidence
    if missing_from_stages:
        findings.append(f"evidence ids not assigned to stages: {sorted(missing_from_stages)}")

    owner_actions = " ".join(_string_list(checklist.get("owner_only_actions")))
    for marker in ("Supabase staging project", "Create/apply", "advisor", "environment", "external user"):
        if marker.lower() not in owner_actions.lower():
            findings.append(f"owner_only_actions missing marker: {marker}")

    forbidden_runtime = " ".join(_string_list(checklist.get("forbidden_actions")))
    for marker in ("Supabase", "migration", "backups", "advisors", "environment variables", "secrets", "can_launch"):
        if marker not in forbidden_runtime:
            findings.append(f"forbidden_actions missing marker: {marker}")

    verification = checklist.get("verification")
    if not isinstance(verification, dict):
        findings.append("verification must be an object")
    elif "membership_supabase_apply_evidence_gate.py --check" not in str(verification.get("local_checklist_gate", "")):
        findings.append("verification.local_checklist_gate must reference this gate")

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
        print("membership Supabase apply evidence gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"membership Supabase apply evidence gate: PASS ({args.checklist})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

