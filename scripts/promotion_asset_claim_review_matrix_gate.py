"""Validate the TASK-134 promotion asset claim review matrix.

This gate validates local claim classification only. It rejects public approval,
final advice, final asset export, live publishing, customer contact,
CRM/payment action, external account action, secret fields, and incomplete
review buckets.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MATRIX = REPO_ROOT / "agents" / "project" / "PROMOTION-ASSET-CLAIM-REVIEW-MATRIX.json"
PREVIEW_MANIFEST_PATH = REPO_ROOT / "agents" / "project" / "PROMOTION-ASSET-PREVIEW-MANIFEST.json"
MARKETING_MATERIALS_PATH = REPO_ROOT / "agents" / "project" / "MARKETING-MATERIALS-V1.json"
RENDERING_CONTRACT_PATH = REPO_ROOT / "agents" / "project" / "PROMOTION-ASSET-RENDERING-CONTRACT.json"

REQUIRED_SOURCE_IDS = {
    "promotion_asset_preview_manifest",
    "marketing_materials_v1",
    "promotion_asset_rendering_contract",
}

EXPECTED_SOURCE_PATHS = {
    "promotion_asset_preview_manifest": "agents/project/PROMOTION-ASSET-PREVIEW-MANIFEST.json",
    "marketing_materials_v1": "agents/project/MARKETING-MATERIALS-V1.json",
    "promotion_asset_rendering_contract": "agents/project/PROMOTION-ASSET-RENDERING-CONTRACT.json",
}

REQUIRED_BOUNDARIES = {
    "local_claim_classification_only",
    "not_publication_approval",
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
    "no_kis_order_risk_prod_deploy_change",
    "owner_approval_required_before_public_use",
    "professional_review_required_before_reliance",
}

REQUIRED_BUCKETS = {
    "allowed_draft",
    "needs_compliance_review",
    "owner_only_before_public_use",
    "reject",
}

REQUIRED_ALLOWED_CLAIMS = {
    "user-controlled investing workflow",
    "auditable operating records",
    "explicit approvals before live action",
    "portfolio visibility and agent-assisted summaries",
    "verified membership review",
    "mock/paper-first verification",
}

REQUIRED_NEEDS_REVIEW_CLAIMS = {
    "agent recommendation flows",
    "user-owned LLM/SNS token integrations",
    "KIS-related wording",
    "automated trading/live-readiness wording",
    "financial-service/regulatory wording",
}

REQUIRED_OWNER_ONLY_CLAIMS = {
    "pricing/paid pilot",
    "public landing hero",
    "PDF/PPTX export",
    "SNS post",
    "customer CTA/contact",
    "paid ads",
}

REQUIRED_REJECT_CLAIMS = {
    "guaranteed returns",
    "risk-free",
    "safe returns",
    "hands-free wealth management",
    "investment advice",
    "paid signal",
    "model portfolio",
    "broker/asset manager/robo-advisor identity",
    "KIS commercial clearance claim",
    "AI selects winning stocks",
}

FORBIDDEN_KEY_NAMES = {
    "access_token",
    "refresh_token",
    "bot_token",
    "client_secret",
    "api_secret",
    "app_secret",
    "password",
    "cookie",
    "session",
    "customer_email",
    "customer_phone",
    "bank_account_number",
    "public_url",
    "external_upload_id",
    "final_pdf_path",
    "final_pptx_path",
    "pdf_binary_path",
    "pptx_binary_path",
    "payment_request_id",
    "customer_record_id",
    "legal_opinion",
    "tax_advice_final",
    "securities_advice_final",
    "kis_app_secret",
}

LIVE_TRUE_KEYS = {
    "public_use_approved",
    "publication_approved",
    "claim_approved_for_publication",
    "final_advice_enabled",
    "final_export_enabled",
    "binary_export_enabled",
    "public_export_enabled",
    "external_upload_enabled",
    "customer_contact_enabled",
    "crm_action_enabled",
    "payment_action_enabled",
    "secret_storage_enabled",
    "live_post_enabled",
    "external_network_calls",
    "external_action_enabled",
    "paid_ads_enabled",
}

TARGET_REQUIRED_TRUE_FLAGS = {
    "public_use_blocked",
    "final_export_blocked",
    "publication_approval_blocked",
    "professional_review_required_before_reliance",
}

TOP_LEVEL_REQUIRED_TRUE_FLAGS = {
    "public_use_blocked",
    "final_advice_blocked",
    "publication_approval_blocked",
}


def load_matrix(path: Path = DEFAULT_MATRIX) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("promotion asset claim review matrix root must be an object")
    return data


def validate_matrix(matrix: dict[str, Any], repo_root: Path = REPO_ROOT) -> list[str]:
    findings: list[str] = []

    if matrix.get("$schema") != "autofolio.promotion-asset-claim-review-matrix/v1":
        findings.append("unexpected or missing promotion asset claim review matrix schema")

    status = str(matrix.get("status", "")).lower()
    if status != "local_claim_classification_not_public_approval":
        findings.append("status must be local_claim_classification_not_public_approval")

    for key in TOP_LEVEL_REQUIRED_TRUE_FLAGS:
        if matrix.get(key) is not True:
            findings.append(f"{key} must be true")

    boundaries = matrix.get("boundaries")
    if not isinstance(boundaries, dict):
        findings.append("boundaries must be an object")
    else:
        for key in REQUIRED_BOUNDARIES:
            if boundaries.get(key) is not True:
                findings.append(f"boundaries.{key} must be true")

    forbidden_keys = _find_forbidden_keys(matrix)
    if forbidden_keys:
        findings.append(f"forbidden export/customer/secret/final-advice key names present: {forbidden_keys}")

    live_true_paths = _find_live_true_keys(matrix)
    if live_true_paths:
        findings.append(f"public/export/customer/payment/final-advice flags must not be true: {live_true_paths}")

    findings.extend(_validate_sources(matrix, repo_root))
    findings.extend(_validate_markdown_companion(matrix, repo_root))
    findings.extend(_validate_buckets(matrix))
    findings.extend(_validate_preview_target_reviews(matrix))
    findings.extend(_validate_outputs(matrix))
    findings.extend(_validate_handoff(matrix))
    findings.extend(_validate_verification(matrix))

    return findings


def _validate_sources(matrix: dict[str, Any], repo_root: Path) -> list[str]:
    findings: list[str] = []
    inputs = matrix.get("source_inputs")
    if not isinstance(inputs, list):
        return ["source_inputs must be a list"]

    source_ids = {item.get("id") for item in inputs if isinstance(item, dict)}
    missing = REQUIRED_SOURCE_IDS - source_ids
    if missing:
        findings.append(f"source_inputs missing ids: {sorted(missing)}")

    for index, item in enumerate(inputs):
        if not isinstance(item, dict):
            findings.append(f"source_inputs[{index}] must be an object")
            continue
        source_id = str(item.get("id", ""))
        rel_path = str(item.get("path", ""))
        expected = EXPECTED_SOURCE_PATHS.get(source_id)
        if expected and rel_path != expected:
            findings.append(f"source_inputs[{index}].path for {source_id} must be {expected}")
        try:
            path = _safe_repo_path(repo_root, rel_path)
        except ValueError as exc:
            findings.append(f"source_inputs[{index}].path invalid: {exc}")
            continue
        if not path.exists():
            findings.append(f"source_inputs[{index}].path missing: {rel_path}")
            continue
        if str(item.get("sha256", "")).lower() != _sha256(path):
            findings.append(f"source_inputs[{index}].sha256 mismatch for {rel_path}")
    return findings


def _validate_markdown_companion(matrix: dict[str, Any], repo_root: Path) -> list[str]:
    rel_path = str(matrix.get("companion_markdown", ""))
    try:
        path = _safe_repo_path(repo_root, rel_path)
    except ValueError as exc:
        return [f"companion_markdown invalid: {exc}"]
    if not path.exists():
        return [f"companion_markdown missing: {rel_path}"]
    text = path.read_text(encoding="utf-8").lower()
    findings: list[str] = []
    for required in (
        "not public approval",
        "public_use_blocked=true",
        "final_export_blocked=true",
        "publication_approval_blocked=true",
    ):
        if required not in text:
            findings.append(f"companion_markdown must mention {required}")
    return findings


def _validate_buckets(matrix: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    buckets = matrix.get("claim_buckets")
    if not isinstance(buckets, dict):
        return ["claim_buckets must be an object"]

    missing_buckets = REQUIRED_BUCKETS - set(buckets)
    if missing_buckets:
        findings.append(f"claim_buckets missing: {sorted(missing_buckets)}")

    for bucket in REQUIRED_BUCKETS:
        values = buckets.get(bucket)
        if not isinstance(values, list) or not values:
            findings.append(f"claim_buckets.{bucket} must be a non-empty list")

    bucket_claims = {
        bucket: _claim_set(buckets.get(bucket))
        for bucket in REQUIRED_BUCKETS
    }
    missing_allowed = REQUIRED_ALLOWED_CLAIMS - bucket_claims["allowed_draft"]
    if missing_allowed:
        findings.append(f"claim_buckets.allowed_draft missing claims: {sorted(missing_allowed)}")
    missing_needs = REQUIRED_NEEDS_REVIEW_CLAIMS - bucket_claims["needs_compliance_review"]
    if missing_needs:
        findings.append(f"claim_buckets.needs_compliance_review missing claims: {sorted(missing_needs)}")
    missing_owner = REQUIRED_OWNER_ONLY_CLAIMS - bucket_claims["owner_only_before_public_use"]
    if missing_owner:
        findings.append(f"claim_buckets.owner_only_before_public_use missing claims: {sorted(missing_owner)}")
    missing_reject = REQUIRED_REJECT_CLAIMS - bucket_claims["reject"]
    if missing_reject:
        findings.append(f"claim_buckets.reject missing claims: {sorted(missing_reject)}")

    for bucket in ("allowed_draft", "needs_compliance_review", "owner_only_before_public_use"):
        for claim in REQUIRED_REJECT_CLAIMS:
            if claim in bucket_claims[bucket]:
                findings.append(f"claim_buckets.{bucket} must not include rejected claim: {claim}")

    return findings


def _validate_preview_target_reviews(matrix: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    reviews = matrix.get("preview_target_reviews")
    if not isinstance(reviews, list):
        return ["preview_target_reviews must be a list"]

    preview_manifest = _load_json(PREVIEW_MANIFEST_PATH)
    previews = preview_manifest.get("asset_previews")
    expected_targets = {
        item.get("target_id")
        for item in previews
        if isinstance(item, dict) and isinstance(item.get("target_id"), str)
    }
    expected_targets.discard(None)
    review_targets = {
        item.get("target_id")
        for item in reviews
        if isinstance(item, dict) and isinstance(item.get("target_id"), str)
    }
    missing_targets = expected_targets - review_targets
    if missing_targets:
        findings.append(f"preview_target_reviews missing targets: {sorted(missing_targets)}")

    for index, review in enumerate(reviews):
        if not isinstance(review, dict):
            findings.append(f"preview_target_reviews[{index}] must be an object")
            continue
        prefix = f"preview_target_reviews[{index}]"
        target_id = review.get("target_id")
        if target_id not in expected_targets:
            findings.append(f"{prefix}.target_id not found in preview manifest: {target_id}")
        if review.get("claim_classification_status") != "classified_draft_not_approved":
            findings.append(f"{prefix}.claim_classification_status must be classified_draft_not_approved")
        if review.get("primary_bucket") not in REQUIRED_BUCKETS:
            findings.append(f"{prefix}.primary_bucket must be one of the required buckets")
        for key in TARGET_REQUIRED_TRUE_FLAGS:
            if review.get(key) is not True:
                findings.append(f"{prefix}.{key} must be true")
        if not _string_list(review.get("allowed_draft_claims")):
            findings.append(f"{prefix}.allowed_draft_claims must be a non-empty string list")
        if not _string_list(review.get("needs_compliance_review")):
            findings.append(f"{prefix}.needs_compliance_review must be a non-empty string list")
        if not _string_list(review.get("owner_only_before_public_use")):
            findings.append(f"{prefix}.owner_only_before_public_use must be a non-empty string list")
        if not _string_list(review.get("reject_claims")):
            findings.append(f"{prefix}.reject_claims must be a non-empty string list")
    return findings


def _validate_outputs(matrix: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    outputs = matrix.get("matrix_outputs")
    if not isinstance(outputs, dict):
        return ["matrix_outputs must be an object"]
    expected = {
        "json_matrix": "agents/project/PROMOTION-ASSET-CLAIM-REVIEW-MATRIX.json",
        "markdown_matrix": "agents/project/PROMOTION-ASSET-CLAIM-REVIEW-MATRIX.md",
    }
    for key, value in expected.items():
        if outputs.get(key) != value:
            findings.append(f"matrix_outputs.{key} must be {value}")
    for key in FORBIDDEN_KEY_NAMES:
        if outputs.get(key) is not None:
            findings.append(f"matrix_outputs.{key} must be null")
    return findings


def _validate_handoff(matrix: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    handoff = matrix.get("taskset_handoff")
    if not isinstance(handoff, dict):
        return ["taskset_handoff must be an object"]
    for key in ("task_134_complete", "taskset_complete"):
        if handoff.get(key) is not True:
            findings.append(f"taskset_handoff.{key} must be true")
    r3_items = set(_string_list(handoff.get("owner_r3_required_for")))
    for required in ("public use of any claim", "final PDF export", "SNS upload", "legal/tax/securities reliance"):
        if required not in r3_items:
            findings.append(f"taskset_handoff.owner_r3_required_for missing {required}")
    return findings


def _validate_verification(matrix: dict[str, Any]) -> list[str]:
    verification = matrix.get("verification")
    if not isinstance(verification, dict):
        return ["verification must be an object"]
    if "promotion_asset_claim_review_matrix_gate.py --check" not in str(verification.get("local_gate", "")):
        return ["verification.local_gate must reference this gate"]
    return []


def _claim_set(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    result: set[str] = set()
    for item in value:
        if isinstance(item, dict) and isinstance(item.get("claim"), str):
            result.add(item["claim"])
        elif isinstance(item, str):
            result.add(item)
    return result


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
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--check", action="store_true", help="validate and return non-zero on findings")
    args = parser.parse_args()

    matrix = load_matrix(args.matrix)
    findings = validate_matrix(matrix)
    if findings:
        print("promotion asset claim review matrix gate: FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(f"promotion asset claim review matrix gate: PASS ({args.matrix})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
