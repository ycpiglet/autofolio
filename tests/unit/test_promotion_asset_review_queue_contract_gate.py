from __future__ import annotations

import copy

from scripts.promotion_asset_review_queue_contract_gate import load_contract, validate_contract


def _contract() -> dict:
    return load_contract()


def test_current_contract_passes():
    assert validate_contract(_contract()) == []


def test_rejects_source_hash_mismatch():
    contract = _contract()
    contract["source_inputs"][0]["sha256"] = "0" * 64

    findings = validate_contract(contract)

    assert any("sha256 mismatch" in finding for finding in findings)


def test_rejects_missing_required_queue_field():
    contract = _contract()
    contract["queue_record_contract"]["required_fields"].remove("public_use_blocked")

    findings = validate_contract(contract)

    assert any("required_fields missing" in finding for finding in findings)


def test_rejects_live_action_state():
    contract = _contract()
    contract["queue_record_contract"]["allowed_states"][0]["live_action"] = True

    findings = validate_contract(contract)

    assert any("live_action must be false" in finding for finding in findings)


def test_rejects_forbidden_live_state_name():
    contract = _contract()
    contract["queue_record_contract"]["allowed_states"].append(
        {
            "id": "approved_for_publication",
            "kind": "approval",
            "terminal": False,
            "live_action": False,
            "allowed_next": [],
        }
    )

    findings = validate_contract(contract)

    assert any("forbidden live/public state" in finding for finding in findings)


def test_rejects_missing_queue_target():
    contract = copy.deepcopy(_contract())
    contract["queue_items"] = [
        item for item in contract["queue_items"] if item["target_id"] != "sns_text_bundle_source"
    ]

    findings = validate_contract(contract)

    assert any("queue_items missing targets" in finding for finding in findings)


def test_rejects_public_use_unblocked():
    contract = _contract()
    contract["queue_items"][0]["public_use_blocked"] = False

    findings = validate_contract(contract)

    assert any("public_use_blocked must be true" in finding for finding in findings)


def test_rejects_forbidden_public_url_key():
    contract = _contract()
    contract["queue_items"][0]["public_url"] = "https://example.invalid/autofolio"

    findings = validate_contract(contract)

    assert any("forbidden export/customer/secret/final-advice key names" in finding for finding in findings)


def test_rejects_final_export_path_output():
    contract = _contract()
    contract["queue_outputs"]["final_pptx_path"] = "dist/final.pptx"

    findings = validate_contract(contract)

    assert any("forbidden export/customer/secret/final-advice key names" in finding for finding in findings)


def test_rejects_live_platform_flag():
    contract = _contract()
    contract["queue_items"][0]["platform_api_call_enabled"] = True

    findings = validate_contract(contract)

    assert any("public/export/customer/payment/platform/final-advice flags must not be true" in finding for finding in findings)
