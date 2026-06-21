from __future__ import annotations

from scripts.promotion_asset_rendering_contract_gate import load_contract, validate_contract


def _contract() -> dict:
    return load_contract()


def test_current_contract_passes():
    assert validate_contract(_contract()) == []


def test_rejects_source_hash_mismatch():
    contract = _contract()
    contract["source_inputs"][0]["sha256"] = "0" * 64

    findings = validate_contract(contract)

    assert any("sha256 mismatch" in finding for finding in findings)


def test_rejects_final_export_enabled():
    contract = _contract()
    contract["render_targets"][0]["final_export_enabled"] = True

    findings = validate_contract(contract)

    assert any("final_export_enabled must be false" in finding for finding in findings)


def test_rejects_public_export_enabled():
    contract = _contract()
    contract["render_targets"][0]["public_export_enabled"] = True

    findings = validate_contract(contract)

    assert any("public_export_enabled must be false" in finding for finding in findings)


def test_rejects_forbidden_final_pdf_path_key():
    contract = _contract()
    contract["render_queue_contract"]["final_pdf_path"] = "dist/final.pdf"

    findings = validate_contract(contract)

    assert any("forbidden export/customer/secret key names" in finding for finding in findings)


def test_rejects_missing_required_target():
    contract = _contract()
    contract["render_targets"] = [
        item for item in contract["render_targets"] if item["target_id"] != "pptx_deck_source"
    ]

    findings = validate_contract(contract)

    assert any("render_targets missing" in finding for finding in findings)


def test_rejects_missing_owner_review():
    contract = _contract()
    contract["render_targets"][0]["review_required"] = ["Marketing Growth", "Compliance Officer"]

    findings = validate_contract(contract)

    assert any("Owner before" in finding for finding in findings)


def test_rejects_missing_task_133_handoff():
    contract = _contract()
    contract["allowed_next_local_slices"] = []

    findings = validate_contract(contract)

    assert any("allowed_next_local_slices must be a non-empty list" in finding for finding in findings)
