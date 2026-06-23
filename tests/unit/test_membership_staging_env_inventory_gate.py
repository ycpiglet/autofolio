from __future__ import annotations

import json

from scripts.membership_staging_env_inventory_gate import (
    ENV_EXAMPLE,
    INVENTORY,
    check_env_example,
    check_inventory,
)


def _baseline_env_text() -> str:
    return ENV_EXAMPLE.read_text(encoding="utf-8")


def test_current_env_example_and_inventory_pass() -> None:
    assert check_env_example(ENV_EXAMPLE) == []
    assert check_inventory(INVENTORY) == []


def test_rejects_secretlike_value(tmp_path) -> None:
    path = tmp_path / ".env.example"
    path.write_text(
        _baseline_env_text().replace("KIS_PAPER_APP_KEY=", "KIS_PAPER_APP_KEY=sk-realish-value"),
        encoding="utf-8",
    )

    findings = check_env_example(path)

    assert "secretlike-key-has-value:KIS_PAPER_APP_KEY" in findings
    assert "suspicious-value:KIS_PAPER_APP_KEY" in findings


def test_rejects_fail_open_defaults(tmp_path) -> None:
    path = tmp_path / ".env.example"
    path.write_text(
        _baseline_env_text()
        .replace("KIS_ENV=mock", "KIS_ENV=paper")
        .replace("AUTOFOLIO_GUEST_DEMO_ENABLED=0", "AUTOFOLIO_GUEST_DEMO_ENABLED=1"),
        encoding="utf-8",
    )

    findings = check_env_example(path)

    assert "bad-default:KIS_ENV:expected:mock:actual:paper" in findings
    assert "bad-default:AUTOFOLIO_GUEST_DEMO_ENABLED:expected:0:actual:1" in findings


def test_rejects_inventory_boundary_flip(tmp_path) -> None:
    data = json.loads(INVENTORY.read_text(encoding="utf-8"))
    data["boundaries"]["no_deploy"] = False
    path = tmp_path / "inventory.json"
    path.write_text(json.dumps(data), encoding="utf-8")

    findings = check_inventory(path)

    assert "boundary-not-true:no_deploy" in findings
