---
type: task
id: TASK-107
display_id: TASK-107
task_uid: 433d9e27-194e-4cd9-b452-4c4d5116ea62
registered_at: 2026-06-19T15:26:20+09:00
created_at: 2026-06-19T15:26:20+09:00
started_at: 2026-06-19T15:26:20+09:00
updated_at: 2026-06-19T15:26:20+09:00
completed_at: 2026-06-19T15:26:20+09:00
status: 완료
owner: Backend Engineer
assignees: [Backend Engineer, UI/UX Designer, QA, Lead Engineer]
priority: High
difficulty: 중
est_hours: 2
est_tokens: 24000
tags: [membership, integrations, llm, sns, token-vault, local-prototype]
initiative_id: INIT-MEMBERSHIP-ACCESS
task_set_id: TASKSET-MEMBERSHIP-ACCESS
gate: local encrypted-vault token harness only; no outbound provider call, no live OAuth, no production DB, no external deploy, no KIS/order/risk/prod/secret change
trigger_meeting: Owner direct request 2026-06-19
audit_log: AUDIT-2026-06-19-017
created: 2026-06-19
---

# TASK-107 User-owned integration token harness

작업 ID: TASK-107
상태: 완료
Owner: Backend Engineer
요청 시각: 2026-06-19T15:26:20+09:00
기록 시각: 2026-06-19T15:26:20+09:00
완료 시각: 2026-06-19T15:26:20+09:00
요청자: Owner
수행자: Backend Engineer + UI/UX Designer + QA + Lead Engineer perspective (Codex)
검토자: Backend Engineer self-review + QA perspective + Lead Engineer perspective
협업 waiver: 단일 세션 범위 작업. 승인된 사용자의 LLM/SNS 연동 상태를 local encrypted vault에 저장하는 write-only prototype이며 outbound provider validation, live OAuth, production DB/deploy/secret 운영은 제외했다.
routing_ref: TASKSET-MEMBERSHIP-ACCESS / TASK-107
selected_model: Codex coding agent
policy_model: AGENTS.md §6 R1/R2 local reversible implementation; AGENTS.md §16 R3 surfaces avoided
실측 비용 (시간): 약 0.7h
실측 비용 (LLM 토큰): unknown
의도: Owner가 말한 "SNS 및 LLM 연동은 사용자의 토큰/계정으로 동작"하는 구조의 첫 제품 하네스를 만든다.
대상: approved-user integration API, local encrypted vault storage, `/settings > 계정/연결` UI, API/E2E tests
방법: provider catalog와 per-user integration records를 추가하고, `require_app_user`/`require_app_user_csrf`로 자기 계정 연동만 읽기/저장/삭제하도록 했다. secret values는 request body로만 받고 response에는 `secret_set`과 masked hint만 반환한다.
감사 로그: AUDIT-2026-06-19-017

## 범위

포함:

- LLM/SNS provider catalog: OpenAI, Anthropic, Telegram, Google, Naver, Kakao, X.
- `GET /api/integrations`: 승인된 owner/member의 provider catalog와 redacted per-user status.
- `PUT /api/integrations/{provider_id}`: current session user의 token/account label/scopes/enabled status 저장.
- `DELETE /api/integrations/{provider_id}`: current session user의 provider record 삭제.
- `/settings > 계정/연결` 사용자 연동 섹션.
- API tests for anonymous/guest boundary, member write, username isolation, CSRF, provider validation, deletion, and response redaction.
- Playwright settings-account E2E coverage for visible integration status and write-only token payload.

제외:

- 실제 provider API 호출, token validity check, OAuth callback, external account login.
- production DB/Supabase schema or migration.
- external deploy.
- KIS app key/account storage or broker credential activation.
- recommendation engine execution using stored tokens.
- public marketing claim, paid signal, investment advice flow.
- KIS/order/risk/prod 변경.

## 완료 조건

- [x] anonymous caller cannot read integrations.
- [x] guest session cannot read integrations.
- [x] owner/member can read their own integration redacted status.
- [x] owner/member can store/delete their own provider record with CSRF.
- [x] different usernames do not see each other's integration records.
- [x] token 원문은 API response와 encrypted vault file bytes에 노출되지 않는다.
- [x] settings account UI shows integration status and sends write-only payload.
- [x] API, lint, build, and settings E2E checks pass.

## 완료 기록

완료일: 2026-06-19
결과: Approved users now have a local, user-owned LLM/SNS token harness. This gives the product a concrete place to manage "the user's own account/token" without making Autofolio the operator of external accounts.
변경 파일: `app/services/integrations.py`, `app/api/routers/integrations.py`, `app/api/schemas/__init__.py`, `app/api/main.py`, `web/src/lib/api.ts`, `web/src/app/settings/page.tsx`, `tests/api/test_integrations.py`, `web/e2e/settings-account.spec.ts`.
이슈: This is local encrypted-vault storage only. It does not solve production secret management, Supabase/RLS, OAuth provider consent, billing, or KIS per-user broker credential activation.
다음 담당자 인수 사항: TASK-087에서 production secret storage/RLS, user_id ownership columns, per-user broker/LLM/SNS execution adapters, and legal/provider policy review를 분리해 설계한다.

## 완료 내용

- Added `app.services.integrations` with provider catalog and per-user vault-backed records.
- Added approved-user integration API.
- Added a settings UI section for user-owned LLM/SNS integration status and token entry.
- Added tests that verify redaction, CSRF, user isolation, and no guest access.

## 결과

TASK-107 완료. 전체 membership/deploy objective는 아직 production DB/Supabase/RLS, real payment/bank integration, external deploy, per-user engine/safety isolation, and actual provider/OAuth execution work가 남아 있어 active 상태로 유지한다.

## 증거

- `app/services/integrations.py`
- `app/api/routers/integrations.py`
- `web/src/app/settings/page.tsx`
- `tests/api/test_integrations.py`
- `web/e2e/settings-account.spec.ts`

## 리뷰

- Backend Engineer self-review: secret input is write-only at API boundary; response contains only boolean/masked status.
- UI/UX Designer perspective: the account settings surface now exposes a concrete integration management section without changing the main navigation.
- QA perspective: API and Playwright tests cover the new authorization and redaction contract.
- Lead Engineer perspective: no external provider call, production DB, deploy, real OAuth, KIS/order/risk/prod boundary was crossed.

## Independent Audit

판정: 통과

Same-session audit note: local prototype only. The encrypted vault file does not contain the raw token bytes, but decrypted in-process vault contents necessarily contain the token until production secret management is designed.

## 검증

- `.venv\Scripts\python.exe -m pytest tests/api/test_integrations.py -q` -> 5 passed, 2 warnings
- `.venv\Scripts\python.exe -m pytest tests/api/test_gate.py tests/api/test_account.py tests/api/test_membership.py -q` -> 48 passed, 2 warnings
- `.venv\Scripts\python.exe -m pytest tests/api -q` -> 330 passed, 20 warnings
- `npm run lint` in `web/` -> pass
- `npm run build` in `web/` -> pass
- `npm run test:e2e -- e2e/settings-account.spec.ts --reporter=line` -> 6 passed
