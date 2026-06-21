---
type: task
id: TASK-104
display_id: TASK-104
task_uid: 3162d5d4-000a-41e1-b2de-721770a3de32
registered_at: 2026-06-19T14:29:49+09:00
created_at: 2026-06-19T14:29:49+09:00
started_at: 2026-06-19T14:29:49+09:00
updated_at: 2026-06-19T14:29:49+09:00
completed_at: 2026-06-19T14:29:49+09:00
status: 완료
owner: Backend Engineer
assignees: [Backend Engineer, QA, Lead Engineer]
priority: High
difficulty: 중
est_hours: 1
est_tokens: 16000
tags: [auth, membership, authorization, member-boundary, local-prototype]
initiative_id: INIT-MEMBERSHIP-ACCESS
task_set_id: TASKSET-MEMBERSHIP-ACCESS
gate: local authorization boundary only; no production DB, deploy, bank/payment API, real account number, KIS/order/risk/prod/secret change
trigger_meeting: Owner direct request 2026-06-19
audit_log: AUDIT-2026-06-19-014
created: 2026-06-19
---

# TASK-104 Membership member/admin boundary

작업 ID: TASK-104
상태: 완료
Owner: Backend Engineer
요청 시각: 2026-06-19T14:29:49+09:00
기록 시각: 2026-06-19T14:29:49+09:00
완료 시각: 2026-06-19T14:29:49+09:00
요청자: Owner
수행자: Backend Engineer + QA + Lead Engineer perspective (Codex)
검토자: Backend Engineer self-review + QA perspective + Lead Engineer perspective
협업 waiver: 단일 세션 범위 작업. 로컬 인증/인가 경계만 좁히는 R2 prototype이며 production DB/payment/deploy/secret 없음.
routing_ref: TASKSET-MEMBERSHIP-ACCESS / TASK-104
selected_model: Codex coding agent
policy_model: AGENTS.md §6 R1/R2 local reversible implementation; AGENTS.md §16 R3 surfaces avoided
실측 비용 (시간): 약 0.3h
실측 비용 (LLM 토큰): unknown
의도: 승인된 `member`가 자기 계정/프로필/동의서 self-service는 사용할 수 있지만 Owner/admin 글로벌 제어 API는 건드리지 못하게 한다.
대상: `app/api/deps.py`, `app/api/main.py`, `app/api/routers/account.py`, `app/api/routers/profile.py`, `app/api/routers/acknowledgements.py`, `app/api/schemas/__init__.py`, `app/services/auth_service.py`, focused tests
방법: `require_owner`/`require_owner_csrf`를 owner-only로 되돌리고, 승인 사용자용 `require_app_user`/`require_app_user_csrf`를 분리했다. member self-service 라우트만 app-user gate로 옮기고 engine/trade/settings/portfolio/membership admin은 owner-only로 유지했다.
감사 로그: AUDIT-2026-06-19-014

## 범위

포함:

- `require_app_user` / `require_app_user_csrf` 추가.
- `require_owner` / `require_owner_csrf`는 owner/admin-only로 고정.
- member는 자기 비밀번호 변경, 투자 프로필 저장, 위험 고지 acknowledgement 기록 가능.
- member는 global engine mutation 같은 Owner control API에서 403.
- manuals/acknowledgements routers를 app factory에 등록.
- manual/acknowledgement response schemas 추가.
- `auth_service.verify_password()` 추가.
- password change가 `role`, `source`, `membership_request_id` 같은 account metadata를 보존하도록 수정.
- API tests로 owner/member/guest 권한 경계 고정.

제외:

- production DB/Supabase schema or migration.
- external deploy.
- real payment/bank API/open-banking/PG.
- 실제 계좌번호, 고객 입금기록, 고객 PII repo 저장.
- user_id 단위 포트폴리오/엔진/주문 데이터 격리 완성.
- KIS/order/risk/prod/secret 변경.

## 완료 조건

- [x] member는 `require_owner` owner-only route를 통과하지 못한다.
- [x] member는 `require_app_user` self-service route를 통과한다.
- [x] member는 global engine mutation을 실행할 수 없다.
- [x] member는 자기 비밀번호, 투자 프로필, risk acknowledgement를 저장할 수 있다.
- [x] password change 후 member role이 owner로 승격되지 않는다.
- [x] API focused/full tests와 web lint가 통과한다.

## 완료 기록

완료일: 2026-06-19
결과: local 승인 member는 자기 계정/프로필/동의서 흐름만 사용할 수 있고, Owner/admin 글로벌 제어 경로는 fail-closed로 막힌다. TASK-087의 production multi-tenant isolation은 여전히 별도 gate다.
변경 파일: `app/api/deps.py`, `app/api/main.py`, `app/api/routers/account.py`, `app/api/routers/profile.py`, `app/api/routers/acknowledgements.py`, `app/api/schemas/__init__.py`, `app/services/auth_service.py`, `tests/api/test_gate.py`, `tests/api/test_account.py`, `tests/api/test_profile_survey.py`, `tests/api/test_manuals_acknowledgements.py`.
이슈: read-only guest/demo and single-owner portfolio data model remain unresolved until production membership architecture and user_id isolation are designed.
다음 담당자 인수 사항: TASK-087에서 member read scope, guest/demo policy, Supabase/RLS schema, and per-user engine/data isolation을 분리 설계한다.

## 완료 내용

- Approved app user gate와 Owner admin gate를 코드 레벨에서 분리했다.
- Self-service mutation은 session username만 사용한다.
- Global controls는 owner-only로 남겼다.
- acknowledgement/manual API registration 누락을 해결했다.
- role metadata loss on password change를 회귀 테스트로 고정했다.

## 결과

TASK-104 완료. 전체 membership product goal은 아직 production schema, deployment, payment provider, and user_id isolation이 남아 있어 active 상태로 유지한다.

## 증거

- `app/api/deps.py`
- `app/api/main.py`
- `app/services/auth_service.py`
- `tests/api/test_gate.py`
- `tests/api/test_account.py`
- `tests/api/test_profile_survey.py`
- `tests/api/test_manuals_acknowledgements.py`

## 리뷰

- Backend Engineer self-review: role split을 dependency level에서 분리했고 global mutation은 owner-only로 유지했다.
- QA perspective: focused auth/membership/profile/manual tests와 전체 API suite로 member/admin boundary를 검증했다.
- Lead Engineer perspective: production DB, deploy, real payment/bank API, KIS/order/risk/secret 경계는 건드리지 않았다.

## Independent Audit

판정: 통과

Same-session audit note: local authorization boundary hardening only. This reduces accidental member escalation before multi-tenant isolation, but does not replace production RLS/user_id isolation.

## 검증

- `.venv\Scripts\python.exe -m pytest tests/api/test_gate.py tests/api/test_account.py tests/api/test_profile_survey.py tests/api/test_manuals_acknowledgements.py tests/api/test_membership.py -q` -> 67 passed, 6 warnings
- `.venv\Scripts\python.exe -m pytest tests/api -q` -> 312 passed, 19 warnings
- `npm run lint` in `web/` -> pass
