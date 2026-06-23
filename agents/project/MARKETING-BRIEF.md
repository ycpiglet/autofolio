# Autofolio Marketing Brief

Status: v1-owner-answered
Owner: Marketing Growth
Last updated: 2026-06-20T11:57:37+09:00
Source of truth: `agents/project/BUSINESS-PLAN.md`
Related tasks: TASK-092, TASK-093, TASK-095, TASK-096, TASK-097, TASK-128, TASK-129, TASK-130, TASK-131, TASK-132, TASK-133, TASK-166, TASK-167, TASK-168, TASK-169, TASK-170
Related tasksets: TASKSET-MARKETING-GROWTH, TASKSET-MARKETING-TEAM-OPERATING-SYSTEM, TASKSET-MARKETING-ASSET-RENDERING-FOUNDATION

## Purpose

This document turns the approved business plan into safe marketing inputs. It is
not a public campaign by itself. Public copy, generated promotional files, and
SNS publishing must all flow through the review gates below.

## Operating Model

Marketing Growth owns:

- positioning, messaging, claim bank, campaign briefs, launch copy, education
  material, landing-page copy, and SNS drafts;
- promotional asset source material for PDF, PPTX, image, and web exports;
- channel experiment plans for early external users.

Sales/Revenue is separate and should not be folded into Marketing Growth. Create
or activate a Sales/Revenue lane only after Business Plan v1 defines pricing,
pilot flow, CRM/support needs, and conversion responsibilities.

Current follow-up taskset:

- `TASKSET-MARKETING-TEAM-OPERATING-SYSTEM` is complete as the plan-based
  local operating lane for the marketing team. TASK-166 through TASK-170 are
  complete. These are local planning and readiness tasks only; they do not
  approve live publication, customer contact, final PDF/PPTX export,
  CRM/payment, OAuth, external account action, or platform API calls.

Compliance Officer reviews any investment, performance, tax, legal, financial
service, or regulatory-adjacent claim. Owner approves any public posting, paid
campaign, customer contact, or external account action.

Routing note:

- Use `@compliance` or `@co` when marketing copy touches investment advice,
  paid signal, model portfolio, automated trading, KIS commercial use, tax/legal
  wording, regulatory wording, public paid launch, or performance claims.
- Compliance review classifies draft claims; it is not legal clearance or
  publication approval.

## Upstream Dependency Map

| Input | Owner | Marketing use | Gate |
|-------|-------|---------------|------|
| Vision, target user, product boundary | Business Planner | Positioning, audience, first promise | Use only current `BUSINESS-PLAN.md` sections. |
| Business registration/admin posture | Regulatory Admin | Admin-readiness wording and launch caveats | Do not claim registration, permits, or compliance before confirmation. |
| Recommendation/signal/legal boundary | Compliance Officer | Claim review and banned-claim list | No public investment-advice, paid-signal, performance, tax, or legal claim before review. |
| Channel policy and external account action | Marketing Growth + Owner | SNS/blog/email/landing-page drafts | Draft-only unless Owner approves live posting or customer contact. |

Marketing artifacts must be downstream from the business plan. If the business
plan changes, campaign copy must be refreshed before use.

## TASK-093 Input Status

Business Plan v1 Owner answers have been recorded. Marketing Materials v1 now
exists as a draft source packet, not publication approval:

- Use `verified signup request` as the working CTA.
- For paid pilot, the signup flow may show price and bank-transfer instructions
  to selected applicants. Public marketing material must not commit real bank
  account numbers or private payment identifiers to the repo.
- Treat the claim bank and `MARKETING-MATERIALS-V1` as draft-safe, not
  publication-approved.
- Do not create final PDF/PPTX, landing-page, SNS, or sales material unless the
  Owner and Compliance Officer approve the claim boundary.
- Keep Sales/Revenue inactive until paid conversion, CRM/customer-record needs,
  or non-acquaintance lead flow emerges.

Current safe marketing frame:

- Autofolio is a verified-membership, user-controlled investing workflow web
  service.
