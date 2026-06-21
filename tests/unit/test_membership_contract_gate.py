from __future__ import annotations

import copy

from scripts.membership_contract_gate import load_contract, validate_contract


def test_membership_contract_gate_accepts_current_contract():
    contract = load_contract()
    assert validate_contract(contract) == []


def test_membership_contract_gate_requires_rls_for_tenant_tables():
    contract = load_contract()
    broken = copy.deepcopy(contract)
    broken["entities"][0]["rls_required"] = False

    findings = validate_contract(broken)

    assert any("profiles: tenant-owned entity must require RLS" in finding for finding in findings)


def test_membership_contract_gate_rejects_plaintext_secret_contract():
    contract = load_contract()
    broken = copy.deepcopy(contract)
    for entity in broken["entities"]:
        if entity["name"] == "integration_secrets":
            entity["plaintext_allowed"] = True
            break

    findings = validate_contract(broken)

    assert "integration_secrets.plaintext_allowed must be false" in findings
