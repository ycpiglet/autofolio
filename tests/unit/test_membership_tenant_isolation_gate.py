from __future__ import annotations

import copy

from scripts.membership_tenant_isolation_gate import load_matrix, validate_matrix


def test_membership_tenant_isolation_gate_accepts_current_matrix():
    matrix = load_matrix()
    assert validate_matrix(matrix) == []


def test_membership_tenant_isolation_gate_requires_rls_for_tenant_surfaces():
    matrix = load_matrix()
    broken = copy.deepcopy(matrix)
    for surface in broken["surfaces"]:
        if surface["id"] == "portfolio_accounts":
            surface["rls_required"] = False
            break

    findings = validate_matrix(broken)

    assert "portfolio_accounts: tenant surface must require RLS" in findings


def test_membership_tenant_isolation_gate_rejects_role_only_member_policy():
    matrix = load_matrix()
    broken = copy.deepcopy(matrix)
    for surface in broken["surfaces"]:
        if surface["id"] == "membership_requests":
            surface["member_policy"] = "select for authenticated users"
            break

    findings = validate_matrix(broken)

    assert "membership_requests: member_policy must include auth.uid() ownership" in findings


def test_membership_tenant_isolation_gate_rejects_plaintext_secret_response():
    matrix = load_matrix()
    broken = copy.deepcopy(matrix)
    for surface in broken["surfaces"]:
        if surface["id"] == "integration_records":
            surface["raw_secret_response_allowed"] = True
            break

    findings = validate_matrix(broken)

    assert "integration_records.raw_secret_response_allowed must be false" in findings
