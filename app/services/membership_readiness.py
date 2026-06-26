"""Membership production-readiness checklist.

This is an owner-visible local diagnostic. It does not read secret values,
connect to Supabase, call payment providers, or deploy anything.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from app.services.flags import guest_demo_enabled, local_auto_register_enabled


def readiness() -> dict[str, Any]:
    """Return the current production-readiness state for membership launch."""
    items = [
        _item(
            "local_membership_flow",
            "로컬 회원 승인 플로우",
            "pass",
            "가입신청, 입금대기, Owner 승인, local member grant, guest 차단, app-user read gate, LLM/SNS token harness까지 로컬에서 구현됨.",
            "TASK-100..TASK-107",
            "R2",
        ),
        _production_contract_item(),
        _payment_evidence_policy_item(),
        _tenant_isolation_matrix_item(),
        _production_secret_policy_item(),
        _engine_safety_contract_item(),
        _supabase_field_map_item(),
        _payment_recognition_decision_item(),
        _secret_store_plan_item(),
        _staging_deploy_preflight_item(),
        _staging_env_inventory_item(),
        _railway_backend_readiness_item(),
        _persistent_storage_decision_item(),
        _supabase_migration_review_packet_item(),
        _supabase_apply_evidence_checklist_item(),
        _kis_terms_review_packet_item(),
        _item(
            "supabase_schema",
            "Supabase production schema",
            "block",
            "field map, migration/RLS review packet, apply evidence checklist는 준비됐지만 production/staging schema는 아직 적용되지 않음.",
            "TASK-116, TASK-123, TASK-124",
            "R3",
        ),
        _item(
            "rls_user_isolation",
            "user_id / RLS 격리",
            "block",
            "tenant isolation matrix와 Supabase review packet은 존재하지만, live database RLS와 cross-user staging 증거는 아직 없음.",
            "TASK-114, TASK-123, TASK-124",
            "R3",
        ),
        _item(
            "production_secret_storage",
            "production secret storage",
            "block",
            "secret policy와 store plan은 존재하지만, production secret store 구현과 rotation/delete staging test는 아직 필요함.",
            "TASK-112, TASK-118",
            "R3",
        ),
        _item(
            "payment_recognition",
            "입금 확인 운영 모델",
            "block",
            "MVP payment recognition decision은 manual bank-app check + code-assisted match로 고정됐지만 production retention, refund/receipt/tax review, real payment evidence implementation은 남아 있음.",
            "TASK-111, TASK-117",
            "R3",
        ),
        _item(
            "per_user_engine_safety",
            "사용자별 엔진/안전장치",
            "block",
            "per-user engine/safety contract는 존재하지만, 엔진 루프, kill switch, risk limit, order queue, order intent 구현은 아직 user_id 단위로 분리되지 않음.",
            "TASK-087",
            "R3",
        ),
        _item(
            "kis_commercial_terms",
            "KIS 약관/상용 사용 확인",
            "watch",
            "KIS terms review packet은 존재하지만 사용자 본인 KIS 키 구조, hosted multi-user web service, commercial use, market-data/order API 경계는 Owner/KIS/legal 확인 필요.",
            "TASK-088, TASK-125",
            "Owner/professional",
        ),
        _item(
            "external_deploy",
            "외부 배포",
            "block",
            "preflight, env inventory, Railway readiness, storage decision, Supabase apply evidence checklist는 준비됐지만 Vercel/Railway/Supabase deploy와 external env write는 아직 실행하지 않음.",
            "TASK-119..TASK-124",
            "R3",
        ),
    ]
    block_count = sum(1 for item in items if item["state"] == "block")
    watch_count = sum(1 for item in items if item["state"] == "watch")
    pass_count = sum(1 for item in items if item["state"] == "pass")
    return {
        "can_launch": block_count == 0,
        "mode": "local_prototype",
        "score": _score(pass_count=pass_count, watch_count=watch_count, block_count=block_count),
        "summary": "로컬 검증회원 플로우와 R2 pre-apply 증거물은 준비됐지만, 외부 사용자/프로덕션 배포 전 R3 실행 증거가 남아 있습니다.",
        "items": items,
        "required_owner_actions": [
            "Supabase staging project 선택, migration 생성/적용, advisor와 cross-user 결과 기록",
            "Vercel/Railway/Supabase external env 값을 repo 밖에서 작성",
            "production secret storage와 삭제/회전 staging test 검증",
            "payment recognition 보존/환불/영수증/세무 운영 검토",
            "KIS 약관/상용 사용 및 추천 기능 법적 경계 확인",
            "staging deploy smoke 후 외부 사용자 전 최종 검증",
        ],
        "environment_flags": _environment_flags(),
    }


def _item(
    item_id: str,
    label: str,
    state: str,
    detail: str,
    evidence: str,
    gate: str,
) -> dict[str, str]:
    return {
        "id": item_id,
        "label": label,
        "state": state,
        "detail": detail,
        "evidence": evidence,
        "gate": gate,
    }


def _artifact_present(
    filename: str,
    schema: str,
    *,
    status_markers: tuple[str, ...],
    required_fields: tuple[str, ...],
) -> bool:
    artifact_path = Path(__file__).resolve().parents[2] / "agents" / "project" / filename
    try:
        with artifact_path.open("r", encoding="utf-8") as fh:
            artifact = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return False

    artifact_schema = artifact.get("$schema") or artifact.get("schema")
    status = str(artifact.get("status", ""))
    return (
        artifact_schema == schema
        and all(marker in status for marker in status_markers)
        and all(bool(artifact.get(field)) for field in required_fields)
    )


def _production_contract_item() -> dict[str, str]:
    if _production_contract_present():
        return _item(
            "production_contract",
            "Supabase/RLS production contract",
            "pass",
            "production schema/RLS/user_id/secret/payment/engine 경계를 적용 전 contract asset과 local gate로 고정함.",
            "TASK-109",
            "R2 contract",
        )
    return _item(
        "production_contract",
        "Supabase/RLS production contract",
        "block",
        "production schema/RLS/user_id/secret/payment/engine 경계를 적용 전 contract asset으로 고정해야 함.",
        "TASK-087",
        "R2 contract",
    )


def _production_contract_present() -> bool:
    contract_path = (
        Path(__file__).resolve().parents[2]
        / "agents"
        / "project"
        / "MEMBERSHIP-PRODUCTION-CONTRACT.json"
    )
    try:
        with contract_path.open("r", encoding="utf-8") as fh:
            contract = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return False
    return (
        contract.get("$schema") == "autofolio.membership-production-contract/v1"
        and "not_applied" in str(contract.get("status", ""))
        and bool(contract.get("entities"))
        and bool(contract.get("security_invariants"))
    )


def _payment_evidence_policy_item() -> dict[str, str]:
    if _payment_evidence_policy_present():
        return _item(
            "payment_evidence_policy",
            "payment evidence retention policy",
            "pass",
            "manual/code-assisted 입금 확인 증거를 최소 필드, masking, 감사 이벤트 중심으로 보존하는 로컬 policy와 gate가 존재함.",
            "TASK-111",
            "R2 policy",
        )
    return _item(
        "payment_evidence_policy",
        "payment evidence retention policy",
        "block",
        "production 입금 증거 보존 전에 최소 필드, masking, 금지 evidence, 감사 invariant를 policy asset으로 고정해야 함.",
        "TASK-087",
        "R2 policy",
    )


def _payment_evidence_policy_present() -> bool:
    policy_path = (
        Path(__file__).resolve().parents[2]
        / "agents"
        / "project"
        / "MEMBERSHIP-PAYMENT-EVIDENCE-POLICY.json"
    )
    try:
        with policy_path.open("r", encoding="utf-8") as fh:
            policy = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return False
    return (
        policy.get("$schema") == "autofolio.membership-payment-evidence-policy/v1"
        and "not_applied" in str(policy.get("status", ""))
        and bool(policy.get("retained_fields"))
        and bool(policy.get("forbidden_evidence"))
        and bool(policy.get("audit_invariants"))
    )


def _tenant_isolation_matrix_item() -> dict[str, str]:
    if _tenant_isolation_matrix_present():
        return _item(
            "tenant_isolation_matrix",
            "user_id/RLS tenant isolation matrix",
            "pass",
            "public/member/owner/worker route group, tenant surface, invariant, staging test target을 적용 전 matrix와 local gate로 고정함.",
            "TASK-114",
            "R2 matrix",
        )
    return _item(
        "tenant_isolation_matrix",
        "user_id/RLS tenant isolation matrix",
        "block",
        "product data, engine state, secret metadata, audit event의 user_id/RLS 격리 matrix가 필요함.",
        "TASK-087",
        "R2 matrix",
    )


def _tenant_isolation_matrix_present() -> bool:
    matrix_path = (
        Path(__file__).resolve().parents[2]
        / "agents"
        / "project"
        / "MEMBERSHIP-TENANT-ISOLATION-MATRIX.json"
    )
    try:
        with matrix_path.open("r", encoding="utf-8") as fh:
            matrix = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return False
    return (
        matrix.get("$schema") == "autofolio.membership-tenant-isolation-matrix/v1"
        and "not_applied" in str(matrix.get("status", ""))
        and bool(matrix.get("route_groups"))
        and bool(matrix.get("surfaces"))
        and bool(matrix.get("security_invariants"))
    )


def _production_secret_policy_item() -> dict[str, str]:
    if _production_secret_policy_present():
        return _item(
            "production_secret_policy",
            "production secret handling policy",
            "pass",
            "user-owned LLM/SNS/OAuth/KIS token, write-only API boundary, rotation/delete, redaction, and audit invariant를 적용 전 policy와 local gate로 고정함.",
            "TASK-112",
            "R2 policy",
        )
    return _item(
        "production_secret_policy",
        "production secret handling policy",
        "block",
        "production secret storage 구현 전에 write-only, redaction, deletion, rotation, audit invariant를 policy asset으로 고정해야 함.",
        "TASK-087",
        "R2 policy",
    )


def _production_secret_policy_present() -> bool:
    policy_path = (
        Path(__file__).resolve().parents[2]
        / "agents"
        / "project"
        / "MEMBERSHIP-PRODUCTION-SECRET-POLICY.json"
    )
    try:
        with policy_path.open("r", encoding="utf-8") as fh:
            policy = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return False
    return (
        policy.get("$schema") == "autofolio.membership-production-secret-policy/v1"
        and "not_applied" in str(policy.get("status", ""))
        and bool(policy.get("provider_categories"))
        and bool(policy.get("forbidden_exposure"))
        and bool(policy.get("audit_invariants"))
    )


def _engine_safety_contract_item() -> dict[str, str]:
    if _engine_safety_contract_present():
        return _item(
            "per_user_engine_safety_contract",
            "per-user engine/safety contract",
            "pass",
            "engine state, queue, kill switch, risk limits, circuit breakers, order intents, logs, notifications의 user_id 격리 계약과 local gate가 존재함.",
            "TASK-113",
            "R2 contract",
        )
    return _item(
        "per_user_engine_safety_contract",
        "per-user engine/safety contract",
        "block",
        "external members가 live-readiness 기능을 쓰기 전 engine/safety/order intent user_id 격리 contract를 고정해야 함.",
        "TASK-087",
        "R2 contract",
    )


def _engine_safety_contract_present() -> bool:
    contract_path = (
        Path(__file__).resolve().parents[2]
        / "agents"
        / "project"
        / "MEMBERSHIP-ENGINE-SAFETY-CONTRACT.json"
    )
    try:
        with contract_path.open("r", encoding="utf-8") as fh:
            contract = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return False
    return (
        contract.get("$schema") == "autofolio.membership-engine-safety-contract/v1"
        and "not_applied" in str(contract.get("status", ""))
        and bool(contract.get("runtime_surfaces"))
        and bool(contract.get("safety_invariants"))
        and bool(contract.get("worker_contract"))
    )


def _supabase_field_map_item() -> dict[str, str]:
    if _artifact_present(
        "MEMBERSHIP-SUPABASE-STAGING-FIELD-MAP.json",
        "autofolio.membership-supabase-staging-field-map/v1",
        status_markers=("not_applied",),
        required_fields=("entities", "required_staging_tests", "advisor_checklist"),
    ):
        return _item(
            "supabase_staging_field_map",
            "Supabase staging field map",
            "pass",
            "membership, secret metadata, payment evidence, portfolio, engine, trading, notification, audit surface의 owner field/RLS/Data API target을 적용 전 field map으로 고정함.",
            "TASK-116",
            "R2 field map",
        )
    return _item(
        "supabase_staging_field_map",
        "Supabase staging field map",
        "block",
        "Supabase migration review 전에 table/owner field/RLS/Data API field map이 필요함.",
        "TASK-087",
        "R2 field map",
    )


def _payment_recognition_decision_item() -> dict[str, str]:
    if _artifact_present(
        "MEMBERSHIP-PAYMENT-RECOGNITION-DECISION-PACKET.json",
        "autofolio.membership-payment-recognition-decision-packet/v1",
        status_markers=("not_applied",),
        required_fields=("selected_mvp", "options", "required_staging_tests"),
    ):
        return _item(
            "payment_recognition_decision",
            "payment recognition decision packet",
            "pass",
            "MVP는 manual bank-app check + code-assisted deposit match로 고정했고 PG/Open Banking은 Owner/R3 upgrade lane으로 분리함.",
            "TASK-117",
            "R2 decision",
        )
    return _item(
        "payment_recognition_decision",
        "payment recognition decision packet",
        "block",
        "production 입금 확인 구현 전에 수동/CSV/PG/Open Banking 선택 기준과 forbidden boundary를 고정해야 함.",
        "TASK-087",
        "R2 decision",
    )


def _secret_store_plan_item() -> dict[str, str]:
    if _artifact_present(
        "MEMBERSHIP-PRODUCTION-SECRET-STORE-IMPLEMENTATION-PLAN.json",
        "autofolio.membership-secret-store-implementation-plan/v1",
        status_markers=("not_applied",),
        required_fields=("candidate_stores", "future_api_boundary", "required_staging_tests"),
    ):
        return _item(
            "production_secret_store_plan",
            "production secret store plan",
            "pass",
            "runtime secrets, Edge Function secrets, Vault/KMS candidate, tenant metadata table, rotation/delete/audit test plan을 적용 전 plan으로 고정함.",
            "TASK-118",
            "R2 plan",
        )
    return _item(
        "production_secret_store_plan",
        "production secret store plan",
        "block",
        "secret policy를 실제 store 후보, API boundary, rotation/delete/audit staging test plan으로 전환해야 함.",
        "TASK-087",
        "R2 plan",
    )


def _staging_deploy_preflight_item() -> dict[str, str]:
    if _artifact_present(
        "MEMBERSHIP-STAGING-DEPLOY-PREFLIGHT-CHECKLIST.json",
        "autofolio.membership-staging-deploy-preflight-checklist/v1",
        status_markers=("not_deployed",),
        required_fields=("services", "required_local_checks", "required_staging_smoke_plan"),
    ):
        return _item(
            "staging_deploy_preflight",
            "staging deploy preflight checklist",
            "pass",
            "Vercel/Railway/Supabase staging target, local checks, smoke plan, rollback plan, forbidden actions, launch gates를 no-deploy checklist로 고정함.",
            "TASK-119",
            "R2 preflight",
        )
    return _item(
        "staging_deploy_preflight",
        "staging deploy preflight checklist",
        "block",
        "external deploy 전에 no-deploy preflight checklist와 smoke/rollback plan이 필요함.",
        "TASK-087",
        "R2 preflight",
    )


def _staging_env_inventory_item() -> dict[str, str]:
    if _artifact_present(
        "MEMBERSHIP-STAGING-ENV-INVENTORY.json",
        "autofolio.membership-staging-env-inventory/v1",
        status_markers=("sanitized_template_only",),
        required_fields=("groups", "fail_closed_defaults", "boundaries"),
    ):
        return _item(
            "staging_env_inventory",
            "staging env inventory",
            "pass",
            "secret-free `.env.example`와 fail-closed placeholder inventory가 존재하고 external env write는 계속 차단됨.",
            "TASK-120",
            "R2 env inventory",
        )
    return _item(
        "staging_env_inventory",
        "staging env inventory",
        "block",
        "external platform env 입력 전 repo에는 sanitized placeholder inventory와 fail-closed defaults가 필요함.",
        "TASK-087",
        "R2 env inventory",
    )


def _railway_backend_readiness_item() -> dict[str, str]:
    if _artifact_present(
        "MEMBERSHIP-RAILWAY-BACKEND-READINESS.json",
        "autofolio.membership-railway-backend-readiness/v1",
        status_markers=("not_deployed",),
        required_fields=("backend", "readiness_checks", "boundaries"),
    ):
        return _item(
            "railway_backend_readiness",
            "Railway backend readiness",
            "pass",
            "local Dockerfile `$PORT` binding과 unauthenticated `/api/health` readiness가 기록됐고 Railway deploy/env/domain은 실행하지 않음.",
            "TASK-121",
            "R2 readiness",
        )
    return _item(
        "railway_backend_readiness",
        "Railway backend readiness",
        "block",
        "Railway deploy 전 backend port binding과 healthcheck readiness 증거가 필요함.",
        "TASK-087",
        "R2 readiness",
    )


def _persistent_storage_decision_item() -> dict[str, str]:
    if _artifact_present(
        "MEMBERSHIP-STAGING-PERSISTENT-STORAGE-DECISION.json",
        "autofolio.membership-staging-persistent-storage-decision/v1",
        status_markers=("not_applied",),
        required_fields=("storage_surfaces", "decision_summary", "required_staging_tests"),
    ):
        return _item(
            "staging_persistent_storage_decision",
            "staging persistent storage decision",
            "pass",
            "external/member staging source of truth를 Supabase Postgres/Auth/RLS로 고정하고 local vault/SQLite/runtime file은 internal-smoke 보조로 제한함.",
            "TASK-122",
            "R2 decision",
        )
    return _item(
        "staging_persistent_storage_decision",
        "staging persistent storage decision",
        "block",
        "external/member staging 전에 tenant source of truth와 local/runtime storage boundary 결정이 필요함.",
        "TASK-087",
        "R2 decision",
    )


def _supabase_migration_review_packet_item() -> dict[str, str]:
    if _artifact_present(
        "MEMBERSHIP-SUPABASE-STAGING-MIGRATION-RLS-REVIEW.json",
        "autofolio.membership-supabase-staging-migration-rls-review/v1",
        status_markers=("not_migration", "not_applied"),
        required_fields=("table_review_specs", "rls_review_requirements", "required_cross_user_tests"),
    ):
        return _item(
            "supabase_migration_review_packet",
            "Supabase migration/RLS review packet",
            "pass",
            "future migration/apply 전에 table groups, RLS grants, Data API order, cross-user tests, rollback/apply review checklist를 local packet으로 고정함.",
            "TASK-123",
            "R2 review packet",
        )
    return _item(
        "supabase_migration_review_packet",
        "Supabase migration/RLS review packet",
        "block",
        "migration 생성/apply 전 table/RLS/Data API/cross-user/rollback review packet이 필요함.",
        "TASK-087",
        "R2 review packet",
    )


def _supabase_apply_evidence_checklist_item() -> dict[str, str]:
    if _artifact_present(
        "MEMBERSHIP-SUPABASE-STAGING-APPLY-EVIDENCE-CHECKLIST.json",
        "autofolio.membership-supabase-staging-apply-evidence-checklist/v1",
        status_markers=("not_applied",),
        required_fields=("evidence_stages", "required_evidence_ids", "owner_only_actions"),
    ):
        return _item(
            "supabase_apply_evidence_checklist",
            "Supabase apply evidence checklist",
            "pass",
            "future Owner/R3 apply lane이 backup, apply log, advisors, Data API, cross-user, smoke evidence 없이 readiness를 주장하지 못하게 required evidence IDs를 고정함.",
            "TASK-124",
            "R2 evidence checklist",
        )
    return _item(
        "supabase_apply_evidence_checklist",
        "Supabase apply evidence checklist",
        "block",
        "actual Supabase apply 전에 backup/apply/advisor/grant/cross-user/smoke evidence checklist가 필요함.",
        "TASK-087",
        "R2 evidence checklist",
    )


def _kis_terms_review_packet_item() -> dict[str, str]:
    if _artifact_present(
        "MEMBERSHIP-KIS-COMMERCIAL-TERMS-REVIEW-PACKET.json",
        "autofolio.membership-kis-commercial-terms-review-packet/v1",
        status_markers=("not_clearance",),
        required_fields=("source_basis", "findings", "owner_kis_legal_question_set"),
    ):
        return _item(
            "kis_terms_review_packet",
            "KIS commercial terms review packet",
            "pass",
            "official-source KIS/FSC findings and Owner/KIS/legal question set are recorded, but this is not KIS/legal clearance.",
            "TASK-125",
            "R2 review packet",
        )
    return _item(
        "kis_terms_review_packet",
        "KIS commercial terms review packet",
        "block",
        "KIS commercial/multi-user OpenAPI boundary needs an official-source packet before external member launch planning.",
        "TASK-087",
        "R2 review packet",
    )


def _score(*, pass_count: int, watch_count: int, block_count: int) -> int:
    total = pass_count + watch_count + block_count
    if total == 0:
        return 0
    raw = (pass_count * 100 + watch_count * 50) / total
    return int(round(raw))


def _environment_flags() -> dict[str, bool]:
    """Expose only whether a class of config is present, never its value."""
    from app.services.flags import (
        auto_exec_enabled,
        recommendation_enabled,
        advice_enabled,
        multi_tenant_enabled,
    )
    return {
        "supabase_url_present": bool(os.getenv("SUPABASE_URL")),
        "membership_bank_runtime_config_present": all(
            bool(os.getenv(name))
            for name in (
                "AUTOFOLIO_MEMBERSHIP_BANK_NAME",
                "AUTOFOLIO_MEMBERSHIP_ACCOUNT_HOLDER",
                "AUTOFOLIO_MEMBERSHIP_BANK_ACCOUNT",
            )
        ),
        "guest_demo_enabled": guest_demo_enabled(),
        "local_auto_register_enabled": local_auto_register_enabled(),
        # Presence-only: never expose the email value itself
        "owner_email_configured": bool(os.getenv("AUTOFOLIO_OWNER_EMAIL")),
        "auto_exec_enabled": auto_exec_enabled(),
        "recommendation_enabled": recommendation_enabled(),
        "advice_enabled": advice_enabled(),
        "multi_tenant_enabled": multi_tenant_enabled(),
    }
