from __future__ import annotations

import copy

from scripts.promotion_publishing_policy_gate import load_packet, validate_packet


def _packet() -> dict:
    return load_packet()


def test_current_packet_passes():
    assert validate_packet(_packet()) == []


def test_rejects_live_channel_flag():
    packet = _packet()
    packet["channel_policies"][0]["external_action_enabled"] = True

    findings = validate_packet(packet)

    assert any("external_action_enabled false" in finding for finding in findings)


def test_rejects_missing_x_official_source():
    packet = _packet()
    packet["official_sources"] = [
        item for item in packet["official_sources"] if item["id"] != "x_create_post"
    ]

    findings = validate_packet(packet)

    assert any("official_sources missing ids" in finding and "x_create_post" in finding for finding in findings)


def test_rejects_forbidden_token_key():
    packet = _packet()
    packet["channel_policies"][1]["bot_token"] = "placeholder"

    findings = validate_packet(packet)

    assert any("forbidden secret/customer/live key names" in finding for finding in findings)


def test_rejects_missing_owner_approval():
    packet = _packet()
    packet["channel_policies"][2]["owner_approval_required"] = False

    findings = validate_packet(packet)

    assert any("must require Owner approval" in finding for finding in findings)


def test_rejects_missing_forbidden_action():
    packet = _packet()
    packet["forbidden_actions"] = [
        item for item in packet["forbidden_actions"] if item != "bulk messaging"
    ]

    findings = validate_packet(packet)

    assert any("forbidden_actions missing" in finding and "bulk messaging" in finding for finding in findings)


def test_rejects_publication_approved_status():
    packet = _packet()
    packet["status"] = "publication_approved_ready_to_publish"

    findings = validate_packet(packet)

    assert any("must not imply publication approval" in finding for finding in findings)


def test_rejects_mutated_copy_without_touching_fixture():
    packet = copy.deepcopy(_packet())
    packet["dry_run_contract"]["external_network_calls"] = True

    findings = validate_packet(packet)

    assert any("external_network_calls must be false" in finding for finding in findings)
