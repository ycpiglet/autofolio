from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCKERFILE = ROOT / "Dockerfile"
MAIN = ROOT / "app" / "api" / "main.py"
READINESS = ROOT / "agents" / "project" / "MEMBERSHIP-RAILWAY-BACKEND-READINESS.json"


def validate_dockerfile_text(text: str) -> list[str]:
    findings: list[str] = []
    if "--host 0.0.0.0" not in text:
        findings.append("dockerfile-missing-0.0.0.0-host")
    if "--port ${PORT:-8000}" not in text:
        findings.append("dockerfile-missing-port-expansion")
    if '"8000"]' in text or "--port 8000" in text:
        findings.append("dockerfile-still-has-fixed-port")
    if 'CMD ["sh", "-c"' not in text:
        findings.append("dockerfile-cmd-must-use-shell-expansion")
    return findings


def validate_health_text(text: str) -> list[str]:
    findings: list[str] = []
    if '@app.get("/api/health"' not in text:
        findings.append("api-health-route-missing")
    if 'HealthResponse(status="ok")' not in text:
        findings.append("api-health-ok-response-missing")
    return findings


def validate_readiness(path: Path = READINESS) -> list[str]:
    if not path.exists():
        return [f"missing:{path}"]
    data = json.loads(path.read_text(encoding="utf-8"))
    findings: list[str] = []
    if data.get("schema") != "autofolio.membership-railway-backend-readiness/v1":
        findings.append("invalid-schema")
    if data.get("status") != "local_readiness_not_deployed":
        findings.append("invalid-status")
    boundaries = data.get("boundaries", {})
    for key in (
        "no_railway_deploy",
        "no_external_project_mutation",
        "no_external_env_write",
        "no_public_url_publish",
        "no_secret_values",
        "no_supabase_apply",
        "no_kis_or_payment_activation",
    ):
        if boundaries.get(key) is not True:
            findings.append(f"boundary-not-true:{key}")
    backend = data.get("backend", {})
    if backend.get("port_binding") != "${PORT:-8000}":
        findings.append("readiness-bad-port-binding")
    if backend.get("healthcheck_path") != "/api/health":
        findings.append("readiness-bad-healthcheck-path")
    if backend.get("deploy_status") != "not_deployed":
        findings.append("readiness-must-remain-not-deployed")
    return findings


def validate_files(
    dockerfile: Path = DOCKERFILE, main: Path = MAIN, readiness: Path = READINESS
) -> list[str]:
    findings: list[str] = []
    findings.extend(validate_dockerfile_text(dockerfile.read_text(encoding="utf-8")))
    findings.extend(validate_health_text(main.read_text(encoding="utf-8")))
    findings.extend(validate_readiness(readiness))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    findings = validate_files()
    if findings:
        print("membership Railway backend readiness gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"membership Railway backend readiness gate: PASS ({DOCKERFILE})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
