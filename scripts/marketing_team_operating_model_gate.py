"""Validate the TASK-166 marketing team operating model.

The model is a local coordination contract. It must not activate public
publishing, customer contact, Sales/Revenue, OAuth, platform APIs, final asset
export, secrets, or KIS/order/risk/prod/deploy work.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = REPO_ROOT / "agents" / "project" / "MARKETING-TEAM-OPERATING-MODEL.json"

REQUIRED_SOURCE_IDS = {
    "business_plan",
    "marketing_brief",
    "marketing_growth_taskset",
    "marketing_team_taskset",
    "marketing_materials_v1",
    "promotion_channel_policy_matrix",
    "promotion_publishing_state_machine",
    "promotion_asset_rendering_contract",
    "sales_revenue_lane_decision",
}

REQUIRED_ROLE_IDS = {
    "lead-engineer",
    "marketing-growth",
    "compliance-officer",
    "business-planner",
    "regulatory-admin",
    "doc-steward",
    "backend",
    "qa",
}

REQUIRED_PHASES = {
    "intake",
    "source_alignment",
    "draft_or_readiness_work",
    "claim_review",
    "qa_gate",
    "closeout",
}

REQUIRED_ROUTE_TYPES = {
    "campaign_copy_or_content_calendar": "TASK-167",
    "pdf_pptx_or_asset_generation": "TASK-168",
    "sns_or_external_publishing_automation": "TASK-169",
    "sales_or_revenue_or_customer_conversion": "TASK-170",
}

REQUIRED_COMPLIANCE_TRIGGERS = {
    "investment advice wording",
    "paid signal wording",
    "model portfolio wording",
    "automated trading wording",
    "performance or return wording",
    "KIS commercial use wording",
    "tax or legal wording",
    "regulatory status wording",
    "public paid launch wording",
    "recommendation wording",
}

REQUIRED_OWNER_R3_TRIGGERS = {
    "public post",
    "SNS upload",
    "paid ads",
    "customer contact",
    "CRM or customer-record system activation",
    "payment request or billing setup",
    "Sales/Revenue role activation",
    "OAuth flow",
    "external platform API call",
    "external account setting change",
    "browser automation against social platform",
    "final PDF/PPTX binary export",
    "public URL publication",
    "secret or token handling",
    "customer private data handling",
    "production DB apply",
    "deploy",
    "KIS/order/risk/prod change",
    "legal/tax/securities final advice",
}

REQUIRED_BOUNDARIES = {
    "local_operating_model_only",
    "not_publication_approval",
    "not_sales_revenue_activation",
    "no_public_post",
    "no_sns_upload",
    "no_paid_ads",
    "no_customer_contact",
    "no_customer_private_data",
    "no_crm_or_customer_record_activation",
    "no_payment_request",
    "no_billing_setup",
    "no_oauth_flow",
    "no_external_account_action",
    "no_external_platform_api_call",
    "no_browser_automation_against_social_platform",
    "no_final_pdf_pptx_binary_export",
    "no_public_url_publication",
    "no_secret_or_token_handling",
    "no_legal_tax_securities_final_advice",
    "no_kis_order_risk_prod_deploy_change",
}

REQUIRED_FORBIDDEN_ACTIONS = {
    "public posting",
    "SNS upload",
    "paid ads",
    "customer contact",
    "CRM activation",
    "customer record storage",
    "payment request",
    "billing setup",
    "Sales/Revenue role activation",
    "OAuth flow",
    "token handling",
    "platform API call",
    "browser automation against social platforms",
    "final PDF export",
    "final PPTX export",
    "public URL publication",
    "secret storage",
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
    "public_post_enabled",
    "sns_upload_enabled",
    "paid_ads_enabled",
    "customer_contact_enabled",
    "crm_enabled",
    "payment_request_enabled",
    "billing_setup_enabled",
    "sales_revenue_lane_active",
    "oauth_flow_enabled",
    "external_platform_api_call_enabled",
    "platform_api_call_enabled",
    "browser_automation_enabled",
    "final_asset_export_approved",
    "live_publication_approved",
    "secret_storage_enabled",
    "kis_order_risk_prod_deploy_enabled",
}


def load_model(path: Path = DEFAULT_MODEL) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("marketing team operating model root must be an object")
    return data


def validate_model(model: dict[str, Any]) -> list[str]:
    findings: list[str] = []

    if model.get("$schema") != "autofolio.marketing-team-operating-model/v1":
        findings.append("unexpected or missing marketing team operating model schema")

    status = str(model.get("status", "")).lower()
    if "local_operating_model" not in status:
        findings.append("status must declare local_operating_model")
    if "not_publication" not in status:
        findings.append("status must declare not_publication")
    if "not_sales_activation" not in status:
        findings.append("status must declare not_sales_activation")

    forbidden_keys = _find_forbidden_keys(model)
    if forbidden_keys:
        findings.append(f"forbidden secret/customer/payment key names present: {forbidden_keys}")

    live_true_paths = _find_live_true_keys(model)
    if live_true_paths:
        findings.append(f"live or external action flags must not be true: {live_true_paths}")

    source_ids = {
        item.get("id")
        for item in model.get("source_inputs", [])
        if isinstance(item, dict)
    }
    missing_sources = REQUIRED_SOURCE_IDS - source_ids
    if missing_sources:
        findings.append(f"source_inputs missing ids: {sorted(missing_sources)}")
    for item in model.get("source_inputs", []):
        if not isinstance(item, dict):
            findings.append("source_inputs entries must be objects")
            continue
        path = item.get("path")
        if not isinstance(path, str) or not path:
            findings.append(f"source input {item.get('id', '?')} missing path")
            continue
        if not (REPO_ROOT / path).exists():
            findings.append(f"source input path missing: {path}")

    roles = model.get("team_roles")
    if not isinstance(roles, list) or not roles:
        findings.append("team_roles must be a non-empty list")
    else:
        role_ids = {item.get("role_id") for item in roles if isinstance(item, dict)}
        missing_roles = REQUIRED_ROLE_IDS - role_ids
        if missing_roles:
            findings.append(f"team_roles missing role_ids: {sorted(missing_roles)}")
        for role in roles:
            if not isinstance(role, dict):
                findings.append("team_roles entries must be objects")
                continue
            role_id = role.get("role_id", "?")
            if not _string_list(role.get("accountable_for")):
                findings.append(f"team_roles.{role_id}.accountable_for must be non-empty")
            if not _string_list(role.get("inputs")):
                findings.append(f"team_roles.{role_id}.inputs must be non-empty")
            if not _string_list(role.get("outputs")):
                findings.append(f"team_roles.{role_id}.outputs must be non-empty")
            if not _string_list(role.get("forbidden_actions")):
                findings.append(f"team_roles.{role_id}.forbidden_actions must be non-empty")

    workflow = model.get("workflow")
    if not isinstance(workflow, list) or not workflow:
        findings.append("workflow must be a non-empty list")
    else:
        phase_ids = {item.get("phase_id") for item in workflow if isinstance(item, dict)}
        missing_phases = REQUIRED_PHASES - phase_ids
        if missing_phases:
            findings.append(f"workflow missing phase_ids: {sorted(missing_phases)}")
        for phase in workflow:
            if not isinstance(phase, dict):
                findings.append("workflow entries must be objects")
                continue
            if phase.get("external_action_enabled") is not False:
                findings.append(f"workflow.{phase.get('phase_id', '?')}.external_action_enabled must be false")

    routing = model.get("routing_rules")
    if not isinstance(routing, list) or not routing:
        findings.append("routing_rules must be a non-empty list")
    else:
        route_map = {
            item.get("request_type"): item.get("next_task")
            for item in routing
            if isinstance(item, dict)
        }
        for request_type, next_task in REQUIRED_ROUTE_TYPES.items():
            if route_map.get(request_type) != next_task:
                findings.append(f"routing_rules missing {request_type} -> {next_task}")

    compliance_triggers = set(_string_list(model.get("compliance_review_triggers")))
    missing_compliance = REQUIRED_COMPLIANCE_TRIGGERS - compliance_triggers
    if missing_compliance:
        findings.append(f"compliance_review_triggers missing: {sorted(missing_compliance)}")

    owner_triggers = set(_string_list(model.get("owner_r3_triggers")))
    missing_owner = REQUIRED_OWNER_R3_TRIGGERS - owner_triggers
    if missing_owner:
        findings.append(f"owner_r3_triggers missing: {sorted(missing_owner)}")

    criteria = model.get("downstream_task_start_criteria")
    if not isinstance(criteria, dict):
        findings.append("downstream_task_start_criteria must be an object")
    else:
        for task_id in REQUIRED_ROUTE_TYPES.values():
            if not _string_list(criteria.get(task_id)):
                findings.append(f"downstream_task_start_criteria.{task_id} must be non-empty")

    boundaries = model.get("boundaries")
    if not isinstance(boundaries, dict):
        findings.append("boundaries must be an object")
    else:
        for key in REQUIRED_BOUNDARIES:
            if boundaries.get(key) is not True:
                findings.append(f"boundaries.{key} must be true")

    forbidden_actions = set(_string_list(model.get("forbidden_actions")))
    missing_forbidden = REQUIRED_FORBIDDEN_ACTIONS - forbidden_actions
    if missing_forbidden:
        findings.append(f"forbidden_actions missing: {sorted(missing_forbidden)}")

    handoff = model.get("taskset_handoff")
    if not isinstance(handoff, dict):
        findings.append("taskset_handoff must be an object")
    else:
        if handoff.get("next_task_candidate") != "TASK-167":
            findings.append("taskset_handoff.next_task_candidate must be TASK-167")
        if handoff.get("taskset_remains_active") is not True:
            findings.append("taskset_handoff.taskset_remains_active must be true")
        for blocked_key in (
            "sales_revenue_lane_active",
            "live_publication_approved",
            "final_asset_export_approved",
        ):
            if handoff.get(blocked_key) is not False:
                findings.append(f"taskset_handoff.{blocked_key} must be false")

    verification = model.get("verification")
    if not isinstance(verification, dict):
        findings.append("verification must be an object")
    elif "marketing_team_operating_model_gate.py --check" not in str(verification.get("local_gate", "")):
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
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--check", action="store_true", help="Return non-zero on findings")
    args = parser.parse_args()

    findings = validate_model(load_model(args.model))
    if findings:
        print("marketing-team-operating-model-gate: fail")
        for finding in findings:
            print(f"- {finding}")
        return 1 if args.check else 0
    print("marketing-team-operating-model-gate: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
