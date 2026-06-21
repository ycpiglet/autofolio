---
type: task
id: TASK-103
display_id: TASK-103
task_uid: 49b3fbd0-57f2-4412-b4b9-be0d800507ba
registered_at: 2026-06-19T14:14:09+09:00
created_at: 2026-06-19T14:14:09+09:00
started_at: 2026-06-19T14:14:09+09:00
updated_at: 2026-06-19T14:14:09+09:00
completed_at: 2026-06-19T14:14:09+09:00
status: 완료
owner: Backend Engineer
assignees: [Backend Engineer, UI/UX Designer, QA, Lead Engineer]
priority: High
difficulty: 중
est_hours: 1
est_tokens: 18000
tags: [membership, deposit-recognition, bank-transfer, approval, local-prototype]
initiative_id: INIT-MEMBERSHIP-ACCESS
task_set_id: TASKSET-MEMBERSHIP-ACCESS
gate: stateless pasted statement recognition only; no real bank API, no raw payment record storage, no production DB, deploy, KIS/order/risk/prod/secret change
trigger_meeting: Owner direct request 2026-06-19
audit_log: AUDIT-2026-06-19-013
created: 2026-06-19
---

# TASK-103 Membership local deposit recognition

작업 ID: TASK-103
상태: 완료
Owner: Backend Engineer
요청 시각: 2026-06-19T14:14:09+09:00
기록 시각: 2026-06-19T14:14:09+09:00
완료 시각: 2026-06-19T14:14:09+09:00
요청자: Owner
수행자: Backend Engineer + UI/UX Designer + QA perspective (Codex)
검토자: Backend Engineer self-review + UI/UX Designer perspective + QA perspective
협업 waiver: 단일 세션 범위 작업. 로컬 pasted statement/CSV text를 메모리에서만 스캔하는 R2 prototype이며 real bank API/payment/deploy/secret 없음.
routing_ref: TASKSET-MEMBERSHIP-ACCESS / TASK-103
selected_model: Codex coding agent
policy_model: AGENTS.md §6 R1/R2 local reversible implementation; AGENTS.md §16 R3 surfaces avoided
실측 비용 (시간): 약 0.25h
실측 비용 (LLM 토큰): unknown
의도: Owner가 은행앱/CSV에서 복사한 입금내역 텍스트로 deposit_pending 신청의 입금코드/금액/신청자 정보를 빠르게 대조할 수 있게 한다.
대상: `app/services/membership.py`, `app/api/routers/membership.py`, `app/api/schemas/__init__.py`, `web/src/lib/api.ts`, `web/src/app/settings/page.tsx`, focused tests
방법: pasted statement text를 저장하지 않고 line 단위로 스캔해 deposit_pending request와 입금코드, 금액, 이름, 연락처를 점수화한다. UI는 confidence/reasons/masked excerpt를 보여주고, 최종 활성화는 Owner가 명시 버튼을 눌러 수행한다.
감사 로그: AUDIT-2026-06-19-013

## 범위

포함:

- `MembershipService.recognize_deposits()` stateless recognizer 추가.
- deposit_pending request만 match 후보로 사용.
- deposit code, amount, display name, contact text 기반 confidence score 산정.
- pasted line의 긴 숫자/account-like 문자열은 masked excerpt로 표시.
- Owner+CSRF 전용 `POST /api/membership/deposits/recognize`.
- `/settings > 회원 승인`에 입금코드 인식 textarea와 결과 표시.
- recognition confidence가 높은 request는 `code_assisted_deposit_match` evidence type으로 활성화 가능.
- low-confidence 결과는 참고용으로만 표시하고 최종 활성화는 Owner explicit action 유지.
- CSRF/admin gate와 non-pending ignore regression tests.

제외:

- 실제 은행 API/OAuth/open-banking/PG/virtual account 연동.
- pasted raw bank statement, 고객 입금기록, 실제 계좌번호 repo 저장.
- production DB/Supabase schema or migration.
- external deploy.
- 자동 무인 활성화.
- user_id 단위 데이터/엔진/안전장치 격리.
- KIS/order/risk/prod/secret 변경.

## 완료 조건

- [x] Owner가 pasted statement/CSV text를 제출하면 match 후보가 반환된다.
- [x] deposit_pending 상태가 아닌 request는 match 대상에서 제외된다.
- [x] recognition API는 Owner CSRF gate를 요구한다.
- [x] UI에서 confidence/reason/masked excerpt를 확인할 수 있다.
- [x] high-confidence match는 계정 활성화 evidence type을 `code_assisted_deposit_match`로 남긴다.
- [x] web lint/build와 focused API tests가 통과한다.

## 완료 기록

완료일: 2026-06-19
결과: Owner는 `/settings > 회원 승인`에서 은행앱/CSV에서 복사한 텍스트를 붙여넣어 deposit_pending 신청과 입금코드/금액/신청자명을 대조할 수 있다. 인식 결과는 활성화 버튼의 보조 evidence로만 쓰이며 자동 활성화는 하지 않는다.
변경 파일: `app/services/membership.py`, `app/api/routers/membership.py`, `app/api/schemas/__init__.py`, `web/src/lib/api.ts`, `web/src/app/settings/page.tsx`, `tests/api/test_membership.py`.
이슈: local recognizer prototype이며 production-grade payment recognition, bank API/PG, immutable audit storage, multi-tenant isolation은 아직 별도 gate다.
다음 담당자 인수 사항: TASK-087에서 production schema, user_id isolation, deployment, payment provider/open-banking decision을 분리 설계한다.

## 완료 내용

- recognizer는 source text를 vault에 쓰지 않고 요청 처리 중에만 사용한다.
- match score는 deposit code exact match를 가장 강하게 보고 amount/name/contact를 보조 signal로 더한다.
- UI는 recognition result를 deposit code 아래에 표시해 Owner가 승인 근거를 빠르게 확인할 수 있게 했다.
- activation 자체는 기존 Owner action과 temporary password/account grant path를 사용한다.

## 결과

TASK-103 완료. TASK-087 전체는 여전히 대기/REVIEW 상태이며, 이번 변경은 local code-assisted deposit recognition prototype까지만 수행했다.

## 증거

- `app/services/membership.py`
- `app/api/routers/membership.py`
- `app/api/schemas/__init__.py`
- `web/src/lib/api.ts`
- `web/src/app/settings/page.tsx`
- `tests/api/test_membership.py`

## 리뷰

- Backend Engineer self-review: raw pasted statement는 저장하지 않고, admin-only endpoint에서 pending requests만 score한다.
- UI/UX Designer perspective: Owner admin row에서 confidence/reason/excerpt를 바로 볼 수 있게 해 수동 확인 시간을 줄였다.
- QA perspective: recognition happy path, non-pending exclusion, CSRF/admin gate regression을 추가/확인했다.
- Compliance perspective: 실제 은행 API, 실제 계좌번호, 고객 입금기록 보관, production DB/payment/deploy 경계는 건드리지 않았다.

## Independent Audit

판정: 통과

Same-session audit note: local stateless recognizer prototype이며 production DB, deploy, external payment/bank API, real bank account data, KIS/order/risk/prod/secret 변경은 없다. 인식 결과는 Owner 승인 보조이며 자동 계정 활성화를 수행하지 않는다.

## 검증

- `.venv\Scripts\python.exe -m pytest tests/api/test_membership.py tests/api/test_auth.py tests/api/test_account.py tests/api/test_gate.py -q` -> 53 passed, 3 warnings
- `npm run lint` in `web/` -> pass
- `npm run build` in `web/` -> pass
