"""Validate the Finance Scenario Input Contract.

The gate keeps TASK-172 local and synthetic. It rejects current-portfolio fact
drift, advice/action wording, private payment data, secrets, and order/prod
flags before TASK-173 can consume the fixture.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = REPO_ROOT / "agents" / "project" / "FINANCE-SCENARIO-INPUT-CONTRACT.json"

REQUIRED_SCHEMA = "autofolio.finance-scenario-input-contract/v1"
REQUIRED_STATUS = "local_synthetic_fixture_not_financial_or_investment_advice"

REQUIRED_SOURCE_KEYS = {
    "finance_accounting_roadmap",
    "business_plan",
    "membership_payment_evidence_policy",
    "sales_handoff_checklist",
    "task_171_record",
    "task_172_record",
}

REQUIRED_BOUNDARIES = {
    "synthetic_fixture_only",
    "planning_support_only",
    "example_not_current_portfolio_fact",
    "read_only_planning_input_only",
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

REQUIRED_BUCKETS = {"observed", "planned", "expected", "missing", "blocked"}
REQUIRED_METRICS = {
    "planned_return_pct",
    "expected_return_range_pct",
    "gap_to_plan_pct_points",
    "allocation_drift",
    "cash_and_payment_readiness",
    "timeline_candidate",
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
    "current_portfolio_fact",
    "real_customer_payment_data",
    "action_permitted_now",
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
    "investment advice",
}


def load_contract(path: Path = DEFAULT_CONTRACT) -> dict[str, Any]:
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


def _is_blocked_context(path: str) -> bool:
    return (
        path.startswith("$.forbidden_outputs")
        or path.startswith("$.sample_fixtures[0].blocked")
        or ".blocked" in path
    )


def _validate_bucket_contract(contract: dict[str, Any], findings: list[str]) -> None:
    buckets = contract.get("scenario_input_contract")
    if not isinstance(buckets, dict):
        findings.append("scenario_input_contract must be an object")
        return

    missing = REQUIRED_BUCKETS - set(buckets)
    if missing:
        findings.append(f"scenario_input_contract missing {sorted(missing)}")
    for key in REQUIRED_BUCKETS:
        if not isinstance(buckets.get(key), list) or not buckets[key]:
            findings.append(f"scenario_input_contract.{key} must be a non-empty list")


def _validate_fixture(fixture: dict[str, Any], findings: list[str]) -> None:
    fixture_id = fixture.get("id", "<unknown>")
    if fixture.get("synthetic") is not True:
        findings.append(f"fixture {fixture_id} must be synthetic")
    if fixture.get("example_is_not_current_portfolio_fact") is not True:
        findings.append(f"fixture {fixture_id} must be marked not current portfolio fact")
    if fixture.get("current_portfolio_fact") is not False:
        findings.append(f"fixture {fixture_id} current_portfolio_fact must be false")
    if fixture.get("real_customer_payment_data") is not False:
        findings.append(f"fixture {fixture_id} real_customer_payment_data must be false")

    missing_sections = REQUIRED_BUCKETS - set(fixture)
    if missing_sections:
        findings.append(f"fixture {fixture_id} missing sections {sorted(missing_sections)}")

    planned = fixture.get("planned")
    if not isinstance(planned, dict) or planned.get("planned_return_pct") != 5.0:
        findings.append(f"fixture {fixture_id} planned_return_pct must be 5.0")

    expected = fixture.get("expected")
    expected_range = expected.get("expected_return_range_pct") if isinstance(expected, dict) else None
    if (
        not isinstance(expected_range, list)
        or len(expected_range) != 2
        or not all(isinstance(item, (int, float)) for item in expected_range)
        or expected_range[0] > 10.0
        or expected_range[1] < 10.0
    ):
        findings.append(f"fixture {fixture_id} expected_return_range_pct must include 10.0")
    if not isinstance(expected, dict) or expected.get("not_guaranteed") is not True:
        findings.append(f"fixture {fixture_id} expected.not_guaranteed must be true")

    for section in ("missing", "blocked"):
        if not isinstance(fixture.get(section), list) or not fixture[section]:
            findings.append(f"fixture {fixture_id} {section} must be a non-empty list")


def validate_contract(contract: dict[str, Any]) -> list[str]:
    findings: list[str] = []

    if contract.get("$schema") != REQUIRED_SCHEMA:
        findings.append(f"$schema must be {REQUIRED_SCHEMA}")
    if contract.get("status") != REQUIRED_STATUS:
        findings.append(f"status must be {REQUIRED_STATUS}")

    sources = contract.get("source_artifacts")
    if not isinstance(sources, dict):
        findings.append("source_artifacts must be an object")
    else:
        missing = REQUIRED_SOURCE_KEYS - set(sources)
        if missing:
            findings.append(f"source_artifacts missing {sorted(missing)}")

    boundary = contract.get("boundary")
    if not isinstance(boundary, dict):
        findings.append("boundary must be an object")
    else:
        missing = REQUIRED_BOUNDARIES - set(boundary)
        if missing:
            findings.append(f"boundary missing {sorted(missing)}")
        for key in REQUIRED_BOUNDARIES:
            if boundary.get(key) is not True:
                findings.append(f"boundary.{key} must be true")

    _validate_bucket_contract(contract, findings)

    metric_ids = {
        item.get("id")
        for item in contract.get("metric_contract", [])
        if isinstance(item, dict)
    }
    missing_metrics = REQUIRED_METRICS - metric_ids
    if missing_metrics:
        findings.append(f"metric_contract missing {sorted(missing_metrics)}")

    fixtures = contract.get("sample_fixtures")
    if not isinstance(fixtures, list) or not fixtures:
        findings.append("sample_fixtures must be a non-empty list")
    else:
        for fixture in fixtures:
            if isinstance(fixture, dict):
                _validate_fixture(fixture, findings)
            else:
                findings.append("sample_fixtures entries must be objects")

    review_candidates = contract.get("portfolio_review_candidates")
    if not isinstance(review_candidates, list) or not review_candidates:
        findings.append("portfolio_review_candidates must be a non-empty list")
    else:
        for item in review_candidates:
            if not isinstance(item, dict):
                findings.append("portfolio_review_candidates entries must be objects")
                continue
            if item.get("no_trade_instruction") is not True:
                findings.append("portfolio_review_candidates must include no_trade_instruction true")
            if item.get("action_permitted_now") is not False:
                findings.append("portfolio_review_candidates action_permitted_now must be false")

    timeline_candidates = contract.get("timeline_candidates")
    if not isinstance(timeline_candidates, list) or not timeline_candidates:
        findings.append("timeline_candidates must be a non-empty list")
    else:
        for item in timeline_candidates:
            if not isinstance(item, dict):
                findings.append("timeline_candidates entries must be objects")
                continue
            if item.get("action_permitted_now") is not False:
                findings.append("timeline_candidates action_permitted_now must be false")
            if not item.get("required_evidence"):
                findings.append("timeline_candidates must include required_evidence")

    handoff = contract.get("handoff")
    if not isinstance(handoff, dict):
        findings.append("handoff must be an object")
    else:
        if handoff.get("next_task") != "TASK-173":
            findings.append("handoff.next_task must be TASK-173")
        if handoff.get("ready_for_read_model") is not True:
            findings.append("handoff.ready_for_read_model must be true")

    for path, value in _walk(contract):
        if path.rsplit(".", 1)[-1] in FORBIDDEN_TRUE_KEYS and value is True:
            findings.append(f"{path} must not be true")

    for key in _key_names(contract):
        lowered = key.lower()
        if any(part in lowered for part in FORBIDDEN_KEY_PARTS):
            findings.append(f"forbidden private/secret/payment key name: {key}")

    for path, text in _string_values(contract):
        if _is_blocked_context(path):
            continue
        lowered_text = text.lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase in lowered_text:
                findings.append(f"forbidden advice/action phrase: {phrase}")

    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Finance Scenario Input Contract")
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    findings = validate_contract(load_contract(args.contract))
    if findings:
        for finding in findings:
            print(f"ERROR: {finding}")
        return 1
    print("OK: finance scenario input contract gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
