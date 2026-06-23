"""Validate the membership payment evidence policy asset.

This gate checks local policy structure only. It must not connect to a bank,
payment provider, Supabase, OAuth provider, deployment target, or secret store.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = REPO_ROOT / "agents" / "project" / "MEMBERSHIP-PAYMENT-EVIDENCE-POLICY.json"

REQUIRED_SOURCES = {
    "manual_bank_app_check",
    "code_assisted_deposit_match",
    "csv_import_review",
    "provider_receipt_reference",
}

REQUIRED_FORBIDDEN = {
    "raw_bank_statement_text",
    "full_bank_account_number",
    "resident_registration_number",
    "card_number",
    "bank_login_credential",
    "payment_provider_secret",
    "unredacted_customer_identifier",
    "freeform_owner_note_with_payment_private_data",
}

REQUIRED_RETAINED_FIELDS = {
    "membership_request_id",
    "target_user_id",
    "actor_user_id",
    "approval_event_id",
    "evidence_type",
    "deposit_code",
    "amount_krw",
    "currency",
    "source_type",
    "source_reference",
    "masked_excerpt",
    "confidence",
    "recorded_at",
}

REQUIRED_REDACTION_RULES = {
    "mask_bank_account_like_numbers",
    "mask_personal_identifier_like_numbers",
    "bound_text_excerpt",
}

REQUIRED_INVARIANTS = {
    "raw_pasted_statement_not_persisted_by_default",
    "payment_evidence_minimal_fields_only",
    "applicant_public_lookup_hides_owner_evidence",
    "activation_requires_explicit_privileged_action",
    "no_real_bank_account_in_repo",
    "refund_receipt_tax_boundary_separate_record",
}

REQUIRED_LAUNCH_GATES = {
    "policy_gate_passes",
    "production_data_model_maps_retained_fields",
    "retention_period_and_delete_path_reviewed",
    "refund_receipt_tax_boundary_recorded",
    "payment_recognition_method_selected",
    "staging_privacy_non_disclosure_tests_pass",
}

FORBIDDEN_TOP_LEVEL_KEYS = {
    "bank_account_number",
    "raw_statement",
    "payment_provider_secret",
    "production_apply_completed",
    "supabase_project_id",
}


def load_policy(path: Path = DEFAULT_POLICY) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("policy root must be an object")
    return data


def validate_policy(policy: dict[str, Any]) -> list[str]:
    findings: list[str] = []

    forbidden_present = FORBIDDEN_TOP_LEVEL_KEYS.intersection(policy)
    if forbidden_present:
        findings.append(f"forbidden production/private keys present: {sorted(forbidden_present)}")

    if policy.get("$schema") != "autofolio.membership-payment-evidence-policy/v1":
        findings.append("unexpected or missing policy schema")

    status = str(policy.get("status", ""))
    if "not_applied" not in status:
        findings.append("policy status must clearly state it is not applied")

    sources = policy.get("allowed_evidence_sources")
    if not isinstance(sources, list):
        findings.append("allowed_evidence_sources must be a list")
        source_ids: set[str] = set()
    else:
        source_ids = {item.get("id") for item in sources if isinstance(item, dict)}
        missing = REQUIRED_SOURCES - source_ids
        if missing:
            findings.append(f"missing allowed evidence sources: {sorted(missing)}")
        for item in sources:
            if not isinstance(item, dict):
                continue
            if item.get("raw_source_persisted") is not False:
                findings.append(f"{item.get('id', '<unknown>')}: raw_source_persisted must be false")

    missing_forbidden = REQUIRED_FORBIDDEN - set(_string_list(policy.get("forbidden_evidence")))
    if missing_forbidden:
        findings.append(f"missing forbidden evidence entries: {sorted(missing_forbidden)}")

    missing_retained = REQUIRED_RETAINED_FIELDS - set(_string_list(policy.get("retained_fields")))
    if missing_retained:
        findings.append(f"missing retained fields: {sorted(missing_retained)}")

    redaction_ids = {
        item.get("id")
        for item in policy.get("redaction_rules", [])
        if isinstance(item, dict)
    }
    missing_redaction = REQUIRED_REDACTION_RULES - redaction_ids
    if missing_redaction:
        findings.append(f"missing redaction rules: {sorted(missing_redaction)}")

    invariant_ids = {
        item.get("id")
        for item in policy.get("audit_invariants", [])
        if isinstance(item, dict)
    }
    missing_invariants = REQUIRED_INVARIANTS - invariant_ids
    if missing_invariants:
        findings.append(f"missing audit invariants: {sorted(missing_invariants)}")

    missing_gates = REQUIRED_LAUNCH_GATES - set(_string_list(policy.get("launch_gates")))
    if missing_gates:
        findings.append(f"missing launch gates: {sorted(missing_gates)}")

    return findings


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--check", action="store_true", help="validate and return non-zero on findings")
    args = parser.parse_args()

    policy = load_policy(args.policy)
    findings = validate_policy(policy)
    if findings:
        print("membership payment policy gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print(f"membership payment policy gate: PASS ({args.policy})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
