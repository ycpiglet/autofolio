from __future__ import annotations

import copy

from scripts.promotion_dry_run_audit_preview_gate import load_preview, validate_preview


def _preview() -> dict:
    return load_preview()


def test_current_preview_passes():
    assert validate_preview(_preview()) == []


def test_rejects_source_hash_mismatch():
    preview = _preview()
    preview["source_inputs"][0]["sha256"] = "0" * 64

    findings = validate_preview(preview)

    assert any("sha256 mismatch" in finding for finding in findings)


def test_rejects_preview_source_hash_mismatch():
    preview = _preview()
    preview["preview_record"]["source_hash"] = "0" * 64

    findings = validate_preview(preview)

    assert any("source_hash does not match source_artifact" in finding for finding in findings)


def test_rejects_external_network_call():
    preview = _preview()
    preview["preview_record"]["external_network_calls"] = True

    findings = validate_preview(preview)

    assert any("external_network_calls must be false" in finding for finding in findings)


def test_rejects_forbidden_token_key():
    preview = _preview()
    preview["preview_record"]["access_token"] = "placeholder"

    findings = validate_preview(preview)

    assert any("forbidden secret/customer/live key names" in finding for finding in findings)


def test_rejects_missing_owner_boundary():
    preview = _preview()
    preview["preview_record"]["owner_approval_required_for_live"] = False

    findings = validate_preview(preview)

    assert any("owner_approval_required_for_live must be true" in finding for finding in findings)


def test_rejects_forbidden_copy_phrase():
    preview = _preview()
    preview["preview_record"]["preview_text"] = "Autofolio provides guaranteed returns."

    findings = validate_preview(preview)

    assert any("guaranteed returns" in finding for finding in findings)


def test_rejects_unknown_channel():
    preview = copy.deepcopy(_preview())
    preview["preview_record"]["channel_id"] = "unknown_channel"

    findings = validate_preview(preview)

    assert any("channel_id not found" in finding for finding in findings)
