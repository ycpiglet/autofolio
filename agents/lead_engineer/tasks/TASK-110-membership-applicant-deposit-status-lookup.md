---
type: task
id: TASK-110
display_id: TASK-110
task_uid: 052c31ce-f76f-475c-b0ee-b74cfb1cc412
registered_at: 2026-06-19T16:01:55+09:00
created_at: 2026-06-19T16:01:55+09:00
started_at: 2026-06-19T16:01:55+09:00
updated_at: 2026-06-19T16:01:55+09:00
completed_at: 2026-06-19T16:01:55+09:00
status: 완료
owner: Backend Engineer
assignees: [Backend Engineer, UI/UX Designer, QA, Lead Engineer]
priority: High
difficulty: 중
est_hours: 1
est_tokens: 18000
tags: [membership, signup, deposit-instructions, applicant-status, local-prototype]
initiative_id: INIT-MEMBERSHIP-ACCESS
task_set_id: TASKSET-MEMBERSHIP-ACCESS
gate: local applicant status lookup only; no production DB, no deploy, no bank/payment API, no real customer payment record, no KIS/order/risk/prod/secret change
trigger_meeting: Owner direct request 2026-06-19
audit_log: AUDIT-2026-06-19-020
created: 2026-06-19
---

# TASK-110 Membership applicant deposit status lookup

작업 ID: TASK-110
상태: 완료
Owner: Backend Engineer
요청 시각: 2026-06-19T16:01:55+09:00
기록 시각: 2026-06-19T16:01:55+09:00
완료 시각: 2026-06-19T16:01:55+09:00
요청자: Owner
수행자: Backend Engineer + UI/UX Designer + QA + Lead Engineer perspective (Codex)
검토자: Backend Engineer self-review + UI/UX Designer perspective + QA perspective + Lead Engineer perspective
협업 waiver: 단일 세션 범위 작업. 신청자용 상태 조회와 입금 안내 표시만 추가했고 production DB, 배포, 은행/결제 API, KIS/order/risk/secret 경계는 건드리지 않았다.
routing_ref: TASKSET-MEMBERSHIP-ACCESS / TASK-110
selected_model: Codex coding agent
policy_model: AGENTS.md §6 R1/R2 local reversible implementation; AGENTS.md §16 R3 surfaces avoided
실측 비용 (시간): 약 0.5h
실측 비용 (LLM 토큰): unknown
의도: 신청자가 신청 후에도 화면에서 직접 request id와 연락처로 상태를 확인하고, Owner가 deposit_pending으로 넘긴 뒤 가격/입금코드/런타임 계좌 안내를 볼 수 있게 한다.
대상: public membership status lookup API, `/signup` applicant status panel, API and Playwright tests
방법: 세션을 만들지 않는 public POST lookup endpoint를 추가하되, `request_id + contact`가 일치할 때만 applicant-safe response를 반환한다. 공개 응답에서는 Owner event/note, account grant, subscription grant를 제거했다.
감사 로그: AUDIT-2026-06-19-020

## 범위

포함:

- `POST /api/membership/requests/status` public applicant lookup.
- Lookup requires request id and contact match.
- Applicant response can show deposit instructions only after Owner moves request to `deposit_pending` or `active`.
- Applicant response strips Owner events/notes, account grant, and subscription grant.
- `/signup` status panel for request id/contact lookup.
- Deposit instruction UI showing price, deposit code, bank name, account holder, account number, due date, and missing runtime account configuration.
- API and Playwright E2E coverage.

제외:

- Production DB or Supabase apply.
- Real bank/payment API, PG, open-banking, virtual account.
- Real customer payment evidence storage.
- External deploy.
- KIS credential activation, order/risk/prod path change.

## 완료 조건

- [x] Applicant can create a signup request without getting a session.
- [x] Applicant can later check status with request id and contact.
- [x] Wrong contact or missing request does not disclose the request.
- [x] Deposit-pending applicant sees amount, deposit code, and runtime-configured bank fields.
- [x] Public lookup does not expose Owner notes/events or account grant internals.
- [x] Signup UI shows a status/deposit-instruction panel.
- [x] API, lint/build, and E2E checks pass.

## 완료 기록

완료일: 2026-06-19
결과: Verified signup now has a complete local applicant-facing loop: request intake, request-id/contact status lookup, and deposit instruction display after Owner verification. This makes the manual bank-transfer flow testable from the applicant screen, not only the Owner admin screen.
변경 파일: `app/services/membership.py`, `app/api/schemas/__init__.py`, `app/api/routers/membership.py`, `web/src/lib/api.ts`, `web/src/app/signup/page.tsx`, `tests/api/test_membership.py`, `web/e2e/signup-membership.spec.ts`.
이슈: This remains local encrypted-vault prototype behavior. Production auth/DB/RLS, real payment evidence, refund/receipt/tax handling, and external deployment remain TASK-087/R3 work.
다음 담당자 인수 사항: Future production implementation should preserve this split: public applicant lookup requires request id + contact, while Owner/admin notes and account grant internals stay server-side.

## 완료 내용

- Added applicant-safe status lookup service and API.
- Added signup status/deposit panel.
- Added API tests for deposit instruction visibility and non-disclosure.
- Added Playwright signup flow coverage.

## 결과

TASK-110 완료. TASK-087 remains open because production DB/Supabase/RLS apply, staging deploy, production secret storage, real payment recognition, per-user engine/safety isolation, KIS terms, and provider execution remain incomplete.

## 증거

- `app/services/membership.py`
- `app/api/routers/membership.py`
- `web/src/app/signup/page.tsx`
- `tests/api/test_membership.py`
- `web/e2e/signup-membership.spec.ts`

## 리뷰

- Backend Engineer self-review: public lookup requires both request id and contact and strips internal events/grants.
- UI/UX Designer perspective: applicant can now see the same deposit state from the signup surface.
- QA perspective: focused API and Playwright tests cover request lookup, deposit instruction display, and wrong-contact refusal.
- Lead Engineer perspective: this directly advances the manual bank-transfer approval loop without crossing production/payment boundaries.

## Independent Audit

판정: 통과

Same-session audit note: public lookup is local-prototype evidence only, not a production privacy/security certification.

## 검증

- `.venv\Scripts\python.exe -m pytest tests\api\test_membership.py -q` -> 16 passed, 2 warnings
- `.venv\Scripts\python.exe -m pytest tests\api -q` -> 334 passed, 20 warnings
- `npm run lint` in `web/` -> pass
- `npm run build` in `web/` -> pass
- `npm run test:e2e -- e2e/signup-membership.spec.ts e2e/settings-membership.spec.ts --reporter=line` in `web/` -> 2 passed
- `python scripts\membership_contract_gate.py --check` -> pass
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
