from __future__ import annotations

import copy

from scripts.marketing_team_operating_model_gate import load_model, validate_model


def _model() -> dict:
    return load_model()


def test_current_model_passes():
    assert validate_model(_model()) == []


def test_rejects_missing_marketing_growth_role():
    model = _model()
    model["team_roles"] = [
        item for item in model["team_roles"] if item["role_id"] != "marketing-growth"
    ]

    findings = validate_model(model)

    assert any("team_roles missing role_ids" in finding for finding in findings)


def test_rejects_empty_role_outputs():
    model = _model()
    model["team_roles"][0]["outputs"] = []

    findings = validate_model(model)

    assert any("outputs must be non-empty" in finding for finding in findings)


def test_rejects_workflow_external_action():
    model = _model()
    model["workflow"][0]["external_action_enabled"] = True

    findings = validate_model(model)

    assert any("external_action_enabled must be false" in finding for finding in findings)


def test_rejects_missing_campaign_route():
    model = _model()
    model["routing_rules"] = [
        item for item in model["routing_rules"] if item["request_type"] != "campaign_copy_or_content_calendar"
    ]

    findings = validate_model(model)

    assert any("campaign_copy_or_content_calendar" in finding for finding in findings)


def test_rejects_missing_compliance_trigger():
    model = _model()
    model["compliance_review_triggers"] = [
        item for item in model["compliance_review_triggers"] if item != "paid signal wording"
    ]

    findings = validate_model(model)

    assert any("compliance_review_triggers missing" in finding for finding in findings)


def test_rejects_missing_owner_r3_trigger():
    model = _model()
    model["owner_r3_triggers"] = [
        item for item in model["owner_r3_triggers"] if item != "SNS upload"
    ]

    findings = validate_model(model)

    assert any("owner_r3_triggers missing" in finding for finding in findings)


def test_rejects_boundary_disabled():
    model = _model()
    model["boundaries"]["no_public_post"] = False

    findings = validate_model(model)

    assert any("boundaries.no_public_post must be true" in finding for finding in findings)


def test_rejects_live_publication_approval():
    model = _model()
    model["taskset_handoff"]["live_publication_approved"] = True

    findings = validate_model(model)

    assert any("live or external action flags must not be true" in finding for finding in findings)


def test_rejects_customer_secret_key_name():
    model = copy.deepcopy(_model())
    model["team_roles"][0]["customer_email"] = "none@example.invalid"

    findings = validate_model(model)

    assert any("forbidden secret/customer/payment key names" in finding for finding in findings)


def test_rejects_missing_downstream_start_criteria():
    model = _model()
    model["downstream_task_start_criteria"]["TASK-167"] = []

    findings = validate_model(model)

    assert any("downstream_task_start_criteria.TASK-167" in finding for finding in findings)


def test_rejects_missing_forbidden_action():
    model = _model()
    model["forbidden_actions"] = [
        item for item in model["forbidden_actions"] if item != "platform API call"
    ]

    findings = validate_model(model)

    assert any("forbidden_actions missing" in finding for finding in findings)
