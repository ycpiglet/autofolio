from __future__ import annotations

import copy

from scripts.sales_revenue_lane_decision_gate import load_packet, validate_packet


def _packet() -> dict:
    return load_packet()


def test_current_packet_passes():
    assert validate_packet(_packet()) == []


def test_rejects_role_activation():
    packet = _packet()
    packet["decision"]["create_sales_revenue_role_now"] = True

    findings = validate_packet(packet)

    assert any("create_sales_revenue_role_now must be false" in finding for finding in findings)


def test_rejects_lane_activation():
    packet = _packet()
    packet["decision"]["activate_sales_revenue_lane_now"] = True

    findings = validate_packet(packet)

    assert any("activate_sales_revenue_lane_now must be false" in finding for finding in findings)


def test_rejects_customer_private_key():
    packet = _packet()
    packet["future_sales_revenue_scope_after_activation"] = [{"customer_email": "none@example.invalid"}]

    findings = validate_packet(packet)

    assert any("forbidden secret/customer/payment key names" in finding for finding in findings)


def test_rejects_support_refund_unblocked():
    packet = _packet()
    packet["current_readiness"]["support_refund_policy"]["blocks_role_activation"] = False

    findings = validate_packet(packet)

    assert any("support_refund_policy must block role activation" in finding for finding in findings)


def test_rejects_missing_activation_trigger():
    packet = _packet()
    packet["activation_triggers"] = [
        item for item in packet["activation_triggers"] if item != "customer_contact_workflow_owner_approved"
    ]

    findings = validate_packet(packet)

    assert any("activation_triggers missing" in finding for finding in findings)


def test_rejects_customer_contact_enabled_flag():
    packet = copy.deepcopy(_packet())
    packet["customer_contact_enabled"] = True

    findings = validate_packet(packet)

    assert any("role/customer/payment/live action flags must not be true" in finding for finding in findings)


def test_rejects_missing_prohibited_paid_signal_claim():
    packet = _packet()
    packet["prohibited_sales_automation"] = [
        item for item in packet["prohibited_sales_automation"] if item != "paid signal sales claim"
    ]

    findings = validate_packet(packet)

    assert any("prohibited_sales_automation missing" in finding for finding in findings)
