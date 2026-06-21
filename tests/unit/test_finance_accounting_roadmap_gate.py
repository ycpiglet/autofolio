from __future__ import annotations

import copy

from scripts.finance_accounting_roadmap_gate import load_roadmap, validate_roadmap


def _roadmap() -> dict:
    return load_roadmap()


def test_current_roadmap_passes():
    assert validate_roadmap(_roadmap()) == []


def test_rejects_financial_advice_status():
    roadmap = _roadmap()
    roadmap["status"] = "financial_advice_ready"

    findings = validate_roadmap(roadmap)

    assert any("status must be" in finding for finding in findings)


def test_rejects_missing_portfolio_source():
    roadmap = _roadmap()
    del roadmap["source_artifacts"]["portfolio_overview_api"]

    findings = validate_roadmap(roadmap)

    assert any("source_artifacts missing" in finding for finding in findings)


def test_rejects_disabled_boundary():
    roadmap = _roadmap()
    roadmap["boundary"]["no_order_execution"] = False

    findings = validate_roadmap(roadmap)

    assert any("boundary.no_order_execution must be true" in finding for finding in findings)


def test_rejects_current_fact_example_drift():
    roadmap = _roadmap()
    roadmap["planning_question"]["example_is_not_current_portfolio_fact"] = False

    findings = validate_roadmap(roadmap)

    assert any("not current portfolio fact" in finding for finding in findings)


def test_rejects_missing_metric():
    roadmap = copy.deepcopy(_roadmap())
    roadmap["metric_contract"] = [
        item for item in roadmap["metric_contract"] if item["id"] != "gap_to_plan_pct_points"
    ]

    findings = validate_roadmap(roadmap)

    assert any("metric_contract missing" in finding for finding in findings)


def test_rejects_missing_gap_category():
    roadmap = _roadmap()
    roadmap["gap_categories"].remove("tax_receipt_refund_policy_gap")

    findings = validate_roadmap(roadmap)

    assert any("gap_categories missing" in finding for finding in findings)


def test_rejects_portfolio_output_without_no_trade_instruction():
    roadmap = copy.deepcopy(_roadmap())
    for item in roadmap["roadmap_outputs"]:
        if item["id"] == "portfolio_review_candidates":
            item["must_include"].remove("no_trade_instruction")

    findings = validate_roadmap(roadmap)

    assert any("no_trade_instruction" in finding for finding in findings)


def test_rejects_action_enabled_flag():
    roadmap = _roadmap()
    roadmap["order_execution_enabled"] = True

    findings = validate_roadmap(roadmap)

    assert any("order_execution_enabled" in finding for finding in findings)


def test_rejects_forbidden_private_key_name():
    roadmap = _roadmap()
    roadmap["raw_statement_text"] = "redacted"

    findings = validate_roadmap(roadmap)

    assert any("forbidden private/secret/payment key name" in finding for finding in findings)


def test_rejects_forbidden_advice_phrase():
    roadmap = _roadmap()
    roadmap["notes"] = "You should buy this position."

    findings = validate_roadmap(roadmap)

    assert any("forbidden advice/action phrase" in finding for finding in findings)


def test_rejects_missing_followup_task():
    roadmap = copy.deepcopy(_roadmap())
    roadmap["next_tasks"] = [
        item for item in roadmap["next_tasks"] if item["task_id"] != "TASK-173"
    ]

    findings = validate_roadmap(roadmap)

    assert any("next_tasks missing" in finding for finding in findings)
