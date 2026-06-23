from __future__ import annotations

import copy

from scripts.membership_supabase_apply_evidence_gate import load_checklist, validate_checklist


def test_membership_supabase_apply_evidence_gate_accepts_current_checklist():
    checklist = load_checklist()
    assert validate_checklist(checklist) == []


def test_membership_supabase_apply_evidence_gate_rejects_applied_status():
    checklist = load_checklist()
    broken = copy.deepcopy(checklist)
    broken["status"] = "applied"

    findings = validate_checklist(broken)

    assert any("not applied" in finding for finding in findings)


def test_membership_supabase_apply_evidence_gate_requires_backup_stage():
    checklist = load_checklist()
    broken = copy.deepcopy(checklist)
    broken["evidence_stages"] = [
        stage for stage in broken["evidence_stages"] if stage["id"] != "pre_apply_review"
    ]

    findings = validate_checklist(broken)

    assert any("pre_apply_review" in finding for finding in findings)


def test_membership_supabase_apply_evidence_gate_rejects_forbidden_backup_key():
    checklist = load_checklist()
    broken = copy.deepcopy(checklist)
    broken["backup_file"] = "placeholder"

    findings = validate_checklist(broken)

    assert any("forbidden apply/backup/secret keys present" in finding for finding in findings)


def test_membership_supabase_apply_evidence_gate_requires_cross_user_evidence():
    checklist = load_checklist()
    broken = copy.deepcopy(checklist)
    broken["required_evidence_ids"] = [
        item for item in broken["required_evidence_ids"] if item != "cross_user_membership_request_test_passed"
    ]

    findings = validate_checklist(broken)

    assert any("cross_user_membership_request_test_passed" in finding for finding in findings)

