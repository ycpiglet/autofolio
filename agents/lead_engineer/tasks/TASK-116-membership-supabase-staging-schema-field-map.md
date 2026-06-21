---
type: task
id: TASK-116
display_id: TASK-116
task_uid: 0bb239de-08a0-4c0a-8987-5182e78d473c
registered_at: 2026-06-19T19:57:08+09:00
created_at: 2026-06-19T19:57:08+09:00
started_at: 2026-06-19T20:10:00+09:00
updated_at: 2026-06-19T20:20:16+09:00
completed_at: 2026-06-19T20:10:00+09:00
status: 완료
owner: Backend Engineer
assignees: [Backend Engineer, Lead Engineer, QA, Compliance Officer]
priority: High
difficulty: 중
est_hours: 2
est_tokens: 30000
tags: [membership, supabase, rls, schema, field-map, production-readiness]
initiative_id: INIT-MEMBERSHIP-ACCESS
task_set_id: TASKSET-MEMBERSHIP-PROD-IMPLEMENTATION-PLANNING
gate: docs/field-map only; no migration file, no schema.sql change, no Supabase project mutation, no production DB apply
trigger_meeting: Owner goal continuation 2026-06-19
audit_log: AUDIT-2026-06-19-026
created: 2026-06-19
---

# TASK-116 Membership Supabase staging schema/RLS field map

작업 ID: TASK-116
상태: 완료
Owner: Backend Engineer
요청 시각: 2026-06-19T19:57:08+09:00
기록 시각: 2026-06-19T19:57:08+09:00
완료 시각: 2026-06-19T20:10:00+09:00
요청자: Owner goal continuation
수행자: Backend Engineer + Lead Engineer + QA + Compliance Officer perspective (Codex)
검토자: Backend Engineer self-review + Lead Engineer handoff review + QA checklist perspective + Compliance Officer boundary perspective; 협업 waiver(사유): single-session docs/field-map scope; no Supabase project, migration, production DB, deploy, secret, payment, or KIS/order/risk surface crossed.
routing_ref: TASKSET-MEMBERSHIP-PROD-IMPLEMENTATION-PLANNING / TASK-116
selected_model: Codex coding agent
policy_model: Supabase skill 0.1.2 + official Supabase changelog/RLS/API/security docs; AGENTS.md §6 R1/R2 local reversible documentation lane; AGENTS.md §16 R3 surfaces avoided
실측 비용 (시간): 약 0.5h
실측 비용 (LLM 토큰): unknown
의도: Existing membership contracts를 Supabase staging schema/RLS field map으로 변환한다.
대상: Membership production contract, tenant isolation matrix, secret policy, payment evidence policy, engine safety contract.
방법: docs/field-map only. No migration file, no schema.sql change, no Supabase project mutation, no production DB apply.
감사 로그: AUDIT-2026-06-19-026

## 범위

포함:

- Reviewable Markdown/JSON field map for membership, integration, payment evidence, engine state, risk, order intent, and audit entities.
- RLS policy names and required staging tests.
- Explicit owner/admin server-audit paths.

제외:

- Migration file creation.
- `app/database/schema.sql` change.
- Supabase project connection or SQL apply.
- Production DB, secrets, payment API, deploy, KIS/order/risk/prod changes.

## 완료 조건

- [x] Field map references existing contracts.
- [x] RLS policy/test checklist exists.
- [x] No migration/apply files are created.
- [x] TASK-087 handoff map is updated.

## 완료 내용

- Official Supabase changelog, RLS, API security, product security docs를 확인하고 Data API exposure, RLS `TO authenticated`, `auth.uid()` ownership predicate, UPDATE `USING`/`WITH CHECK`, service key browser exposure 금지, user_metadata auth 금지 지침을 field map에 반영했다.
- `agents/project/MEMBERSHIP-SUPABASE-STAGING-FIELD-MAP.json`/`.md`를 추가했다.
- `scripts/membership_supabase_field_map_gate.py`와 focused tests를 추가해 field map의 RLS/auth/Data API/secret/payment/test checklist를 로컬에서 검증하도록 했다.
- Field map은 profiles, membership_requests, deposit_instructions, approval_events, subscription_grants, integration_secret_metadata, payment_evidence, portfolio_accounts, holdings_snapshots, risk_settings, engine_state, engine_run_queue, trade_conditions, order_intents, order_logs, execution_logs, notifications, audit_events를 owner field/RLS/Data API/policy/test target으로 매핑한다.
- TASK-087 handoff map과 `MEMBERSHIP-PRODUCTION-IMPLEMENTATION-PLAN.md`를 TASK-116 완료 상태로 갱신했다.

## 완료 기록

완료일: 2026-06-19
결과: Supabase staging schema/RLS migration 작성 전 review target이 생겼다. 이 산출물은 적용 전 field map이며 launch evidence가 아니다.
변경 파일: `agents/project/MEMBERSHIP-SUPABASE-STAGING-FIELD-MAP.json`, `agents/project/MEMBERSHIP-SUPABASE-STAGING-FIELD-MAP.md`, `scripts/membership_supabase_field_map_gate.py`, `tests/unit/test_membership_supabase_field_map_gate.py`, `MEMBERSHIP-PRODUCTION-IMPLEMENTATION-PLAN.md`, `TASK-087`, TASKSET/STATUS/AUDIT/BRIEF/generated views.
이슈: 실제 staging migration, Supabase RLS apply, Data API grants, advisor output, cross-user test evidence는 아직 없다.
다음 담당자 인수 사항: Next no-approval candidate is TASK-117 payment recognition option decision packet. It must not set up bank/PG/Open Banking accounts, credentials, API calls, or real payment records.

## 증거

- `agents/project/MEMBERSHIP-SUPABASE-STAGING-FIELD-MAP.json`
- `agents/project/MEMBERSHIP-SUPABASE-STAGING-FIELD-MAP.md`
- `scripts/membership_supabase_field_map_gate.py`
- `tests/unit/test_membership_supabase_field_map_gate.py`
- `agents/project/MEMBERSHIP-PRODUCTION-IMPLEMENTATION-PLAN.md`
- `agents/lead_engineer/tasks/TASK-087-web-deploy-membership-gating.md`

## 검증

- `python -m json.tool agents/project/MEMBERSHIP-SUPABASE-STAGING-FIELD-MAP.json`
- `python scripts/membership_supabase_field_map_gate.py --check`
- `.venv\Scripts\python.exe -m pytest tests\unit\test_membership_supabase_field_map_gate.py -q`
- `python scripts/build_task_index.py --check`
- `python scripts/generate_views.py --check`
- `python scripts/generate_report_views.py --check`
- `python scripts/work_schema_gate.py --items --check`
- `python scripts/check_agent_docs.py`
- `git diff --check`

## 리뷰

- Backend Engineer self-review: field map is a review target, not migration SQL. It avoids schema.sql and Supabase project mutation.
- QA perspective: staging tests are explicit for anon access, member A/B isolation, update reassign blocking, admin route audit, secret redaction, and append-only trading logs.
- Compliance Officer perspective: payment evidence, secret handling, KIS credentials, live execution, and public launch remain blocked behind separate review.

## Independent Audit

판정: 통과
- Same-session audit note: The task only added planning/field-map artifacts and updated handoff records.
- No migration file, `app/database/schema.sql` change, Supabase project mutation, production DB apply, deploy, secret read/write, payment API, KIS/order/risk/prod change was performed.
