# Autofolio Marketing Materials V1

Status: draft source packet, not publication approval
Owner: Marketing Growth
Created: 2026-06-19T22:36:50+09:00
Related tasks: TASK-093, TASK-095, TASK-096, TASK-097
Related taskset: TASKSET-MARKETING-GROWTH

## Purpose

This packet turns `BUSINESS-PLAN.md` and `MARKETING-BRIEF.md` into reviewable
text sources for landing copy, a PDF one-pager, a PPTX outline, SNS drafts, a
support FAQ, and disclaimers.

It is not public material. It must not be posted, emailed, exported as final
PDF/PPTX, used in paid ads, or uploaded to external accounts until the relevant
Owner, Compliance Officer, Business Planner, QA, and Doc Steward reviews are
complete.

## Campaign Brief

| Field | Value |
|-------|-------|
| campaign_id | `MKT-2026-06-19-001` |
| name | Verified Membership Pilot Explainer |
| audience | Acquaintances and selected Korean individual investors who can manage their own broker, LLM, SNS, approval, and risk boundaries. |
| promise | A user-controlled investing workflow that puts safety guards, portfolio visibility, agent summaries, and explicit approvals in one auditable place. |
| CTA | Request verified membership review. |
| claim_review | draft |
| publishing_mode | manual-export review only |

## Allowed Draft Claims

- user-controlled investing workflow
- auditable operating records
- explicit approvals before live action
- portfolio visibility and agent-assisted summaries
- verified-person account approval
- mock/paper-first verification

## Needs Review

| Claim | Review | Reason |
|-------|--------|--------|
| agent recommendation flows | Compliance Officer | Must not imply investment advice, paid signals, model portfolios, or discretionary management. |
| low-price paid pilot | Owner + Business Planner | Exact pricing, payment, refund, support, privacy, and receipt policy are not public-ready. |
| user-owned LLM/SNS token integrations | Compliance Officer + QA | Provider policy, privacy, OAuth/token handling, and secret storage need review before public copy. |

## Do Not Use

- guaranteed returns
- AI selects winning stocks
- hands-free wealth management
- investment advice
- safe returns or risk-free
- broker, asset manager, robo-advisor, or paid signal service as Autofolio identity
- KIS commercial integration cleared

## Landing Page Draft

Headline:

> Run an auditable investing workflow with safety gates first.

Subheadline:

> For selected users who want portfolio visibility, agent summaries, and explicit approvals while keeping their own account authority.

Sections:

| Section | Draft Copy |
|---------|------------|
| Safety-first workflow | Mock and paper verification, manual approval boundaries, readiness checks, and records make every step reviewable. |
| Portfolio context in one place | Bring portfolio visibility, manuals, acknowledgements, and agent summaries into a single workspace. |
| Verified membership | Start with a verified membership request. Access is approved only after review, and payment details stay outside repository artifacts. |

CTA: Request verified membership review.

## PDF One-Pager Source

Title: Autofolio Pilot Explainer

1. What it is: a user-controlled investing workflow service for selected users.
2. Who it is for: people comfortable managing their own broker, LLM, SNS,
   approval, and risk boundaries.
3. What it emphasizes: safety guards, portfolio visibility, workflow records,
   agent summaries, and explicit approvals.
4. What it is not: an account-control service, public recommendation service,
   or hands-off account operator.
5. Next step: verified membership review.

## PPTX Deck Source

| Slide | Title | Draft Body |
|-------|-------|------------|
| 1 | Autofolio | Verified-membership investing workflow service. |
| 2 | Problem | Investor context is fragmented across apps, notes, spreadsheets, alerts, and AI prompts. |
| 3 | Approach | Connect safety guards, portfolio visibility, agent summaries, explicit approvals, and records. |
| 4 | Pilot Boundary | Selected users, user-owned accounts and tokens, mock/paper-first checks, and human approval before live action. |
| 5 | Review Gates | Public claims, paid pilot terms, KIS commercial use, recommendation wording, privacy, payment, and support policies require review. |
| 6 | Next Step | Request verified membership review. |

## SNS Draft Bundle

All items are draft-only and must not be posted until TASK-096 defines the
approval queue, channel policy, audit log, and rollback path.

| Channel | Draft |
|---------|-------|
| Owner blog | Development note: Autofolio is being shaped as a verified-membership investing workflow with safety gates first, then portfolio visibility, workflow, and live-readiness. Public launch claims remain under review. |
| X | Draft: Autofolio focuses on safety-first investing workflows for selected users: portfolio visibility, agent summaries, explicit approvals, and auditable records. |
| LinkedIn | Draft: Autofolio is moving toward a verified-membership pilot for users who want structured investing operations while keeping account authority and final decisions under their own control. |
| Naver blog | Draft: Autofolio combines portfolio context, manuals, acknowledgement flows, agent summaries, and approval checks into one reviewable workflow. |

## Support FAQ Draft

| Question | Answer |
|----------|--------|
| Who can use the pilot? | Only selected users who pass verified membership review. |
| Does Autofolio control my brokerage account? | No. Users keep their own account authority, settings, approvals, and risk responsibility. |
| How should agent summaries be described? | They should be described as workflow assistance for user review until compliance and professional review approve stronger wording. |
| Can this material be posted now? | No. It is draft source only. Public posting, customer contact, paid ads, or external account actions require Owner approval. |

## Disclaimer Draft

This draft describes a workflow product under review. It is not investment
advice, a performance promise, a public offer, or confirmation of KIS commercial
clearance.

## Validation

The canonical machine-readable source is `MARKETING-MATERIALS-V1.json`.

```powershell
python scripts/marketing_materials_gate.py --check
python -m pytest tests/unit/test_marketing_materials_gate.py -q
```
