from __future__ import annotations

import copy

from scripts.membership_staging_storage_decision_gate import load_packet, validate_packet


def test_membership_staging_storage_decision_gate_accepts_current_packet():
    packet = load_packet()
    assert validate_packet(packet) == []


def test_membership_staging_storage_decision_gate_rejects_local_vault_source_of_truth():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    for option in broken["options"]:
        if option["id"] == "local_encrypted_vault":
            option["tenant_source_of_truth"] = True

    findings = validate_packet(broken)

    assert any("local_encrypted_vault cannot be tenant source of truth" in finding for finding in findings)


def test_membership_staging_storage_decision_gate_requires_supabase_selection():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    broken["decision_summary"]["selected_external_staging_source_of_truth"] = "railway_volume"

    findings = validate_packet(broken)

    assert any("select supabase_postgres_auth_rls" in finding for finding in findings)


def test_membership_staging_storage_decision_gate_rejects_railway_volume_tenant_data():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    for option in broken["options"]:
        if option["id"] == "railway_volume":
            option["tenant_source_of_truth"] = True

    findings = validate_packet(broken)

    assert any("railway_volume cannot be tenant source of truth" in finding for finding in findings)


def test_membership_staging_storage_decision_gate_requires_cross_user_test():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    broken["required_staging_tests"] = [
        item
        for item in broken["required_staging_tests"]
        if item != "cross_user_membership_request_read_blocked"
    ]

    findings = validate_packet(broken)

    assert any("cross_user_membership_request_read_blocked" in finding for finding in findings)


def test_membership_staging_storage_decision_gate_rejects_forbidden_storage_key():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    broken["database_url"] = "placeholder"

    findings = validate_packet(broken)

    assert any("forbidden deploy/storage/secret keys present" in finding for finding in findings)

