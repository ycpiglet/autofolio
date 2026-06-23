from __future__ import annotations

import json

from scripts.membership_railway_backend_readiness_gate import (
    DOCKERFILE,
    READINESS,
    validate_dockerfile_text,
    validate_files,
    validate_health_text,
    validate_readiness,
)


def test_current_railway_backend_readiness_passes() -> None:
    assert validate_files() == []


def test_rejects_fixed_dockerfile_port() -> None:
    text = DOCKERFILE.read_text(encoding="utf-8").replace("${PORT:-8000}", "8000")

    findings = validate_dockerfile_text(text)

    assert "dockerfile-missing-port-expansion" in findings
    assert "dockerfile-still-has-fixed-port" in findings


def test_rejects_missing_health_route() -> None:
    findings = validate_health_text("def create_app():\n    pass\n")

    assert "api-health-route-missing" in findings
    assert "api-health-ok-response-missing" in findings


def test_rejects_deployed_readiness_status(tmp_path) -> None:
    data = json.loads(READINESS.read_text(encoding="utf-8"))
    data["backend"]["deploy_status"] = "deployed"
    path = tmp_path / "readiness.json"
    path.write_text(json.dumps(data), encoding="utf-8")

    findings = validate_readiness(path)

    assert "readiness-must-remain-not-deployed" in findings
