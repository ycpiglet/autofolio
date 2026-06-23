---
type: task
id: TASK-102
display_id: TASK-102
task_uid: 631e6d86-9efc-43d6-b8ce-a6c763657292
registered_at: 2026-06-19T14:01:11+09:00
created_at: 2026-06-19T14:01:11+09:00
started_at: 2026-06-19T14:01:11+09:00
updated_at: 2026-06-19T14:01:11+09:00
completed_at: 2026-06-19T14:01:11+09:00
status: 완료
owner: Backend Engineer
assignees: [Backend Engineer, UI/UX Designer, QA, Lead Engineer]
priority: High
difficulty: 중
est_hours: 1
est_tokens: 22000
tags: [auth, membership, approval, account-grant, subscription, local-prototype]
initiative_id: INIT-MEMBERSHIP-ACCESS
task_set_id: TASKSET-MEMBERSHIP-ACCESS
gate: local encrypted-vault account grant only; no production DB, deploy, payment, bank API, real account number, KIS/order/risk/prod/secret change
trigger_meeting: Owner direct request 2026-06-19
audit_log: AUDIT-2026-06-19-012
created: 2026-06-19
---

# TASK-102 Membership local account grant

작업 ID: TASK-102
상태: 완료
Owner: Backend Engineer
요청 시각: 2026-06-19T14:01:11+09:00
기록 시각: 2026-06-19T14:01:11+09:00
완료 시각: 2026-06-19T14:01:11+09:00
요청자: Owner
수행자: Backend Engineer + UI/UX Designer + QA perspective (Codex)
검토자: Backend Engineer self-review + UI/UX Designer perspective + QA perspective
협업 waiver: 단일 세션 범위 작업. 기존 local vault auth와 membership API를 연결하는 R2 prototype이며 production DB/payment/deploy/secret 없음.
routing_ref: TASKSET-MEMBERSHIP-ACCESS / TASK-102
selected_model: Codex coding agent
policy_model: AGENTS.md §6 R1/R2 local reversible implementation; AGENTS.md §16 R3 surfaces avoided
실측 비용 (시간): 약 0.3h
실측 비용 (LLM 토큰): unknown
의도: Owner가 입금 확인 후 임시 비밀번호를 입력하면 해당 신청자가 실제 로컬 ID/PW로 로그인할 수 있게 한다.
대상: `app/services/auth_service.py`, `app/services/membership.py`, `app/api/deps.py`, `app/api/routers/auth.py`, `app/api/routers/membership.py`, `app/api/schemas/__init__.py`, `web/src/lib/api.ts`, `web/src/app/settings/page.tsx`, focused tests
방법: active 전환 payload에 로그인 ID와 임시 비밀번호를 선택적으로 받게 하고, 서버는 plaintext 비밀번호를 저장/응답하지 않고 PBKDF2 hash만 vault에 저장한다. 승인 계정은 `member` role로 로그인되며, 멤버십 관리 API는 `owner` 전용으로 분리한다.
감사 로그: AUDIT-2026-06-19-012

## 범위

포함:

- `auth_service.create_or_update_user()` 추가.
- `auth_service.role_for_user()`와 session role 반영.
- active membership transition에서 `login_username` + `initial_password`가 있으면 local approved account 생성/재설정.
- `subscription_grant` 응답 구조 추가.
- 승인 계정은 `member` role로 발급.
- 기존 app-control gate는 `owner`/`member`를 승인된 앱 사용자로 허용.
- membership review/list/transition API는 `owner` admin 전용으로 유지.
- `/settings > 회원 승인`에서 입금대기 신청에 로그인 ID와 임시 비밀번호 입력 후 `입금 확인 + 계정 활성화`.
- member 계정은 계정 화면에서 본인 비밀번호 변경 가능.
- plaintext 임시 비밀번호가 API 응답이나 vault에 남지 않는 테스트.

제외:

