# Promotion Campaign Backlog Calendar V1

Status: draft backlog/calendar, not publication approval.
Owner: Marketing Growth
Created: 2026-06-20T11:11:07+09:00
Related task: TASK-167
Related taskset: TASKSET-MARKETING-TEAM-OPERATING-SYSTEM
Canonical JSON: `agents/project/PROMOTION-CAMPAIGN-BACKLOG-CALENDAR-V1.json`

## Purpose

This packet turns the current Marketing Brief and Marketing Materials v1 into a
draft-only campaign backlog and four-week content calendar. It is a planning
artifact only. It does not approve public posting, paid ads, customer contact,
external account action, OAuth, platform API calls, public URLs, final PDF/PPTX
export, payment requests, CRM records, Sales/Revenue activation, or any KIS /
order / risk / production change.

## Source Inputs

- `agents/project/BUSINESS-PLAN.md`
- `agents/project/MARKETING-BRIEF.md`
- `agents/project/MARKETING-MATERIALS-V1.json`
- `agents/project/MARKETING-TEAM-OPERATING-MODEL.json`
- `agents/project/PROMOTION-CHANNEL-POLICY-MATRIX.json`
- `agents/project/PROMOTION-PUBLISHING-STATE-MACHINE.json`

## Campaign Backlog

| ID | Surface | Status | Review Gate | Blocked Action |
|----|---------|--------|-------------|----------------|
| private_pilot_explainer | pilot explainer | draft only | Compliance + Owner/R3 before external sharing | customer contact, payment request, CRM |
| owner_blog_devlog | blog/dev log source | draft only | Compliance + Owner/R3 before publication | public posting, paid ads, account action |
| landing_page_source | landing source | draft only | Business Planner + Compliance + Owner/R3 before public URL | public URL, signup funnel, payment |
| pdf_pptx_source_bundle | one-pager/deck source | draft only | Doc Steward + Compliance + Owner/R3 before final export | final PDF/PPTX export |
| sns_draft_bundle | SNS variants | draft only | Compliance + Owner/R3 before upload/API/browser automation | SNS upload, OAuth, platform API call |

## Four-Week Draft Calendar

| Week | Date | Item | Channel Candidate | Status |
|------|------|------|-------------------|--------|
| 1 | 2026-06-24 | Pilot explainer outline | private review material | draft only |
| 1 | 2026-06-26 | Safety-first workflow build note | owner blog | review gate |
| 2 | 2026-07-01 | Verified membership landing source | landing page | draft only |
| 2 | 2026-07-03 | One-pager and deck source split | PDF/PPTX source | draft only |
| 3 | 2026-07-08 | SNS variant source batch | X / LinkedIn / Naver Blog manual drafts | review gate |
| 3 | 2026-07-10 | FAQ and disclaimer alignment | private review material | draft only |
| 4 | 2026-07-15 | Review-required claim quarantine pass | landing page | review gate |
| 4 | 2026-07-17 | Asset-readiness handoff packet | PDF/PPTX source | draft only |

## Claim Separation

Allowed draft copy may use only:

- user-controlled investing workflow;
- auditable operating records;
- explicit approvals before live action;
- portfolio visibility;
- agent-assisted summaries;
- verified-person account approval;
- mock/paper-first verification.

The following stay outside campaign copy until review:

- agent recommendation flows;
- low-price paid pilot;
- user-owned LLM/SNS token integrations;
- KIS commercial use.

The do-not-use claims from `MARKETING-BRIEF.md` remain quarantined and are not
copy seeds.

## Next Handoff

- TASK-168: asset generator implementation readiness map.
- TASK-169: SNS publishing automation readiness backlog.
- TASK-170: Sales handoff readiness checklist.

Recommended next no-Owner slice: TASK-168, because PDF/PPTX and landing source
now have draft backlog entries but no generator-readiness map yet.

## Verification

```powershell
python -m json.tool agents\project\PROMOTION-CAMPAIGN-BACKLOG-CALENDAR-V1.json
python -m py_compile scripts\promotion_campaign_backlog_calendar_gate.py
python scripts\promotion_campaign_backlog_calendar_gate.py --check
python -m pytest tests\unit\test_promotion_campaign_backlog_calendar_gate.py -q
```
