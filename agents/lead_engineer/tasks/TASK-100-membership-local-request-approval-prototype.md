---
type: task
id: TASK-100
display_id: TASK-100
task_uid: e2eb33e3-4678-4661-8643-347a24bd74fd
registered_at: 2026-06-19T13:42:39+09:00
created_at: 2026-06-19T13:42:39+09:00
started_at: 2026-06-19T13:42:39+09:00
updated_at: 2026-06-19T13:42:39+09:00
completed_at: 2026-06-19T13:42:39+09:00
status: 완료
owner: Backend Engineer
assignees: [Backend Engineer, UI/UX Designer, QA, Lead Engineer]
priority: High
difficulty: 상
est_hours: 2
est_tokens: 30000
tags: [auth, membership, approval, signup, local-prototype, tests]
initiative_id: INIT-MEMBERSHIP-ACCESS
task_set_id: TASKSET-MEMBERSHIP-ACCESS
gate: local encrypted-vault prototype only; no production DB, deploy, payment, bank API, secret, KIS/order/risk/prod change
trigger_meeting: Owner direct request 2026-06-19
audit_log: AUDIT-2026-06-19-010
created: 2026-06-19
---

# TASK-100 Membership local request approval prototype

작업 ID: TASK-100
상태: 완료
Owner: Backend Engineer
요청 시각: 2026-06-19T13:42:39+09:00
기록 시각: 2026-06-19T13:42:39+09:00
완료 시각: 2026-06-19T13:42:39+09:00
요청자: Owner
수행자: Backend Engineer + UI/UX Designer + QA perspective (Codex)
검토자: Backend Engineer self-review + UI/UX Designer perspective + QA perspective + Compliance perspective
협업 waiver(사유): 단일 세션 local prototype 범위 작업. production DB/payment/deploy/secret 없이 focused tests와 build로 검증.
routing_ref: TASKSET-MEMBERSHIP-ACCESS / TASK-100
selected_model: Codex coding agent
policy_model: AGENTS.md §6 R1/R2 local reversible implementation; AGENTS.md §16 R3 surfaces avoided
실측 비용 (시간): 약 0.4h
실측 비용 (LLM 토큰): unknown
의도: 검증회원 가입신청, 입금대기, Owner 수동 승인 상태전이를 production 경계 없이 실제 API/UI로 테스트 가능하게 만든다.
대상: `app/services/membership.py`, `app/api/routers/membership.py`, API schemas, `/signup` page, login link, API tests
방법: `.autofolio` encrypted vault를 사용해 local-only membership request를 저장하고, 공개 signup request와 Owner-only review/transition API를 추가한다. 실제 계정 생성, 결제, 은행 API, DB migration, 배포는 제외한다.
감사 로그: AUDIT-2026-06-19-010

## 범위

포함:

- 공개 `POST /api/membership/requests`로 가입 승인 신청 접수.
- Owner-only `GET /api/membership/requests`와 detail 조회.
- Owner + CSRF `POST /api/membership/requests/{id}/transition` 상태전이.
- 상태: `requested`, `verification_pending`, `deposit_pending`, `active`, `rejected`, `expired`.
- `deposit_pending`/`active` 상태에서 고유 입금코드와 런타임 환경변수 기반 계좌 안내 구조 반환.
- `/signup` 공개 신청 화면과 `/login`에서 신청 화면 링크.
- API/권한/CSRF/상태전이/환경변수 계좌 안내 회귀 테스트.

제외:

- 실제 로그인 계정 생성 또는 활성 세션 발급.
- 실제 결제 확인, 은행 API/OAuth/PG 연동.
- production DB schema/migration.
- external deploy.
- 실제 계좌번호, 입금기록, 고객 개인정보 repo 저장.
- KIS/order/risk/prod/secret 변경.

## 완료 조건

