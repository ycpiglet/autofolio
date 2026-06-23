from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_EXAMPLE = ROOT / ".env.example"
INVENTORY = ROOT / "agents" / "project" / "MEMBERSHIP-STAGING-ENV-INVENTORY.json"

REQUIRED_KEYS = {
    "AUTOFOLIO_ENV",
    "AUTOFOLIO_HOME",
    "PORT",
    "API_INTERNAL_URL",
    "AUTOFOLIO_PUBLIC_BASE_URL",
    "NEXT_PUBLIC_BASE_URL",
    "KIS_ENV",
    "AUTOFOLIO_LOCAL_AUTO_REGISTER",
    "AUTOFOLIO_GUEST_DEMO_ENABLED",
    "AUTOFOLIO_SSO_MOCK_ENABLED",
    "AUTOFOLIO_KIS_WS_ENABLE",
    "AUTOFOLIO_MEMBERSHIP_PRICE_KRW",
    "AUTOFOLIO_MEMBERSHIP_BANK_ACCOUNT",
    "AUTOFOLIO_SSO_ALLOWED_EMAILS",
    "GOOGLE_CLIENT_SECRET",
    "KAKAO_CLIENT_SECRET",
    "NAVER_CLIENT_SECRET",
    "SUPABASE_URL",
    "SUPABASE_PUBLISHABLE_KEY",
    "SUPABASE_SECRET_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "KIS_PAPER_APP_KEY",
    "KIS_PAPER_APP_SECRET",
    "KIS_PAPER_ACCOUNT_NO",
    "KIS_PROD_APP_KEY",
    "KIS_PROD_APP_SECRET",
    "KIS_PROD_ACCOUNT_NO",
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
    "TELEGRAM_BOT_TOKEN",
}

REQUIRED_DEFAULTS = {
    "KIS_ENV": "mock",
    "AUTOFOLIO_LOCAL_AUTO_REGISTER": "0",
    "AUTOFOLIO_GUEST_DEMO_ENABLED": "0",
    "AUTOFOLIO_SSO_MOCK_ENABLED": "0",
    "AUTOFOLIO_KIS_WS_ENABLE": "0",
    "AUTOFOLIO_MEMBERSHIP_PRICE_KRW": "0",
}

SECRET_MARKERS = (
    "SECRET",
    "TOKEN",
    "PASSWORD",
    "API_KEY",
    "APP_KEY",
    "CLIENT_SECRET",
    "SERVICE_ROLE",
    "ACCOUNT_NO",
    "BANK_ACCOUNT",
    "HTS_ID",
    "CHAT_ID",
    "ACCESS_TOKEN",
)

ALLOWED_NONEMPTY_SECRETLIKE_KEYS = {"KIS_ENV"}

SUSPICIOUS_VALUE_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"sk-[A-Za-z0-9_-]{8,}",
        r"ghp_[A-Za-z0-9_]{8,}",
        r"xox[baprs]-[A-Za-z0-9-]{8,}",
        r"AKIA[0-9A-Z]{12,}",
        r"ya29\.[A-Za-z0-9_-]{8,}",
        r"\d{2,6}-\d{2,6}-\d{2,8}",
        r"(?<![A-Za-z0-9])\d{10,}(?![A-Za-z0-9])",
        r"-----BEGIN [A-Z ]+PRIVATE KEY-----",
    )
]


def _parse_env(path: Path) -> tuple[dict[str, str], list[str]]:
    values: dict[str, str] = {}
    findings: list[str] = []
    if not path.exists():
        return values, [f"missing:{path}"]
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            findings.append(f"line:{line_no}:export-not-allowed")
            continue
        if "=" not in line:
            findings.append(f"line:{line_no}:missing-equals")
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", key):
            findings.append(f"line:{line_no}:invalid-key:{key}")
            continue
        if key in values:
            findings.append(f"line:{line_no}:duplicate-key:{key}")
        values[key] = value
    return values, findings


def _is_secretlike(key: str) -> bool:
    return any(marker in key for marker in SECRET_MARKERS)


def check_env_example(path: Path = ENV_EXAMPLE, *, require_required_keys: bool = True) -> list[str]:
    values, findings = _parse_env(path)
    if require_required_keys:
        missing = sorted(REQUIRED_KEYS - set(values))
        findings.extend(f"missing-required-key:{key}" for key in missing)
    for key, expected in REQUIRED_DEFAULTS.items():
        actual = values.get(key)
        if actual != expected:
            findings.append(f"bad-default:{key}:expected:{expected}:actual:{actual}")
    for key, value in values.items():
        if _is_secretlike(key) and key not in ALLOWED_NONEMPTY_SECRETLIKE_KEYS and value:
            findings.append(f"secretlike-key-has-value:{key}")
        if "<" in value or ">" in value:
            findings.append(f"placeholder-angle-value:{key}")
        for pattern in SUSPICIOUS_VALUE_PATTERNS:
            if value and pattern.search(value):
                findings.append(f"suspicious-value:{key}")
                break
    return findings


def check_inventory(path: Path = INVENTORY) -> list[str]:
    if not path.exists():
        return [f"missing:{path}"]
    data = json.loads(path.read_text(encoding="utf-8"))
    findings: list[str] = []
    if data.get("schema") != "autofolio.membership-staging-env-inventory/v1":
        findings.append("invalid-schema")
    if data.get("status") != "sanitized_template_only":
        findings.append("invalid-status")
    boundaries = data.get("boundaries", {})
    for key in (
        "no_secret_values",
        "no_external_env_write",
        "no_external_project_mutation",
        "no_deploy",
        "no_public_url_publish",
        "no_supabase_apply",
        "no_kis_activation",
        "no_payment_or_bank_api",
    ):
        if boundaries.get(key) is not True:
            findings.append(f"boundary-not-true:{key}")
    for key, expected in REQUIRED_DEFAULTS.items():
        actual = data.get("fail_closed_defaults", {}).get(key)
        if actual != expected:
            findings.append(f"inventory-bad-default:{key}")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--env-file", default=str(ENV_EXAMPLE))
    parser.add_argument("--inventory", default=str(INVENTORY))
    args = parser.parse_args()

    findings = check_env_example(Path(args.env_file))
    findings.extend(check_inventory(Path(args.inventory)))
    if findings:
        print("membership staging env inventory gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"membership staging env inventory gate: PASS ({args.env_file})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
