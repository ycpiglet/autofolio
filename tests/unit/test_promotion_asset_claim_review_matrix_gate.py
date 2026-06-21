from __future__ import annotations

import copy

from scripts.promotion_asset_claim_review_matrix_gate import load_matrix, validate_matrix


def _matrix() -> dict:
    return load_matrix()


def test_current_matrix_passes():
    assert validate_matrix(_matrix()) == []


def test_rejects_source_hash_mismatch():
    matrix = _matrix()
    matrix["source_inputs"][0]["sha256"] = "0" * 64

    findings = validate_matrix(matrix)

    assert any("sha256 mismatch" in finding for finding in findings)


def test_rejects_missing_boundary():
    matrix = _matrix()
    matrix["boundaries"]["not_publication_approval"] = False

    findings = validate_matrix(matrix)

    assert any("boundaries.not_publication_approval must be true" in finding for finding in findings)


def test_rejects_public_approval_status():
    matrix = _matrix()
    matrix["status"] = "approved_for_publication"

    findings = validate_matrix(matrix)

    assert any("status must be local_claim_classification_not_public_approval" in finding for finding in findings)


def test_rejects_forbidden_secret_key():
    matrix = _matrix()
    matrix["preview_target_reviews"][0]["access_token"] = "placeholder"

    findings = validate_matrix(matrix)

    assert any("forbidden export/customer/secret/final-advice key names" in finding for finding in findings)


def test_rejects_missing_reject_phrase():
    matrix = _matrix()
    matrix["claim_buckets"]["reject"] = [
        item for item in matrix["claim_buckets"]["reject"] if item["claim"] != "guaranteed returns"
    ]

    findings = validate_matrix(matrix)

    assert any("claim_buckets.reject missing claims" in finding for finding in findings)


def test_rejects_missing_preview_target():
    matrix = copy.deepcopy(_matrix())
    matrix["preview_target_reviews"] = [
        item for item in matrix["preview_target_reviews"] if item["target_id"] != "pptx_deck_source"
    ]

    findings = validate_matrix(matrix)

    assert any("preview_target_reviews missing targets" in finding for finding in findings)


def test_rejects_public_use_unblocked():
    matrix = _matrix()
    matrix["preview_target_reviews"][0]["public_use_blocked"] = False

    findings = validate_matrix(matrix)

    assert any("public_use_blocked must be true" in finding for finding in findings)


def test_rejects_final_export_path_output():
    matrix = _matrix()
    matrix["matrix_outputs"]["final_pdf_path"] = "dist/final.pdf"

    findings = validate_matrix(matrix)

    assert any("forbidden export/customer/secret/final-advice key names" in finding for finding in findings)


def test_rejects_live_public_approval_flag():
    matrix = _matrix()
    matrix["preview_target_reviews"][0]["public_use_approved"] = True

    findings = validate_matrix(matrix)

    assert any("public/export/customer/payment/final-advice flags must not be true" in finding for finding in findings)
