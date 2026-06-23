from __future__ import annotations

import copy

from scripts.promotion_asset_generator_readiness_map_gate import (
    load_readiness_map,
    validate_readiness_map,
)


def _readiness_map() -> dict:
    return load_readiness_map()


def test_current_readiness_map_passes():
    assert validate_readiness_map(_readiness_map()) == []


def test_rejects_source_hash_mismatch():
    readiness_map = _readiness_map()
    readiness_map["source_inputs"][0]["sha256"] = "0" * 64

    findings = validate_readiness_map(readiness_map)

    assert any("sha256 mismatch" in finding for finding in findings)


def test_rejects_missing_required_source():
    readiness_map = copy.deepcopy(_readiness_map())
    readiness_map["source_inputs"] = [
        item for item in readiness_map["source_inputs"] if item["id"] != "promotion_asset_preview_manifest"
    ]

    findings = validate_readiness_map(readiness_map)

    assert any("source_inputs missing ids" in finding for finding in findings)


def test_rejects_missing_required_surface():
    readiness_map = copy.deepcopy(_readiness_map())
    readiness_map["asset_surfaces"] = [
        item for item in readiness_map["asset_surfaces"] if item["target_id"] != "pptx_deck_source"
    ]

    findings = validate_readiness_map(readiness_map)

    assert any("asset_surfaces missing" in finding for finding in findings)


def test_rejects_surface_source_hash_drift():
    readiness_map = _readiness_map()
    readiness_map["asset_surfaces"][0]["source_sha256"] = "0" * 64

    findings = validate_readiness_map(readiness_map)

    assert any("source_sha256" in finding and "mismatch" in finding for finding in findings)


def test_rejects_final_export_enabled():
    readiness_map = _readiness_map()
    readiness_map["asset_surfaces"][0]["final_export_enabled"] = True

    findings = validate_readiness_map(readiness_map)

    assert any("final_export_enabled must be false" in finding for finding in findings)


def test_rejects_external_action_tooling():
    readiness_map = _readiness_map()
    readiness_map["tooling_readiness"][0]["external_action_enabled"] = True

    findings = validate_readiness_map(readiness_map)

    assert any("external_action_enabled must be false" in finding for finding in findings)


def test_rejects_missing_owner_review():
    readiness_map = _readiness_map()
    readiness_map["asset_surfaces"][0]["required_reviews"] = ["Marketing Growth", "Compliance Officer"]

    findings = validate_readiness_map(readiness_map)

    assert any("Owner/R3 before final or public use" in finding for finding in findings)


def test_rejects_forbidden_secret_key():
    readiness_map = _readiness_map()
    readiness_map["asset_surfaces"][0]["access_token"] = "placeholder"

    findings = validate_readiness_map(readiness_map)

    assert any("forbidden export/customer/secret key names" in finding for finding in findings)


def test_rejects_missing_blocked_output():
    readiness_map = copy.deepcopy(_readiness_map())
    readiness_map["forbidden_outputs"] = [
        item for item in readiness_map["forbidden_outputs"] if item != "SNS upload"
    ]

    findings = validate_readiness_map(readiness_map)

    assert any("forbidden_outputs missing" in finding for finding in findings)


def test_rejects_missing_r3_future_task():
    readiness_map = copy.deepcopy(_readiness_map())
    readiness_map["future_implementation_tasks"] = [
        item for item in readiness_map["future_implementation_tasks"] if item["reversibility_level"] != "R3"
    ]

    findings = validate_readiness_map(readiness_map)

    assert any("must include at least one R3" in finding for finding in findings)


def test_rejects_final_asset_export_approval_flag():
    readiness_map = _readiness_map()
    readiness_map["taskset_handoff"]["final_asset_export_approved"] = True

    findings = validate_readiness_map(readiness_map)

    assert any("taskset_handoff.final_asset_export_approved must be false" in finding for finding in findings)
