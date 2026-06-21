from __future__ import annotations

import copy

from scripts.membership_staging_deploy_preflight_gate import load_checklist, validate_checklist


def test_membership_staging_deploy_preflight_gate_accepts_current_checklist():
    checklist = load_checklist()
    assert validate_checklist(checklist) == []


def test_membership_staging_deploy_preflight_gate_rejects_deployed_status():
    checklist = load_checklist()
    broken = copy.deepcopy(checklist)
    broken["status"] = "deployed"

    findings = validate_checklist(broken)

    assert any("not deployed" in finding for finding in findings)


def test_membership_staging_deploy_preflight_gate_requires_repo_blockers():
    checklist = load_checklist()
    broken = copy.deepcopy(checklist)
    broken["repo_state_findings"] = [
        item
        for item in broken["repo_state_findings"]
        if item["id"] != "env_inventory_template_created_external_env_write_blocked"
    ]

    findings = validate_checklist(broken)

    assert any("env_inventory_template_created_external_env_write_blocked" in finding for finding in findings)


def test_membership_staging_deploy_preflight_gate_requires_railway_readiness():
    checklist = load_checklist()
    broken = copy.deepcopy(checklist)
    broken["repo_state_findings"] = [
        item
        for item in broken["repo_state_findings"]
        if item["id"] != "railway_backend_port_binding_ready_external_deploy_blocked"
    ]

    findings = validate_checklist(broken)

    assert any("railway_backend_port_binding_ready_external_deploy_blocked" in finding for finding in findings)


def test_membership_staging_deploy_preflight_gate_requires_storage_decision():
    checklist = load_checklist()
    broken = copy.deepcopy(checklist)
    broken["repo_state_findings"] = [
        item
        for item in broken["repo_state_findings"]
        if item["id"] != "persistent_storage_decision_recorded_implementation_blocked"
    ]

    findings = validate_checklist(broken)

    assert any("persistent_storage_decision_recorded_implementation_blocked" in finding for finding in findings)


def test_membership_staging_deploy_preflight_gate_requires_supabase_review_packet():
    checklist = load_checklist()
    broken = copy.deepcopy(checklist)
    broken["repo_state_findings"] = [
        item
        for item in broken["repo_state_findings"]
        if item["id"] != "supabase_migration_review_packet_recorded_apply_blocked"
    ]

    findings = validate_checklist(broken)

    assert any("supabase_migration_review_packet_recorded_apply_blocked" in finding for finding in findings)


def test_membership_staging_deploy_preflight_gate_requires_kis_terms_packet():
    checklist = load_checklist()
    broken = copy.deepcopy(checklist)
    broken["repo_state_findings"] = [
        item
        for item in broken["repo_state_findings"]
        if item["id"] != "kis_terms_review_packet_recorded_clearance_blocked"
    ]

    findings = validate_checklist(broken)

    assert any("kis_terms_review_packet_recorded_clearance_blocked" in finding for finding in findings)


def test_membership_staging_deploy_preflight_gate_rejects_real_kis_staging_value():
    checklist = load_checklist()
    broken = copy.deepcopy(checklist)
    for item in broken["environment_inventory_placeholders"]:
        if item["id"] == "backend_kis_env":
            item["required_staging_value"] = "paper"

    findings = validate_checklist(broken)

    assert any("backend_kis_env.required_staging_value must be mock" in finding for finding in findings)


def test_membership_staging_deploy_preflight_gate_requires_railway_port_placeholder():
    checklist = load_checklist()
    broken = copy.deepcopy(checklist)
    for service in broken["services"]:
        if service["id"] == "railway_backend":
            service["required_env_placeholders"] = [
                item for item in service["required_env_placeholders"] if item != "PORT"
            ]

    findings = validate_checklist(broken)

    assert any("railway_backend must include PORT placeholder" in finding for finding in findings)


def test_membership_staging_deploy_preflight_gate_rejects_forbidden_secret_key_name():
    checklist = load_checklist()
    broken = copy.deepcopy(checklist)
    broken["vercel_token"] = "placeholder"

    findings = validate_checklist(broken)

    assert any("forbidden deploy/secret/value keys present" in finding for finding in findings)
