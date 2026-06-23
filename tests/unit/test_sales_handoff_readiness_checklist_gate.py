from __future__ import annotations

import copy

from scripts.sales_handoff_readiness_checklist_gate import load_packet, validate_packet


def _packet() -> dict:
    return load_packet()


def test_current_packet_passes():
    assert validate_packet(_packet()) == []


def test_rejects_sales_activation_status():
    packet = _packet()
    packet["status"] = "sales_activation_ready"

    findings = validate_packet(packet)

    assert any("checklist and not_sales_activation" in finding for finding in findings)


def test_rejects_sales_revenue_role_active():
    packet = _packet()
    packet["current_decision"]["sales_revenue_role_active_now"] = True

    findings = validate_packet(packet)

    assert any("sales/customer/payment/live action flags" in finding for finding in findings)


def test_rejects_customer_contact_flag():
    packet = copy.deepcopy(_packet())
    packet["customer_contact_enabled"] = True

    findings = validate_packet(packet)

    assert any("sales/customer/payment/live action flags" in finding for finding in findings)


def test_rejects_forbidden_customer_key():
    packet = copy.deepcopy(_packet())
    packet["customer_email"] = "none@example.invalid"

    findings = validate_packet(packet)

    assert any("forbidden secret/customer/payment key names" in finding for finding in findings)


def test_rejects_missing_activation_precondition():
    packet = _packet()
    packet["activation_preconditions"] = [
        item for item in packet["activation_preconditions"] if item != "customer_contact_workflow_owner_approved"
    ]

    findings = validate_packet(packet)

    assert any("activation_preconditions missing" in finding for finding in findings)


def test_rejects_missing_blocked_condition():
    packet = _packet()
    packet["blocked_conditions"] = [
        item for item in packet["blocked_conditions"] if item != "owner_has_not_activated_sales_revenue_role"
    ]

    findings = validate_packet(packet)

    assert any("blocked_conditions missing" in finding for finding in findings)


def test_rejects_unblocked_readiness_item():
    packet = _packet()
    packet["readiness_checklist"][0]["blocks_role_activation"] = False

    findings = validate_packet(packet)

    assert any("blocks_role_activation must be true" in finding for finding in findings)


def test_rejects_marketing_only_activation_required():
    packet = _packet()
    packet["handoff_matrix"][0]["activation_required"] = True

    findings = validate_packet(packet)

    assert any("marketing-only work" in finding for finding in findings)


def test_rejects_sales_handoff_without_activation_required():
    packet = _packet()
    packet["handoff_matrix"][1]["activation_required"] = False

    findings = validate_packet(packet)

    assert any("sales handoff work" in finding for finding in findings)


def test_rejects_crm_record_allowed():
    packet = _packet()
    packet["handoff_matrix"][1]["crm_record_allowed"] = True

    findings = validate_packet(packet)

    assert any("crm_record_allowed must be false" in finding for finding in findings)


def test_rejects_handoff_missing_next_task():
    packet = _packet()
    packet["taskset_handoff"]["next_task_candidates"] = ["TASK-168"]

    findings = validate_packet(packet)

    assert any("next_task_candidates missing TASK-169" in finding for finding in findings)