- It emphasizes safety guards first, then portfolio visibility, workflow, and
  live-readiness.
- Users connect their own LLM/SNS accounts or tokens where integrations are
  enabled. Autofolio provides agent personalities, harness behavior, workflow,
  logs, and safety gates.
- It must not be framed as a broker, asset manager, robo-advisor, packaged paid
  signal service, guaranteed-profit system, or hands-free account operator.

## Primary Audience

Initial audience:

- Acquaintances and selected Korean individual investors who want a structured
  personal investing workflow and are comfortable managing their own broker/API
  keys, LLM tokens, SNS accounts, settings, approvals, and risk responsibility.

Early-user hypothesis:

- They already use broker apps, spreadsheets, notes, alerts, and AI prompts, but
  lack one auditable workflow for portfolio visibility, risk checks, agent
  summaries, and explicit approvals.

Out of scope for initial marketing:

- managed investment service buyers;
- users seeking guaranteed profit;
- users who want Autofolio to operate their account without supervision;
- paid signal or strategy-pack buyers until regulatory review clears that path.

## Positioning Draft

Autofolio is an invitation-only investing workflow web service that connects
safety guards, portfolio visibility, agent recommendation flows, explicit
approvals, and user-owned account/token integrations.

Short version:

Autofolio helps selected users run agent-assisted investing workflows without
handing over trading authority.

## Claim Bank

Allowed as draft:

- user-controlled investing workflow
- auditable operating records
- explicit approvals before live action
- risk gates and safety defaults
- portfolio visibility
- agent-assisted summaries
- user-owned LLM/SNS token integrations
- verified-person account approval
- manual or code-assisted bank-transfer confirmation
- agent personalities and harness-provided workflows
- mock/paper-first verification
- free or low-price pilot, if pricing remains internal and non-public

Needs Compliance Officer review before use:

- comparison with licensed advisors, brokers, robo-advisors, or signal services;
- tax, legal, regulatory, or investment-outcome claims;
- any statement about fully automated live trading for other users;
- any paid recommendation, strategy pack, ranking, signal, model portfolio, or
  personalized investment-advice wording.

Do not use:

- guaranteed returns
- profit promises
- "AI selects winning stocks"
- "hands-free wealth management"
- "investment advice" unless the regulatory position intentionally changes
- "safe returns" or "risk-free"
- "broker" or "asset manager" as Autofolio identity

## Channel Strategy

| Channel | Status | First use | Gate |
|---------|--------|-----------|------|
| Private pilot explainer | draft | Explain the workflow to selected acquaintances / early users | Business Plan v1 + claim review |
| Owner blog/dev log | draft | Build credibility around workflow, safety, and auditability | Marketing Growth + Compliance review |
| Landing page | later | Verified signup request with approval-pending state | Pricing/payment/support/privacy/refund boundary |
| PDF one-pager | draft source | Shareable early-user explainer after review | TASK-095 |
| PPTX pitch deck | draft source | Partner, pilot, or investor conversations after review | TASK-095 |
| SNS posts | draft only | Awareness and learning-in-public | TASK-129 policy matrix + TASK-096 approval queue |
| Paid ads | blocked | Not an early lane | Approved claims + business/admin setup |
| Mass messaging | rejected | Do not build | Spam/compliance/platform risk |

## Promotional Asset Pipeline

Canonical source:

- `BUSINESS-PLAN.md` for product and business facts;
- this `MARKETING-BRIEF.md` for claim and campaign policy;
- campaign YAML/Markdown for each asset set.

Generation direction:

1. Draft campaign brief in Markdown/YAML.
2. Render human-reviewable copy preview.
3. Use `PROMOTION-ASSET-RENDERING-CONTRACT` before any PDF/PPTX/landing/SNS
   rendering work. The contract is source/hash/review/boundary metadata only.
4. Generate PDF one-pager and PPTX deck only from an approved source in a
   later Owner/R3 lane.
