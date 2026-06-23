---
type: task
id: TASK-119
display_id: TASK-119
task_uid: 0df1db0a-3456-4468-9407-c1b6d698aa9b
registered_at: 2026-06-19T19:57:08+09:00
created_at: 2026-06-19T19:57:08+09:00
updated_at: 2026-06-19T21:06:22+09:00
started_at: 2026-06-19T21:00:04+09:00
completed_at: 2026-06-19T21:06:22+09:00
status: 완료
owner: CI/CD Engineer
assignees: [CI/CD Engineer, Lead Engineer, Backend Engineer, QA]
priority: Medium
difficulty: 중
est_hours: 2
est_tokens: 25000
tags: [membership, deploy, staging, preflight, vercel, railway, supabase]
initiative_id: INIT-MEMBERSHIP-ACCESS
task_set_id: TASKSET-MEMBERSHIP-PROD-IMPLEMENTATION-PLANNING
gate: checklist only; no deploy, no external project mutation, no env var write, no public URL publish
trigger_meeting: Owner goal continuation 2026-06-19
audit_log: AUDIT-2026-06-19-030
created: 2026-06-19
---

# TASK-119 Membership staging deploy preflight checklist

작업 ID: TASK-119
상태: 완료
Owner: CI/CD Engineer
요청 시각: 2026-06-19T19:57:08+09:00
기록 시각: 2026-06-19T19:57:08+09:00
완료 시각: 2026-06-19T21:06:22+09:00
요청자: Owner goal continuation
수행자: CI/CD Engineer + Lead Engineer + Backend Engineer + QA perspective (Codex)
검토자: CI/CD Engineer self-review + Lead Engineer handoff review + Backend Engineer deploy-surface review + QA checklist perspective; 협업 waiver(사유): single-session checklist/gate scope; no deploy, external project mutation, env var write, public URL publication, Supabase migration/apply, secret handling, KIS/payment activation, or .github workflow change crossed.
routing_ref: TASKSET-MEMBERSHIP-PROD-IMPLEMENTATION-PLANNING / TASK-119
selected_model: Codex coding agent
policy_model: Supabase skill 0.1.2 + Vercel deployments-cicd skill + official Vercel/Railway/Supabase docs; AGENTS.md §6 R1/R2 checklist lane; AGENTS.md §16 R3 surfaces avoided
실측 비용 (시간): 약 0.4h
실측 비용 (LLM 토큰): unknown
의도: Vercel/Railway/Supabase staging deploy 전에 필요한 evidence checklist와 smoke plan을 작성한다.
대상: staging deploy preflight checklist, environment inventory placeholders, smoke/rollback plan.
방법: checklist only. No deploy, no external project mutation, no env var write, no public URL publish.
감사 로그: AUDIT-2026-06-19-030

## 범위

포함:

- Environment inventory placeholders.
- Required smoke tests and rollback checklist.
- Owner/R3 action boundary for actual deploy.

제외:

- Vercel/Railway/Supabase deploy.
- Environment variable write.
- Public URL publication.
- Production DB, secrets, KIS/order/risk changes.

## 완료 조건

- [x] Preflight checklist exists.
- [x] Required smoke tests are listed.
- [x] Deploy actions remain Owner/R3 gated.

## 완료 내용

- Official Vercel Git deployment, environment variable, and environment docs를 확인해 Vercel frontend staging target을 preview/custom staging으로 제한했다.
- Official Railway variables, healthcheck, public networking, Dockerfile docs를 확인해 Railway backend가 `/api/health` healthcheck와 `$PORT` binding 검토를 필요로 한다는 blocker를 기록했다.
- Official Supabase CLI, API security, RLS docs를 확인해 Supabase staging migration/RLS/Data API/advisor/cross-user tests를 actual deploy 전 gate로 분리했다.
- `MEMBERSHIP-STAGING-DEPLOY-PREFLIGHT-CHECKLIST.json`/`.md`를 작성해 Vercel frontend, Railway backend, Supabase staging service targets, environment inventory placeholders, local checks, staging smoke plan, rollback plan, forbidden actions, launch gates를 고정했다.
- 현재 repo blocker로 `.env.example` 부재, Railway fixed `8000` port Dockerfile, Supabase migration/RLS 미적용, local vault/runtime persistence 전략 미확정, KIS/payment external boundary를 기록했다.
- `scripts/membership_staging_deploy_preflight_gate.py`와 focused unit tests를 추가해 checklist가 deploy/applied 상태나 secret/env value 기록으로 오인되지 않도록 검증한다.

