"""Validate the TASK-097 Sales/Revenue lane decision packet.

This gate keeps Sales/Revenue deferred until Owner, compliance, support/refund,
privacy, payment, and customer-record inputs exist. It rejects role activation,
customer contact, CRM/payment actions, secret fields, paid ads, scraping, and
unapproved sales claims.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKET = REPO_ROOT / "agents" / "project" / "SALES-REVENUE-LANE-DECISION.json"

REQUIRED_BOUNDARIES = {
    "decision_record_only",
    "not_role_activation",
    "no_role_registry_change",
    "no_customer_contact",
    "no_customer_private_data",
    "no_crm_account_creation",
    "no_payment_request",
    "no_payment_provider_action",
    "no_bank_or_receipt_action",
    "no_public_sales_claim",
    "no_paid_ads",
    "no_lead_scraping",
    "no_bulk_outreach",
    "no_external_account_action",
    "no_oauth_flow",
    "no_secret_or_token_storage",
    "no_investment_advice_or_paid_signal_sales",
    "owner_approval_required_before_customer_contact",
    "compliance_review_required_before_paid_or_public_sales_claims",
}

REQUIRED_READINESS_KEYS = {
    "pricing_hypothesis",
    "pilot_flow",
    "support_refund_policy",
    "crm_or_customer_record_policy",
    "payment_collection_policy",
    "compliance_sales_claim_review",
}

REQUIRED_ACTIVATION_TRIGGERS = {
    "owner_approves_sales_revenue_role_activation",
    "support_refund_policy_defined",
    "privacy_and_customer_record_policy_defined",
    "payment_collection_and_receipt_policy_defined",
    "crm_or_no_crm_decision_defined",
    "compliance_review_for_sales_claims_complete",
    "customer_contact_workflow_owner_approved",
    "business_registration_or_admin_posture_recorded_for_paid_offer",
}

REQUIRED_PROHIBITED_AUTOMATION = {
    "cold email or direct message",
    "customer contact without Owner approval",
    "CRM account creation or sync",
    "payment request or checkout creation",
    "bank or receipt action",
    "lead scraping",
    "bulk outreach",
    "paid ads",
    "retargeting pixel setup",
    "viewbot or fake engagement",
    "investment advice sales claim",
    "paid signal sales claim",
    "model portfolio sales claim",
    "performance guarantee",
    "KIS commercial clearance claim",
}

REQUIRED_FUTURE_ROLE_FIELDS = {
    "role_id",
    "aliases",
    "required_inputs",
    "forbidden_inputs",
    "output_contract",
    "audit_gate",
}

FORBIDDEN_KEY_NAMES = {
    "access_token",
    "refresh_token",
    "client_secret",
    "api_secret",
    "app_secret",
    "password",
    "cookie",
    "session",
    "customer_email",
    "customer_phone",
    "customer_name",
    "bank_account_number",
    "card_number",
    "payment_provider_secret",
    "crm_api_key",
    "ad_account_id",
    "kis_app_secret",
}

LIVE_TRUE_KEYS = {
    "create_sales_revenue_role_now",
    "activate_sales_revenue_lane_now",
    "customer_contact_enabled",
    "crm_account_creation_enabled",
    "payment_request_enabled",
    "paid_ads_enabled",
    "external_account_action_enabled",
    "oauth_flow_enabled",
    "secret_storage_enabled",
}

BAD_STATUS_FRAGMENTS = {
    "activated",
    "ready_for_sales",
    "crm_enabled",
    "payment_enabled",
}


def load_packet(path: Path = DEFAULT_PACKET) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("sales revenue lane decision root must be an object")
    return data


def validate_packet(packet: dict[str, Any]) -> list[str]:
    findings: list[str] = []

    if packet.get("$schema") != "autofolio.sales-revenue-lane-decision/v1":
        findings.append("unexpected or missing sales revenue lane decision schema")

    status = str(packet.get("status", "")).lower()
    if "deferred" not in status or "not_active" not in status:
        findings.append("status must clearly remain deferred and not_active")
    for fragment in BAD_STATUS_FRAGMENTS:
        if fragment in status:
            findings.append(f"status must not imply activation: {fragment}")

    forbidden_keys = _find_forbidden_keys(packet)
    if forbidden_keys:
        findings.append(f"forbidden secret/customer/payment key names present: {forbidden_keys}")

    live_true_paths = _find_live_true_keys(packet)
    if live_true_paths:
        findings.append(f"role/customer/payment/live action flags must not be true: {live_true_paths}")

    decision = packet.get("decision")
    if not isinstance(decision, dict):
        findings.append("decision must be an object")
    else:
        if decision.get("create_sales_revenue_role_now") is not False:
            findings.append("decision.create_sales_revenue_role_now must be false")
        if decision.get("activate_sales_revenue_lane_now") is not False:
            findings.append("decision.activate_sales_revenue_lane_now must be false")
        if "marketing_growth_only" not in str(decision.get("current_operating_mode", "")):
            findings.append("decision.current_operating_mode must keep Marketing Growth only")
        if not _string_list(decision.get("reason")):
            findings.append("decision.reason must be a non-empty list")

    readiness = packet.get("current_readiness")
    if not isinstance(readiness, dict):
        findings.append("current_readiness must be an object")
    else:
        missing = REQUIRED_READINESS_KEYS - set(readiness)
        if missing:
            findings.append(f"current_readiness missing keys: {sorted(missing)}")
        support = readiness.get("support_refund_policy", {})
        if not isinstance(support, dict) or support.get("blocks_role_activation") is not True:
            findings.append("support_refund_policy must block role activation")
        crm = readiness.get("crm_or_customer_record_policy", {})
        if not isinstance(crm, dict) or crm.get("blocks_role_activation") is not True:
            findings.append("crm_or_customer_record_policy must block role activation")
        compliance = readiness.get("compliance_sales_claim_review", {})
        if not isinstance(compliance, dict) or compliance.get("blocks_role_activation") is not True:
            findings.append("compliance_sales_claim_review must block role activation")

    if not _string_list(packet.get("marketing_growth_scope_until_activation")):
        findings.append("marketing_growth_scope_until_activation must be a non-empty list")
    if not _string_list(packet.get("future_sales_revenue_scope_after_activation")):
        findings.append("future_sales_revenue_scope_after_activation must be a non-empty list")

    triggers = set(_string_list(packet.get("activation_triggers")))
    missing_triggers = REQUIRED_ACTIVATION_TRIGGERS - triggers
    if missing_triggers:
        findings.append(f"activation_triggers missing: {sorted(missing_triggers)}")

    future_role = packet.get("future_role_contract_if_activated")
    if not isinstance(future_role, dict):
        findings.append("future_role_contract_if_activated must be an object")
    else:
        missing_role_fields = REQUIRED_FUTURE_ROLE_FIELDS - set(future_role)
        if missing_role_fields:
            findings.append(f"future_role_contract_if_activated missing: {sorted(missing_role_fields)}")
        if future_role.get("role_id") != "sales-revenue":
            findings.append("future_role_contract_if_activated.role_id must be sales-revenue")
        if future_role.get("audit_gate") is not True:
            findings.append("future_role_contract_if_activated.audit_gate must be true")

    boundaries = packet.get("boundaries")
    if not isinstance(boundaries, dict):
        findings.append("boundaries must be an object")
    else:
        for key in REQUIRED_BOUNDARIES:
            if boundaries.get(key) is not True:
                findings.append(f"boundaries.{key} must be true")

    prohibited = set(_string_list(packet.get("prohibited_sales_automation")))
    missing_prohibited = REQUIRED_PROHIBITED_AUTOMATION - prohibited
    if missing_prohibited:
        findings.append(f"prohibited_sales_automation missing: {sorted(missing_prohibited)}")

    handoff = packet.get("taskset_handoff")
    if not isinstance(handoff, dict):
        findings.append("taskset_handoff must be an object")
    else:
        if handoff.get("task_097_complete") is not True:
            findings.append("taskset_handoff.task_097_complete must be true")
        if handoff.get("taskset_marketing_growth_complete") is not True:
            findings.append("taskset_handoff.taskset_marketing_growth_complete must be true")
        if handoff.get("sales_revenue_lane_active") is not False:
            findings.append("taskset_handoff.sales_revenue_lane_active must be false")
        r3_items = set(_string_list(handoff.get("owner_r3_required_for")))
        for required in ("real customer contact", "CRM or customer-record system activation", "payment request or provider setup"):
            if required not in r3_items:
                findings.append(f"taskset_handoff.owner_r3_required_for missing {required}")

    verification = packet.get("verification")
    if not isinstance(verification, dict):
        findings.append("verification must be an object")
    elif "sales_revenue_lane_decision_gate.py --check" not in str(verification.get("local_gate", "")):
        findings.append("verification.local_gate must reference this gate")

    return findings


def _find_forbidden_keys(value: Any, prefix: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}"
            if key.lower() in FORBIDDEN_KEY_NAMES:
                findings.append(path)
            findings.extend(_find_forbidden_keys(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(_find_forbidden_keys(child, f"{prefix}[{index}]"))
    return findings


def _find_live_true_keys(value: Any, prefix: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}"
            if key.lower() in LIVE_TRUE_KEYS and child is True:
                findings.append(path)
            findings.extend(_find_live_true_keys(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(_find_live_true_keys(child, f"{prefix}[{index}]"))
    return findings


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--check", action="store_true", help="validate and return non-zero on findings")
    args = parser.parse_args()

    packet = load_packet(args.packet)
    findings = validate_packet(packet)
    if findings:
        print("sales revenue lane decision gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"sales revenue lane decision gate: PASS ({args.packet})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
