---
schema_version: agent-runtime-work-item/v1
work_id: INIT-MEMBERSHIP-ACCESS
work_uid: 6a3a85ef-b3df-4ef6-9126-6d64f5c69315
kind: initiative
status: active
owner: Lead Engineer
created_at: 2026-06-19T13:18:08+09:00
updated_at: 2026-06-19T19:29:22+09:00
origin_type: owner_request
origin_ref: AUDIT-2026-06-19-008
created_by: lead_engineer
title: Membership Access — Verified signup and manual deposit approval
summary: 검증된 사람만 회원가입 승인하고, 무통장입금/입금코드 확인 및 로컬 입금내역 인식 보조를 통해 계정 활성화하되 member/admin 권한과 product read scope를 분리하고 기본 guest/demo 진입을 차단하며 user-owned LLM/SNS 연동 하네스, production readiness gate, payment evidence policy, production secret policy, per-user engine/safety contract, tenant isolation matrix를 제공하는 v1 access lane.
tags: [membership, access, payment, bank-transfer, approval, auth, tenant-isolation]
priority: P1
---

# INIT-MEMBERSHIP-ACCESS — verified signup and manual deposit approval

## 목적

Autofolio를 self-serve 공개 가입이 아니라 검증된 사람만 승인하는 회원제로 만든다.
v1은 수동 무통장입금 확인과 Owner 승인으로 시작하고, 이후 입금코드 기반 인식
또는 은행/API 연동은 별도 게이트로 확장한다.

## 포함 작업

| ID | 설명 | Owner | 순서 |
|----|------|-------|------|
| TASK-098 | Membership access plan — verified signup + manual deposit approval | Lead Engineer | 1 |
| TASK-099 | Local auto-register fail-closed — unknown local accounts cannot self-create owner sessions by default | Backend Engineer | 2 |
| TASK-100 | Local request approval prototype — signup request and Owner approval-state API/UI | Backend Engineer | 3 |
| TASK-101 | Membership admin settings tab — Owner review and manual approval UI over local APIs | UI/UX Designer | 4 |
| TASK-102 | Membership local account grant — active approval creates local member login/subscription grant | Backend Engineer | 5 |
| TASK-103 | Membership local deposit recognition — pasted statement/CSV recognition aid for deposit-pending requests | Backend Engineer | 6 |
| TASK-104 | Membership member/admin boundary — approved member self-service separated from Owner/admin global controls | Backend Engineer | 7 |
| TASK-105 | Membership guest demo fail-closed — no server-issued guest session or public guest CTA by default | Backend Engineer | 8 |
| TASK-106 | Membership app-user read boundary — product read APIs require approved owner/member | Backend Engineer | 9 |
| TASK-107 | User-owned integration token harness — approved users manage their own LLM/SNS token status locally | Backend Engineer | 10 |
| TASK-108 | Membership production readiness gate — Owner-visible launch blocker checklist | Backend Engineer | 11 |
| TASK-109 | Membership Supabase/RLS production contract — local contract and gate only | Backend Engineer | 12 |
| TASK-110 | Membership applicant deposit status lookup — applicant-safe request status/deposit instruction lookup | Backend Engineer | 13 |
| TASK-111 | Membership payment evidence policy gate — minimal retained payment evidence policy and local gate | Backend Engineer | 14 |
| TASK-112 | Membership production secret policy — provider/KIS/user token handling policy and local gate | Backend Engineer | 15 |
| TASK-113 | Membership per-user engine safety contract — engine state/queue/risk/order intent contract and local gate | Lead Engineer | 16 |
| TASK-114 | Membership tenant isolation matrix — user_id/RLS route/surface/test matrix and local gate | Backend Engineer | 17 |
| TASK-087 | Web deploy + buyer-only membership gating implementation | Lead Engineer | 18 |

## 완료 기준

- membership access plan이 Business Plan, Marketing Brief, Admin Register와 연결된다.
- unknown local account 자동가입이 기본값에서 차단된다.
- local encrypted-vault signup request and approval-state prototype이 동작한다.
- Owner가 `/settings`에서 local 가입신청을 검증/입금대기/활성/거절/만료로 전환할 수 있다.
- Owner가 입금 확인 시 local member login account와 subscription grant를 생성할 수 있다.
- Owner가 pasted bank statement/CSV text를 사용해 deposit_pending 신청의 입금코드/금액/신청자 정보를 보조 인식할 수 있다.
- 승인 member는 자기 계정/프로필/동의서 self-service는 가능하지만 Owner/admin 글로벌 제어 API는 통과하지 못한다.
- 게스트 데모 로그인은 기본값에서 서버가 발급하지 않고, 공개 로그인 화면도 게스트 CTA를 제공하지 않는다.
- 제품 read API는 승인된 `owner`/`member` 계정만 통과하고 guest session은 403으로 차단된다.
- 승인 사용자는 `/settings > 계정/연결`에서 자기 LLM/SNS 연동 상태를 write-only/redacted 방식으로 관리할 수 있다.
- Owner는 `/settings > 회원 승인`에서 production readiness blocker를 볼 수 있고 R3 증거 전까지 `can_launch=false`로 남는다.
- payment evidence retention policy와 local gate가 존재해 raw payment data persistence를 금지한다.
- production secret policy와 local gate가 존재해 user-owned LLM/SNS/OAuth/KIS token의 write-only/redacted/lifecycle 기준을 고정한다.
- per-user engine/safety contract와 local gate가 존재해 engine state, queue, kill switch, risk limit, circuit breaker, order intent, log, notification scope를 user_id 단위로 고정해야 한다는 구현 입력을 제공한다.
- tenant-isolation matrix와 local gate가 존재해 public/member/owner/worker route, tenant surface, `auth.uid()` ownership, staging cross-user tests를 구현 입력으로 제공한다.
- TASK-087이 verified-person signup, deposit-pending, manual/code-assisted approval을 구현 입력으로 가진다.
- 실제 계좌번호, 고객 개인정보, bank API secret, production payment integration은 Owner 승인 전까지 repo에 들어가지 않는다.
