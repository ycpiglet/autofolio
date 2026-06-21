from __future__ import annotations

import copy

from scripts.promotion_asset_review_queue_audit_preview_gate import load_preview, validate_preview


def _preview() -> dict:
    return load_preview()


def test_current_preview_passes():
    assert validate_preview(_preview()) == []


def test_rejects_source_hash_mismatch():
    preview = _preview()
    preview["source_inputs"][0]["sha256"] = "0" * 64

    findings = validate_preview(preview)

    assert any("sha256 mismatch" in finding for finding in findings)


def test_rejects_missing_boundary():
    preview = _preview()
    preview["boundaries"]["not_publication_approval"] = False

    findings = validate_preview(preview)

    assert any("boundaries.not_publication_approval must be true" in finding for finding in findings)


def test_rejects_summary_count_drift():
    preview = _preview()
    preview["audit_summary"]["public_use_blocked_items"] = 3

    findings = validate_preview(preview)

    assert any("audit_summary.public_use_blocked_items must be 4" in finding for finding in findings)


def test_rejects_missing_queue_item_summary():
    preview = copy.deepcopy(_preview())
    preview["queue_item_summaries"] = [
        item for item in preview["queue_item_summaries"] if item["queue_item_id"] != "review-queue-sns-text-bundle-source"
    ]

    findings = validate_preview(preview)

    assert any("queue_item_summaries missing queue items" in finding for finding in findings)


def test_rejects_public_use_unblocked():
    preview = _preview()
    preview["queue_item_summaries"][0]["public_use_blocked"] = False

    findings = validate_preview(preview)

    assert any("public_use_blocked must be true" in finding for finding in findings)


def test_rejects_scan_not_blocked_all():
    preview = _preview()
    preview["blocked_action_scan"]["sns_upload"]["blocked_all"] = False

    findings = validate_preview(preview)

    assert any("blocked_action_scan.sns_upload.blocked_all must be true" in finding for finding in findings)


def test_rejects_scan_match():
    preview = _preview()
    preview["blocked_action_scan"]["external_action"]["matches"] = ["platform_api_call_enabled"]

    findings = validate_preview(preview)

    assert any("blocked_action_scan.external_action.matches must be empty" in finding for finding in findings)


def test_rejects_forbidden_customer_key():
    preview = _preview()
    preview["queue_item_summaries"][0]["customer_email"] = "test@example.invalid"

    findings = validate_preview(preview)

    assert any("forbidden export/customer/secret/final-advice key names" in finding for finding in findings)


def test_rejects_live_platform_flag():
    preview = _preview()
    preview["audit_summary"]["platform_api_call_enabled"] = True

    findings = validate_preview(preview)

    assert any("public/export/customer/payment/platform/final-advice flags must not be true" in finding for finding in findings)
