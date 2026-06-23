"""Validate the membership payment recognition decision packet.

This gate checks local decision structure only. It must not connect to a bank,
Open Banking, a payment provider, Supabase, a deployment target, or a secret
store, and it must not process real payment records.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKET = (
    REPO_ROOT
    / "agents"
    / "project"
    / "MEMBERSHIP-PAYMENT-RECOGNITION-DECISION-PACKET.json"
)

REQUIRED_OPTIONS = {
    "manual_bank_app_check",
    "code_assisted_deposit_match",
    "csv_import_review",
    "provider_receipt_reference",
    "pg_virtual_account_webhook",
    "open_banking_transaction_inquiry",
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

REQUIRED_STAGING_TESTS = {
    "public_lookup_hides_payment_evidence",
    "raw_bank_statement_not_persisted",
    "code_assisted_match_requires_owner_activation",
    "csv_import_discards_raw_after_review",
    "provider_webhook_requires_signature_or_ip_verification",
    "provider_webhook_is_idempotent",
    "provider_webhook_handles_delayed_or_corrected_notification",
    "open_banking_disabled_without_approval",
    "refund_receipt_tax_boundary_marked_watch",
}

REQUIRED_LAUNCH_GATES = {
    "decision_packet_gate_passes",
    "payment_evidence_policy_gate_passes",
    "payment_method_selected_for_stage",
    "retention_period_and_delete_path_reviewed",
    "refund_receipt_tax_boundary_professional_review",
    "privacy_notice_and_consent_reviewed",
    "pg_contract_or_open_banking_approval_if_used",
    "staging_non_disclosure_tests_pass",
    "can_launch_remains_false_until_r3_evidence",
}

REQUIRED_BOUNDARIES = {
    "not_applied_to_production",
    "no_bank_account_setup",
    "no_bank_login",
    "no_api_credential",
    "no_payment_provider_action",
    "no_real_payment_data",
    "no_raw_bank_statement_persisted",
    "no_legal_tax_accounting_final_advice",
    "keeps_can_launch_false",
}

FORBIDDEN_KEY_NAMES = {
    "bank_account_number",
    "full_bank_account_number",
    "raw_statement",
    "raw_bank_statement",
    "payment_provider_secret",
    "api_credential",
    "api_key",
    "client_secret",
    "real_payment_record",
    "open_banking_client_id",
    "pg_merchant_id",
    "supabase_project_id",
    "production_apply_completed",
}


def load_packet(path: Path = DEFAULT_PACKET) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("decision packet root must be an object")
    return data


def validate_packet(packet: dict[str, Any]) -> list[str]:
    findings: list[str] = []

    forbidden_paths = list(_find_forbidden_keys(packet))
    if forbidden_paths:
        findings.append(f"forbidden payment/production keys present: {forbidden_paths}")

    if packet.get("$schema") != "autofolio.membership-payment-recognition-decision-packet/v1":
        findings.append("unexpected or missing decision packet schema")

    status = str(packet.get("status", ""))
    if "not_applied" not in status:
        findings.append("packet status must clearly state it is not applied")

    boundaries = packet.get("boundaries")
    if not isinstance(boundaries, dict):
        findings.append("boundaries must be an object")
    else:
        for key in REQUIRED_BOUNDARIES:
            if boundaries.get(key) is not True:
                findings.append(f"boundaries.{key} must be true")

    source_text = " ".join(
        item.get("id", "") + " " + item.get("authority", "") + " " + item.get("url", "") + " " + item.get("note", "")
        for item in packet.get("source_basis", [])
        if isinstance(item, dict)
    )
    for marker in (
        "Financial Services Commission",
        "openbanking.or.kr",
        "Hometax",
        "privacy.go.kr",
        "virtual",
        "webhook",
        "KG Inicis",
    ):
        if marker.lower() not in source_text.lower():
            findings.append(f"source_basis missing marker: {marker}")

    summary = packet.get("decision_summary")
    if not isinstance(summary, dict):
        findings.append("decision_summary must be an object")
    else:
        if summary.get("mvp_method") != "manual_bank_app_check_plus_code_assisted_deposit_match":
            findings.append("decision_summary.mvp_method must select manual plus code-assisted matching")
        not_now = str(summary.get("not_now", ""))
        if "open_banking" not in not_now:
            findings.append("decision_summary.not_now must keep Open Banking out of MVP")

    options = packet.get("options")
    option_map: dict[str, dict[str, Any]] = {}
    if not isinstance(options, list):
        findings.append("options must be a list")
    else:
        option_map = {item.get("id"): item for item in options if isinstance(item, dict)}
        missing = REQUIRED_OPTIONS - set(option_map)
        if missing:
            findings.append(f"missing payment recognition options: {sorted(missing)}")
        for option_id, item in option_map.items():
            if item.get("raw_source_persisted") is not False:
                findings.append(f"{option_id}: raw_source_persisted must be false")
            if item.get("stores_real_payment_data") is not False:
                findings.append(f"{option_id}: stores_real_payment_data must be false")

    manual = option_map.get("manual_bank_app_check")
    if manual and manual.get("decision") != "selected_mvp":
        findings.append("manual_bank_app_check must be selected_mvp")

    assisted = option_map.get("code_assisted_deposit_match")
    if assisted and assisted.get("decision") != "selected_mvp_helper":
        findings.append("code_assisted_deposit_match must be selected_mvp_helper")

    pg = option_map.get("pg_virtual_account_webhook")
    if pg:
        if pg.get("external_action_required") is not True:
            findings.append("pg_virtual_account_webhook must require external action")
        if "selected" in str(pg.get("decision", "")) and "after_owner_approval" not in str(pg.get("decision", "")):
            findings.append("pg_virtual_account_webhook cannot be selected for immediate MVP")

    open_banking = option_map.get("open_banking_transaction_inquiry")
    if open_banking:
        decision = str(open_banking.get("decision", ""))
        if "blocked" not in decision or "r3" not in decision.lower():
            findings.append("open_banking_transaction_inquiry must stay blocked R3")
        if open_banking.get("external_action_required") is not True:
            findings.append("open_banking_transaction_inquiry must require external action")

    selected = packet.get("selected_mvp")
    if not isinstance(selected, dict):
        findings.append("selected_mvp must be an object")
    else:
        if selected.get("method") != "manual_bank_app_check_plus_code_assisted_deposit_match":
            findings.append("selected_mvp.method must select manual plus code-assisted matching")
        activation_rule = str(selected.get("activation_rule", ""))
        if "explicit" not in activation_rule.lower() or "Owner" not in activation_rule:
            findings.append("selected_mvp.activation_rule must require explicit Owner/admin activation")

    missing_retained = REQUIRED_RETAINED_FIELDS - set(_string_list(packet.get("retained_fields")))
    if missing_retained:
        findings.append(f"missing retained fields: {sorted(missing_retained)}")

    missing_tests = REQUIRED_STAGING_TESTS - set(_string_list(packet.get("required_staging_tests")))
    if missing_tests:
        findings.append(f"missing required staging tests: {sorted(missing_tests)}")

    missing_gates = REQUIRED_LAUNCH_GATES - set(_string_list(packet.get("launch_gates")))
    if missing_gates:
        findings.append(f"missing launch gates: {sorted(missing_gates)}")

    forbidden_runtime = " ".join(_string_list(packet.get("forbidden_actions")))
    for marker in ("bank", "Open Banking", "PG", "credential", "real customer payment", "legal"):
        if marker not in forbidden_runtime:
            findings.append(f"forbidden_actions missing marker: {marker}")

    verification = packet.get("verification")
    if not isinstance(verification, dict):
        findings.append("verification must be an object")
    else:
        if "membership_payment_recognition_decision_gate.py --check" not in str(
            verification.get("local_decision_gate", "")
        ):
            findings.append("verification.local_decision_gate must reference this gate")

    return findings


def _find_forbidden_keys(value: Any, prefix: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}"
            if key in FORBIDDEN_KEY_NAMES:
                findings.append(path)
            findings.extend(_find_forbidden_keys(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(_find_forbidden_keys(child, f"{prefix}[{index}]"))
    return findings


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--check", action="store_true", help="validate and return non-zero on findings")
    args = parser.parse_args()

    packet = load_packet(args.packet)
    findings = validate_packet(packet)
    if findings:
        print("membership payment recognition decision gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print(f"membership payment recognition decision gate: PASS ({args.packet})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
