from __future__ import annotations

import copy

from scripts.sns_publishing_automation_readiness_backlog_gate import (
    load_backlog,
    validate_backlog,
)


def _backlog() -> dict:
    return load_backlog()


def test_current_backlog_passes():
    assert validate_backlog(_backlog()) == []


def test_rejects_source_hash_mismatch():
    backlog = _backlog()
    backlog["source_inputs"][0]["sha256"] = "0" * 64

    findings = validate_backlog(backlog)

    assert any("sha256 mismatch" in finding for finding in findings)


def test_rejects_missing_required_channel():
    backlog = copy.deepcopy(_backlog())
    backlog["channel_readiness"] = [
        item for item in backlog["channel_readiness"] if item["channel_id"] != "linkedin_share"
    ]

    findings = validate_backlog(backlog)

    assert any("channel_readiness missing channel ids" in finding for finding in findings)


def test_rejects_invalid_classification():
    backlog = _backlog()
    backlog["channel_readiness"][0]["classification"] = "auto_post_now"

    findings = validate_backlog(backlog)

    assert any("classification must be one of" in finding for finding in findings)


def test_rejects_live_post_enabled():
    backlog = _backlog()
    backlog["channel_readiness"][0]["live_post_enabled"] = True

    findings = validate_backlog(backlog)

    assert any("live_post_enabled must be false" in finding for finding in findings)


def test_rejects_platform_api_call_enabled():
    backlog = _backlog()
    backlog["channel_readiness"][0]["platform_api_call_enabled"] = True

    findings = validate_backlog(backlog)

    assert any("platform_api_call_enabled must be false" in finding for finding in findings)


def test_rejects_forbidden_secret_key():
    backlog = _backlog()
    backlog["channel_readiness"][0]["access_token"] = "placeholder"

    findings = validate_backlog(backlog)

    assert any("forbidden live/customer/secret key names" in finding for finding in findings)


def test_rejects_missing_queue_field():
    backlog = copy.deepcopy(_backlog())
    backlog["local_queue_contract"]["required_fields"] = [
        item for item in backlog["local_queue_contract"]["required_fields"] if item != "source_hash"
    ]

    findings = validate_backlog(backlog)

    assert any("local_queue_contract.required_fields missing" in finding for finding in findings)


def test_rejects_network_dry_run():
    backlog = _backlog()
    backlog["no_network_dry_run_contract"]["external_network_calls"] = True

    findings = validate_backlog(backlog)

    assert any("external_network_calls must be false" in finding for finding in findings)


def test_rejects_missing_no_network_test():
    backlog = copy.deepcopy(_backlog())
    backlog["no_network_test_plan"] = [
        item for item in backlog["no_network_test_plan"] if item["test_id"] != "forbidden_automation_terms_blocked"
    ]

    findings = validate_backlog(backlog)

    assert any("no_network_test_plan missing test ids" in finding for finding in findings)


def test_rejects_missing_r3_backlog_item():
    backlog = copy.deepcopy(_backlog())
    backlog["implementation_backlog"] = [
        item for item in backlog["implementation_backlog"] if item["reversibility_level"] != "R3"
    ]

    findings = validate_backlog(backlog)

    assert any("implementation_backlog must include R3" in finding for finding in findings)


def test_rejects_live_publication_handoff():
    backlog = _backlog()
    backlog["taskset_handoff"]["live_publication_approved"] = True

    findings = validate_backlog(backlog)

    assert any("taskset_handoff.live_publication_approved must be false" in finding for finding in findings)
