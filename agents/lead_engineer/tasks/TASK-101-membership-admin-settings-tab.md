---
type: task
id: TASK-101
display_id: TASK-101
task_uid: 9e4d2efc-0166-4c5e-99db-155bd2146fa2
registered_at: 2026-06-19T13:50:33+09:00
created_at: 2026-06-19T13:50:33+09:00
started_at: 2026-06-19T13:50:33+09:00
updated_at: 2026-06-19T13:50:33+09:00
completed_at: 2026-06-19T13:50:33+09:00
status: 완료
owner: UI/UX Designer
assignees: [UI/UX Designer, Backend Engineer, QA, Lead Engineer]
priority: High
difficulty: 중
est_hours: 1
est_tokens: 18000
tags: [auth, membership, approval, admin-ui, settings, local-prototype]
initiative_id: INIT-MEMBERSHIP-ACCESS
task_set_id: TASKSET-MEMBERSHIP-ACCESS
gate: local Owner admin UI over existing membership APIs only; no production DB, deploy, payment, bank API, secret, KIS/order/risk/prod change
trigger_meeting: Owner direct request 2026-06-19
audit_log: AUDIT-2026-06-19-011
created: 2026-06-19
---

# TASK-101 Membership admin settings tab

작업 ID: TASK-101
상태: 완료
Owner: UI/UX Designer
요청 시각: 2026-06-19T13:50:33+09:00
기록 시각: 2026-06-19T13:50:33+09:00
완료 시각: 2026-06-19T13:50:33+09:00
요청자: Owner
수행자: UI/UX Designer + Backend Engineer + QA perspective (Codex)
검토자: UI/UX Designer self-review + Backend Engineer perspective + QA perspective
협업 waiver: 단일 세션 범위 작업. 기존 local membership API 위에 Owner settings 화면만 추가하는 R2 prototype이며 production DB/payment/deploy/secret 없음.
routing_ref: TASKSET-MEMBERSHIP-ACCESS / TASK-101
selected_model: Codex coding agent
policy_model: AGENTS.md §6 R1/R2 local reversible implementation; AGENTS.md §16 R3 surfaces avoided
실측 비용 (시간): 약 0.2h
실측 비용 (LLM 토큰): unknown
의도: Owner가 `/settings`에서 가입 승인 신청을 보고 검증대기, 입금대기, 활성, 거절, 만료 상태로 전환할 수 있게 한다.
대상: `web/src/app/settings/page.tsx`
방법: 기존 `getMembershipRequests()`와 `postMembershipTransition()` API helper를 settings 탭에 연결하고, 신청자/상태/입금코드/액션을 한 화면에 표시한다.
감사 로그: AUDIT-2026-06-19-011

## 범위

포함:

- `설정 > 회원 승인` 탭 추가.
- Owner-only membership request list 호출.
- 상태 라벨 표시: `requested`, `verification_pending`, `deposit_pending`, `active`, `rejected`, `expired`.
- 신청자명, 연락처, request id, 업데이트 시각, 금액, 입금코드, 계좌 설정 여부 표시.
- Owner 액션:
  - `requested` -> `verification_pending`
  - `requested`/`verification_pending` -> `deposit_pending`
  - `deposit_pending` -> `active` with `manual_bank_app_check`
  - non-terminal -> `rejected` 또는 `expired`
- 401/403/detail 오류 메시지 표시와 재시도 버튼.

제외:

- 실제 로그인 계정 생성 또는 subscription grant 연결.
- 실제 결제 확인, 은행 API/OAuth/PG 연동.
- production DB schema/migration.
- external deploy.
- 실제 계좌번호, 입금기록, 고객 개인정보 repo 저장.
- KIS/order/risk/prod/secret 변경.

## 완료 조건

- [x] `/settings` 탭 목록에 `회원 승인`이 보인다.
- [x] 탭 선택 시 membership request list를 불러온다.
- [x] Owner가 상태전이 API를 호출할 수 있는 버튼이 있다.
- [x] 입금코드와 계좌 설정 여부를 표시한다.
- [x] web lint/build와 membership API focused test가 통과한다.

## 완료 기록

완료일: 2026-06-19
결과: Owner는 `/settings`에서 local membership request를 조회하고 입금대기/활성/거절/만료 전환을 수행할 수 있다.
변경 파일: `web/src/app/settings/page.tsx`.
이슈: active 상태는 아직 실제 로그인 계정 또는 subscription grant와 연결되지 않는다.
다음 담당자 인수 사항: 다음 안전 후보는 active membership을 local login/subscription grant에 연결하는 설계/프로토타입이다. production DB, deploy, real payment recognition은 별도 Owner gate로 유지한다.

## 완료 내용

- Settings tab type과 tab bar에 `membership`을 추가했다.
- `MembershipTab`이 Owner membership request 목록을 로드하고 refresh/retry 상태를 처리한다.
- `MembershipRow`가 신청자, 상태, 금액, 입금코드, 계좌 설정 여부, 상태전이 버튼을 표시한다.
- React lint 규칙에 맞게 초기 effect에서는 동기 loading setState 없이 fetch 결과만 반영한다.

## 결과

TASK-101 완료. TASK-087 전체는 여전히 대기/REVIEW 상태이며, 이번 변경은 local Owner admin UI까지만 수행했다.

## 증거

- `web/src/app/settings/page.tsx`
- `app/api/routers/membership.py`
- `web/src/lib/api.ts`
- `tests/api/test_membership.py`

## 리뷰

- UI/UX Designer self-review: 기존 설정 탭 구조를 유지하면서 승인 작업을 별도 탭으로 추가했다.
- Backend Engineer perspective: 기존 Owner-only API와 CSRF transition helper를 재사용했고 새 backend mutation은 없다.
- QA perspective: membership API focused test와 web lint/build로 계약과 타입을 확인했다.
- Compliance perspective: 실제 계좌번호, 결제 증거, 고객 개인정보, 투자 추천 claim을 추가하지 않았다.

## Independent Audit

판정: 통과

Same-session audit note: local admin UI prototype이며 production DB, deploy, external payment/bank API, real bank account data, KIS/order/risk/prod/secret 변경은 없다.

## 검증

- `.venv\Scripts\python.exe -m pytest tests/api/test_membership.py -q` -> 8 passed, 2 warnings
- `npm run lint` in `web/` -> pass
- `npm run build` in `web/` -> pass
- 참고: root `npm run lint`는 root `package.json` 부재로 실행 대상이 아니어서 실패했고, 올바른 `web/` 작업 디렉터리에서 재실행해 통과했다.
