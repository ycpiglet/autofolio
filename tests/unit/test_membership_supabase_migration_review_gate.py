from __future__ import annotations

import copy

from scripts.membership_supabase_migration_review_gate import load_packet, validate_packet


def test_membership_supabase_migration_review_gate_accepts_current_packet():
    packet = load_packet()
    assert validate_packet(packet) == []


def test_membership_supabase_migration_review_gate_rejects_applied_status():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    broken["status"] = "applied"

    findings = validate_packet(broken)

    assert any("not migration and not applied" in finding for finding in findings)


def test_membership_supabase_migration_review_gate_rejects_sql_payload_key():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    broken["migration_sql"] = "placeholder"

    findings = validate_packet(broken)

    assert any("forbidden migration/apply/secret keys present" in finding for finding in findings)


def test_membership_supabase_migration_review_gate_requires_update_with_check():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    for spec in broken["table_review_specs"]:
        if spec["table"] == "risk_settings":
            spec["update_with_check_required"] = False

    findings = validate_packet(broken)

    assert any("risk_settings: update_with_check_required must be true" in finding for finding in findings)


def test_membership_supabase_migration_review_gate_rejects_append_only_update_grant():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    for spec in broken["table_review_specs"]:
        if spec["table"] == "order_logs":
            spec["authenticated_grants"].append("update")

    findings = validate_packet(broken)

    assert any("order_logs: append-only table must not grant authenticated update/delete" in finding for finding in findings)


def test_membership_supabase_migration_review_gate_requires_cross_user_test():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    broken["required_cross_user_tests"] = [
        item for item in broken["required_cross_user_tests"] if item != "member_a_cannot_read_member_b"
    ]

    findings = validate_packet(broken)

    assert any("member_a_cannot_read_member_b" in finding for finding in findings)