- production DB/Supabase schema or migration.
- external deploy.
- 실제 결제 확인, 은행 API/OAuth/PG 연동.
- 실제 계좌번호, 입금기록, 고객 개인정보 repo 저장.
- user_id 단위 데이터/엔진/안전장치 격리.
- KIS/order/risk/prod/secret 변경.

## 완료 조건

- [x] active 전환 시 임시 비밀번호로 local account가 생성된다.
- [x] 생성된 계정은 `/api/auth/login`으로 로그인된다.
- [x] 임시 비밀번호는 plaintext로 응답/저장되지 않는다.
- [x] 승인 계정은 `member`, 관리자는 `owner`로 구분된다.
- [x] `member`는 app-user gate를 통과하지만 membership admin API는 통과하지 못한다.
- [x] web lint/build와 focused API tests가 통과한다.

## 완료 기록

완료일: 2026-06-19
결과: Owner가 `/settings`에서 입금 확인 시 로그인 ID와 임시 비밀번호를 넣으면 해당 신청자는 local vault 계정으로 로그인할 수 있다. 동시에 멤버십 관리 API는 owner 전용으로 유지된다.
변경 파일: `app/services/auth_service.py`, `app/services/membership.py`, `app/api/deps.py`, `app/api/routers/auth.py`, `app/api/routers/membership.py`, `app/api/schemas/__init__.py`, `web/src/lib/api.ts`, `web/src/app/settings/page.tsx`, `tests/api/test_membership.py`, `tests/api/test_gate.py`.
이슈: local vault prototype이며 user_id 단위 데이터/엔진/안전장치 격리, production schema, 결제 인식, 배포는 아직 별도 gate다.
다음 담당자 인수 사항: 다음 안전 후보는 manual/code-assisted deposit recognition 설계 또는 CSV 기반 local recognizer prototype이다. production bank API/OAuth/PG는 Owner gate다.

## 완료 내용

- 승인 계정 생성은 hash/salt만 vault에 저장한다.
- `role_for_user()`로 local login session에 저장 role을 반영한다.
- `member` role을 도입했지만 membership admin API는 `require_admin`/`require_admin_csrf`로 owner-only 유지한다.
- Settings membership row는 deposit pending 상태에서 로그인 ID와 임시 비밀번호를 요구한다.
- Active response에는 `account_grant`와 `subscription_grant`가 포함되지만 비밀번호는 포함되지 않는다.

## 결과

TASK-102 완료. TASK-087 전체는 여전히 대기/REVIEW 상태이며, 이번 변경은 local account grant prototype까지만 수행했다.

## 증거

- `app/services/auth_service.py`
- `app/services/membership.py`
- `app/api/deps.py`
- `web/src/app/settings/page.tsx`
- `tests/api/test_membership.py`
- `tests/api/test_gate.py`

## 리뷰

- Backend Engineer self-review: membership active transition과 local auth vault 연결을 구현했고 plaintext password는 저장/응답하지 않는다.
- UI/UX Designer perspective: Owner approval row에서 계정 활성화에 필요한 ID/password 입력을 명시했다.
- QA perspective: active -> account grant -> login roundtrip, member/admin split, focused auth/account/gate tests를 추가/확인했다.
- Compliance perspective: 실제 결제, 실제 계좌번호, 고객 입금기록, production DB, KIS/order/risk/secret 경계는 건드리지 않았다.

## Independent Audit

판정: 통과

Same-session audit note: local encrypted-vault account grant prototype이며 production DB, deploy, external payment/bank API, real bank account data, KIS/order/risk/prod/secret 변경은 없다. member role은 local prototype의 승인 사용자 구분이며 production multi-tenant isolation을 대체하지 않는다.

## 검증

- `.venv\Scripts\python.exe -m pytest tests/api/test_membership.py tests/api/test_auth.py tests/api/test_account.py tests/api/test_gate.py -q` -> 50 passed, 3 warnings
- `npm run lint` in `web/` -> pass
- `npm run build` in `web/` -> pass
