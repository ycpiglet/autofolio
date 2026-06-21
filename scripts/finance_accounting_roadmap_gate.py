"""Validate the Finance Accounting planning-support roadmap.

This gate keeps the lane local-only. It rejects final accounting/tax/legal/
securities advice, trade/order instructions, customer payment action, private
payment data, secrets, and KIS/order/risk/prod/deploy drift.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROADMAP = REPO_ROOT / "agents" / "project" / "FINANCE-ACCOUNTING-ROADMAP.json"

REQUIRED_STATUS = "local_planning_support_not_financial_or_investment_advice"

REQUIRED_SOURCE_KEYS = {
    "business_plan",
    "membership_access_plan",
    "payment_evidence_policy",
    "payment_recognition_decision_packet",
    "portfolio_overview_api",
    "investor_profile_model",
    "sales_handoff_checklist",
}

REQUIRED_BOUNDARIES = {
    "planning_support_only",
    "not_tax_accounting_final_advice",
    "not_legal_or_securities_advice",
    "not_investment_recommendation",
    "no_trade_recommendation_or_order",
    "no_order_execution",
    "no_profit_guarantee",
    "no_customer_payment_action",
    "no_bank_or_pg_api_call",
    "no_raw_statement_or_private_payment_record",
    "no_secret_or_token_handling",
    "no_kis_order_risk_prod_deploy_change",
}

REQUIRED_INPUT_BUCKETS = {"observed", "planned", "expected", "missing"}
REQUIRED_METRICS = {
    "planned_return_pct",
    "expected_return_range_pct",
    "gap_to_plan_pct_points",
    "allocation_drift",
    "cash_and_payment_readiness",
    "timeline_candidate",
}
REQUIRED_GAP_CATEGORIES = {
    "portfolio_goal_gap",
    "allocation_or_concentration_gap",
    "cashflow_or_payment_evidence_gap",
    "business_plan_alignment_gap",
    "tax_receipt_refund_policy_gap",
    "compliance_or_professional_review_gap",
    "data_quality_gap",
}
REQUIRED_OUTPUTS = {
    "scenario_summary",
    "portfolio_review_candidates",
    "operations_support_gaps",
    "timeline_plan",
}
REQUIRED_NEXT_TASKS = {"TASK-172", "TASK-173", "TASK-174"}
REQUIRED_BLOCKED_ACTIONS = {
    "trade recommendation",
    "order placement",
    "profit taking instruction",
    "additional investment instruction",
    "portfolio rebalance instruction",
    "customer payment request",
    "receipt or tax filing action",
    "bank or payment-provider API call",
    "raw statement persistence",
    "secret or token handling",
    "public performance claim",
    "guaranteed return claim",
    "KIS/order/risk/prod/deploy change",
}

FORBIDDEN_TRUE_KEYS = {
    "order_execution_enabled",
    "trade_recommendation_enabled",
    "investment_advice_enabled",
    "tax_advice_enabled",
    "accounting_advice_enabled",
    "customer_payment_action_enabled",
    "bank_api_enabled",
    "pg_api_enabled",
    "open_banking_enabled",
    "secret_handling_enabled",
    "kis_order_enabled",
    "production_deploy_enabled",
}

FORBIDDEN_KEY_PARTS = {
    "access_token",
    "refresh_token",
    "client_secret",
    "api_secret",
    "app_secret",
    "password",
    "cookie",
    "bank_account_number",
    "raw_statement_text",
    "raw_statement_payload",
    "resident_registration",
    "customer_email",
    "customer_phone",
    "customer_name",
    "customer_payment_record",
    "real_payment_record",
    "payment_record_value",
    "kis_app_key",
    "kis_secret",
}

FORBIDDEN_PHRASES = {
    "you should buy",
    "you should sell",
    "guaranteed return",
    "execute order",
    "place order",
    "tax advice",
    "accounting advice",
}


def load_roadmap(path: Path = DEFAULT_ROADMAP) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _walk(value: Any, path: str = "$") -> list[tuple[str, Any]]:
    items = [(path, value)]
    if isinstance(value, dict):
        for key, child in value.items():
            items.extend(_walk(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            items.extend(_walk(child, f"{path}[{index}]"))
    return items


def _string_values(value: Any) -> list[tuple[str, str]]:
    return [(path, str(item)) for path, item in _walk(value) if isinstance(item, str)]


def _key_names(value: Any) -> list[str]:
    keys: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            keys.append(str(key))
            keys.extend(_key_names(child))
    elif isinstance(value, list):
        for child in value:
            keys.extend(_key_names(child))
    return keys


def validate_roadmap(roadmap: dict[str, Any]) -> list[str]:
    findings: list[str] = []

    if roadmap.get("status") != REQUIRED_STATUS:
        findings.append(f"status must be {REQUIRED_STATUS}")

    sources = roadmap.get("source_artifacts")
    if not isinstance(sources, dict):
        findings.append("source_artifacts must be an object")
    else:
        missing = REQUIRED_SOURCE_KEYS - set(sources)
        if missing:
            findings.append(f"source_artifacts missing {sorted(missing)}")

    boundary = roadmap.get("boundary")
    if not isinstance(boundary, dict):
        findings.append("boundary must be an object")
    else:
        missing = REQUIRED_BOUNDARIES - set(boundary)
        if missing:
            findings.append(f"boundary missing {sorted(missing)}")
        for key in REQUIRED_BOUNDARIES:
            if boundary.get(key) is not True:
                findings.append(f"boundary.{key} must be true")

    question = roadmap.get("planning_question")
    if not isinstance(question, dict):
        findings.append("planning_question must be an object")
    elif question.get("example_is_not_current_portfolio_fact") is not True:
        findings.append("planning_question example must be marked not current portfolio fact")

    input_contract = roadmap.get("input_contract")
    if not isinstance(input_contract, dict):
        findings.append("input_contract must be an object")
    else:
        missing = REQUIRED_INPUT_BUCKETS - set(input_contract)
        if missing:
            findings.append(f"input_contract missing {sorted(missing)}")
        for key in REQUIRED_INPUT_BUCKETS:
            if not isinstance(input_contract.get(key), list) or not input_contract[key]:
                findings.append(f"input_contract.{key} must be a non-empty list")

    metric_ids = {
        item.get("id")
        for item in roadmap.get("metric_contract", [])
        if isinstance(item, dict)
    }
    missing_metrics = REQUIRED_METRICS - metric_ids
    if missing_metrics:
        findings.append(f"metric_contract missing {sorted(missing_metrics)}")

    gap_categories = set(roadmap.get("gap_categories") or [])
    missing_gap_categories = REQUIRED_GAP_CATEGORIES - gap_categories
    if missing_gap_categories:
        findings.append(f"gap_categories missing {sorted(missing_gap_categories)}")

    output_ids = {
        item.get("id")
        for item in roadmap.get("roadmap_outputs", [])
        if isinstance(item, dict)
    }
    missing_outputs = REQUIRED_OUTPUTS - output_ids
    if missing_outputs:
        findings.append(f"roadmap_outputs missing {sorted(missing_outputs)}")
    for item in roadmap.get("roadmap_outputs", []):
        if isinstance(item, dict) and item.get("id") == "portfolio_review_candidates":
            required = set(item.get("must_include") or [])
            if "no_trade_instruction" not in required:
                findings.append("portfolio_review_candidates must include no_trade_instruction")

    blocked_actions = set(roadmap.get("blocked_actions") or [])
    missing_blocked = REQUIRED_BLOCKED_ACTIONS - blocked_actions
    if missing_blocked:
        findings.append(f"blocked_actions missing {sorted(missing_blocked)}")

    next_task_ids = {
        item.get("task_id")
        for item in roadmap.get("next_tasks", [])
        if isinstance(item, dict)
    }
    missing_next = REQUIRED_NEXT_TASKS - next_task_ids
    if missing_next:
        findings.append(f"next_tasks missing {sorted(missing_next)}")

    for path, value in _walk(roadmap):
        if path.rsplit(".", 1)[-1] in FORBIDDEN_TRUE_KEYS and value is True:
            findings.append(f"{path} must not be true")

    for key in _key_names(roadmap):
        lowered = key.lower()
        if any(part in lowered for part in FORBIDDEN_KEY_PARTS):
            findings.append(f"forbidden private/secret/payment key name: {key}")

    for path, text in _string_values(roadmap):
        if path.startswith("$.blocked_actions"):
            continue
        lowered_text = text.lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase in lowered_text:
                findings.append(f"forbidden advice/action phrase: {phrase}")

    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Finance Accounting roadmap")
    parser.add_argument("--roadmap", type=Path, default=DEFAULT_ROADMAP)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    findings = validate_roadmap(load_roadmap(args.roadmap))
    if findings:
        for finding in findings:
            print(f"ERROR: {finding}")
        return 1
    print("OK: finance accounting roadmap gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