5. Generate SNS draft bundle with per-channel text variants.
6. Keep all live posting actions out of v1; TASK-129 supplies the policy
   matrix plus stricter publishing policy packet, TASK-130 supplies the local
   state machine, TASK-131 supplies the no-network dry-run preview, and
   TASK-169 supplies the SNS publishing automation readiness backlog.
   TASK-096 local design/preview scope is complete; live publishing still
   requires Owner/R3 approval and a separate live implementation lane.

Generated assets should be reproducible and should not contain secrets,
customer data, account credentials, or private runtime state.

## TASK-095 Marketing Materials V1 Draft Packet

`TASK-095` is complete as a draft-source task. The canonical packet is:

- `agents/project/MARKETING-MATERIALS-V1.json`
- `agents/project/MARKETING-MATERIALS-V1.md`

Included draft sources:

- early-user campaign brief;
- landing-page copy;
- PDF one-pager source;
- PPTX deck source;
- SNS draft bundle;
- support FAQ;
- disclaimer draft;
- claim review map.

Validation:

```powershell
python scripts/marketing_materials_gate.py --check
python -m pytest tests/unit/test_marketing_materials_gate.py -q
```

Publication boundary:

- No public post, paid ad, customer contact, external account action, SNS upload,
  or final PDF/PPTX export is approved by this packet.
- Recommendation, pricing, KIS commercial use, provider token, payment,
  refund, privacy, and support wording still requires the relevant review before
  use.

## TASK-129 Promotion Channel Policy Matrix

`TASK-129` is complete as a research-only channel policy packet. The canonical
packets are:

- `agents/project/PROMOTION-CHANNEL-POLICY-MATRIX.json`
- `agents/project/PROMOTION-CHANNEL-POLICY-MATRIX.md`
- `agents/project/PROMOTION-PUBLISHING-POLICY-PACKET.json`
- `agents/project/PROMOTION-PUBLISHING-POLICY-PACKET.md`
- `agents/research_agent/notes/EVIDENCE-2026-06-19-008-promotion-channel-policy.md`

Channel classifications:

- Owner blog/dev log: manual export candidate, not approved for publication.
- X: future approval-queue candidate after Owner developer setup, current auth
  scope review, policy review, and Compliance Officer copy review.
- LinkedIn: future approval-queue candidate after Owner profile/page choice,
  permission/page role review, and current API-version check.
- Instagram: defer live API publishing until account type, media requirements,
  permissions, app review, and deletion behavior are proven.
- Naver Blog: manual-only; automated write API is treated as unsupported.
- Telegram, KakaoTalk, Naver Cafe, Naver Share, and Google Business Profile:
  policy-reviewed candidates only; live use requires Owner/R3 account, consent,
  credential, or business-profile decisions as applicable.

Validation:

```powershell
python scripts/promotion_channel_policy_gate.py --check
python -m pytest tests/unit/test_promotion_channel_policy_gate.py -q
python scripts/promotion_publishing_policy_gate.py --check
python -m pytest tests/unit/test_promotion_publishing_policy_gate.py -q
```

Publication boundary:

- TASK-129 does not approve live posting, OAuth, external API upload, account
  login, paid ads, customer contact, browser automation, lead scraping, or
  public financial/performance/recommendation claims.
- TASK-130 completed the local state-machine contract; TASK-131 completed the
  dry-run audit preview generation.

## TASK-130 Promotion Publishing State Machine

`TASK-130` is complete as a local approval-queue state-machine contract. The
canonical contract is:

- `agents/project/PROMOTION-PUBLISHING-STATE-MACHINE.json`
- `agents/project/PROMOTION-PUBLISHING-STATE-MACHINE.md`

State model:

- `draft_created`
- `copy_review`
- `compliance_review_required`
- `owner_review_required`
- `approved_for_manual_export`
- `dry_run_scheduled`
- `live_recorded_after_owner_action`
- `blocked`
- `withdrawn_or_archived`

Important boundary:

