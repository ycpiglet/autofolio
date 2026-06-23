---
schema_version: agent-runtime-work-item/v1
work_id: TASKSET-MEMBERSHIP-ACCESS
work_uid: 34e57848-8c35-4437-991f-20268ee8089e
kind: taskset
parent_id: INIT-MEMBERSHIP-ACCESS
status: active
owner: Lead Engineer
created_at: 2026-06-19T13:18:08+09:00
updated_at: 2026-06-19T19:29:22+09:00
origin_type: owner_request
origin_ref: AUDIT-2026-06-19-008
created_by: lead_engineer
title: Membership Access Taskset — verified signup to account activation
summary: 검증된 회원가입 신청, 무통장입금 안내, 입금확인, 계정 승인 흐름을 문서화하고 로컬 자동가입 차단, request prototype, Owner 승인 UI, applicant status/deposit lookup, local account grant, pasted statement 입금 인식 보조, member/admin boundary, guest demo fail-closed, app-user read boundary, user-owned LLM/SNS token harness, production readiness gate, Supabase/RLS production contract, payment evidence policy, production secret/token policy, per-user engine/safety contract, tenant isolation matrix 후 구현 TASK-087로 연결한다.
tags: [membership, signup, bank-transfer, payment-code, admin-approval]
priority: P1
---

# TASKSET-MEMBERSHIP-ACCESS — verified signup and deposit approval

## 부모 이니셔티브

`INIT-MEMBERSHIP-ACCESS`

## 포함 태스크

tasks:
  - TASK-098
  - TASK-099
  - TASK-100
  - TASK-101
  - TASK-102
  - TASK-103
  - TASK-104
  - TASK-105
  - TASK-106
  - TASK-107
  - TASK-108
  - TASK-109
  - TASK-110
  - TASK-111
  - TASK-112
  - TASK-113
  - TASK-114
  - TASK-087

| work_id | 설명 | Owner | 상태 | Gate |
|---------|------|-------|------|------|
| TASK-098 | Membership access plan — 검증된 사람만 가입승인 + 수동/코드 기반 입금확인 설계 | Lead Engineer | 완료 | docs/planning only |
| TASK-099 | Local auto-register fail-closed — 미승인 로컬 계정 자동 owner session 차단 | Backend Engineer | 완료 | local auth only |
| TASK-100 | Local request approval prototype — 가입신청/입금대기/활성 상태전이 API와 `/signup` 화면 | Backend Engineer | 완료 | local encrypted vault only |
| TASK-101 | Membership admin settings tab — `/settings`에서 Owner가 신청 조회와 수동 승인 상태전이를 수행 | UI/UX Designer | 완료 | local admin UI only |
| TASK-102 | Membership local account grant — 입금 확인 시 local member 로그인 계정과 subscription grant 생성 | Backend Engineer | 완료 | local encrypted vault only |
| TASK-103 | Membership local deposit recognition — pasted bank statement/CSV text로 deposit_pending 신청 matching | Backend Engineer | 완료 | stateless local recognition only |
| TASK-104 | Membership member/admin boundary — 승인 member self-service와 Owner/admin global controls 분리 | Backend Engineer | 완료 | local authorization only |
| TASK-105 | Membership guest demo fail-closed — default public guest/demo login 발급과 CTA 차단 | Backend Engineer | 완료 | local auth/login UI only |
| TASK-106 | Membership app-user read boundary — 제품 read API를 승인 owner/member 전용으로 전환 | Backend Engineer | 완료 | local API authorization only |
| TASK-107 | User-owned integration token harness — 승인 사용자별 LLM/SNS 연동 토큰 상태를 write-only/redacted로 관리 | Backend Engineer | 완료 | local encrypted vault only; no provider call/OAuth |
| TASK-108 | Membership production readiness gate — Owner 화면/API에서 production blocker를 pass/watch/block로 표시 | Backend Engineer | 완료 | local diagnostic only |
| TASK-109 | Membership Supabase/RLS production contract — 적용 전 production entity/RLS/secret/payment/engine 계약과 local gate | Backend Engineer | 완료 | contract asset only; no DB apply |
| TASK-110 | Membership applicant deposit status lookup — `/signup`에서 request id/contact로 상태와 입금 안내 확인 | Backend Engineer | 완료 | local applicant lookup only; no payment API |
| TASK-111 | Membership payment evidence policy gate — 최소 입금 증거 보존 정책과 local gate | Backend Engineer | 완료 | local policy/gate only; no payment API |
| TASK-112 | Membership production secret policy — user-owned LLM/SNS/OAuth/KIS token 처리 정책과 local gate | Backend Engineer | 완료 | local policy/gate only; no secret read/write |
| TASK-113 | Membership per-user engine safety contract — user_id 단위 engine state/queue/risk/order intent 계약과 local gate | Lead Engineer | 완료 | local contract/gate only; no engine/order/risk code change |
| TASK-114 | Membership tenant isolation matrix — user_id/RLS route/surface/test matrix와 local gate | Backend Engineer | 완료 | local matrix/gate only; no DB apply |
| TASK-087 | 웹 배포 + 구매자 한정 회원제 구현 | Lead Engineer | 대기 | no external deploy, no production DB apply, no secrets without explicit approval |

## 의존 관계

