---
type: task
id: TASK-108
display_id: TASK-108
task_uid: 8553ae33-5c79-4ad9-ba67-984a49930b7e
registered_at: 2026-06-19T15:31:20+09:00
created_at: 2026-06-19T15:31:20+09:00
started_at: 2026-06-19T15:31:20+09:00
updated_at: 2026-06-19T15:31:20+09:00
completed_at: 2026-06-19T15:31:20+09:00
status: 완료
owner: Backend Engineer
assignees: [Backend Engineer, UI/UX Designer, QA, Lead Engineer]
priority: High
difficulty: 중
est_hours: 1
est_tokens: 18000
tags: [membership, readiness, deploy-gate, production, local-prototype]
initiative_id: INIT-MEMBERSHIP-ACCESS
task_set_id: TASKSET-MEMBERSHIP-ACCESS
gate: owner-visible local readiness checklist only; no production DB, deploy, bank/payment API, provider call, KIS/order/risk/prod/secret change
trigger_meeting: Owner direct request 2026-06-19
audit_log: AUDIT-2026-06-19-018
created: 2026-06-19
---

# TASK-108 Membership production readiness gate

작업 ID: TASK-108
상태: 완료
Owner: Backend Engineer
요청 시각: 2026-06-19T15:31:20+09:00
기록 시각: 2026-06-19T15:31:20+09:00
완료 시각: 2026-06-19T15:31:20+09:00
요청자: Owner
수행자: Backend Engineer + UI/UX Designer + QA + Lead Engineer perspective (Codex)
검토자: Backend Engineer self-review + UI/UX Designer perspective + QA perspective + Lead Engineer perspective
협업 waiver: 단일 세션 범위 작업. 운영 전환 체크리스트를 화면/API로 추가했으며 production DB, 배포, secret, provider call, KIS/order/risk 경계는 건드리지 않았다.
routing_ref: TASKSET-MEMBERSHIP-ACCESS / TASK-108
selected_model: Codex coding agent
policy_model: AGENTS.md §6 R1/R2 local reversible implementation; AGENTS.md §16 R3 surfaces avoided
실측 비용 (시간): 약 0.5h
실측 비용 (LLM 토큰): unknown
의도: 검증회원/입금승인 local flow가 어디까지 준비됐고, 외부 사용자/프로덕션 배포 전 무엇이 아직 차단인지 Owner가 화면에서 확인할 수 있게 한다.
대상: membership readiness service/API, `/settings > 회원 승인` readiness panel, API/E2E tests
방법: static local readiness checklist를 Owner-only API로 노출하고, 설정의 회원 승인 탭 상단에 pass/watch/block 상태를 표시했다. 환경값은 존재 여부만 bool로 반환하고 secret 값은 노출하지 않는다.
감사 로그: AUDIT-2026-06-19-018

## 범위

포함:

- `GET /api/membership/readiness` Owner-only endpoint.
- Local readiness items: local flow pass, Supabase schema block, RLS/user_id block, production secret storage block, payment recognition block, per-user engine/safety block, KIS terms watch, external deploy block.
- `/settings > 회원 승인` 운영 전환 체크 panel.
- API tests for Owner access, guest/member/anonymous boundary, no secret value exposure.
- Playwright E2E for visible readiness blockers.

제외:

- Supabase schema creation or migration.
- production DB/RLS apply.
- external deploy.
- real payment/bank API/PG/open-banking.
- provider API/OAuth validation.
- KIS credential activation, order/risk/prod changes.

## 완료 조건

- [x] Owner can read production-readiness status.
- [x] anonymous, guest, and member callers cannot read Owner readiness.
- [x] readiness response has `can_launch=false` while R3 gates are incomplete.
- [x] response exposes only environment flag booleans, never secret values.
- [x] settings membership tab shows local prototype/readiness blockers.
- [x] API, lint, build, and E2E checks pass.

## 완료 기록

완료일: 2026-06-19
결과: Owner can now see why the membership flow is still local-only before external users or deployment: production DB/RLS, secret storage, payment recognition, per-user engine safety, KIS terms, and deploy gates are explicit.
변경 파일: `app/services/membership_readiness.py`, `app/api/routers/membership.py`, `app/api/schemas/__init__.py`, `web/src/lib/api.ts`, `web/src/app/settings/page.tsx`, `tests/api/test_membership.py`, `web/e2e/settings-membership.spec.ts`.
이슈: The checklist is a local diagnostic, not proof that production is ready. It intentionally blocks launch until R3 work is explicitly approved and verified.
다음 담당자 인수 사항: TASK-087에서 Supabase/RLS schema, production secret storage, payment recognition, per-user engine/safety isolation, and deployment should each move from block to verified pass only with direct evidence.

## 완료 내용

- Added local membership production-readiness service and Owner-only API.
- Added membership settings readiness panel.
- Added focused API and E2E coverage.

## 결과

TASK-108 완료. 전체 membership/deploy objective는 production DB/Supabase/RLS, real payment/bank integration, external deploy, production secret storage, per-user engine/safety isolation, and provider/OAuth execution work가 남아 있어 active 상태로 유지한다.

## 증거

- `app/services/membership_readiness.py`
- `app/api/routers/membership.py`
- `web/src/app/settings/page.tsx`
- `tests/api/test_membership.py`
- `web/e2e/settings-membership.spec.ts`

## 리뷰

- Backend Engineer self-review: readiness endpoint is Owner-only and exposes no secret values.
- UI/UX Designer perspective: readiness blockers are visible in the existing membership admin surface.
- QA perspective: API and Playwright checks cover access boundaries and visible blockers.
- Lead Engineer perspective: this clarifies production blockers without crossing production deploy/DB/secret/order boundaries.

## Independent Audit

판정: 통과

Same-session audit note: readiness is a checklist over current known blockers, not a production certification.

## 검증

- `.venv\Scripts\python.exe -m pytest tests/api/test_membership.py tests/api/test_integrations.py -q` -> 19 passed, 3 warnings
- `npm run lint` in `web/` -> pass
- `npm run build` in `web/` -> pass
- `npm run test:e2e -- e2e/settings-membership.spec.ts --reporter=line` -> 1 passed