- [x] 가입신청은 세션 없이 접수되지만 계정/session을 만들지 않는다.
- [x] Owner만 신청 목록과 상세를 볼 수 있다.
- [x] Owner + CSRF만 상태전이를 수행할 수 있다.
- [x] `deposit_pending` 상태에서 고유 입금코드와 price/account instruction structure가 나온다.
- [x] 실제 계좌번호는 repo가 아니라 runtime env에서만 들어온다.
- [x] `/signup` 화면이 build에 포함된다.

## 완료 기록

완료일: 2026-06-19
결과: 승인제 멤버십의 local request/approval prototype이 동작한다. 신청자는 `/signup`에서 요청을 만들고, Owner는 API로 verification/deposit/active 상태를 바꿀 수 있다.
변경 파일: `app/services/membership.py`, `app/api/routers/membership.py`, `app/api/main.py`, `app/api/schemas/__init__.py`, `web/src/lib/api.ts`, `web/src/app/signup/page.tsx`, `web/src/app/login/page.tsx`, `tests/api/test_membership.py`.
이슈: active 상태는 아직 실제 로그인 계정 또는 subscription grant와 연결되지 않는다.
다음 담당자 인수 사항: TASK-087 후속은 admin UI, 실제 account activation, subscription grant, SSO allowlist hardening, production DB/Supabase migration을 별도 승인 경계로 분리해야 한다.

## 완료 내용

- Membership service가 encrypted local vault에 request records를 저장한다.
- Duplicate open contact는 기존 request를 반환해 중복 신청을 줄인다.
- 입금코드는 `AF-XXXXXX` 형식으로 생성된다.
- 계좌번호/은행명/예금주 표시는 `AUTOFOLIO_MEMBERSHIP_BANK_NAME`, `AUTOFOLIO_MEMBERSHIP_ACCOUNT_HOLDER`, `AUTOFOLIO_MEMBERSHIP_BANK_ACCOUNT` 런타임 환경변수로만 주입된다.
- `/signup`은 신청 접수 후 request id와 status를 보여주며 세션을 발급하지 않는다.

## 결과

TASK-100 완료. TASK-087 전체는 아직 대기/REVIEW 상태이며, 이번 변경은 local prototype까지만 수행했다.

## 증거

- `app/services/membership.py`
- `app/api/routers/membership.py`
- `web/src/app/signup/page.tsx`
- `tests/api/test_membership.py`

## 리뷰

- Backend Engineer self-review: production DB와 auth account creation을 건드리지 않고 request/transition domain만 추가했다.
- UI/UX Designer perspective: 로그인 전 신청 화면을 추가하고, 계정 즉시 생성으로 오해되지 않도록 문구와 완료 상태를 분리했다.
- QA perspective: public intake, owner-only review, CSRF transition, deposit instruction env injection, invalid transition을 테스트했다.
- Compliance perspective: 계좌번호와 입금 증거는 repository에 넣지 않았고, 추천/수익/투자자문 claim은 추가하지 않았다.

## Independent Audit

판정: 통과

Same-session audit note: local encrypted-vault prototype이며 production DB, deploy, external payment/bank API, real bank account data, KIS/order/risk/prod/secret 변경은 없다.

## 검증

- `.venv\Scripts\python.exe -m pytest tests/api/test_membership.py tests/api/test_auth.py tests/api/test_account.py -q` -> 35 passed, 3 warnings
- `.venv\Scripts\python.exe -m pytest tests/api/test_membership.py -q` -> 8 passed, 2 warnings
- `npm run lint` -> pass
- `npm run build` -> pass
- `python scripts/build_task_index.py --check`
- `python scripts/generate_views.py --check`
- `python scripts/generate_report_views.py --check`
- `python scripts/validate_task_schema.py`
- `python scripts/work_schema_gate.py --items --check`
- `python scripts/continuity_contract_gate.py --check`
- `python scripts/conversation_work_audit.py --check`
- `python scripts/owner_governance_gate.py --allow-empty-owner-docs`
- `python scripts/check_agent_docs.py`
- `git diff --check`
