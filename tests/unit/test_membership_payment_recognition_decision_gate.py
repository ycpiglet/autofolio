from __future__ import annotations

import copy

from scripts.membership_payment_recognition_decision_gate import load_packet, validate_packet


def test_membership_payment_recognition_decision_gate_accepts_current_packet():
    packet = load_packet()
    assert validate_packet(packet) == []


def test_membership_payment_recognition_decision_gate_rejects_raw_source_persistence():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    broken["options"][0]["raw_source_persisted"] = True

    findings = validate_packet(broken)

    assert any("raw_source_persisted must be false" in finding for finding in findings)


def test_membership_payment_recognition_decision_gate_rejects_open_banking_mvp_selection():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    for option in broken["options"]:
        if option["id"] == "open_banking_transaction_inquiry":
            option["decision"] = "selected_mvp"

    findings = validate_packet(broken)

    assert any("open_banking_transaction_inquiry must stay blocked R3" in finding for finding in findings)


def test_membership_payment_recognition_decision_gate_requires_hometax_source():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    broken["source_basis"] = [
        item for item in broken["source_basis"] if item["id"] != "hometax_cash_receipt_service"
    ]

    findings = validate_packet(broken)

    assert any("source_basis missing marker: Hometax" in finding for finding in findings)


def test_membership_payment_recognition_decision_gate_rejects_forbidden_payment_key_name():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    broken["bank_account_number"] = "placeholder"

    findings = validate_packet(broken)

    assert any("forbidden payment/production keys present" in finding for finding in findings)


def test_membership_payment_recognition_decision_gate_requires_provider_webhook_test():
    packet = load_packet()
    broken = copy.deepcopy(packet)
    broken["required_staging_tests"] = [
        item
        for item in broken["required_staging_tests"]
        if item != "provider_webhook_is_idempotent"
    ]

    findings = validate_packet(broken)

    assert any("provider_webhook_is_idempotent" in finding for finding in findings)
