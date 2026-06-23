---
type: task
id: TASK-109
display_id: TASK-109
task_uid: d4e621ac-24c0-400a-8dfa-fdc629d6584e
registered_at: 2026-06-19T15:45:36+09:00
created_at: 2026-06-19T15:45:36+09:00
started_at: 2026-06-19T15:45:36+09:00
updated_at: 2026-06-19T15:45:36+09:00
completed_at: 2026-06-19T15:45:36+09:00
status: 완료
owner: Backend Engineer
assignees: [Backend Engineer, Lead Engineer, QA]
priority: High
difficulty: 중
est_hours: 1
est_tokens: 18000
tags: [membership, supabase, rls, production-contract, deploy-gate]
initiative_id: INIT-MEMBERSHIP-ACCESS
task_set_id: TASKSET-MEMBERSHIP-ACCESS
gate: local contract and validation gate only; no production DB migration/apply, no Supabase project mutation, no deploy, no secret, no bank/payment API, no KIS/order/risk change
trigger_meeting: Owner direct request 2026-06-19
audit_log: AUDIT-2026-06-19-019
created: 2026-06-19
---

# TASK-109 Membership Supabase/RLS production contract

작업 ID: TASK-109
상태: 완료
Owner: Backend Engineer
요청 시각: 2026-06-19T15:45:36+09:00
기록 시각: 2026-06-19T15:45:36+09:00
완료 시각: 2026-06-19T15:45:36+09:00
요청자: Owner
수행자: Backend Engineer + Lead Engineer + QA perspective (Codex)
검토자: Backend Engineer self-review + QA perspective + Lead Engineer perspective
협업 waiver: 단일 세션 범위 작업. Supabase/RLS contract asset과 local validation gate만 추가했고 production DB/schema migration/deploy/secret/payment/KIS 경계는 건드리지 않았다.
routing_ref: TASKSET-MEMBERSHIP-ACCESS / TASK-109
selected_model: Codex coding agent
policy_model: AGENTS.md §6 R1/R2 local reversible implementation; AGENTS.md §16 DB migration/R3 surfaces avoided
실측 비용 (시간): 약 0.4h
실측 비용 (LLM 토큰): unknown
의도: 외부 사용자/웹서비스 전환 전에 필요한 Supabase/RLS/user_id/secret/payment/engine 계약을 DB 적용 없이 검증 가능한 asset으로 고정한다.
대상: membership production contract JSON/Markdown, validation script, readiness checklist item, focused tests
방법: Context7로 Supabase RLS guidance를 확인한 뒤, contract JSON을 machine-readable source로 만들고 `scripts/membership_contract_gate.py`가 필수 entity/invariant/launch gate를 검사하도록 했다.
감사 로그: AUDIT-2026-06-19-019

## 범위

포함:

- `agents/project/MEMBERSHIP-PRODUCTION-CONTRACT.json` machine-readable production contract.
- `agents/project/MEMBERSHIP-PRODUCTION-CONTRACT.md` human-readable contract.
- `scripts/membership_contract_gate.py --check` local contract gate.
- Unit tests for the contract gate.
- `GET /api/membership/readiness`에 `production_contract` pass item 추가.

제외:

- Supabase project connection or mutation.
- DB schema migration file or production DB apply.
- actual RLS policy execution in Supabase.
- provider secret storage implementation.
- bank/payment API, PG, open-banking, virtual account.
- external deploy.
- KIS credential activation, order/risk/prod path change.

## 완료 조건

- [x] Contract clearly says it is not applied to production.
- [x] Contract lists tenant-owned production entities and requires user-owned RLS.
- [x] Contract forbids service/secret key browser exposure and plaintext provider token responses.
- [x] Contract requires server-audited owner/admin operations.
- [x] Contract includes minimal payment evidence and user-scoped engine/safety invariants.
- [x] Local gate fails if core RLS/secret requirements are removed.
- [x] Readiness API can show the contract exists while launch remains blocked.

## 완료 기록

완료일: 2026-06-19
결과: Supabase/RLS production architecture is now a durable, validated local asset instead of only a prose TODO. It gives TASK-087 a concrete acceptance target while keeping `can_launch=false` until real staging/production evidence exists.
변경 파일: `agents/project/MEMBERSHIP-PRODUCTION-CONTRACT.json`, `agents/project/MEMBERSHIP-PRODUCTION-CONTRACT.md`, `scripts/membership_contract_gate.py`, `tests/unit/test_membership_contract_gate.py`, `app/services/membership_readiness.py`, `tests/api/test_membership.py`.
이슈: This is a contract gate only. It does not prove that a Supabase project, RLS policies, service key handling, payment recognition, or per-user engine isolation is implemented. A standalone `python scripts\taskset_work_gate.py --check` run still fails on pre-existing legacy TASK records missing `task_set_id`; owner-governance skipped that host-inapplicable gate and this task did not change those legacy records.
다음 담당자 인수 사항: TASK-087 should treat production schema/RLS implementation, staging migration, tenant isolation tests, secret storage, payment evidence policy, per-user engine/safety, and deploy smoke as separate evidence gates.

## 완료 내용

- Added membership production contract JSON and Markdown asset.
- Added local validation gate for required entities, RLS invariants, service key restrictions, secret redaction, payment minimization, and launch gates.
- Added unit/API tests.
- Updated readiness service to distinguish contract evidence from production apply evidence.

## 결과

TASK-109 완료. TASK-087 remains open because production DB/Supabase/RLS apply, staging deploy, production secret storage, real payment recognition, per-user engine/safety isolation, KIS terms, and provider execution remain incomplete.

## 증거

- `agents/project/MEMBERSHIP-PRODUCTION-CONTRACT.json`
- `agents/project/MEMBERSHIP-PRODUCTION-CONTRACT.md`
- `scripts/membership_contract_gate.py`
- `tests/unit/test_membership_contract_gate.py`
- `app/services/membership_readiness.py`
- `tests/api/test_membership.py`

## 리뷰

- Backend Engineer self-review: the gate is stdlib-only and reads local JSON; it cannot mutate Supabase or secrets.
- QA perspective: focused unit and membership API tests cover pass state and failure modes.
- Lead Engineer perspective: this lowers launch ambiguity without crossing AGENTS.md §16 R3 DB/deploy/secret boundaries.

## Independent Audit

판정: 통과

Same-session audit note: this is a design/contract verification, not a production security certification.

## 검증

- `python scripts\membership_contract_gate.py --check` -> pass
- `.venv\Scripts\python.exe -m pytest tests\unit\test_membership_contract_gate.py tests\api\test_membership.py -q` -> 17 passed, 2 warnings
- `.venv\Scripts\python.exe -m pytest tests\api -q` -> 332 passed, 20 warnings
- `npm run lint` in `web/` -> pass
- `npm run build` in `web/` -> pass
- `npm run test:e2e -- e2e/settings-membership.spec.ts --reporter=line` in `web/` -> 1 passed
- `python scripts\build_task_index.py --check` -> pass
- `python scripts\generate_views.py --check` -> pass
- `python scripts\generate_report_views.py --check` -> pass
- `python scripts\validate_task_schema.py` -> pass
- `python scripts\work_schema_gate.py --items --check` -> pass
- `python scripts\continuity_contract_gate.py --check` -> pass
- `python scripts\conversation_work_audit.py --check` -> pass
- `python scripts\owner_governance_gate.py --allow-empty-owner-docs` -> pass
- `python scripts\check_agent_docs.py` -> 0 errors, 130 existing warnings
- `git diff --check` -> no whitespace errors; existing CRLF warnings only
