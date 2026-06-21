---
type: task
id: TASK-105
display_id: TASK-105
task_uid: f7b69ee3-a9a9-4dec-8054-34bcd9fbabb8
registered_at: 2026-06-19T14:49:58+09:00
created_at: 2026-06-19T14:49:58+09:00
started_at: 2026-06-19T14:49:58+09:00
updated_at: 2026-06-19T14:49:58+09:00
completed_at: 2026-06-19T14:49:58+09:00
status: 완료
owner: Backend Engineer
assignees: [Backend Engineer, UI/UX Designer, QA, Lead Engineer]
priority: High
difficulty: 중
est_hours: 1
est_tokens: 14000
tags: [auth, membership, guest-demo, fail-closed, local-prototype]
initiative_id: INIT-MEMBERSHIP-ACCESS
task_set_id: TASKSET-MEMBERSHIP-ACCESS
gate: local auth/login UI only; no production DB, deploy, bank/payment API, real account number, KIS/order/risk/prod/secret change
trigger_meeting: Owner direct request 2026-06-19
audit_log: AUDIT-2026-06-19-015
created: 2026-06-19
---

# TASK-105 Membership guest demo fail-closed

작업 ID: TASK-105
상태: 완료
Owner: Backend Engineer
요청 시각: 2026-06-19T14:49:58+09:00
기록 시각: 2026-06-19T14:49:58+09:00
완료 시각: 2026-06-19T14:49:58+09:00
요청자: Owner
수행자: Backend Engineer + UI/UX Designer + QA + Lead Engineer perspective (Codex)
검토자: Backend Engineer self-review + QA perspective + Lead Engineer perspective
협업 waiver: 단일 세션 범위 작업. 승인제 회원가입과 충돌하는 기본 guest/demo 발급과 공개 CTA만 좁게 차단했으며 production DB/payment/deploy/secret 없음.
routing_ref: TASKSET-MEMBERSHIP-ACCESS / TASK-105
selected_model: Codex coding agent
policy_model: AGENTS.md §6 R1/R2 local reversible implementation; AGENTS.md §16 R3 surfaces avoided
실측 비용 (시간): 약 0.4h
실측 비용 (LLM 토큰): unknown
의도: 검증된 사람만 승인하는 회원제 흐름에서 기본 게스트 데모 로그인으로 우회 진입하지 못하게 한다.
대상: `app/api/routers/auth.py`, `web/src/app/login/page.tsx`, `web/src/app/onboarding/investor-profile/page.tsx`, `web/src/lib/api.ts`, `tests/api/test_auth.py`, `web/e2e/login.spec.ts`, `web/e2e/dashboard.spec.ts`, membership planning records
방법: `/api/auth/login`의 `guest=true` 발급을 기본 403으로 차단하고, `AUTOFOLIO_GUEST_DEMO_ENABLED=1`이 있을 때만 로컬/dev guest demo session을 발급하게 했다. 로그인 화면에서는 게스트 CTA를 제거하고 가입 승인 신청으로 유도했다.
감사 로그: AUDIT-2026-06-19-015

## 범위

포함:

- `AUTOFOLIO_GUEST_DEMO_ENABLED` 명시 opt-in이 없으면 `/api/auth/login` guest flow를 403으로 차단.
- 개발/로컬 테스트용 opt-in guest flow는 유지.
- 공개 로그인 화면에서 guest/demo CTA 제거.
- onboarding 저장 안내 문구를 승인 계정 로그인 기준으로 갱신.
- auth API test를 default fail-closed + env opt-in success로 변경.
- login E2E는 guest button 부재와 가입 승인 신청 CTA를 검증.
- dashboard E2E는 guest button login 대신 승인 member session mock으로 진입하도록 변경.
- 포트폴리오 E2E mock을 현재 `/api/portfolio/overview` 계약에 맞게 갱신.

제외:

