from __future__ import annotations

import copy

from scripts.promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_candidate_gate import (
    load_contract,
    validate_contract,
)


def _contract() -> dict:
    return load_contract()


def test_current_contract_passes():
    assert validate_contract(_contract()) == []


def test_rejects_source_hash_mismatch():
    contract = _contract()
    contract["source_inputs"][0]["sha256"] = "0" * 64

    findings = validate_contract(contract)

    assert any("sha256 mismatch" in finding for finding in findings)


def test_rejects_missing_packet_candidate_not_approval_boundary():
    contract = _contract()
    contract["boundaries"]["packet_candidate_not_approval"] = False

    findings = validate_contract(contract)

    assert any("boundaries.packet_candidate_not_approval must be true" in finding for finding in findings)


def test_rejects_summary_packet_candidate_record_drift():
    contract = _contract()
    contract["contract_summary"]["packet_candidate_records"] = 8

    findings = validate_contract(contract)

    assert any("contract_summary.packet_candidate_records must be 9" in finding for finding in findings)


def test_rejects_missing_packet_candidate_record():
    contract = copy.deepcopy(_contract())
    contract["packet_candidate_records"] = [
        item for item in contract["packet_candidate_records"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_contract(contract)

    assert any("packet_candidate_records missing decision types" in finding for finding in findings)


def test_rejects_actual_refresh_executed():
    contract = _contract()
    contract["packet_candidate_records"][0]["actual_refresh_executed"] = True

    findings = validate_contract(contract)

    assert any(
        "refresh/approval/signature/public/export/customer/payment/platform/final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_actual_owner_approval_recorded():
    contract = _contract()
    contract["packet_candidate_records"][0]["actual_owner_approval_recorded"] = True

    findings = validate_contract(contract)

    assert any(
        "refresh/approval/signature/public/export/customer/payment/platform/final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_actual_owner_signature_collected():
    contract = _contract()
    contract["packet_candidate_records"][0]["actual_owner_signature_collected"] = True

    findings = validate_contract(contract)

    assert any(
        "refresh/approval/signature/public/export/customer/payment/platform/final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_packet_is_approval():
    contract = _contract()
    contract["packet_candidate_records"][0]["packet_is_approval"] = True

    findings = validate_contract(contract)

    assert any(
        "refresh/approval/signature/public/export/customer/payment/platform/final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_public_use_approved():
    contract = _contract()
    contract["packet_candidate_records"][0]["public_use_approved"] = True

    findings = validate_contract(contract)

    assert any(
        "refresh/approval/signature/public/export/customer/payment/platform/final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_missing_evidence_bundle_reference():
    contract = copy.deepcopy(_contract())
    contract["evidence_bundle_references"] = [
        item for item in contract["evidence_bundle_references"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_contract(contract)

    assert any("evidence_bundle_references missing decision types" in finding for finding in findings)


def test_rejects_evidence_required_count_mismatch():
    contract = _contract()
    contract["evidence_bundle_references"][0]["required_evidence_count"] = 99

    findings = validate_contract(contract)

    assert any("required_evidence_count must match source preview" in finding for finding in findings)


def test_rejects_missing_owner_decision_prompt():
    contract = copy.deepcopy(_contract())
    contract["owner_decision_prompt_map"] = [
        item for item in contract["owner_decision_prompt_map"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_contract(contract)

    assert any("owner_decision_prompt_map missing decision types" in finding for finding in findings)


def test_rejects_prompt_candidate_is_approval():
    contract = _contract()
    contract["owner_decision_prompt_map"][0]["candidate_is_approval"] = True

    findings = validate_contract(contract)

    assert any(
        "refresh/approval/signature/public/export/customer/payment/platform/final-advice/live flags must not be true"
        in finding
        for finding in findings
    )


def test_rejects_missing_unresolved_blocker():
    contract = copy.deepcopy(_contract())
    contract["unresolved_blocker_map"] = [
        item for item in contract["unresolved_blocker_map"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_contract(contract)

    assert any("unresolved_blocker_map missing decision types" in finding for finding in findings)


def test_rejects_blocked_scan_match():
    contract = _contract()
    contract["blocked_action_scan"]["owner_signature"]["matches"] = ["actual_owner_signature_collected"]

    findings = validate_contract(contract)

    assert any("blocked_action_scan.owner_signature.matches must be empty" in finding for finding in findings)


def test_rejects_forbidden_signature_key():
    contract = _contract()
    contract["packet_candidate_records"][0]["owner_signature_file"] = "signed"

    findings = validate_contract(contract)

    assert any(
        "forbidden refresh/approval/signature/export/customer/secret/final-advice key names" in finding
        for finding in findings
    )


def test_rejects_live_platform_flag():
    contract = _contract()
    contract["contract_summary"]["platform_api_call_enabled"] = True

    findings = validate_contract(contract)

    assert any(
        "refresh/approval/signature/public/export/customer/payment/platform/final-advice/live flags must not be true"
        in finding
        for finding in findings
    )
