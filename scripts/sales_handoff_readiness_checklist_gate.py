"""Validate the TASK-170 Sales handoff readiness checklist.

The checklist is local-only. It must not activate Sales/Revenue, customer
contact, CRM/customer records, payment/billing, public sales claims, external
accounts, OAuth, platform APIs, secrets, or KIS/order/risk/prod/deploy work.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKET = REPO_ROOT / "agents" / "project" / "SALES-HANDOFF-READINESS-CHECKLIST.json"

REQUIRED_SOURCE_KEYS = {
    "business_plan",
    "marketing_brief",
    "sales_revenue_lane_decision",
    "marketing_team_operating_model",
    "campaign_backlog_calendar",
}

REQUIRED_BOUNDARIES = {
    "checklist_only",
    "not_sales_revenue_activation",
    "no_role_registry_change",
    "no_customer_contact",
    "no_customer_private_data",
    "no_customer_records",
    "no_crm_account_creation",
    "no_payment_request",
    "no_billing_setup",
    "no_payment_provider_action",
    "no_bank_or_receipt_action",
    "no_public_sales_claim",
    "no_paid_ads",
    "no_external_account_action",
    "no_oauth_flow",
    "no_platform_api_call",
    "no_secret_or_token_handling",
    "no_lead_scraping",
    "no_bulk_outreach",
    "no_legal_tax_securities_final_advice",
    "no_kis_order_risk_prod_deploy_change",
}

REQUIRED_PRECONDITIONS = {
    "owner_approves_sales_revenue_role_activation",
    "support_refund_policy_defined",
    "privacy_and_customer_record_policy_defined",
    "payment_collection_and_receipt_policy_defined",
    "crm_or_no_crm_decision_defined",
    "compliance_review_for_sales_claims_complete",
    "customer_contact_workflow_owner_approved",
    "business_registration_or_admin_posture_recorded_for_paid_offer",
}

REQUIRED_BLOCKED_CONDITIONS = {
    "support_refund_policy_missing",
    "privacy_and_customer_record_policy_missing",
    "payment_collection_and_receipt_policy_missing",
    "crm_or_no_crm_decision_missing",
    "compliance_sales_claim_review_missing",
    "customer_contact_workflow_not_owner_approved",
    "business_admin_posture_for_paid_offer_not_recorded",
    "owner_has_not_activated_sales_revenue_role",
}

REQUIRED_CHECKLIST_IDS = {
    "pricing_package_policy",
    "pilot_intake_flow",
    "support_refund_policy",
    "privacy_customer_record_policy",
    "crm_or_no_crm_decision",
    "payment_receipt_policy",
    "customer_contact_workflow",
    "compliance_sales_claim_review",
    "business_admin_posture",
}

REQUIRED_FORBIDDEN_ACTIONS = {
    "Sales/Revenue role activation",
    "role registry change",
    "customer contact",
    "customer record storage",
    "CRM activation",
    "payment request",
    "billing setup",
    "payment provider action",
    "bank or receipt action",
    "public sales claim",
    "paid ads",
    "external account action",
    "OAuth flow",
    "platform API call",
    "secret storage",
    "lead scraping",
    "bulk outreach",
    "investment advice sales claim",
    "paid signal sales claim",
    "KIS/order/risk/prod/deploy change",
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
    "sales_revenue_role_active_now",
    "sales_revenue_lane_active_now",
    "sales_revenue_lane_active",
    "customer_contact_enabled",
    "customer_contact_allowed",
    "payment_action_allowed",
    "payment_request_enabled",
    "crm_enabled",
    "crm_record_allowed",
    "crm_account_creation_enabled",
    "billing_setup_enabled",
    "paid_ads_enabled",
    "external_account_action_enabled",
    "oauth_flow_enabled",
    "platform_api_call_enabled",
    "secret_storage_enabled",
    "kis_order_risk_prod_deploy_enabled",
}


def load_packet(path: Path = DEFAULT_PACKET) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("sales handoff readiness checklist root must be an object")
    return data


def validate_packet(packet: dict[str, Any]) -> list[str]:
    findings: list[str] = []

    if packet.get("$schema") != "autofolio.sales-handoff-readiness-checklist/v1":
        findings.append("unexpected or missing sales handoff readiness checklist schema")

    status = str(packet.get("status", "")).lower()
    if "checklist" not in status or "not_sales_activation" not in status:
        findings.append("status must clearly remain checklist and not_sales_activation")

    forbidden_keys = _find_forbidden_keys(packet)
    if forbidden_keys:
        findings.append(f"forbidden secret/customer/payment key names present: {forbidden_keys}")

    live_true_paths = _find_live_true_keys(packet)
    if live_true_paths:
        findings.append(f"sales/customer/payment/live action flags must not be true: {live_true_paths}")

    sources = packet.get("source_of_truth")
    if not isinstance(sources, dict):
        findings.append("source_of_truth must be an object")
    else:
        missing_sources = REQUIRED_SOURCE_KEYS - set(sources)
        if missing_sources:
            findings.append(f"source_of_truth missing keys: {sorted(missing_sources)}")
        for key, raw_path in sources.items():
            if not isinstance(raw_path, str) or not raw_path:
                findings.append(f"source_of_truth.{key} must be a path")
                continue
            if not (REPO_ROOT / raw_path).exists():
                findings.append(f"source_of_truth.{key} path missing: {raw_path}")

    boundaries = packet.get("boundaries")
    if not isinstance(boundaries, dict):
        findings.append("boundaries must be an object")
    else:
        for key in REQUIRED_BOUNDARIES:
            if boundaries.get(key) is not True:
                findings.append(f"boundaries.{key} must be true")

    decision = packet.get("current_decision")
    if not isinstance(decision, dict):
        findings.append("current_decision must be an object")
    else:
        if decision.get("sales_revenue_role_active_now") is not False:
            findings.append("current_decision.sales_revenue_role_active_now must be false")
        if decision.get("sales_revenue_lane_active_now") is not False:
            findings.append("current_decision.sales_revenue_lane_active_now must be false")
        if "Marketing Growth" not in str(decision.get("current_owner", "")):
            findings.append("current_decision.current_owner must keep Marketing Growth as no-contact owner")

    preconditions = set(_string_list(packet.get("activation_preconditions")))
    missing_preconditions = REQUIRED_PRECONDITIONS - preconditions
    if missing_preconditions:
        findings.append(f"activation_preconditions missing: {sorted(missing_preconditions)}")

    blocked = set(_string_list(packet.get("blocked_conditions")))
    missing_blocked = REQUIRED_BLOCKED_CONDITIONS - blocked
    if missing_blocked:
        findings.append(f"blocked_conditions missing: {sorted(missing_blocked)}")

    checklist = packet.get("readiness_checklist")
    if not isinstance(checklist, list) or not checklist:
        findings.append("readiness_checklist must be a non-empty list")
    else:
        checklist_ids = {item.get("id") for item in checklist if isinstance(item, dict)}
        missing_checklist = REQUIRED_CHECKLIST_IDS - checklist_ids
        if missing_checklist:
            findings.append(f"readiness_checklist missing ids: {sorted(missing_checklist)}")
        for index, item in enumerate(checklist):
            if not isinstance(item, dict):
                findings.append(f"readiness_checklist[{index}] must be an object")
                continue
            if item.get("blocks_role_activation") is not True:
                findings.append(f"readiness_checklist[{index}].blocks_role_activation must be true")
            for key in ("state", "source", "activation_condition"):
                if not str(item.get(key, "")).strip():
                    findings.append(f"readiness_checklist[{index}].{key} is required")

    matrix = packet.get("handoff_matrix")
    if not isinstance(matrix, list) or not matrix:
        findings.append("handoff_matrix must be a non-empty list")
    else:
        states = {item.get("handoff_state") for item in matrix if isinstance(item, dict)}
        if "stay_with_marketing" not in states:
            findings.append("handoff_matrix must include stay_with_marketing")
        if not any(str(state).startswith("blocked_until") for state in states):
            findings.append("handoff_matrix must include blocked_until states")
        for index, item in enumerate(matrix):
            if not isinstance(item, dict):
                findings.append(f"handoff_matrix[{index}] must be an object")
                continue
            if item.get("handoff_state") == "stay_with_marketing":
                if item.get("activation_required") is not False:
                    findings.append(f"handoff_matrix[{index}].activation_required must be false for marketing-only work")
            else:
                if item.get("activation_required") is not True:
                    findings.append(f"handoff_matrix[{index}].activation_required must be true for sales handoff work")
            for blocked_key in ("customer_contact_allowed", "payment_action_allowed", "crm_record_allowed"):
                if item.get(blocked_key) is not False:
                    findings.append(f"handoff_matrix[{index}].{blocked_key} must be false")
            if not _string_list(item.get("examples")):
                findings.append(f"handoff_matrix[{index}].examples must be non-empty")

    r3_required = set(_string_list(packet.get("owner_r3_required_for")))
    for required in (
        "Sales/Revenue role activation",
        "customer contact",
        "CRM or customer-record system activation",
        "payment request or billing setup",
    ):
        if required not in r3_required:
            findings.append(f"owner_r3_required_for missing {required}")

    forbidden_actions = set(_string_list(packet.get("forbidden_actions")))
    missing_forbidden = REQUIRED_FORBIDDEN_ACTIONS - forbidden_actions
    if missing_forbidden:
        findings.append(f"forbidden_actions missing: {sorted(missing_forbidden)}")

    handoff = packet.get("taskset_handoff")
    if not isinstance(handoff, dict):
        findings.append("taskset_handoff must be an object")
    else:
        if handoff.get("task_170_complete") is not True:
            findings.append("taskset_handoff.task_170_complete must be true")
        if handoff.get("taskset_remains_active") is not True:
            findings.append("taskset_handoff.taskset_remains_active must be true")
        next_tasks = set(_string_list(handoff.get("next_task_candidates")))
        for task_id in ("TASK-168", "TASK-169"):
            if task_id not in next_tasks:
                findings.append(f"taskset_handoff.next_task_candidates missing {task_id}")

    verification = packet.get("verification")
    if not isinstance(verification, dict):
        findings.append("verification must be an object")
    elif "sales_handoff_readiness_checklist_gate.py --check" not in str(verification.get("local_gate", "")):
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
            if key in LIVE_TRUE_KEYS and child is True:
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
        print("sales-handoff-readiness-checklist-gate: fail")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("sales-handoff-readiness-checklist-gate: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