- production DB/Supabase schema or migration.
- external deploy.
- real payment/bank API/open-banking/PG.
- 실제 계좌번호, 고객 입금기록, 고객 PII repo 저장.
- user_id 단위 포트폴리오/엔진/주문 데이터 격리 완성.
- KIS/order/risk/prod/secret 변경.

## 완료 조건

- [x] guest login is denied by default.
- [x] guest login works only with explicit local/dev env opt-in.
- [x] public login UI does not expose a guest/demo CTA.
- [x] 가입 승인 신청 CTA remains visible.
- [x] E2E login/dashboard flows no longer rely on guest demo login.
- [x] API, lint, build, and focused E2E checks pass.

## 완료 기록

완료일: 2026-06-19
결과: public access path is now approval-based by default. The server no longer issues guest demo sessions unless a developer explicitly opts in with `AUTOFOLIO_GUEST_DEMO_ENABLED=1`, and the login screen directs users to approved login or signup approval request.
변경 파일: `app/api/routers/auth.py`, `web/src/app/login/page.tsx`, `web/src/app/onboarding/investor-profile/page.tsx`, `web/src/lib/api.ts`, `tests/api/test_auth.py`, `web/e2e/login.spec.ts`, `web/e2e/dashboard.spec.ts`, `agents/project/MEMBERSHIP-ACCESS-PLAN.md`, `agents/project/initiatives/INIT-MEMBERSHIP-ACCESS.md`, `agents/project/initiatives/TASKSET-MEMBERSHIP-ACCESS.md`, `agents/lead_engineer/tasks/TASK-087-web-deploy-membership-gating.md`.
이슈: Internal signed guest fixtures still exist for legacy read-only/mock test coverage. They do not create server-issued public guest sessions, but production member read-scope and user_id isolation remain unresolved.
다음 담당자 인수 사항: TASK-087에서 production Supabase/RLS schema, member read scope, and per-user data/engine/safety isolation을 설계한다.

## 완료 내용

- Guest demo issuance is fail-closed by default.
- Login surface no longer presents a guest demo action.
- Signup approval is the default non-login CTA.
- E2E fixtures were moved away from guest login and aligned to approved member session assumptions.
- Portfolio E2E mocks were updated to the current overview API contract while touching the dashboard spec.

## 결과

TASK-105 완료. 전체 membership product goal은 아직 production schema, deployment, payment provider, and user_id isolation이 남아 있어 active 상태로 유지한다.

## 증거

- `app/api/routers/auth.py`
- `web/src/app/login/page.tsx`
- `tests/api/test_auth.py`
- `web/e2e/login.spec.ts`
- `web/e2e/dashboard.spec.ts`

## 리뷰

- Backend Engineer self-review: server-issued guest session path now requires explicit dev env opt-in.
- UI/UX Designer perspective: login screen now matches approval-based signup flow instead of offering guest access.
- QA perspective: API tests cover default deny and opt-in allow; E2E login/dashboard paths no longer depend on guest demo login.
- Lead Engineer perspective: production DB, deploy, real payment/bank API, KIS/order/risk/secret 경계는 건드리지 않았다.

## Independent Audit

판정: 통과

Same-session audit note: local fail-closed auth/UI hardening only. This reduces public bypass risk for the verified signup model, but it does not replace production RLS/user_id isolation.

## 검증

- `.venv\Scripts\python.exe -m pytest tests/api/test_auth.py tests/api/test_gate.py tests/api/test_account.py tests/api/test_membership.py -q` -> 59 passed, 3 warnings
- `.venv\Scripts\python.exe -m pytest tests/api -q` -> 311 passed, 19 warnings
- `npm run lint` in `web/` -> pass
- `npm run build` in `web/` -> pass
- `npm run test:e2e -- e2e/login.spec.ts --reporter=line` -> 5 passed
- `npm run test:e2e -- e2e/dashboard.spec.ts --reporter=line` -> 6 passed
