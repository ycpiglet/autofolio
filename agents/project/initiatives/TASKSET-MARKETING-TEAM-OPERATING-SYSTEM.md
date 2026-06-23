---
schema_version: agent-runtime-work-item/v1
work_id: TASKSET-MARKETING-TEAM-OPERATING-SYSTEM
work_uid: 2bad42ff-86ed-4c86-ab6c-642a338761e2
kind: taskset
parent_id: INIT-MARKETING-GROWTH
status: completed
owner: Marketing Growth
created_at: 2026-06-20T10:42:57+09:00
updated_at: 2026-06-20T11:54:55+09:00
completed_at: 2026-06-20T11:54:55+09:00
resolution: done
verification_status: passed
origin_type: owner_request
origin_ref: AUDIT-2026-06-20-065
created_by: lead_engineer
title: Marketing Team Operating System
summary: TASK-166 through TASK-170 are complete as a local marketing team operating system: team operating model, campaign backlog/calendar, asset-generator readiness, SNS automation readiness, and sales handoff readiness. Public posting, customer contact, final PDF/PPTX export, CRM/payment, OAuth, external platform action, and Sales/Revenue activation remain blocked.
tags: [marketing, agents, go-to-market, operations, assets, sns, sales]
priority: P2
---

# TASKSET-MARKETING-TEAM-OPERATING-SYSTEM

## Purpose

This taskset turns the completed Marketing Growth plan into the next practical
agent-team operating lane. It does not repeat `TASKSET-MARKETING-GROWTH`; it
uses that taskset as source material and creates follow-up work that Marketing
Growth, Compliance Officer, Doc Steward, Backend Engineer, Business Planner, and
QA can execute in small reversible units.

## Source Plan

- `agents/project/BUSINESS-PLAN.md`
- `agents/project/MARKETING-BRIEF.md`
- `agents/project/initiatives/TASKSET-MARKETING-GROWTH.md`
- `TASK-095` Marketing Materials v1 draft source
- `TASK-096` Promotion Publishing Pipeline local design
- `TASK-097` Sales/Revenue lane decision
- `TASK-128` Compliance business routing alignment
- `TASK-129` Promotion Channel Policy Matrix
- `TASK-130` Promotion Publishing State Machine
- `TASK-131` Promotion Dry-run Audit Preview
- `TASK-132` Promotion Asset Rendering Contract
- `TASK-133` Promotion Asset Preview Manifest

## Included Tasks

tasks:
  - TASK-166
  - TASK-167
  - TASK-168
  - TASK-169
  - TASK-170

| work_id | Description | Owner | Status | Gate |
|---------|-------------|-------|--------|------|
| TASK-166 | Marketing team operating model | Lead Engineer | 완료 | local role/routing docs only |
| TASK-167 | Campaign backlog and content calendar v1 | Marketing Growth | 완료 | draft-only campaign planning |
| TASK-168 | Asset generator implementation readiness map | Doc Steward | 완료 | source/hash/tooling map only |
| TASK-169 | SNS publishing automation readiness backlog | Backend Engineer | 완료 | no OAuth, token, API upload, or live post |
| TASK-170 | Sales handoff readiness checklist | Business Planner | 완료 | no Sales/Revenue activation, CRM, payment, or customer contact |

## Dependency Map

```text
TASK-166
  -> TASK-167
       -> TASK-168
       -> TASK-169
       -> TASK-170
```

- TASK-166 fixes the team operating model before additional work is split.
- TASK-167 turns the existing marketing plan into a concrete backlog/calendar.
- TASK-168 reuses the existing rendering contract and preview manifest to define
  generator implementation readiness without final export.
- TASK-169 reuses the publishing policy/state-machine/dry-run artifacts to
  define automation readiness without external platform action.
- TASK-170 reuses the Sales/Revenue decision to define handoff prerequisites
  without creating or activating a sales lane.

## Boundaries

Allowed:

- local Markdown/JSON planning artifacts;
- local source/hash/checklist records;
- local tests or gates that prove the boundaries stay closed;
- updates to generated task views and status records.

Blocked:

- public post, SNS upload, paid ads, external platform API call, OAuth flow,
  browser automation against social platforms, customer contact, CRM/customer
  records, payment requests, final PDF/PPTX binary export, public landing page
  deployment, secret/token handling, legal/tax/securities final advice, KIS,
  order, risk, production DB, or deploy changes.

## Completion Criteria

- TASK-166 through TASK-170 are completed or explicitly deferred with evidence.
- `MARKETING-BRIEF.md` points to the taskset as the current marketing-team
  operating lane.
- Generated task views and backlog board are refreshed.
- `python scripts/check_agent_docs.py` returns 0 errors.

## Current Progress

- TASK-166 is complete. `MARKETING-TEAM-OPERATING-MODEL.json` and `.md` define
  role boundaries, workflow phases, routing rules, Compliance review triggers,
  Owner/R3 triggers, downstream start criteria, and blocked action gates.
- TASK-167 is complete. `PROMOTION-CAMPAIGN-BACKLOG-CALENDAR-V1.json` and `.md`
  define five draft-only campaign backlog items, a four-week content calendar,
  claim separation, review queues, and Owner/R3 blocked actions.
- TASK-168 is complete. `PROMOTION-ASSET-GENERATOR-READINESS-MAP.json` and `.md`
  map source hashes, target surfaces, renderer candidates, local tooling
  readiness, future R2/R3 implementation candidates, and final-export blockers
  without creating any binary asset or external action.
- TASK-169 is complete. `SNS-PUBLISHING-AUTOMATION-READINESS-BACKLOG.json` and
  `.md` classify channels as manual-only, future approval queue, defer, or
  rejected; define local queue/dry-run fields; separate R2 local backlog from
  R3 live connector work; and keep OAuth, token handling, platform API calls,
  live posts, browser automation, paid ads, customer contact, spam, scraping,
  fake engagement, and KIS/order/risk/prod/deploy work blocked.
- TASK-170 is complete. `SALES-HANDOFF-READINESS-CHECKLIST.json` and `.md`
  separate Marketing-only no-contact material from future Sales/Revenue
  conversion, CRM, customer record, payment, support, and retention work.
- TASKSET-MARKETING-TEAM-OPERATING-SYSTEM is complete as a local readiness and
  planning lane. Future live publishing, final asset export, customer contact,
  CRM/payment, Sales/Revenue activation, OAuth/platform API, and secret-handling
  work requires a separate Owner/R3 lane.
