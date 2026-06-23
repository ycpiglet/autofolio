---
schema_version: agent-runtime-work-item/v1
work_id: TASKSET-FINANCE-ACCOUNTING-PLANNING-SUPPORT
work_uid: ffcc4e32-0436-4557-8927-3af822fb39e5
kind: taskset
parent_id: INIT-FINANCE-ACCOUNTING
status: active
owner: Finance Accounting
created_at: 2026-06-21T16:30:12+09:00
updated_at: 2026-06-21T17:06:02+09:00
origin_type: owner_request
origin_ref: AUDIT-2026-06-21-001
created_by: lead_engineer
title: Finance Accounting Planning Support
summary: Register and execute the first finance/accounting planning-support slice: role contract, plan-vs-expected roadmap packet, local gate, and follow-up tasks for scenario fixtures, read model, and UI preview.
tags: [finance, accounting, portfolio, planning, operations, roadmap]
priority: P2
---

# TASKSET-FINANCE-ACCOUNTING-PLANNING-SUPPORT

## Purpose

Build the finance/accounting planning-support lane in small reversible units.
The lane compares planned return, expected scenario, operating gaps, portfolio
review candidates, and timeline candidates without becoming trade advice,
financial advice, tax/accounting advice, payment execution, or production work.

## Source Plan

- `agents/project/BUSINESS-PLAN.md`
- `agents/project/MEMBERSHIP-ACCESS-PLAN.md`
- `agents/project/MEMBERSHIP-PAYMENT-EVIDENCE-POLICY.md`
- `agents/project/MEMBERSHIP-PAYMENT-RECOGNITION-DECISION-PACKET.md`
- `agents/project/SALES-HANDOFF-READINESS-CHECKLIST.md`
- `app/api/routers/portfolio.py`
- `app/services/investor_profile.py`

## Included Tasks

| work_id | Description | Owner | Status | Gate |
|---------|-------------|-------|--------|------|
| TASK-171 | Finance/accounting planning-support lane foundation | Finance Accounting | 완료 | local docs/JSON/gate/tests only |
| TASK-172 | Finance scenario input contract and sample fixture | Finance Accounting | 완료 | synthetic fixture only; no real customer/payment data |
| TASK-173 | Portfolio goal-gap read model | Backend Engineer | 대기 | read-only derived model; no order path change |
| TASK-174 | Finance roadmap UI preview | UI/UX Designer | 대기 | no recommendation wording |

## Dependency Map

```text
TASK-171
  -> TASK-172
       -> TASK-173
       -> TASK-174
```

TASK-171 fixes the role, source contract, and gate. TASK-172 created the
deterministic synthetic fixture. TASK-173 may turn that fixture into a read
model. TASK-174 may expose the result in the UI after wording and boundary
checks are stable.

## Boundaries

Allowed:

- local Markdown/JSON planning artifacts;
- role registry and alias wiring;
- source contract, gap matrix, and candidate roadmap;
- deterministic local gates and tests;
- review, audit, doc-steward, and scribe-ready closeout records.

Blocked:

- final tax/accounting/legal/securities advice;
- trade recommendation, order placement, profit-taking instruction, additional
  investment instruction, or rebalancing instruction;
- customer payment request, CRM/customer record creation, receipt/refund/tax
  execution, bank/PG/Open Banking calls;
- raw statement, real payment record, private identifier, secret, token, KIS key;
- KIS/order/risk/prod/deploy changes.

## Next

Continue with TASK-173 using `FINANCE-SCENARIO-INPUT-CONTRACT.json` as the
stable local input. Continue with TASK-174 only after the read model and wording
gate exist.
