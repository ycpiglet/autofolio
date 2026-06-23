---
type: task
id: TASK-173
display_id: TASK-173
task_uid: e8120499-841e-40a0-aadd-7887c610a48a
registered_at: 2026-06-21T16:30:12+09:00
created_at: 2026-06-21T16:30:12+09:00
updated_at: 2026-06-21T16:30:12+09:00
status: 대기
owner: Backend Engineer
assignees: [Backend Engineer, Finance Accounting, Compliance Officer, QA]
priority: Medium
difficulty: 중
est_hours: 5
est_tokens: 70000
tags: [finance, accounting, portfolio, backend, read-model]
initiative_id: INIT-FINANCE-ACCOUNTING
task_set_id: TASKSET-FINANCE-ACCOUNTING-PLANNING-SUPPORT
gate: read-only derived model only; no order path change, no trade recommendation, no private payment data, no KIS/order/risk/prod/deploy
trigger_meeting: Owner direct request 2026-06-21
audit_log: AUDIT-2026-06-21-001
created: 2026-06-21
---

# TASK-173 Portfolio Goal-Gap Read Model

작업 ID: TASK-173
상태: 대기
Owner: Backend Engineer
요청 시각: 2026-06-21T16:30:12+09:00
기록 시각: 2026-06-21T16:30:12+09:00
요청자: Owner
수행자: Backend Engineer, Finance Accounting, Compliance Officer, QA
의도: TASK-172 fixture와 read-only portfolio/account data를 사용해 planned vs expected,
gap, allocation drift, data-quality, timeline candidate를 계산하는 read model을 만든다.
대상: portfolio read surfaces, finance scenario fixture, future API schema
방법: order/trade/risk path를 건드리지 않고 derived read model과 tests만 추가한다.
감사 로그: AUDIT-2026-06-21-001

## 범위

포함:

- read-only finance roadmap model.
- deterministic calculations from fixture + available portfolio overview fields.
- no-action candidate records with evidence and missing-data fields.
- focused tests for no order path, no advice wording, no private data.

제외:

- actual order placement or order intent creation.
- buy/sell/rebalance/profit-taking instruction.
- portfolio mutation.
- customer payment/receipt/tax action.
- KIS/order/risk/prod/deploy changes.

## 완료 조건

- [ ] Read model returns planned/expected/gap/timeline fields.
- [ ] Output marks all portfolio changes as Owner-review candidates only.
- [ ] Tests prove no order/advice/payment/private-data drift.
- [ ] TASK-174 can consume the model in a UI preview.

## 다음

Start after TASK-172 is complete.
