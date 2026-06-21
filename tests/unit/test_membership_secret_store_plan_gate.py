from __future__ import annotations

import copy

from scripts.membership_secret_store_plan_gate import load_plan, validate_plan


def test_membership_secret_store_plan_gate_accepts_current_plan():
    plan = load_plan()
    assert validate_plan(plan) == []


def test_membership_secret_store_plan_gate_rejects_implemented_candidate():
    plan = load_plan()
    broken = copy.deepcopy(plan)
    broken["candidate_stores"][0]["production_status"] = "implemented"

    findings = validate_plan(broken)

    assert any("production_status cannot be implemented" in finding for finding in findings)


def test_membership_secret_store_plan_gate_rejects_plaintext_provider_response():
    plan = load_plan()
    broken = copy.deepcopy(plan)
    broken["provider_category_map"][0]["plaintext_response_allowed"] = True

    findings = validate_plan(broken)

    assert any("plaintext_response_allowed must be false" in finding for finding in findings)


def test_membership_secret_store_plan_gate_requires_delete_test():
    plan = load_plan()
    broken = copy.deepcopy(plan)
    broken["required_staging_tests"] = [
        item for item in broken["required_staging_tests"] if item != "secret_delete_removes_payload_reference"
    ]

    findings = validate_plan(broken)

    assert any("secret_delete_removes_payload_reference" in finding for finding in findings)


def test_membership_secret_store_plan_gate_rejects_forbidden_raw_key_name():
    plan = load_plan()
    broken = copy.deepcopy(plan)
    broken["secret_value"] = "placeholder"

    findings = validate_plan(broken)

    assert any("forbidden secret/production keys present" in finding for finding in findings)
