---
type: task
id: TASK-122
display_id: TASK-122
task_uid: a5dca9a3-6be7-4499-a15e-13a1a99f76bd
registered_at: 2026-06-19T21:17:00+09:00
created_at: 2026-06-19T21:17:00+09:00
updated_at: 2026-06-19T21:46:56+09:00
started_at: 2026-06-19T21:42:53+09:00
completed_at: 2026-06-19T21:46:56+09:00
status: 완료
owner: Backend Engineer
assignees: [Backend Engineer, Lead Engineer, QA]
priority: Medium
difficulty: 중
est_hours: 2
est_tokens: 22000
tags: [membership, deploy, storage, staging, preflight]
initiative_id: INIT-MEMBERSHIP-ACCESS
task_set_id: TASKSET-MEMBERSHIP-DEPLOY-PREFLIGHT-REMEDIATION
gate: decision packet only; no DB migration, no Supabase apply, no production data
trigger_meeting: Owner goal continuation 2026-06-19
audit_log: AUDIT-2026-06-19-033
created: 2026-06-19
---

# TASK-122 Membership staging persistent storage decision

작업 ID: TASK-122
상태: 완료
Owner: Backend Engineer
요청 시각: 2026-06-19T21:17:00+09:00
기록 시각: 2026-06-19T21:17:00+09:00
요청자: Owner goal continuation
수행자: Backend Engineer + Lead Engineer + QA perspective (Codex)
검토자: Backend Engineer self-review + Supabase/Railway source review + QA gate perspective; 협업 waiver(사유): single-session local decision packet scope; no DB migration, Supabase apply, external project mutation, external env write, Railway volume creation, public URL, secret, production data, KIS/payment/provider, order/risk boundary crossed.
routing_ref: TASKSET-MEMBERSHIP-DEPLOY-PREFLIGHT-REMEDIATION / TASK-122
의도: TASK-119에서 기록한 local vault/runtime persistence blocker를 staging 전 decision packet으로 줄인다.
대상: local vault, SQLite, Supabase staging, runtime filesystem, and tenant data persistence options.
방법: decision packet/gate only. No migration/apply or production data write.
감사 로그: AUDIT-2026-06-19-033
완료 시각: 2026-06-19T21:46:56+09:00
실측 비용 (시간): 약 0.15h
실측 비용 (LLM 토큰): unknown

## 완료 조건

- [x] Staging persistence options are compared.
- [x] MVP staging recommendation and R3 boundary are explicit.
- [x] No Supabase migration/apply, secret handling, production data, or deploy occurs.

## 완료 내용

- `MEMBERSHIP-STAGING-PERSISTENT-STORAGE-DECISION.json`/`.md`를 추가해 external/member staging의 source of truth를 Supabase Postgres/Auth/RLS로 고정했다.
- Local encrypted vault, SQLite file, Railway volume, runtime filesystem은 single-operator internal smoke 또는 non-tenant artifact 보조로만 허용하고, tenant account/membership/payment/secret metadata source of truth로 쓰지 않도록 명시했다.
- Auth/profile, membership request, subscription grant, payment evidence, integration secret metadata, portfolio/engine/trading state, audit events별 selected target과 external-user 전 선행 조건을 기록했다.
- `scripts/membership_staging_storage_decision_gate.py`와 focused tests를 추가해 Supabase 선택, local vault/Railway volume 비선택, cross-user test 요구, forbidden secret/storage key 차단을 검증한다.
- TASK-119 preflight checklist/gate를 persistent storage missing에서 decision recorded but implementation blocked 상태로 갱신했다.

## 완료 기록

완료일: 2026-06-19
결과: TASK-122 persistent-storage decision evidence가 완료됐다. Actual external staging still requires Owner/R3 Supabase project selection, migration/RLS review/apply, advisors, cross-user tests, backup/restore review, and external env writes.
변경 파일: `agents/project/MEMBERSHIP-STAGING-PERSISTENT-STORAGE-DECISION.json`, `agents/project/MEMBERSHIP-STAGING-PERSISTENT-STORAGE-DECISION.md`, `scripts/membership_staging_storage_decision_gate.py`, `tests/unit/test_membership_staging_storage_decision_gate.py`, `agents/project/MEMBERSHIP-STAGING-DEPLOY-PREFLIGHT-CHECKLIST.json`, `agents/project/MEMBERSHIP-STAGING-DEPLOY-PREFLIGHT-CHECKLIST.md`, `scripts/membership_staging_deploy_preflight_gate.py`, `tests/unit/test_membership_staging_deploy_preflight_gate.py`.
이슈: Decision is recorded, but no Supabase schema, migration, RLS policy, backup setup, Railway volume, deploy, or external env state was created or changed.
다음 담당자 인수 사항: The next safe R2 candidate is a Supabase staging migration/RLS review packet only; actual migration creation/apply remains Owner/R3.

## 증거

- `agents/project/MEMBERSHIP-STAGING-PERSISTENT-STORAGE-DECISION.json`
- `agents/project/MEMBERSHIP-STAGING-PERSISTENT-STORAGE-DECISION.md`
- `scripts/membership_staging_storage_decision_gate.py`
- `tests/unit/test_membership_staging_storage_decision_gate.py`

## 검증

- `python -m json.tool agents\project\MEMBERSHIP-STAGING-PERSISTENT-STORAGE-DECISION.json`
- `python -m json.tool agents\project\MEMBERSHIP-STAGING-DEPLOY-PREFLIGHT-CHECKLIST.json`
- `python scripts\membership_staging_storage_decision_gate.py --check`
- `python scripts\membership_staging_deploy_preflight_gate.py --check`
- `python -m pytest tests\unit\test_membership_staging_storage_decision_gate.py -q`
- `python -m pytest tests\unit\test_membership_staging_deploy_preflight_gate.py -q`

## 리뷰

- Backend Engineer self-review: The decision matches current code surfaces: `vault.users`, `vault.membership_requests`, `vault.user_integrations`, and SQLite runtime data stay prototype/internal only for external staging.
- Supabase/Railway source review: Supabase Postgres/Auth/RLS is the selected structured tenant data target; Railway volume is not a row-policy tenant store.
- QA perspective: Gates reject local vault or Railway volume becoming tenant source of truth and require cross-user/storage decision tests.

## Independent Audit

판정: 통과
- Same-session audit note: Only local decision packet, docs, gate, tests, and preflight checklist state changed.
- No DB migration, Supabase apply, external project mutation, external env write, Railway volume creation, public URL, secret, production data, KIS/payment/provider, order, or risk boundary changed.
