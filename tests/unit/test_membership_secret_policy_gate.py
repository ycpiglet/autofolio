from __future__ import annotations

import copy

from scripts.membership_secret_policy_gate import load_policy, validate_policy


def test_membership_secret_policy_gate_accepts_current_policy():
    policy = load_policy()
    assert validate_policy(policy) == []


def test_membership_secret_policy_gate_rejects_raw_secret_response():
    policy = load_policy()
    broken = copy.deepcopy(policy)
    broken["provider_categories"][0]["raw_secret_response_allowed"] = True

    findings = validate_policy(broken)

    assert any("raw_secret_response_allowed must be false" in finding for finding in findings)


def test_membership_secret_policy_gate_rejects_secret_response_field():
    policy = load_policy()
    broken = copy.deepcopy(policy)
    broken["provider_categories"][0]["response_allowed_fields"].append("secret_value")

    findings = validate_policy(broken)

    assert any("forbidden response fields present" in finding for finding in findings)


def test_membership_secret_policy_gate_requires_lifecycle_audit():
    policy = load_policy()
    broken = copy.deepcopy(policy)
    broken["lifecycle_actions"][0]["audit_required"] = False

    findings = validate_policy(broken)

    assert any("audit_required must be true" in finding for finding in findings)
