---
type: task
id: TASK-114
display_id: TASK-114
task_uid: 547b4537-2a53-4c45-b9b0-4c5bf6fc05ee
registered_at: 2026-06-19T18:31:09+09:00
created_at: 2026-06-19T18:31:09+09:00
started_at: 2026-06-19T18:31:09+09:00
updated_at: 2026-06-19T18:31:09+09:00
completed_at: 2026-06-19T18:31:09+09:00
status: 완료
owner: Backend Engineer
assignees: [Backend Engineer, Lead Engineer, QA]
priority: High
difficulty: 중
est_hours: 1
est_tokens: 18000
tags: [membership, supabase, rls, tenant-isolation, deploy-gate]
initiative_id: INIT-MEMBERSHIP-ACCESS
task_set_id: TASKSET-MEMBERSHIP-PROD-READINESS
gate: local tenant-isolation matrix and validation gate only; no production DB, no Supabase project mutation, no SQL migration, no deploy, no secret, no bank/payment API, no KIS/order/risk change
trigger_meeting: Owner goal continuation 2026-06-19
audit_log: AUDIT-2026-06-19-022
created: 2026-06-19
---

# TASK-114 Membership tenant isolation matrix

작업 ID: TASK-114
상태: 완료
Owner: Backend Engineer
요청 시각: 2026-06-19T18:31:09+09:00
기록 시각: 2026-06-19T18:31:09+09:00
완료 시각: 2026-06-19T18:31:09+09:00
요청자: Owner goal continuation ("승인 필요 없는 작업 계속")
수행자: Backend Engineer + Lead Engineer + QA perspective (Codex)
검토자: Backend Engineer self-review + QA perspective + Lead Engineer perspective
협업 waiver: 단일 세션 범위 작업. Supabase/user_id/RLS 격리 matrix와 local gate만 추가했고 production DB/schema migration/deploy/secret/payment/KIS 경계는 건드리지 않았다.
routing_ref: TASKSET-MEMBERSHIP-PROD-READINESS / TASK-114
selected_model: Codex coding agent
policy_model: AGENTS.md §6 R1/R2 local reversible implementation; AGENTS.md §16 DB/deploy/secret/KIS R3 surfaces avoided
실측 비용 (시간): 약 0.6h
실측 비용 (LLM 토큰): unknown
의도: TASK-087의 남은 multi-tenant/user_id/RLS 위험을 production 적용 전 검증 가능한 route/surface/invariant/test matrix로 고정한다.
대상: tenant isolation matrix JSON/Markdown, validation script, readiness checklist item, focused tests, membership planning records
방법: Supabase changelog/RLS/API security docs를 확인한 뒤 matrix JSON을 machine-readable source로 만들고 `scripts/membership_tenant_isolation_gate.py`가 필수 route group, tenant surface, invariant, test case를 검사하도록 했다.
감사 로그: AUDIT-2026-06-19-022

## 범위

포함:

- `agents/project/MEMBERSHIP-TENANT-ISOLATION-MATRIX.json` machine-readable matrix.
- `agents/project/MEMBERSHIP-TENANT-ISOLATION-MATRIX.md` human-readable summary.
- `scripts/membership_tenant_isolation_gate.py --check` local gate.
- Unit tests for the gate.
- `GET /api/membership/readiness`에 `tenant_isolation_matrix` pass item 추가.
- TASKSET/TASK-087/MEMBERSHIP-ACCESS-PLAN production handoff 업데이트.

제외:

- Supabase project connection or mutation.
- SQL migration file or production DB apply.
- Actual RLS policy execution in Supabase.
- Production secret storage implementation.
- Bank/payment API, PG, open-banking, virtual account.
- External deploy.
- KIS credential activation, order/risk/prod path change.

## 완료 조건

- [x] Matrix clearly says it is not applied to Supabase.
- [x] Matrix separates public, member self-service, member product read, owner admin, and engine worker route groups.
- [x] Matrix lists tenant-owned surfaces and requires `auth.uid()` ownership policies.
- [x] Matrix forbids browser service key/secret exposure and client-side-only filtering as authorization.
- [x] Matrix preserves applicant lookup non-disclosure.
- [x] Local gate fails if RLS, `auth.uid()` ownership, or secret redaction requirements are removed.
- [x] Readiness API can show matrix evidence while launch remains blocked.

## 완료 기록

완료일: 2026-06-19
결과: Membership production isolation now has a separate route/surface/test matrix. TASK-087 can proceed later with a concrete RLS and cross-user test target while `can_launch=false` remains correct until staging evidence exists.
변경 파일: `agents/project/MEMBERSHIP-TENANT-ISOLATION-MATRIX.json`, `agents/project/MEMBERSHIP-TENANT-ISOLATION-MATRIX.md`, `scripts/membership_tenant_isolation_gate.py`, `tests/unit/test_membership_tenant_isolation_gate.py`, `app/services/membership_readiness.py`, `tests/api/test_membership.py`, planning/task/report records.
이슈: This is a matrix/gate only. It does not prove actual Supabase RLS, staging isolation, production secret handling, payment evidence policy, or per-user engine isolation.
다음 담당자 인수 사항: Next no-approval candidate is a production payment-evidence retention decision record or per-user engine/safety isolation design, still without DB apply/deploy/secrets.

## 완료 내용

- Added tenant-isolation matrix JSON and Markdown asset.
- Added local validation gate for required route groups, tenant surfaces, RLS/user ownership, secret redaction, applicant lookup non-disclosure, and required staging tests.
- Added unit/API tests.
- Updated readiness service and membership lane records.

## 결과

TASK-114 완료. TASK-087 remains open because Supabase schema/RLS apply, staging deploy, production secret storage, real payment recognition, per-user engine/safety isolation, KIS terms, and provider execution remain incomplete.

## 증거

- `agents/project/MEMBERSHIP-TENANT-ISOLATION-MATRIX.json`
- `agents/project/MEMBERSHIP-TENANT-ISOLATION-MATRIX.md`
- `scripts/membership_tenant_isolation_gate.py`
- `tests/unit/test_membership_tenant_isolation_gate.py`
- `app/services/membership_readiness.py`
- `tests/api/test_membership.py`
- `agents/research_agent/notes/EVIDENCE-2026-06-19-004-membership-tenant-isolation-supabase.md`

## 리뷰

- Backend Engineer self-review: the gate is stdlib-only and reads local JSON; it cannot mutate Supabase, secrets, payment providers, or KIS paths.
- QA perspective: focused unit tests cover pass state and failure modes for RLS requirement, ownership policy, and secret redaction.
- Lead Engineer perspective: this narrows TASK-087's production risk without crossing AGENTS.md §16 R3 DB/deploy/secret/KIS boundaries.

## Independent Audit

판정: 통과

Same-session audit note: this is a design/contract verification, not a production tenant-isolation certification.

## 검증

- `python scripts\membership_tenant_isolation_gate.py --check` -> pass
- `python scripts\membership_contract_gate.py --check` -> pass
- `.venv\Scripts\python.exe -m pytest tests\unit\test_membership_tenant_isolation_gate.py tests\unit\test_membership_contract_gate.py tests\api\test_membership.py -q` -> pass
- generated task/report/schema/continuity/owner-governance/check_agent_docs gates -> pass
