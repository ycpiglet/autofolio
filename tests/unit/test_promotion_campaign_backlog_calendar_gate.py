from __future__ import annotations

import copy

from scripts.promotion_campaign_backlog_calendar_gate import load_packet, validate_packet


def _packet() -> dict:
    return load_packet()


def test_current_packet_passes():
    assert validate_packet(_packet()) == []


def test_rejects_publication_status():
    packet = _packet()
    packet["status"] = "publication_approved"

    findings = validate_packet(packet)

    assert any("draft and not_publication" in finding for finding in findings)


def test_rejects_missing_boundary():
    packet = _packet()
    packet["boundaries"]["no_public_posting"] = False

    findings = validate_packet(packet)

    assert any("boundaries.no_public_posting must be true" in finding for finding in findings)


def test_rejects_missing_campaign_item():
    packet = _packet()
    packet["campaign_backlog"] = [
        item for item in packet["campaign_backlog"] if item["id"] != "sns_draft_bundle"
    ]

    findings = validate_packet(packet)

    assert any("campaign_backlog missing ids" in finding for finding in findings)


def test_rejects_calendar_without_four_weeks():
    packet = _packet()
    packet["content_calendar"] = packet["content_calendar"][:2]

    findings = validate_packet(packet)

    assert any("at least 4 distinct week_index" in finding for finding in findings)


def test_rejects_calendar_live_action():
    packet = _packet()
    packet["content_calendar"][0]["live_action_enabled"] = True

    findings = validate_packet(packet)

    assert any("live or external action flags must not be true" in finding for finding in findings)


def test_rejects_publish_ready_calendar_item():
    packet = _packet()
    packet["content_calendar"][0]["publish_ready"] = True

    findings = validate_packet(packet)

    assert any("live or external action flags must not be true" in finding for finding in findings)


def test_rejects_forbidden_key_name():
    packet = copy.deepcopy(_packet())
    packet["customer_email"] = "none@example.invalid"

    findings = validate_packet(packet)

    assert any("forbidden secret/customer/payment key names" in finding for finding in findings)


def test_rejects_review_required_claim_in_copy_seed():
    packet = _packet()
    packet["campaign_backlog"][0]["copy_seed"] = "Autofolio includes agent recommendation flows for selected users."

    findings = validate_packet(packet)

    assert any("review-required or forbidden claim" in finding for finding in findings)


def test_rejects_do_not_use_claim_in_copy_seed():
    packet = _packet()
    packet["campaign_backlog"][0]["copy_seed"] = "Autofolio is a risk-free workflow."

    findings = validate_packet(packet)

    assert any("risk-free" in finding for finding in findings)


def test_rejects_campaign_without_owner_r3_approval_gate():
    packet = _packet()
    packet["campaign_backlog"][0]["required_approval"] = ["Compliance Officer review only"]

    findings = validate_packet(packet)

    assert any("Owner/R3" in finding for finding in findings)


def test_rejects_handoff_sales_activation():
    packet = _packet()
    packet["taskset_handoff"]["sales_revenue_lane_active"] = True

    findings = validate_packet(packet)

    assert any("live or external action flags must not be true" in finding for finding in findings)
