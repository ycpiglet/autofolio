from __future__ import annotations

import copy

from scripts.promotion_asset_owner_decision_evidence_checklist_gate import load_contract, validate_contract


def _contract() -> dict:
    return load_contract()


def test_current_contract_passes():
    assert validate_contract(_contract()) == []


def test_rejects_source_hash_mismatch():
    contract = _contract()
    contract["source_inputs"][0]["sha256"] = "0" * 64

    findings = validate_contract(contract)

    assert any("sha256 mismatch" in finding for finding in findings)


def test_rejects_missing_actual_evidence_boundary():
    contract = _contract()
    contract["boundaries"]["not_actual_approval_evidence_collection"] = False

    findings = validate_contract(contract)

    assert any("boundaries.not_actual_approval_evidence_collection must be true" in finding for finding in findings)


def test_rejects_summary_actual_evidence_count_drift():
    contract = _contract()
    contract["checklist_summary"]["actual_approval_evidence_records"] = 1

    findings = validate_contract(contract)

    assert any("checklist_summary.actual_approval_evidence_records must be 0" in finding for finding in findings)


def test_rejects_missing_required_contract_field():
    contract = copy.deepcopy(_contract())
    contract["checklist_contract"]["required_fields"].remove("actual_approval_evidence_collected")

    findings = validate_contract(contract)

    assert any("checklist_contract.required_fields missing" in finding for finding in findings)


def test_rejects_missing_checklist_item():
    contract = copy.deepcopy(_contract())
    contract["checklist_items"] = [
        item for item in contract["checklist_items"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_contract(contract)

    assert any("checklist_items missing decision types" in finding for finding in findings)


def test_rejects_actual_approval_evidence_collected():
    contract = _contract()
    contract["checklist_items"][0]["actual_approval_evidence_collected"] = True

    findings = validate_contract(contract)

    assert any("approval/public/export/customer/payment/platform/final-advice flags must not be true" in finding for finding in findings)


def test_rejects_item_action_permitted():
    contract = _contract()
    contract["checklist_items"][0]["action_permitted_now"] = True

    findings = validate_contract(contract)

    assert any("approval/public/export/customer/payment/platform/final-advice flags must not be true" in finding for finding in findings)


def test_rejects_public_use_unblocked():
    contract = _contract()
    contract["checklist_items"][0]["public_use_blocked"] = False

    findings = validate_contract(contract)

    assert any("public_use_blocked must be true" in finding for finding in findings)


def test_rejects_evidence_count_mismatch():
    contract = copy.deepcopy(_contract())
    contract["checklist_items"][0]["required_evidence"] = contract["checklist_items"][0]["required_evidence"][:1]

    findings = validate_contract(contract)

    assert any("required_evidence must match source evidence gap count" in finding for finding in findings)


def test_rejects_missing_stale_trigger():
    contract = _contract()
    contract["checklist_items"][0]["stale_evidence_triggers"] = []

    findings = validate_contract(contract)

    assert any("stale_evidence_triggers must be non-empty" in finding for finding in findings)


def test_rejects_forbidden_approval_key():
    contract = _contract()
    contract["checklist_items"][0]["owner_signature_file"] = "signed"

    findings = validate_contract(contract)

    assert any("forbidden approval/export/customer/secret/final-advice key names" in finding for finding in findings)


def test_rejects_live_platform_flag():
    contract = _contract()
    contract["checklist_summary"]["platform_api_call_enabled"] = True

    findings = validate_contract(contract)

    assert any("approval/public/export/customer/payment/platform/final-advice flags must not be true" in finding for finding in findings)
