from __future__ import annotations

import copy

from scripts.membership_kis_terms_review_gate import load_packet, validate_packet


def test_membership_kis_terms_review_gate_accepts_current_packet():
    packet = load_packet()
    assert validate_packet(packet) == []


def test_membership_kis_terms_review_gate_rejects_clearance_status():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    broken["status"] = "clearance_complete"

    findings = validate_packet(broken)

    assert any("not clearance" in finding for finding in findings)


def test_membership_kis_terms_review_gate_requires_provider_source():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    broken["source_basis"] = [
        item for item in broken["source_basis"] if item["id"] != "kis_developers_provider_guide"
    ]

    findings = validate_packet(broken)

    assert any("kis_developers_provider_guide" in finding for finding in findings)


def test_membership_kis_terms_review_gate_rejects_kis_secret_keys():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    broken["kis_app_secret"] = "placeholder"

    findings = validate_packet(broken)

    assert any("forbidden KIS credential/clearance keys present" in finding for finding in findings)


def test_membership_kis_terms_review_gate_requires_market_data_question():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    broken["owner_kis_legal_question_set"] = [
        item for item in broken["owner_kis_legal_question_set"] if item["id"] != "market_data_display_rights"
    ]

    findings = validate_packet(broken)

    assert any("market_data_display_rights" in finding for finding in findings)
