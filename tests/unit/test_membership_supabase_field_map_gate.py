from __future__ import annotations

import copy

from scripts.membership_supabase_field_map_gate import load_field_map, validate_field_map


def test_membership_supabase_field_map_gate_accepts_current_map():
    field_map = load_field_map()
    assert validate_field_map(field_map) == []


def test_membership_supabase_field_map_gate_rejects_anon_tenant_access():
    field_map = load_field_map()
    broken = copy.deepcopy(field_map)
    broken["entities"][0]["data_api"]["anon"] = ["select"]

    findings = validate_field_map(broken)

    assert any("profiles: anon Data API access must be none" in finding for finding in findings)


def test_membership_supabase_field_map_gate_requires_update_with_check():
    field_map = load_field_map()
    broken = copy.deepcopy(field_map)
    for policy in broken["entities"][0]["policies"]:
        if policy["operation"] == "update":
            policy.pop("with_check")
            break

    findings = validate_field_map(broken)

    assert any("profiles.profiles_update_own: update policy must include WITH CHECK auth.uid() ownership" in finding for finding in findings)


def test_membership_supabase_field_map_gate_rejects_plaintext_secret_metadata():
    field_map = load_field_map()
    broken = copy.deepcopy(field_map)
    for entity in broken["entities"]:
        if entity["table"] == "integration_secret_metadata":
            entity["plaintext_secret_allowed"] = True
            break

    findings = validate_field_map(broken)

    assert "integration_secret_metadata.plaintext_secret_allowed must be false" in findings


def test_membership_supabase_field_map_gate_rejects_missing_cross_user_test():
    field_map = load_field_map()
    broken = copy.deepcopy(field_map)
    broken["required_staging_tests"] = [
        item for item in broken["required_staging_tests"] if item["id"] != "member_a_cannot_read_member_b"
    ]

    findings = validate_field_map(broken)

    assert any("member_a_cannot_read_member_b" in finding for finding in findings)
