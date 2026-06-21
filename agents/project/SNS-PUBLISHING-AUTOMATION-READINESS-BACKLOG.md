# SNS Publishing Automation Readiness Backlog

Status: local readiness backlog, not live publication
Owner: Backend Engineer
Updated: 2026-06-20T11:57:37+09:00
Related task: TASK-169
Related taskset: TASKSET-MARKETING-TEAM-OPERATING-SYSTEM

This backlog prepares future SNS publishing automation without creating OAuth
flows, acquiring or storing tokens, calling platform APIs, posting or scheduling
live content, automating browsers against social platforms, running paid ads,
contacting customers, scraping leads, creating fake engagement, or touching
KIS/order/risk/prod/deploy surfaces.

## Source Inputs

| Source | Path | Use |
|--------|------|-----|
| Channel policy matrix | `agents/project/PROMOTION-CHANNEL-POLICY-MATRIX.json` | channel risk and platform boundary |
| Publishing policy packet | `agents/project/PROMOTION-PUBLISHING-POLICY-PACKET.json` | policy foundation and channel policies |
| Publishing state machine | `agents/project/PROMOTION-PUBLISHING-STATE-MACHINE.json` | queue states and record-only after-live state |
| Dry-run audit preview | `agents/project/PROMOTION-DRY-RUN-AUDIT-PREVIEW.json` | existing no-network dry-run pattern |
| Asset generator readiness map | `agents/project/PROMOTION-ASSET-GENERATOR-READINESS-MAP.json` | SNS draft/image source readiness |
| Marketing materials | `agents/project/MARKETING-MATERIALS-V1.json` | draft copy source |
| Marketing brief | `agents/project/MARKETING-BRIEF.md` | claim bank and marketing boundary |

Hashes are canonical in `SNS-PUBLISHING-AUTOMATION-READINESS-BACKLOG.json`.

## Channel Classification

| Channel | Classification | Current action |
|---------|----------------|----------------|
| Owner blog manual export | manual-only | local copy packet only |
| Telegram bot/channel | future approval queue | no connector implementation |
| X API | future approval queue | no OAuth/API work |
| LinkedIn share | future approval queue | no OAuth/API work |
| Instagram | defer | wait for media/account/policy review |
| Naver Share | manual-only | public URL share helper only after approved URL exists |
| Naver Blog | manual-only | no automated posting or browser login scripting |
| Naver Cafe write | defer | wait for exact cafe, permission, and community policy |
| KakaoTalk Message API | rejected | do not treat as marketing broadcast |
| Google Business Profile | defer | wait for business profile/location readiness |

## Queue Contract

Required local queue records include campaign id, channel id, channel
classification, copy surface, source artifact, source hash, draft text, claim
review status, compliance reviewer, Owner approval fields, required scopes,
dry-run preview, schedule placeholder, live-action blocker, after-live-only
external references, rollback/delete instruction, blocked reason, and audit
events.

Forbidden queue fields include token, credential, cookie, customer, payment,
ad-account, and KIS secret material.

## No-Network Dry-Run Contract

Dry-run records must stay local and include:

- campaign id;
- channel id;
- source hash;
- claim review status;
- Owner approval status;
- planned visibility;
- schedule placeholder;
- `external_network_calls=false`;
- `external_action_enabled=false`;
- `live_action_blocked_by_default=true`;
- rollback instruction;
- blocked reason.

## No-Network Test Plan

| Test | Purpose |
|------|---------|
| source_hash_required | reject queue or dry-run records without source evidence |
| queue_record_has_no_secret_fields | reject token, customer, payment, ad, or KIS fields |
| dry_run_has_no_network_or_external_action | prove local dry-runs do not call platforms |
| channel_classification_complete | ensure every channel is classified |
| rollback_delete_evidence_required | require delete/edit/archive/withdraw evidence |
| record_only_after_owner_external_action | allow after-live records only for Owner actions outside automation |
| forbidden_automation_terms_blocked | block OAuth, live posting, spam, fake engagement, scraping, and paid ads |

## Implementation Backlog

R2 without Owner approval:

- local manual export packet;
- local approval queue storage contract;
- no-network dry-run adapter;
- record-only-after-Owner-action logger;
- unsupported channel registry;
- policy refresh check.

R3 with Owner approval:

- any live platform connector implementation;
- OAuth login or callback validation;
- token handling;
- SNS upload, edit, delete, or scheduled post;
- paid ads, customer contact, CRM/customer records, or billing setup.

## Handoff

TASK-169 completes `TASKSET-MARKETING-TEAM-OPERATING-SYSTEM`. The marketing
team now has operating model, campaign backlog/calendar, asset-generator
readiness, SNS publishing automation readiness, and Sales handoff readiness.
Live publication remains blocked until a separate Owner/R3 lane exists.

## Validation

```powershell
python scripts/sns_publishing_automation_readiness_backlog_gate.py --check
python -m pytest tests/unit/test_sns_publishing_automation_readiness_backlog_gate.py -q
```