- `live_recorded_after_owner_action` is record-only and terminal. It records a
  publication that the Owner performed outside automation; it never triggers
  platform publication.
- Every transition has `live_action: false`.

Validation:

```powershell
python scripts/promotion_publishing_state_machine_gate.py --check
python -m pytest tests/unit/test_promotion_publishing_state_machine_gate.py -q
```

## TASK-131 Promotion Dry-run Audit Preview

`TASK-131` is complete as the no-Owner local dry-run preview slice for
`TASK-096`.

Canonical preview:

- `agents/project/PROMOTION-DRY-RUN-AUDIT-PREVIEW.json`
- `agents/project/PROMOTION-DRY-RUN-AUDIT-PREVIEW.md`
- `scripts/promotion_dry_run_audit_preview_gate.py`
- `tests/unit/test_promotion_dry_run_audit_preview_gate.py`

Result:

- Preview uses source hashes from `MARKETING-MATERIALS-V1`,
  `PROMOTION-CHANNEL-POLICY-MATRIX`, `PROMOTION-PUBLISHING-POLICY-PACKET`, and
  `PROMOTION-PUBLISHING-STATE-MACHINE`.
- Preview record uses `owner_blog_manual`, `dry_run_scheduled`,
  `local_preview_only`, `not_scheduled`, `external_network_calls=false`, and
  `external_action_enabled=false`.
- Gate rejects source hash mismatch, external network calls, token/customer
  fields, missing Owner boundary, forbidden copy phrases, and unknown channels.

Validation:

```powershell
python scripts/promotion_dry_run_audit_preview_gate.py --check
python -m pytest tests/unit/test_promotion_dry_run_audit_preview_gate.py -q
```

Boundary:

- No live post, OAuth, external API call, token handling, customer contact,
  paid ads, browser automation, generated public asset export, KIS/order/risk/
  prod, or deploy changes.

## TASK-132 Promotion Asset Rendering Contract

`TASK-132` is complete as the no-Owner local contract slice for future
PDF/PPTX/landing/SNS asset rendering foundations.

Canonical contract:

- `agents/project/PROMOTION-ASSET-RENDERING-CONTRACT.json`
- `agents/project/PROMOTION-ASSET-RENDERING-CONTRACT.md`
- `scripts/promotion_asset_rendering_contract_gate.py`
- `tests/unit/test_promotion_asset_rendering_contract_gate.py`

Result:

- The contract records source hashes for `MARKETING-MATERIALS-V1.json`, this
  marketing brief, and `SALES-REVENUE-LANE-DECISION.json`.
- Render targets are landing page source, PDF one-pager source, PPTX deck
  source, and SNS text bundle source.
- Every target remains `local_preview_source_only`; final PDF/PPTX export,
  binary generation, public URL/upload, SNS upload, customer contact, CRM,
  payment, secrets, KIS/order/risk/prod, and deploy changes are blocked.
- `TASK-133` completed the local preview manifest slice.

Validation:

```powershell
python scripts/promotion_asset_rendering_contract_gate.py --check
python -m pytest tests/unit/test_promotion_asset_rendering_contract_gate.py -q
```

Boundary:

- No renderer implementation, final PDF/PPTX binary, public landing page,
  SNS upload, customer contact, CRM/payment record, external account action,
  secret, KIS/order/risk/prod, or deploy change.

## TASK-133 Promotion Asset Preview Manifest

`TASK-133` is complete as the no-Owner local preview-manifest slice for landing,
PDF, PPTX, and SNS asset sources.

Canonical manifest:

- `agents/project/PROMOTION-ASSET-PREVIEW-MANIFEST.json`
- `agents/project/PROMOTION-ASSET-PREVIEW-MANIFEST.md`
- `scripts/promotion_asset_preview_manifest_gate.py`
- `tests/unit/test_promotion_asset_preview_manifest_gate.py`

Result:

- The manifest records source hashes for `PROMOTION-ASSET-RENDERING-CONTRACT`
  and `MARKETING-MATERIALS-V1`.
