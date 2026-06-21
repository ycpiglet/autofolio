from __future__ import annotations

import copy

from scripts.promotion_asset_owner_decision_evidence_freshness_contract_gate import (
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


def test_rejects_missing_actual_evidence_boundary():
    contract = _contract()
    contract["boundaries"]["not_actual_approval_evidence_collection"] = False

    findings = validate_contract(contract)

    assert any("boundaries.not_actual_approval_evidence_collection must be true" in finding for finding in findings)


def test_rejects_summary_stale_trigger_count_drift():
    contract = _contract()
    contract["freshness_summary"]["total_stale_evidence_trigger_items"] = 26

    findings = validate_contract(contract)

    assert any("freshness_summary.total_stale_evidence_trigger_items must be 27" in finding for finding in findings)


def test_rejects_missing_freshness_record():
    contract = copy.deepcopy(_contract())
    contract["freshness_records"] = [
        item for item in contract["freshness_records"] if item["decision_type"] != "paid_ads"
    ]

    findings = validate_contract(contract)

    assert any("freshness_records missing decision types" in finding for finding in findings)


def test_rejects_actual_approval_evidence_collected():
    contract = _contract()
    contract["freshness_records"][0]["actual_approval_evidence_collected"] = True

    findings = validate_contract(contract)

    assert any("approval/public/export/customer/payment/platform/final-advice/live flags must not be true" in finding for finding in findings)


def test_rejects_action_permitted():
    contract = _contract()
    contract["freshness_records"][0]["action_permitted_now"] = True

    findings = validate_contract(contract)

    assert any("approval/public/export/customer/payment/platform/final-advice/live flags must not be true" in finding for finding in findings)


def test_rejects_state_live_action():
    contract = _contract()
    contract["freshness_states"][0]["live_action"] = True

    findings = validate_contract(contract)

    assert any("approval/public/export/customer/payment/platform/final-advice/live flags must not be true" in finding for finding in findings)


def test_rejects_missing_refresh_trigger():
    contract = copy.deepcopy(_contract())
    contract["refresh_state_map"] = [
        item for item in contract["refresh_state_map"] if item["trigger_id"] != "blocked_action_scan_change"
    ]

    findings = validate_contract(contract)

    assert any("refresh_state_map missing triggers" in finding for finding in findings)


def test_rejects_unknown_refresh_state_target():
    contract = _contract()
    contract["refresh_state_map"][0]["target_refresh_state"] = "approved_for_public_use"

    findings = validate_contract(contract)

    assert any("target_refresh_state must be a known freshness state" in finding for finding in findings)


def test_rejects_stale_trigger_count_mismatch():
    contract = _contract()
    contract["freshness_records"][0]["stale_trigger_to_refresh_state"] = contract["freshness_records"][0]["stale_trigger_to_refresh_state"][:2]

    findings = validate_contract(contract)

    assert any("stale_trigger_to_refresh_state count must match source preview" in finding for finding in findings)


def test_rejects_missing_source_hash_invalidating_event():
    contract = _contract()
    contract["freshness_records"][0]["invalidating_events"] = ["blocked_action_scan_change"]

    findings = validate_contract(contract)

    assert any("invalidating_events must include source_preview_hash_change" in finding for finding in findings)


def test_rejects_scan_match():
    contract = _contract()
    contract["blocked_action_scan"]["approval_evidence_collection"]["matches"] = ["actual_approval_evidence_collected"]

    findings = validate_contract(contract)

    assert any("blocked_action_scan.approval_evidence_collection.matches must be empty" in finding for finding in findings)


def test_rejects_forbidden_approval_key():
    contract = _contract()
    contract["freshness_records"][0]["owner_signature_file"] = "signed"

    findings = validate_contract(contract)

    assert any("forbidden approval/export/customer/secret/final-advice key names" in finding for finding in findings)


def test_rejects_live_platform_flag():
    contract = _contract()
    contract["freshness_summary"]["platform_api_call_enabled"] = True

    findings = validate_contract(contract)

    assert any("approval/public/export/customer/payment/platform/final-advice/live flags must not be true" in finding for finding in findings)
