from __future__ import annotations

import copy

from scripts.promotion_asset_preview_manifest_gate import load_manifest, validate_manifest


def _manifest() -> dict:
    return load_manifest()


def test_current_manifest_passes():
    assert validate_manifest(_manifest()) == []


def test_rejects_source_hash_mismatch():
    manifest = _manifest()
    manifest["source_inputs"][0]["sha256"] = "0" * 64

    findings = validate_manifest(manifest)

    assert any("sha256 mismatch" in finding for finding in findings)


def test_rejects_preview_source_hash_mismatch():
    manifest = _manifest()
    manifest["asset_previews"][0]["source_hash"] = "0" * 64

    findings = validate_manifest(manifest)

    assert any("source_hash mismatch" in finding for finding in findings)


def test_rejects_final_export_enabled():
    manifest = _manifest()
    manifest["asset_previews"][0]["final_export_enabled"] = True

    findings = validate_manifest(manifest)

    assert any("final_export_enabled must be false" in finding for finding in findings)


def test_rejects_public_export_unblocked():
    manifest = _manifest()
    manifest["asset_previews"][0]["public_export_blocked"] = False

    findings = validate_manifest(manifest)

    assert any("public_export_blocked must be true" in finding for finding in findings)


def test_rejects_forbidden_public_url_output():
    manifest = _manifest()
    manifest["manifest_outputs"]["public_url"] = "https://example.invalid/autofolio"

    findings = validate_manifest(manifest)

    assert any("manifest_outputs.public_url must be null" in finding for finding in findings)


def test_rejects_forbidden_secret_key():
    manifest = _manifest()
    manifest["asset_previews"][0]["access_token"] = "placeholder"

    findings = validate_manifest(manifest)

    assert any("forbidden export/customer/secret key names" in finding for finding in findings)


def test_rejects_missing_owner_boundary():
    manifest = _manifest()
    manifest["asset_previews"][0]["owner_approval_status"] = "not_required"

    findings = validate_manifest(manifest)

    assert any("owner_approval_status must require Owner approval" in finding for finding in findings)


def test_rejects_missing_required_target():
    manifest = copy.deepcopy(_manifest())
    manifest["asset_previews"] = [
        item for item in manifest["asset_previews"] if item["target_id"] != "pptx_deck_source"
    ]

    findings = validate_manifest(manifest)

    assert any("asset_previews missing" in finding for finding in findings)


def test_rejects_forbidden_copy_phrase():
    manifest = _manifest()
    manifest["asset_previews"][0]["preview_snapshot"] = ["Autofolio provides guaranteed returns."]

    findings = validate_manifest(manifest)

    assert any("guaranteed returns" in finding for finding in findings)