- Preview targets are landing page source, PDF one-pager source, PPTX deck
  source, and SNS text bundle source.
- Every preview remains `local_preview_source_only`; final PDF/PPTX export,
  public URL/upload, SNS upload, customer contact, CRM/payment, secrets,
  KIS/order/risk/prod, and deploy changes are blocked.
- `TASKSET-MARKETING-ASSET-RENDERING-FOUNDATION` is complete.
- The downstream claim-review / owner-review chain is deferred to a separate
  lane and is not part of this branch.

## TASKSET-MARKETING-TEAM-OPERATING-SYSTEM

This taskset is complete as the plan-based follow-up lane for the marketing
team. It does not replace the completed Marketing Growth plan; it makes the
next work queue explicit. TASK-166 through TASK-170 are complete as local
planning and readiness work.

Included tasks:

- `TASK-166` Marketing Team Operating Model - complete
- `TASK-167` Promotion Campaign Backlog And Content Calendar V1 - complete
- `TASK-168` Promotion Asset Generator Readiness Map - complete
- `TASK-169` SNS Publishing Automation Readiness Backlog - complete
- `TASK-170` Sales Handoff Readiness Checklist - complete

TASK-168 canonical map:

- `agents/project/PROMOTION-ASSET-GENERATOR-READINESS-MAP.json`
- `agents/project/PROMOTION-ASSET-GENERATOR-READINESS-MAP.md`
- `scripts/promotion_asset_generator_readiness_map_gate.py`
- `tests/unit/test_promotion_asset_generator_readiness_map_gate.py`

TASK-169 canonical backlog:

- `agents/project/SNS-PUBLISHING-AUTOMATION-READINESS-BACKLOG.json`
- `agents/project/SNS-PUBLISHING-AUTOMATION-READINESS-BACKLOG.md`
- `scripts/sns_publishing_automation_readiness_backlog_gate.py`
- `tests/unit/test_sns_publishing_automation_readiness_backlog_gate.py`

Use this taskset when the request is about making the marketing agents more
operational, preparing repeatable campaigns, preparing PDF/PPTX generation,
planning SNS automation, or separating marketing from future sales work.

Boundary:

- All included tasks are local planning/readiness work. Public posting, paid
  ads, customer contact, CRM/customer records, payment requests, external
  account actions, OAuth, token handling, platform API calls, public URLs, final
  PDF/PPTX binary export, and final legal/tax/securities advice remain blocked
  until a separate approved lane exists.

Validation:

```powershell
python scripts/promotion_asset_preview_manifest_gate.py --check
python -m pytest tests/unit/test_promotion_asset_preview_manifest_gate.py -q
python scripts/promotion_campaign_backlog_calendar_gate.py --check
python -m pytest tests/unit/test_promotion_campaign_backlog_calendar_gate.py -q
python scripts/promotion_asset_generator_readiness_map_gate.py --check
python -m pytest tests/unit/test_promotion_asset_generator_readiness_map_gate.py -q
python scripts/sns_publishing_automation_readiness_backlog_gate.py --check
python -m pytest tests/unit/test_sns_publishing_automation_readiness_backlog_gate.py -q
```

Boundary:

- No final PDF/PPTX binary, public landing page, SNS upload, customer contact,
  CRM/payment record, external account action, secret, legal/tax/securities
  final advice, KIS/order/risk/prod, or deploy change.

## Campaign Brief Template

Each campaign brief must include:

| Field | Meaning |
|-------|---------|
| campaign_id | Stable ID such as `MKT-YYYY-MM-DD-NNN`. |
| audience | Early-user segment and exclusion notes. |
| promise | One supported, reviewable promise. |
| proof | Product evidence, screenshots, docs, or demo flow that supports the promise. |
| channel | Blog, landing page, PDF, PPTX, X, LinkedIn, Naver, etc. |
| CTA | Verified signup request, approval-pending account request, deposit-pending account request, demo request, or follow-up action. |
| claim_review | draft, compliance-review, owner-review, approved, rejected. |
| publishing_mode | manual-export, approval-queue, or blocked. |
| rollback | How to withdraw, correct, or archive the campaign. |

