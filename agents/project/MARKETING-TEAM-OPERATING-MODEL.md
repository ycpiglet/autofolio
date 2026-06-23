# Marketing Team Operating Model

Status: complete local operating model, not publication approval.
Owner: Lead Engineer
Related task: TASK-166
Related taskset: TASKSET-MARKETING-TEAM-OPERATING-SYSTEM

## Purpose

This document turns the completed Marketing Growth plan into a repeatable
operating model for the marketing team. It defines who handles each kind of
promotion work, when Compliance Officer review is required, when Owner/R3 gates
are required, and which next TASK should handle each follow-up slice.

## Source Inputs

- `agents/project/BUSINESS-PLAN.md`
- `agents/project/MARKETING-BRIEF.md`
- `agents/project/initiatives/TASKSET-MARKETING-GROWTH.md`
- `agents/project/initiatives/TASKSET-MARKETING-TEAM-OPERATING-SYSTEM.md`
- `agents/project/MARKETING-MATERIALS-V1.json`
- `agents/project/PROMOTION-CHANNEL-POLICY-MATRIX.json`
- `agents/project/PROMOTION-PUBLISHING-STATE-MACHINE.json`
- `agents/project/PROMOTION-ASSET-RENDERING-CONTRACT.json`
- `agents/project/SALES-REVENUE-LANE-DECISION.json`

## Team Routing

| Work type | Primary role | Review roles | Next task |
|-----------|--------------|--------------|-----------|
| Campaign copy or content calendar | Marketing Growth | Compliance Officer, QA, Doc Steward | TASK-167 |
| PDF/PPTX or asset generation readiness | Doc Steward | Marketing Growth, Backend Engineer, QA, Compliance Officer | TASK-168 |
| SNS or external publishing automation readiness | Backend Engineer | Marketing Growth, Compliance Officer, QA, Doc Steward | TASK-169 |
| Sales, revenue, or customer conversion handoff | Business Planner | Marketing Growth, Compliance Officer, Managing Partner, Lead Engineer | TASK-170 |

## Workflow

1. Intake: Lead Engineer identifies the source plan, task, and R2/R3 boundary.
2. Source alignment: Doc Steward records source paths and review status.
3. Draft or readiness work: Marketing Growth or the assigned primary role
   creates a local draft, checklist, map, or readiness artifact.
4. Claim review: Compliance Officer classifies any financial, performance,
   investment-advice, tax, legal, regulatory, KIS, paid-signal, or public paid
   launch wording.
5. QA gate: QA runs local parse, gate, and focused tests.
6. Closeout: Lead Engineer updates TASK, BRIEF, AUDIT, STATUS, pointer, and
   generated views.

Every phase is local-only and has `external_action_enabled=false`.

## Role Boundaries

| Role | Owns | Must not do |
|------|------|-------------|
| Lead Engineer | taskset sequencing, TASK/BRIEF/AUDIT/STATUS alignment | public posting, customer contact, external account action |
| Marketing Growth | positioning, campaign brief, copy drafts, channel draft plans | public posting, paid ads, customer email/DM, performance guarantee |
| Compliance Officer | claim classification and review flags | legal/tax/securities final advice or publication approval |
| Business Planner | business-plan consistency and sales handoff prerequisites | customer contact, payment request, CRM activation |
| Regulatory Admin | admin readiness notes and official-form input boundary | official filing, login, signature, payment, private identity storage |
| Doc Steward | source inventory, freshness, review references, handoff docs | audit verdict, priority decision, product implementation |
| Backend Engineer | local queue contract, no-network adapter tests, dry-run record schema | OAuth, token handling, platform API call, live post, final export |
| QA | local gates, regression tests, forbidden-action checks | publication approval or platform execution |

## Compliance Review Triggers

- investment advice wording
- paid signal wording
- model portfolio wording
- automated trading wording
- performance or return wording
- KIS commercial use wording
- tax or legal wording
- regulatory status wording
- public paid launch wording
- recommendation wording

## Owner/R3 Triggers

- public post
- SNS upload
- paid ads
- customer contact
- CRM or customer-record system activation
- payment request or billing setup
- Sales/Revenue role activation
- OAuth flow
- external platform API call
- external account setting change
- browser automation against social platform
- final PDF/PPTX binary export
- public URL publication
- secret or token handling
- customer private data handling
- production DB apply
- deploy
- KIS/order/risk/prod change
- legal/tax/securities final advice

## Downstream Start Criteria

| Task | Start criteria |
|------|----------------|
| TASK-167 | This operating model is complete, source claim bank remains draft-safe, public action gate is closed. |
| TASK-168 | TASK-167 campaign backlog exists, asset rendering contract remains local-only, final export gate is closed. |
| TASK-169 | TASK-167 campaign backlog exists, publishing state machine remains `live_action=false`, OAuth/platform API gates are closed. |
| TASK-170 | TASK-167 campaign backlog exists, Sales/Revenue decision remains not active, customer contact/payment gates are closed. |

## Boundary

This model does not approve public posting, SNS upload, paid ads, customer
contact, CRM/customer records, payment requests, billing setup, Sales/Revenue
role activation, OAuth, token handling, platform API calls, browser automation
against social platforms, final PDF/PPTX export, public URL publication,
secrets, customer private data, legal/tax/securities final advice, KIS, order,
risk, production, or deploy changes.

## Verification

```powershell
python -m json.tool agents\project\MARKETING-TEAM-OPERATING-MODEL.json
python scripts\marketing_team_operating_model_gate.py --check
python -m pytest tests\unit\test_marketing_team_operating_model_gate.py -q
```

## Result

TASK-166 is complete for the local operating-model scope. The next taskset
slice is TASK-167 campaign backlog and content calendar. No public posting,
SNS upload, paid ads, customer contact, CRM/payment, OAuth, platform API call,
final PDF/PPTX export, public URL, secret/customer data, KIS/order/risk/prod, or
deploy boundary was crossed.
