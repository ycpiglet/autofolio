from __future__ import annotations

import copy

from scripts.promotion_channel_policy_gate import load_packet, validate_packet


def test_promotion_channel_policy_gate_accepts_current_packet():
    packet = load_packet()
    assert validate_packet(packet) == []


def test_promotion_channel_policy_gate_rejects_live_enabled_channel():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    broken["channels"][1]["live_action"] = True

    findings = validate_packet(broken)

    assert any("live_action must be false" in finding for finding in findings)


def test_promotion_channel_policy_gate_requires_owner_r3_for_live():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    broken["channels"][1]["owner_r3_required_for_live"] = False

    findings = validate_packet(broken)

    assert any("owner_r3_required_for_live must be true" in finding for finding in findings)


def test_promotion_channel_policy_gate_rejects_secret_key_names():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    broken["channels"][1]["access_token"] = "placeholder"

    findings = validate_packet(broken)

    assert any("forbidden secret/customer key names present" in finding for finding in findings)


def test_promotion_channel_policy_gate_requires_naver_auto_posting_unsupported():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    for channel in broken["channels"]:
        if channel["id"] == "naver_blog":
            channel["api_posting_possible"] = "possible_after_owner_setup"

    findings = validate_packet(broken)

    assert any("naver_blog.api_posting_possible must be unsupported_for_auto_posting" in finding for finding in findings)


def test_promotion_channel_policy_gate_rejects_publish_ready_value():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    broken["channel_selection"]["live_api_mode"] = "live_enabled"

    findings = validate_packet(broken)

    assert any("live_enabled" in finding for finding in findings)
