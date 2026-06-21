from __future__ import annotations

import copy

from scripts.promotion_asset_owner_review_packet_gate import load_packet, validate_packet


def _packet() -> dict:
    return load_packet()


def test_current_packet_passes():
    assert validate_packet(_packet()) == []


def test_rejects_source_hash_mismatch():
    packet = _packet()
    packet["source_inputs"][0]["sha256"] = "0" * 64

    findings = validate_packet(packet)

    assert any("sha256 mismatch" in finding for finding in findings)


def test_rejects_missing_boundary():
    packet = _packet()
    packet["boundaries"]["not_publication_approval"] = False

    findings = validate_packet(packet)

    assert any("boundaries.not_publication_approval must be true" in finding for finding in findings)


def test_rejects_missing_owner_decision():
    packet = copy.deepcopy(_packet())
    packet["owner_decision_list"] = [
        item for item in packet["owner_decision_list"] if item["decision_id"] != "sns_upload"
    ]

    findings = validate_packet(packet)

    assert any("owner_decision_list missing decisions" in finding for finding in findings)


def test_rejects_decision_action_permitted_now():
    packet = _packet()
    packet["owner_decision_list"][0]["action_permitted_now"] = True

    findings = validate_packet(packet)

    assert any("action_permitted_now must be false" in finding for finding in findings)


def test_rejects_missing_review_item():
    packet = copy.deepcopy(_packet())
    packet["review_items"] = [
        item for item in packet["review_items"] if item["queue_item_id"] != "review-queue-pptx-deck-source"
    ]

    findings = validate_packet(packet)

    assert any("review_items missing queue items" in finding for finding in findings)


def test_rejects_public_use_unblocked():
    packet = _packet()
    packet["review_items"][0]["public_use_blocked"] = False

    findings = validate_packet(packet)

    assert any("public_use_blocked must be true" in finding for finding in findings)


def test_rejects_missing_blocked_action():
    packet = copy.deepcopy(_packet())
    packet["blocked_action_list"] = [
        item for item in packet["blocked_action_list"] if item["action_id"] != "crm_payment"
    ]

    findings = validate_packet(packet)

    assert any("blocked_action_list missing actions" in finding for finding in findings)


def test_rejects_blocked_action_false():
    packet = _packet()
    packet["blocked_action_list"][0]["blocked"] = False

    findings = validate_packet(packet)

    assert any("blocked must be true" in finding for finding in findings)


def test_rejects_forbidden_customer_key():
    packet = _packet()
    packet["review_items"][0]["customer_email"] = "test@example.invalid"

    findings = validate_packet(packet)

    assert any("forbidden export/customer/secret/final-advice key names" in finding for finding in findings)


def test_rejects_live_platform_flag():
    packet = _packet()
    packet["packet_summary"]["platform_api_call_enabled"] = True

    findings = validate_packet(packet)

    assert any("public/export/customer/payment/platform/final-advice flags must not be true" in finding for finding in findings)


def test_rejects_missing_evidence_map():
    packet = copy.deepcopy(_packet())
    packet["evidence_map"] = [
        item for item in packet["evidence_map"] if item["evidence_id"] != "professional_review"
    ]

    findings = validate_packet(packet)

    assert any("evidence_map missing evidence ids" in finding for finding in findings)