```text
TASK-098
  -> TASK-099
  -> TASK-100
  -> TASK-101
  -> TASK-102
  -> TASK-103
  -> TASK-104
  -> TASK-105
  -> TASK-106
  -> TASK-107
  -> TASK-108
  -> TASK-109
  -> TASK-110
  -> TASK-111
  -> TASK-112
  -> TASK-113
  -> TASK-114
  -> TASK-087
```

## 안전 경계

금지:

- 실제 은행 계좌번호 repo 커밋.
- 실제 고객 개인정보 또는 입금 기록 repo 저장.
- 외부 은행 API/OAuth 연결.
- production payment, production DB, external deploy, secret 변경.
- KIS/order/risk/prod 경로 변경.

허용:

- 문서/계획/요구사항 정리.
- placeholder-safe UI copy와 flow 설계.
- local-only prototype planning.
- local auth fail-closed changes that do not add production DB/payment/deploy.
- local encrypted-vault membership request prototype and signup UI.
- local Owner admin UI over existing membership APIs.
- local encrypted-vault account grant on Owner-confirmed activation.
- stateless pasted statement/CSV deposit recognition over deposit-pending
  requests as an Owner approval aid.
- local authorization boundary hardening that keeps approved `member`
  self-service separate from Owner/admin global controls.
- local guest-demo login issuance fail-closed policy and login UI CTA removal.
- local product read API gating to approved owner/member sessions.
- local approved-user LLM/SNS integration token harness with redacted responses
  and no outbound provider call.
- local Owner-visible production readiness checklist that keeps launch blocked
  until R3 evidence exists.
- local Supabase/RLS production contract asset and contract validation gate that
  does not apply a database migration.
- local applicant request-status/deposit-instruction lookup that requires
  request id plus contact and does not expose Owner notes/events.
- local payment evidence policy and gate that forbid raw/private evidence
  persistence and define minimal retained audit fields.
- local production secret/token policy and gate that define user-owned
  LLM/SNS/OAuth/KIS token categories, write-only handling, redaction,
  lifecycle, audit, and launch gates without reading or writing any secret.
- local per-user engine/safety contract and gate that define user-scoped
  engine state, queue, kill switch, risk limits, circuit breakers,
  append-only order intents, logs, notifications, worker context, and launch
  gates without changing engine/order/risk behavior.
- local tenant-isolation matrix and gate that define route groups, tenant
  surfaces, `auth.uid()` ownership, and required staging tests without applying
  Supabase schema/RLS.
- TASK-087 구현 입력 보강.

## 다음 구현 입력

- account status: requested, verification_pending, deposit_pending, active,
  rejected, expired
- bank-transfer instruction fields loaded from runtime/admin configuration
- unique deposit code per request
- Owner manual approval admin action
- code-assisted deposit recognition as later approval aid
- approval event audit log
- local ID/PW auto-registration is fail-closed by default; first-run/dev opt-in
  requires AUTOFOLIO_LOCAL_AUTO_REGISTER=1
- local API endpoints exist for request intake, Owner review, and Owner+CSRF
  state transition
- local `/settings` admin UI exists for Owner review and manual state transition
- local active transition can create a `member` login account and subscription
  grant with plaintext password excluded from responses/storage
- local Owner-only deposit recognition endpoint/UI can scan pasted statement or
  CSV text by deposit code, amount, applicant name, and contact without storing
  the raw pasted text
- local app-user and owner-admin gates are split; `member` accounts can mutate
  only session-derived self-service account/profile/acknowledgement state and
  cannot mutate global engine/trading/admin controls
- `/api/auth/login` rejects `guest=true` by default; local/dev guest demo can be
  enabled only with `AUTOFOLIO_GUEST_DEMO_ENABLED=1`
- public login UI does not show a guest/demo CTA; users are directed to approved
  login or 가입 승인 신청
- product read APIs require `require_app_user`; anonymous callers receive 401,
  guest sessions receive 403, and approved `member`/`owner` sessions read
- approved users can manage their own local LLM/SNS integration records under
  `/settings > 계정/연결`; token values are write-only at API boundary and
  redacted from responses
- Owner can see production readiness blockers under `/settings > 회원 승인`;
  `can_launch` remains false while R3 blockers remain
- production entity/RLS/user_id/secret/payment/engine contract exists in
  `agents/project/MEMBERSHIP-PRODUCTION-CONTRACT.json`, and
  `python scripts/membership_contract_gate.py --check` validates it locally
- applicants can check `/signup` status with request id plus contact and see
  deposit instructions after Owner moves the request to `deposit_pending`
- payment evidence retention policy exists in
  `agents/project/MEMBERSHIP-PAYMENT-EVIDENCE-POLICY.json`, and
  `python scripts/membership_payment_policy_gate.py --check` validates it locally
- production secret policy exists in
  `agents/project/MEMBERSHIP-PRODUCTION-SECRET-POLICY.json`, and
  `python scripts/membership_secret_policy_gate.py --check` validates it locally
- per-user engine/safety contract exists in
  `agents/project/MEMBERSHIP-ENGINE-SAFETY-CONTRACT.json`, and
  `python scripts/membership_engine_safety_gate.py --check` validates it locally
- tenant-isolation matrix exists in
  `agents/project/MEMBERSHIP-TENANT-ISOLATION-MATRIX.json`, and
  `python scripts/membership_tenant_isolation_gate.py --check` validates it locally
- production DB, multi-tenant isolation, and deployment remain future gates
