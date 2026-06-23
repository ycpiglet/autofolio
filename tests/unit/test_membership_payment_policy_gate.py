from __future__ import annotations

import copy

from scripts.membership_payment_policy_gate import load_policy, validate_policy


def test_membership_payment_policy_gate_accepts_current_policy():
    policy = load_policy()
    assert validate_policy(policy) == []


def test_membership_payment_policy_gate_rejects_raw_source_persistence():
    policy = load_policy()
    broken = copy.deepcopy(policy)
    broken["allowed_evidence_sources"][0]["raw_source_persisted"] = True

    findings = validate_policy(broken)

    assert any("raw_source_persisted must be false" in finding for finding in findings)


def test_membership_payment_policy_gate_requires_redaction_rules():
    policy = load_policy()
    broken = copy.deepcopy(policy)
    broken["redaction_rules"] = []

    findings = validate_policy(broken)

    assert any("missing redaction rules" in finding for finding in findings)
