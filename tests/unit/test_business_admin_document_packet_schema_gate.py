from __future__ import annotations

import copy

from scripts.business_admin_document_packet_schema_gate import load_packet, validate_packet


def test_business_admin_document_packet_schema_gate_accepts_current_packet():
    packet = load_packet()
    assert validate_packet(packet) == []


def test_business_admin_document_packet_schema_gate_rejects_owner_login_boundary_change():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    broken["boundaries"]["no_login_or_authentication"] = False

    findings = validate_packet(broken)

    assert any("no_login_or_authentication" in finding for finding in findings)


def test_business_admin_document_packet_schema_gate_requires_nts_source():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    broken["source_basis"] = [
        item for item in broken["source_basis"] if item["authority"] != "National Tax Service"
    ]

    findings = validate_packet(broken)

    assert any("source_basis missing marker: National Tax Service" in finding for finding in findings)


def test_business_admin_document_packet_schema_gate_rejects_private_key_name():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    broken["resident_registration_number"] = "placeholder"

    findings = validate_packet(broken)

    assert any("forbidden private/secret keys present" in finding for finding in findings)


def test_business_admin_document_packet_schema_gate_requires_hwpx_xml_diff():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    broken["future_hwpx_policy"]["xml_diff_required"] = False

    findings = validate_packet(broken)

    assert any("future_hwpx_policy.xml_diff_required" in finding for finding in findings)


def test_business_admin_document_packet_schema_gate_requires_submission_owner_only_step():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    broken["owner_only_steps"] = [
        item for item in broken["owner_only_steps"] if item != "official_submission"
    ]

    findings = validate_packet(broken)

    assert any("official_submission" in finding for finding in findings)