## Review And Publishing Gates

Drafting:

- Marketing Growth may draft copy, channel plans, PDF/PPTX source, and SNS text.
- Business Planner checks alignment with Business Plan v1.
- Compliance Officer checks prohibited investment/performance/legal claims.
- QA or Doc Steward checks reproducibility and source traceability for generated
  files.

Publishing:

- Manual export is allowed only after claim review.
- Any public post, paid campaign, customer email, API upload, external account
  change, or scheduled publication requires Owner approval.
- Automated posting is roadmap-only. TASK-129 has completed the channel policy
  matrix, TASK-130 has completed the local state-machine contract, TASK-131 has
  completed the dry-run audit preview, and TASK-169 has completed the SNS
  publishing automation readiness backlog. TASK-096 local design/preview scope
  is complete, but any live path still requires Owner/R3 approval, refreshed
  platform review, credential/secret handling design, and separate
  implementation.

Prohibited automation:

- viewbots;
- fake traffic or engagement;
- spam or unauthorized bulk posting;
- ToS evasion;
- platform manipulation;
- unsourced lead scraping;
- public posting of investment advice, performance guarantees, or secret data.

## Sales Handoff

Marketing-to-sales handoff is not active yet. `TASK-097` closed the current
decision as "defer Sales/Revenue role activation."

Canonical decision:

- `agents/project/SALES-REVENUE-LANE-DECISION.json`
- `agents/project/SALES-REVENUE-LANE-DECISION.md`
- `scripts/sales_revenue_lane_decision_gate.py`

Sales/Revenue becomes its own lane when these inputs exist:

- Business Plan v1 chooses pricing and first paid product form;
- pilot intake and qualification questions are known;
- support/refund scope is defined;
- CRM or customer record policy is defined;
- Compliance Officer confirms the sale does not imply investment advice,
  discretionary management, or paid signal service unless intentionally cleared.

Until then, Marketing Growth may produce awareness and early-user education
material, but should not own pricing, customer contracting, payment collection,
or conversion pipeline operations.

TASK-097 decision:

- Do not create or activate `sales-revenue` now.
- Keep customer contact, CRM/customer-record system activation, payment request,
  support/refund finalization, public sales copy approval, paid ads, and billing
  setup behind Owner/R3.
- Future role contract is documented only as a candidate; no role registry,
  worker alias, external account, CRM, payment, customer data, or outreach path
  was created.

## Next Tasks

- TASK-093: finalize Business Plan v1 inputs for target user, pricing, support,
  and GTM boundary.
- TASK-095: completed draft-only Marketing Materials v1 from current
  business-plan inputs.
- TASK-096: completed safe Promotion Publishing Pipeline local design/preview
  scope; live publishing remains Owner/R3.
- TASK-097: completed Sales/Revenue lane decision; role activation is deferred.
- TASK-128: completed Compliance Officer routing alignment for business/admin/
  marketing claim review.
- TASK-129: completed official-source channel policy matrix and publishing
  policy packet for future promotion publishing.
- TASK-130: completed local promotion publishing state-machine contract.
- TASK-131: completed no-network dry-run audit preview slice.
- TASK-132: completed local promotion asset rendering contract.
- TASK-133: completed local promotion asset preview manifest.
- TASK-168: completed local promotion asset generator readiness map.
- TASK-169: completed local SNS publishing automation readiness backlog.
- TASKSET-MARKETING-GROWTH: completed.
- TASKSET-MARKETING-TEAM-OPERATING-SYSTEM: completed.
- TASKSET-MARKETING-ASSET-RENDERING-FOUNDATION: completed.
- The downstream claim-review / owner-review / decision-queue chain is deferred
  to a separate lane and is not part of this branch; no public approval, final
  advice, export, publication, customer contact, CRM/payment, external account
  action, OAuth, or platform API action is approved.
