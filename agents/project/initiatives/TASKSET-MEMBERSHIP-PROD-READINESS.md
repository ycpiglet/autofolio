---
schema_version: agent-runtime-work-item/v1
work_id: TASKSET-MEMBERSHIP-PROD-READINESS
work_uid: 9186e4ea-6096-40c9-8fe7-2fd3bc6b80f1
kind: taskset
parent_id: INIT-MEMBERSHIP-ACCESS
status: completed
owner: Lead Engineer
created_at: 2026-06-19T18:29:43+09:00
updated_at: 2026-06-19T19:46:50+09:00
completed_at: 2026-06-19T19:46:50+09:00
closed_by: lead_engineer
resolution: done
verification_status: passed
verified_at: 2026-06-19T20:00:59+09:00
verified_by: lead_engineer
verification:
  - membership_payment_policy_gate pass
  - membership_tenant_isolation_gate pass
  - membership_secret_policy_gate pass
  - membership_engine_safety_gate pass
  - membership_contract_gate pass
origin_type: owner_request
origin_ref: AUDIT-2026-06-19-021
created_by: lead_engineer
title: Membership Production Readiness Taskset — local contracts before launch
summary: TASK-087의 남은 production blocker를 실제 production apply 없이 policy, contract, matrix, local gate, test evidence로 쪼개는 R2 readiness lane.
tags: [membership, production-readiness, payment-evidence, secret-policy, engine-safety, tenant-isolation]
priority: P1
---

# TASKSET-MEMBERSHIP-PROD-READINESS — local contracts before launch

## 부모 이니셔티브

`INIT-MEMBERSHIP-ACCESS`

## 목적

TASK-087의 production 전환 blocker 중 Owner 승인 없이 처리 가능한 R2 작업을
작은 단위로 반복 처리한다. 이 taskset은 production DB apply, 외부 배포, 실제
결제/은행 API, secret 처리, KIS/order/risk/prod 변경을 하지 않는다.

## 포함 태스크

tasks:
  - TASK-111
  - TASK-112
  - TASK-113
  - TASK-114

| work_id | 설명 | Owner | 상태 | Gate |
|---------|------|-------|------|------|
| TASK-111 | Membership payment evidence policy gate — 입금 증거 보존 최소정책과 local gate | Backend Engineer | 완료 | local policy/gate only |
| TASK-112 | Membership production secret policy — provider/KIS/user token 보존·회전·삭제 정책과 local gate | Backend Engineer | 완료 | policy/gate only; no secret read/write |
| TASK-113 | Membership per-user engine safety contract — user_id 단위 엔진/안전장치 격리 계약과 local gate | Lead Engineer | 완료 | contract/gate only; no order/risk code change |
| TASK-114 | Membership tenant isolation matrix — user_id/RLS route/surface/test matrix와 local gate | Backend Engineer | 완료 | matrix/gate only; no DB apply |

## 의존 관계

```text
TASK-111
  -> TASK-114
  -> TASK-112
  -> TASK-113
```

## 안전 경계

금지:

- production DB, Supabase schema/RLS apply, migration execution.
- real bank/payment API, open-banking, PG, virtual account setup.
- actual secret read/write, OAuth callback validation, provider API call.
- KIS credential activation, KIS/order/risk/prod path change.
- external deploy or public launch.

허용:

- local policy/contract documents.
- local tenant-isolation matrix documents.
- deterministic local validation scripts.
- unit/API tests that prove readiness checklist visibility and policy shape.
- TASK-087 completion map updates.
