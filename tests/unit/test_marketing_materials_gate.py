from __future__ import annotations

import copy

from scripts.marketing_materials_gate import load_packet, validate_packet


def test_marketing_materials_gate_accepts_current_packet():
    packet = load_packet()
    assert validate_packet(packet) == []


def test_marketing_materials_gate_rejects_publication_approval_status():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    broken["status"] = "publication_approved"
    broken["campaign_brief"]["claim_review"] = "approved"

    findings = validate_packet(broken)

    assert any("status must clearly remain draft" in finding for finding in findings)
    assert any("claim_review must not be approved" in finding for finding in findings)


def test_marketing_materials_gate_requires_no_public_posting_boundary():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    broken["boundaries"]["no_public_posting"] = False

    findings = validate_packet(broken)

    assert any("boundaries.no_public_posting must be true" in finding for finding in findings)


def test_marketing_materials_gate_rejects_forbidden_copy_phrase():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    broken["copy_inventory"][0]["text"] = "Autofolio provides guaranteed returns."

    findings = validate_packet(broken)

    assert any("guaranteed returns" in finding for finding in findings)


def test_marketing_materials_gate_rejects_secret_key_names():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    broken["kis_app_secret"] = "placeholder"

    findings = validate_packet(broken)

    assert any("forbidden secret/private key names present" in finding for finding in findings)


def test_marketing_materials_gate_requires_sns_drafts():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    broken["assets"]["sns_draft_bundle"]["channels"] = []

    findings = validate_packet(broken)

    assert any("at least 3 channel drafts" in finding for finding in findings)
