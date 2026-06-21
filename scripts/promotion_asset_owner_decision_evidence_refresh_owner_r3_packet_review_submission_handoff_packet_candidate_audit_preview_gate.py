"""Validate the TASK-155 handoff packet candidate audit preview.

This gate validates local audit/readiness preview metadata only. It rejects
actual Owner/R3 review submission, review start, evidence refresh execution,
approval records, signatures, approval evidence collection, public approval,
final exports, customer/CRM/payment action, external account action, platform
calls, secrets, and drift from the source handoff packet candidate.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PREVIEW = (
    REPO_ROOT
    / "agents"
    / "project"
    / "PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-REVIEW-SUBMISSION-HANDOFF-PACKET-CANDIDATE-AUDIT-PREVIEW.json"
)
SOURCE_CANDIDATE_PATH = (
    REPO_ROOT
    / "agents"
    / "project"
    / "PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-REVIEW-SUBMISSION-HANDOFF-PACKET-CANDIDATE.json"
)
SOURCE_ID = "promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate"
SOURCE_REL = (
    "agents/project/PROMOTION-ASSET-OWNER-DECISION-EVIDENCE-REFRESH-OWNER-R3-PACKET-REVIEW-SUBMISSION-HANDOFF-PACKET-CANDIDATE.json"
)


def _load_candidate_gate() -> Any:
    path = REPO_ROOT / "scripts" / "promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_gate.py"
    spec = importlib.util.spec_from_file_location("handoff_packet_candidate_gate", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import source candidate gate from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CANDIDATE_GATE = _load_candidate_gate()

REQUIRED_DECISION_TYPES = set(CANDIDATE_GATE.REQUIRED_DECISION_TYPES)
REQUIRED_BLOCKED_SCAN_KEYS = set(CANDIDATE_GATE.REQUIRED_BLOCKED_SCAN_KEYS)
REQUIRED_FORBIDDEN_OUTPUTS = set(CANDIDATE_GATE.REQUIRED_FORBIDDEN_OUTPUTS)
FORBIDDEN_KEY_NAMES = set(CANDIDATE_GATE.FORBIDDEN_KEY_NAMES)
LIVE_TRUE_KEYS = set(CANDIDATE_GATE.LIVE_TRUE_KEYS) | {
    "handoff_packet_candidate_audit_is_submission",
    "handoff_packet_candidate_audit_is_approval",
    "handoff_packet_includes_actual_input_values",
    "audit_preview_is_approval",
    "audit_preview_is_submission",
}

REQUIRED_BOUNDARIES = {
    "local_owner_r3_packet_review_submission_handoff_packet_candidate_audit_readiness_preview_only",
    "handoff_packet_candidate_audit_not_submission",
    "handoff_packet_candidate_not_submission",
    "handoff_packet_candidate_audit_not_approval",
    "handoff_packet_candidate_not_approval",
    "source_preflight_audit_not_submission",
    "source_preflight_audit_not_approval",
    "source_preflight_not_submission",
    "source_preflight_not_approval",
    "review_queue_audit_not_approval",
    "review_queue_not_approval",
    "not_actual_owner_r3_review_submission",
    "not_actual_owner_review_started",
    "not_actual_refresh_execution",
    "not_actual_owner_approval_record",
    "not_actual_owner_signature",
    "not_actual_approval_evidence_collection",
    "not_publication_approval",
    "no_public_use_clearance",
    "not_legal_tax_securities_final_advice",
    "no_final_pdf_export",
    "no_final_pptx_export",
    "no_public_url_or_upload",
    "no_sns_upload",
    "no_customer_contact",
    "no_customer_private_data",
    "no_crm_or_payment_action",
    "no_secret_or_token_storage",
    "no_external_account_action",
    "no_oauth_flow",
    "no_platform_api_call",
    "no_kis_order_risk_prod_deploy_change",
    "owner_approval_required_before_public_use",
    "professional_review_required_before_reliance",
}

REQUIRED_SUMMARY_COUNTS = {
    "decision_types": 9,
    "source_handoff_packet_records": 9,
    "handoff_packet_record_summaries": 9,
    "owner_r3_required_input_summaries": 9,
    "unresolved_blocker_summaries": 9,
    "invalidating_trigger_summaries": 9,
    "source_preflight_state_safety_scan_items": 6,
    "source_queue_state_safety_scan_items": 6,
    "source_state_reference_summaries": 5,
    "source_trigger_reference_summaries": 8,
    "handoff_packet_assembly_steps": 7,
    "blocked_action_scan_items": 13,
    "total_source_required_evidence_items": 25,
    "total_source_stale_evidence_trigger_items": 27,
    "total_source_invalidating_event_items": 36,
    "records_requiring_owner_r3": 9,
    "records_with_non_submission_status": 9,
    "records_with_non_approval_status": 9,
    "records_with_owner_review_not_started": 9,
    "records_with_public_use_blocked": 9,
    "records_with_final_export_blocked": 9,
    "records_with_external_action_blocked": 9,
    "records_with_customer_contact_blocked": 9,
    "records_with_crm_payment_blocked": 9,
    "records_with_secret_material_blocked": 9,
    "records_with_final_advice_blocked": 9,
    "records_with_kis_order_risk_prod_deploy_blocked": 9,
    "owner_r3_inputs_missing": 9,
    "unresolved_blockers_active": 9,
    "invalidating_triggers_blocked_from_refresh_or_submission": 9,
    "blocked_scan_items_passed": 13,
    "ready_for_owner_r3_submission_records": 0,
    "ready_for_public_use_records": 0,
    "actual_review_started_records": 0,
    "actual_review_submissions": 0,
    "actual_refresh_executions": 0,
    "actual_owner_approval_records": 0,
    "actual_owner_signatures": 0,
    "actual_approval_evidence_records": 0,
    "actual_public_approvals": 0,
    "final_export_outputs": 0,
    "public_publication_outputs": 0,
    "customer_or_payment_outputs": 0,
    "secret_or_token_outputs": 0,
    "final_advice_outputs": 0,
    "live_action_states": 0,
}

REQUIRED_AUDIT_EVENTS = {
    "handoff_packet_candidate_audit_preview_generated",
    "source_handoff_packet_candidate_hash_recorded",
    "handoff_packet_record_summaries_audited",
    "owner_r3_required_inputs_audited",
    "unresolved_blockers_audited",
    "invalidating_trigger_coverage_audited",
    "source_reference_coverage_audited",
    "blocked_action_scan_passed",
}


def load_preview(path: Path = DEFAULT_PREVIEW) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("promotion asset Owner/R3 handoff packet candidate audit preview root must be an object")
    return data


def validate_preview(preview: dict[str, Any], repo_root: Path = REPO_ROOT) -> list[str]:
    source = _load_json(SOURCE_CANDIDATE_PATH)
    findings: list[str] = []

    source_findings = CANDIDATE_GATE.validate_candidate(source, repo_root)
    if source_findings:
        findings.append(f"source handoff packet candidate gate must pass: {source_findings}")

    if preview.get("$schema") != (
        "autofolio.promotion-asset-owner-decision-evidence-refresh-owner-r3-packet-review-submission-handoff-packet-candidate-audit-preview/v1"
    ):
        findings.append("unexpected or missing promotion asset Owner/R3 handoff packet candidate audit preview schema")
    if preview.get("status") != "local_owner_r3_packet_review_submission_handoff_packet_candidate_audit_readiness_preview_not_actual_submission":
        findings.append(
            "status must be local_owner_r3_packet_review_submission_handoff_packet_candidate_audit_readiness_preview_not_actual_submission"
        )

    findings.extend(_validate_boundaries(preview))
    findings.extend(_validate_sources(preview, repo_root))
    findings.extend(_validate_markdown(preview, repo_root))
    findings.extend(_validate_summary(preview, source))
    findings.extend(_validate_source_copies(preview, source))
    findings.extend(_validate_decision_coverage(preview))
    findings.extend(_validate_blocked_scan(preview, source))
    findings.extend(_validate_audit_events(preview))
    findings.extend(_validate_forbidden_outputs(preview))
    findings.extend(_validate_handoff(preview))
    findings.extend(_validate_verification(preview))

    forbidden_keys = _find_forbidden_keys(preview)
    if forbidden_keys:
        findings.append(
            "forbidden review-submission/approval/signature/export/customer/secret/final-advice key names "
            f"present: {forbidden_keys}"
        )
    live_true_paths = _find_live_true_keys(preview)
    if live_true_paths:
        findings.append(
            "review-start/submission/refresh/approval/signature/public/export/customer/payment/platform/"
            f"final-advice/live flags must not be true: {live_true_paths}"
        )
    return findings


def _validate_boundaries(preview: dict[str, Any]) -> list[str]:
    boundaries = preview.get("boundaries")
    if not isinstance(boundaries, dict):
        return ["boundaries must be an object"]
    return [f"boundaries.{key} must be true" for key in REQUIRED_BOUNDARIES if boundaries.get(key) is not True]


def _validate_sources(preview: dict[str, Any], repo_root: Path) -> list[str]:
    inputs = preview.get("source_inputs")
    if not isinstance(inputs, list):
        return ["source_inputs must be a list"]
    findings: list[str] = []
    source_ids = {item.get("id") for item in inputs if isinstance(item, dict)}
    if SOURCE_ID not in source_ids:
        findings.append(f"source_inputs missing ids: {[SOURCE_ID]}")
    for index, item in enumerate(inputs):
        if not isinstance(item, dict):
            findings.append(f"source_inputs[{index}] must be an object")
            continue
        if item.get("id") == SOURCE_ID and item.get("path") != SOURCE_REL:
            findings.append(f"source_inputs[{index}].path for {SOURCE_ID} must be {SOURCE_REL}")
        try:
            path = _safe_repo_path(repo_root, str(item.get("path", "")))
        except ValueError as exc:
            findings.append(f"source_inputs[{index}].path invalid: {exc}")
            continue
        if not path.exists():
            findings.append(f"source_inputs[{index}].path missing: {item.get('path')}")
            continue
        if str(item.get("sha256", "")).lower() != _sha256(path):
            findings.append(f"source_inputs[{index}].sha256 mismatch for {item.get('path')}")
    return findings


def _validate_markdown(preview: dict[str, Any], repo_root: Path) -> list[str]:
    try:
        path = _safe_repo_path(repo_root, str(preview.get("companion_markdown", "")))
    except ValueError as exc:
        return [f"companion_markdown invalid: {exc}"]
    if not path.exists():
        return [f"companion_markdown missing: {preview.get('companion_markdown')}"]
    text = path.read_text(encoding="utf-8").lower()
    required = (
        "handoff packet candidate audit/readiness preview",
        "handoff packet candidate audit not submission",
        "handoff packet candidate audit not approval",
        "handoff packet candidate not submission",
        "handoff packet candidate not approval",
        "source preflight audit not submission",
        "source preflight audit not approval",
        "not actual owner/r3 review submission",
        "not actual owner/r3 review start",
        "not actual owner approval",
        "not actual owner signature",
        "not actual approval evidence",
        "handoff packet record summaries",
        "owner/r3 required input summaries",
        "unresolved blocker summaries",
        "invalidating trigger summaries",
        "source reference coverage",
        "blocked action scan",
    )
    return [f"companion_markdown must mention {item}" for item in required if item not in text]


def _validate_summary(preview: dict[str, Any], source: dict[str, Any]) -> list[str]:
    summary = preview.get("audit_summary")
    if not isinstance(summary, dict):
        return ["audit_summary must be an object"]
    findings = [f"audit_summary.{key} must be {value}" for key, value in REQUIRED_SUMMARY_COUNTS.items() if summary.get(key) != value]
    if summary.get("source_handoff_packet_candidate") != source.get("candidate_id"):
        findings.append("audit_summary.source_handoff_packet_candidate must match source candidate_id")
    if summary.get("source_candidate_status") != source.get("status"):
        findings.append("audit_summary.source_candidate_status must match source status")
    if summary.get("gate_result") != "pass":
        findings.append("audit_summary.gate_result must be pass")
    source_summary = source.get("candidate_summary", {})
    for key in (
        "total_source_required_evidence_items",
        "total_source_stale_evidence_trigger_items",
        "total_source_invalidating_event_items",
        "actual_review_started_records",
        "actual_review_submissions",
        "actual_refresh_executions",
        "actual_owner_approval_records",
        "actual_owner_signatures",
        "actual_approval_evidence_records",
        "actual_public_approvals",
        "final_export_outputs",
        "public_publication_outputs",
        "customer_or_payment_outputs",
        "secret_or_token_outputs",
        "final_advice_outputs",
        "live_action_states",
    ):
        if summary.get(key) != source_summary.get(key):
            findings.append(f"audit_summary.{key} must match source candidate summary")
    return findings


def _validate_source_copies(preview: dict[str, Any], source: dict[str, Any]) -> list[str]:
    pairs = (
        ("source_candidate_summary", "candidate_summary"),
        ("handoff_packet_record_summaries", "handoff_packet_records"),
        ("owner_r3_required_input_summaries", "owner_r3_required_input_summaries"),
        ("unresolved_blocker_summaries", "unresolved_blocker_summaries"),
        ("invalidating_trigger_summaries", "invalidating_trigger_summaries"),
        ("source_preflight_state_safety_scan", "source_preflight_state_safety_scan"),
        ("source_queue_state_safety_scan", "source_queue_state_safety_scan"),
        ("source_state_reference_safety_scan", "source_state_reference_safety_scan"),
        ("source_trigger_reference_coverage_scan", "source_trigger_reference_coverage_scan"),
        ("handoff_packet_assembly_step_summaries", "handoff_packet_assembly_steps"),
    )
    return [f"{key} must match source candidate {src}" for key, src in pairs if preview.get(key) != source.get(src)]


def _validate_decision_coverage(preview: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    for key in (
        "handoff_packet_record_summaries",
        "owner_r3_required_input_summaries",
        "unresolved_blocker_summaries",
        "invalidating_trigger_summaries",
    ):
        records = preview.get(key)
        if not isinstance(records, list):
            findings.append(f"{key} must be a list")
            continue
        found = {item.get("decision_type") for item in records if isinstance(item, dict)}
        missing = REQUIRED_DECISION_TYPES - found
        if missing:
            findings.append(f"{key} missing decision types: {sorted(missing)}")
    steps = preview.get("handoff_packet_assembly_step_summaries")
    if not isinstance(steps, list):
        findings.append("handoff_packet_assembly_step_summaries must be a list")
    else:
        for index, item in enumerate(steps):
            if not isinstance(item, dict):
                findings.append(f"handoff_packet_assembly_step_summaries[{index}] must be an object")
                continue
            if item.get("external_action") is not False:
                findings.append(f"handoff_packet_assembly_step_summaries[{index}].external_action must be false")
            if item.get("owner_r3_required_before_action") is not True:
                findings.append(f"handoff_packet_assembly_step_summaries[{index}].owner_r3_required_before_action must be true")
    return findings


def _validate_blocked_scan(preview: dict[str, Any], source: dict[str, Any]) -> list[str]:
    scan = preview.get("blocked_action_scan")
    if not isinstance(scan, dict):
        return ["blocked_action_scan must be an object"]
    source_scan = source.get("blocked_action_scan", {})
    findings: list[str] = []
    missing = REQUIRED_BLOCKED_SCAN_KEYS - set(scan)
    if missing:
        findings.append(f"blocked_action_scan missing keys: {sorted(missing)}")
    for key in REQUIRED_BLOCKED_SCAN_KEYS:
        item = scan.get(key)
        if not isinstance(item, dict):
            findings.append(f"blocked_action_scan.{key} must be an object")
            continue
        if item != source_scan.get(key):
            findings.append(f"blocked_action_scan.{key} must match source blocked action scan")
        if item.get("status") != "pass":
            findings.append(f"blocked_action_scan.{key}.status must be pass")
        if item.get("blocked_all") is not True:
            findings.append(f"blocked_action_scan.{key}.blocked_all must be true")
        if item.get("matches") != []:
            findings.append(f"blocked_action_scan.{key}.matches must be empty")
    return findings


def _validate_audit_events(preview: dict[str, Any]) -> list[str]:
    events = preview.get("audit_events")
    if not isinstance(events, list):
        return ["audit_events must be a list"]
    findings: list[str] = []
    found = {item.get("event") for item in events if isinstance(item, dict)}
    for event in REQUIRED_AUDIT_EVENTS - found:
        findings.append(f"audit_events missing {event}")
    for index, item in enumerate(events):
        if not isinstance(item, dict):
            findings.append(f"audit_events[{index}] must be an object")
            continue
        if item.get("external_action") is not False:
            findings.append(f"audit_events[{index}].external_action must be false")
    return findings


def _validate_forbidden_outputs(preview: dict[str, Any]) -> list[str]:
    outputs = set(_string_list(preview.get("forbidden_outputs")))
    missing = REQUIRED_FORBIDDEN_OUTPUTS - outputs
    return [f"forbidden_outputs missing: {sorted(missing)}"] if missing else []


def _validate_handoff(preview: dict[str, Any]) -> list[str]:
    handoff = preview.get("taskset_handoff")
    if not isinstance(handoff, dict):
        return ["taskset_handoff must be an object"]
    findings: list[str] = []
    for key in ("task_155_preview_ready", "taskset_local_scope_complete_when_task_closes"):
        if handoff.get(key) is not True:
            findings.append(f"taskset_handoff.{key} must be true")
    if "archive/rollback manifest" not in str(handoff.get("next_allowed_no_owner_slice", "")).lower():
        findings.append("taskset_handoff.next_allowed_no_owner_slice must describe archive/rollback manifest")
    r3_items = set(_string_list(handoff.get("owner_r3_required_for")))
    for required in (
        "actual Owner/R3 review submission",
        "actual Owner/R3 review start",
        "actual evidence refresh execution",
        "actual Owner approval record",
        "actual Owner signature",
        "actual approval evidence collection",
        "public use of any claim",
        "final PDF export",
        "SNS upload",
        "OAuth flow or platform API call",
        "secret or token handling",
    ):
        if required not in r3_items:
            findings.append(f"taskset_handoff.owner_r3_required_for missing {required}")
    return findings


def _validate_verification(preview: dict[str, Any]) -> list[str]:
    verification = preview.get("verification")
    if not isinstance(verification, dict):
        return ["verification must be an object"]
    expected = (
        "promotion_asset_owner_decision_evidence_refresh_owner_r3_packet_review_submission_handoff_packet_candidate_audit_preview_gate.py --check"
    )
    if expected not in str(verification.get("local_gate", "")):
        return ["verification.local_gate must reference this gate"]
    return []


def _safe_repo_path(repo_root: Path, rel_path: str) -> Path:
    if not rel_path or Path(rel_path).is_absolute():
        raise ValueError("path must be a non-empty relative path")
    resolved = (repo_root / rel_path).resolve()
    root = repo_root.resolve()
    if root not in resolved.parents and resolved != root:
        raise ValueError("path must stay inside repository")
    return resolved


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, dict) else {}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _find_forbidden_keys(value: Any, prefix: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}"
            if key.lower() in FORBIDDEN_KEY_NAMES:
                findings.append(path)
            findings.extend(_find_forbidden_keys(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(_find_forbidden_keys(child, f"{prefix}[{index}]"))
    return findings


def _find_live_true_keys(value: Any, prefix: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}"
            if key.lower() in LIVE_TRUE_KEYS and child is True:
                findings.append(path)
            findings.extend(_find_live_true_keys(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(_find_live_true_keys(child, f"{prefix}[{index}]"))
    return findings


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", type=Path, default=DEFAULT_PREVIEW)
    parser.add_argument("--check", action="store_true", help="validate and return non-zero on findings")
    args = parser.parse_args()

    preview = load_preview(args.preview)
    findings = validate_preview(preview)
    if findings:
        print("promotion asset Owner/R3 handoff packet candidate audit preview gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"promotion asset Owner/R3 handoff packet candidate audit preview gate: PASS ({args.preview})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