## 완료 기록

완료일: 2026-06-19
결과: TASK-119 staging deploy preflight checklist가 생성됐다. 이 산출물은 checklist only이며 staging deploy evidence가 아니다. Actual deploy는 repo blocker 해소 또는 Owner/R3 waiver 전까지 차단된다.
변경 파일: `agents/project/MEMBERSHIP-STAGING-DEPLOY-PREFLIGHT-CHECKLIST.json`, `agents/project/MEMBERSHIP-STAGING-DEPLOY-PREFLIGHT-CHECKLIST.md`, `scripts/membership_staging_deploy_preflight_gate.py`, `tests/unit/test_membership_staging_deploy_preflight_gate.py`, `agents/project/MEMBERSHIP-PRODUCTION-IMPLEMENTATION-PLAN.md`, `agents/project/initiatives/TASKSET-MEMBERSHIP-PROD-IMPLEMENTATION-PLANNING.md`, `agents/lead_engineer/tasks/TASK-087-web-deploy-membership-gating.md`, TASKSET/STATUS/AUDIT/BRIEF/generated views.
이슈: actual staging deploy remains blocked by `.env.example` mismatch, Railway `$PORT` binding review, Supabase migration/RLS apply, persistent storage strategy, and KIS/payment external boundaries.
다음 담당자 인수 사항: Create a follow-up no-Owner R2 taskset for deploy-preflight blocker remediation where safe: sanitized env inventory template, Railway port/healthcheck config plan or patch, and persistent storage decision packet. Supabase migration/apply and external deploy remain Owner/R3.

## 증거

- `agents/project/MEMBERSHIP-STAGING-DEPLOY-PREFLIGHT-CHECKLIST.json`
- `agents/project/MEMBERSHIP-STAGING-DEPLOY-PREFLIGHT-CHECKLIST.md`
- `scripts/membership_staging_deploy_preflight_gate.py`
- `tests/unit/test_membership_staging_deploy_preflight_gate.py`
- `agents/project/MEMBERSHIP-PRODUCTION-IMPLEMENTATION-PLAN.md`
- `agents/project/initiatives/TASKSET-MEMBERSHIP-PROD-IMPLEMENTATION-PLANNING.md`
- `agents/lead_engineer/tasks/TASK-087-web-deploy-membership-gating.md`

## 검증

- `python -m json.tool agents\project\MEMBERSHIP-STAGING-DEPLOY-PREFLIGHT-CHECKLIST.json`
- `python scripts\membership_staging_deploy_preflight_gate.py --check`
- `python -m pytest tests\unit\test_membership_staging_deploy_preflight_gate.py -q`
- `python scripts\membership_contract_gate.py --check`
- `python scripts\membership_supabase_field_map_gate.py --check`
- `python scripts\membership_secret_store_plan_gate.py --check`
- `python scripts\membership_payment_recognition_decision_gate.py --check`
- `python scripts\membership_payment_policy_gate.py --check`
- `python scripts\membership_secret_policy_gate.py --check`
- `python scripts\membership_tenant_isolation_gate.py --check`
- `python scripts\membership_engine_safety_gate.py --check`
- `python scripts\build_task_index.py --check`
- `python scripts\generate_views.py --check`
- `python scripts\generate_report_views.py --check`
- `python scripts\work_item_classifier.py --check`
- `python scripts\work_schema_gate.py --items --check`
- `python scripts\continuity_contract_gate.py --check`
- `python scripts\owner_governance_gate.py --allow-empty-owner-docs`
- `python scripts\check_agent_docs.py`
- `git diff --check`

## 리뷰

- CI/CD Engineer self-review: The checklist defines deploy prerequisites and smoke/rollback evidence only; it does not execute deploy or alter CI/CD workflows.
- Backend Engineer perspective: Current root Dockerfile fixed port and local runtime persistence are correctly marked as blockers for actual Railway staging.
- QA perspective: Smoke plan covers frontend load, proxied health, signup safety, guest/autoregister fail-closed, readiness blocked, mock KIS, and no disclosure.
- Lead Engineer perspective: The taskset's R2 planning slice is now complete; actual deploy, env writes, Supabase apply, and external publication remain Owner/R3.

## Independent Audit

판정: 통과
- Same-session audit note: The task added checklist/gate/test artifacts and handoff records only.
- No Vercel, Railway, Supabase, GitHub workflow, environment variable, public URL, Supabase migration, secret, KIS credential, bank/PG/Open Banking, payment, production DB, or deploy target was changed.
