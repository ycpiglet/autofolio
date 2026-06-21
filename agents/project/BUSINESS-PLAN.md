# Autofolio Business Plan

Status: v1-owner-answered
Owner: Business Planner
Last updated: 2026-06-19T23:32:08+09:00
Related tasks: TASK-092, TASK-093, TASK-094, TASK-095, TASK-096, TASK-097

## Purpose

This document is the living business-plan source of truth for Autofolio. It is
used to align agents on the vision, product boundary, business model,
regulatory/admin preparation, and future marketing material.

## TASK-093 Work State

Current business question:

- Can Autofolio be offered as a subscription web service for selected invited
  users while keeping broker, LLM, and SNS authority under each user's own
  account/token boundary?

Current working answer:

- Draft Business Plan v1 around a membership-gated subscription web service.
- Start with acquaintances / selected users, not broad public signup.
- Prioritize the product promise as safety guards first, then portfolio
  visibility, then workflow, then live trading readiness.
- Include agent recommendation flows, but frame them as user-owned LLM/SNS token
  integrations and agent-harness behavior. Public claims about recommendations,
  signals, model portfolios, or investment advice require Compliance Officer
  and professional/regulator review before sale or marketing.

## Current Position

Confirmed:

- Autofolio is currently a personal KIS-based automated trading operating system.
- Safety policy remains mock/paper-first, automatic trading OFF by default, and
  human approval for real orders.
- The v1 paid direction is a membership-gated web service for selected users.
- Membership approval is not self-serve. The Owner approves only verified people.
- Users bring and control their own broker/API credentials, LLM tokens, SNS
  accounts, settings, approvals, and account responsibility.
- Autofolio provides the agent personalities, harness, workflow, safety gates,
  audit trail, and integration surface.

Hypothesis:

- The safest commercial positioning is "user-controlled investing workflow
  service" and not discretionary management, broker service, asset management,
  or hands-free account operation.
- Business registration, e-commerce/admin filings, and document automation will
  be needed before real sales.
- Agent recommendations can be a product feature, but recommendation wording,
  paid signal implications, model portfolio behavior, and user-specific advice
  claims need Compliance Officer and professional/regulator review.

Owner decisions needed:

- Personal business vs corporation.
- Exact business name, 업태/업종, business address, payment/refund policy, and
  support policy.
- Exact invite flow, verified-person approval rules, bank-transfer account
  display policy, deposit-code matching, and manual approval workflow.
- Whether recommendation features remain user-prompted agent output only or
  later become packaged signals/strategies.

## Vision

Autofolio should help an individual investor operate a disciplined, auditable,
agent-assisted investment workflow while keeping keys, decisions, approvals, and
risk responsibility under the user's control.

## Problem

Individual investors often combine broker apps, notes, spreadsheets, alerts,
manual order checks, and ad hoc AI prompts. The result is fragmented context,
weak auditability, inconsistent risk controls, and poor handoff between research,
decision, execution, and review.

## Proposed Solution

Autofolio provides a local or user-owned web workspace that connects portfolio
state, risk gates, investor profile, paper/live verification, agent summaries,
and documentation into one operating loop.

Non-negotiable boundary:

- Autofolio should not place real orders without user-controlled settings,
  explicit approvals, and active safety gates.
- Any feature that becomes recommendation, paid signal, automated discretionary
  management, or public investment advice requires Compliance Officer review and
  professional/regulator confirmation before sale.

## Target Users

Primary v1 segment:

- Acquaintances and selected Korean individual investors who can manage their
  own brokerage credentials, LLM tokens, SNS accounts, and investment decisions.

Secondary future segments:

- Power users who want local automation and reporting.
- Small investment study groups, only if legal/community boundaries are cleared.

## Value Proposition

Draft:

Autofolio helps selected users run a safer personal investing workflow by
combining safety guards, portfolio visibility, agent-assisted recommendations,
traceable approvals, and user-owned account/token integrations.

Do not use yet:

- "Guaranteed returns"
- "AI will pick winning stocks"
- "Fully automatic profit system"
- "Investment advisory service" unless the regulatory position changes

## Business Model Options

| Option | Status | Notes |
|--------|--------|-------|
| Subscription web service | selected for v1 | Requires verified-person membership approval, account gating, billing, support, cancellation, privacy, and terms operations. |
| Free private pilot | selected pre-paid step | Useful before payment and refund policy are ready. |
| Low-price paid pilot around KRW 20,000 | selected hypothesis | Treat as an introductory subscription price, subject to final payment/support/refund decisions. |
| Setup/support service | later candidate | May fit early users, but support scope must avoid investment advice unless licensed. |
| One-time software license | not v1 | Lower priority than the web-service direction. |
| Managed portfolio / packaged paid signal | blocked | Treat as regulatory review required before planning or marketing. |

## Go-To-Market

Draft sequence:

1. Owner-operated personal product maturity.
2. Invite acquaintances / selected users into a gated web-service pilot.
3. Use only approved safety-guard, portfolio-visibility, workflow, and
   user-owned integration claims.
4. Run free or low-price pilot before broad paid signup.
5. Move to paid subscription only after KIS terms, business registration,
   payment, refund, privacy, and investment-advice boundaries are cleared.
6. Public marketing only after the claim bank is approved in
   `agents/project/MARKETING-BRIEF.md`.

Marketing/sales split:

- Marketing Growth owns early-user positioning, campaign briefs, landing copy,
  PDF/PPTX source, and SNS drafts.
- Sales/Revenue should be a separate later lane for pricing, CRM, demos, lead
  qualification, conversion, support handoff, and retention after Business Plan
  v1 clarifies the paid product.
- External publishing and customer contact stay Owner-approved until explicit
  workflow and compliance gates exist.

TASK-097 Sales/Revenue decision:

- Sales/Revenue role creation is deferred for now.
- The future `sales-revenue` role is only a candidate contract in
  `SALES-REVENUE-LANE-DECISION`.
- Activate it only after support/refund policy, privacy/customer-record policy,
  payment/receipt policy, CRM/no-CRM decision, Compliance Officer sales-claim
  review, customer-contact workflow Owner approval, and paid-offer admin posture
  exist.
- Until then, Marketing Growth may draft no-contact educational material but
  must not own customer contracting, CRM, payment collection, sales outreach, or
  retention operations.

## Business Plan V1 Draft Packet

This packet is the current TASK-093 working draft. It separates confirmed facts,
safe assumptions, and decisions that still need the Owner.

### Confirmed Facts

| Area | Confirmed input |
|------|-----------------|
| Product origin | Autofolio started as a personal KIS-based automated trading operating system. |
| Current safety posture | Mock/paper-first, automatic trading OFF by default, kill switch, explicit human approval for real orders. |
| Current UI/product surface | Next.js + FastAPI product with portfolio, investor profile, manuals, safety acknowledgement, and KIS/paper workflow support. |
| Business lane | Business Planner, Regulatory Admin, and Marketing Growth roles exist as repo-visible planning surfaces. |
| Marketing boundary | Public posting, paid ads, customer contact, external account actions, and live publishing are Owner-approved gates. |

### Working Hypotheses

| Hypothesis | Why it is useful | Current risk |
|------------|------------------|--------------|
| Start as selected-user subscription web service, not public SaaS. | Matches the Owner's membership-gated web-service direction. | Requires auth, membership approval, privacy, support, and payment operations. |
| Let users connect their own LLM/SNS/broker-related accounts and tokens. | Keeps authority and usage cost under the user's account boundary. | Requires secret handling, OAuth/token UX, provider policy review, and clear data handling terms. |
| Agent recommendation can be included as a user-controlled workspace feature. | Provides the core perceived value beyond dashboarding. | Recommendation/signal/advice claims can trigger financial-service review. |
| Start with acquaintances and selected users. | Keeps feedback loop tight and reduces compliance/support blast radius. | Requires clear invitation, disclaimer, support policy, and privacy terms. |

### Product Form Options

| Option | V1 recommendation | Notes |
|--------|-------------------|-------|
| Membership-gated web subscription | Selected | Account holders only; verified-person signup approval; user-owned LLM/SNS tokens and accounts. |
| Free pilot | Selected first step | Good while support, refund, and compliance boundaries are being validated. |
| Low-price paid pilot around KRW 20,000 | Selected pricing hypothesis | Use only after payment/refund/support terms are ready. |
| Local/user-owned software license | Not v1 | Possible future packaging, but not the current web-service direction. |
| Setup/support service | Later add-on | Must avoid investment advice and trading decisions unless licensed/cleared. |
| Packaged paid signals/strategy packs | Blocked for v1 | Agent recommendations may exist, but packaged signals/strategies require compliance review. |
| Managed trading/operation on behalf of users | Rejected for v1 | Crosses the wrong boundary for the current product and risk posture. |

### First Offer Draft

Safe draft offer:

- Invite-only web service for acquaintances / selected users who want safety
  guards, portfolio visibility, workflow, and later live-readiness around their
  own investing account.
- Signup is approved only after the Owner verifies the person and, for a paid
  pilot, confirms a bank-transfer deposit manually or through a deposit code
  recognition workflow.
- Users connect or provide their own LLM/SNS account or token where integrations
  are enabled. Autofolio provides agent personalities, harness behavior,
  workflow, logs, and safety gates.
- The pilot may include agent recommendation flows, but users remain responsible
  for final decisions and approvals.
- It does not promise profit, winning-stock selection, legal/tax/investment
  advice, managed execution, or hands-free account operation.

Verified signup / payment approval interpretation:

- The previous CTA question meant "what action should a prospective user take
  first?" The Owner clarified that v1 should not be open signup or ordinary
  waitlist/demo flow.
- v1 CTA is now `verified signup request`.
- The service may show a price and bank-transfer instructions to selected
  applicants, but final activation happens only after the Owner verifies the
  person and confirms payment.
- Payment confirmation starts manual: Owner checks the bank app/admin evidence
  and approves the account.
- Later automation may recognize deposits by unique transfer code, depositor
  name, or amount pattern. That recognition must remain an approval aid unless
  a separate payment/finance workflow promotes it.
- Actual bank account numbers, depositor names, payment identifiers, and private
  payment records must not be committed to the repo. Use placeholders in docs
  and runtime/admin configuration for real values.

### Pricing And Revenue Draft

Do not publish pricing broadly yet. Current pricing should stay internal until
the first pilot promise, support workload, payment policy, and refund policy are
clear.

| Path | Fit | Gate |
|------|-----|------|
| Free private pilot | Selected starting point | Owner verifies people and approves accounts manually. |
| Low-price subscription around KRW 20,000 | Selected paid hypothesis | Requires displayed bank-transfer instructions, manual or code-based deposit confirmation, receipt/refund/privacy/cancellation terms. |
| Subscription | Selected model | Requires verified membership, billing, privacy, cancellation, support ops, and account approval logs. |
| Setup/support package | Practical early add-on | Must avoid investment advice and trading decisions. |

### Early-User GTM

Sequence:

1. Build as a gated web service with account-based access.
2. Accept only verified people, starting with acquaintances / selected users.
3. Lead with safety guards, then portfolio visibility, then workflow, then live
   readiness.
4. For paid pilot, show price and bank-transfer instructions only in the
   controlled signup/approval flow, not as broad public checkout.
5. Owner manually confirms deposit first; code-based recognition is a later
   approval aid.
6. Use Marketing Materials v1 draft source from the current claim bank.
7. Use manual-export PDF/PPTX/blog/dev-log material for private review.
8. Collect account requests only after privacy/support/refund/payment boundaries are clear.
9. Consider approval-queued publishing only after channel policy/API research.

### Owner Decision List

Owner answers recorded on 2026-06-19:

| Question | Owner answer | Business-plan interpretation |
|----------|--------------|------------------------------|
| First product form | 구독 | Membership-gated web subscription. |
| First external audience | 지인 | Start with acquaintances / selected invited users. |
| First promise priority | 안정장치 > 포트폴리오 > 워크플로 > live | Lead with safety guards, then portfolio visibility, then workflow, then live-readiness. |
| Recommendation/signal inclusion | 포함 | Include agent recommendation flows, but keep user approval and compliance/professional review gates. |
| CTA | 검증된 사람만 회원가입 승인. 무통장입금 계좌번호/가격 안내 후 수동 입금 확인 또는 코드 인식으로 승인. | Verified signup request -> bank-transfer instructions -> Owner/manual or code-assisted deposit confirmation -> account activation. |
| Support/product scope | 웹 서비스, 선별 회원가입, account holders only, SNS/LLM own-token integration, agent recommendation via user's accounts/tokens | Build gated web service; users bring own accounts/tokens; Autofolio provides agent personalities, harness, workflow, safety gates. |
| Pricing posture | 무료 or 2만원 정도 저가 | Start free or low-price pilot around KRW 20,000 subscription hypothesis. |
| Sales lane trigger | 질문이 이해 안 됨 | Interpreted as no separate Sales lane now; revisit after paid conversion, CRM/customer-record need, or non-acquaintance lead flow emerges. |

### Professional Review Required

| Topic | Required review |
|-------|-----------------|
| KIS commercial/multi-user use | KIS terms/legal review before paid deployment. |
| Agent recommendations / robo-advisor / paid signals | Compliance Officer plus professional/regulator review before public claim or paid launch. |
| User-owned LLM/SNS token integrations | Provider policy, privacy, secret handling, and account-authorization review. |
| Bank-transfer deposit approval | Payment/refund/receipt/tax handling, account-number display policy, deposit-code matching, and admin audit log review. |
| Business registration and tax treatment | Tax accountant or relevant official guidance before filing. |
| Privacy, terms, refund, support policy | Legal/professional review before collecting customer data or payment. |

### Agent Context Summary

Autofolio should be described internally as a verified-membership,
user-controlled investing workflow web service. The v1 product model is
subscription-oriented and starts with acquaintances / selected users. Signup is
not open self-serve: the Owner verifies the person, optionally checks a
bank-transfer deposit manually or with a code-assisted recognition workflow, and
then approves the account. Users bring their own broker, LLM, and SNS accounts
or tokens. Autofolio provides the agent personalities, harness, workflow, safety
gates, audit trail, portfolio visibility, and integration surface.

Downstream agents may draft product material around safety guards, portfolio
visibility, workflow, and user-owned agent recommendation flows. They must not
market Autofolio as a broker, asset manager, robo-advisor, guaranteed-profit
system, packaged paid signal service, or hands-free trading operator unless a
later compliance task explicitly changes that boundary.

### Agent Operating Map

| Stage | Lead role | Source file | Output | Gate |
|-------|-----------|-------------|--------|------|
| Vision and business model | Business Planner | `BUSINESS-PLAN.md` | Business plan section, Owner decision list, downstream context summary | No legal/tax/securities final advice; no product/KIS/order/risk mutation. |
| Admin and formal document prep | Regulatory Admin | `BUSINESS-ADMIN-REGISTER.md` | Official-source checklist, owner-data field map, document packet plan, HWPX/DOCX/PDF draft plan | Owner performs login, signature, payment, upload, and submission. |
| Financial-service boundary | Compliance Officer | `BUSINESS-PLAN.md`, `BUSINESS-ADMIN-REGISTER.md`, product evidence | Watch list and review flags for recommendation, signal, robo-advisor, and managed-operation claims | Professional/regulator confirmation before public sale or claim. |
| Marketing derivation | Marketing Growth | `MARKETING-BRIEF.md` | Claim bank, banned-claim list, campaign brief, landing/PDF/PPTX/SNS draft source | Owner approval for any public post, paid ad, customer contact, or external-account action. |

The intended flow is Business Planner first, Regulatory Admin and Compliance
Officer for formal/business-risk boundaries, then Marketing Growth for copy and
assets derived only from approved plan sections.

## Operations

Needed before formal sale:

- Business registration path and business type decision.
- Payment/receipt/refund policy.
- Bank-transfer account display policy, unique deposit code policy, and manual
  approval audit log.
- Privacy policy and user data handling policy.
- Terms of service and investment-risk disclosure.
- Customer support and incident response process.
- Document-packet generation workflow for official forms and applications.

## TASK-095 Result

`TASK-095` completed `MARKETING-MATERIALS-V1.json` and
`MARKETING-MATERIALS-V1.md` as draft-only source material for landing copy, PDF,
PPTX, SNS drafts, support FAQ, and disclaimer text.

This does not approve public publication, final PDF/PPTX export, customer
contact, paid ads, external account action, recommendation/performance/KIS
commercial-use claims, or SNS upload. Those remain review/Owner-gated.

`TASK-132` completed `PROMOTION-ASSET-RENDERING-CONTRACT.json` and `.md` as a
local-only source/hash/review boundary contract for future landing/PDF/PPTX/SNS
asset rendering. It does not implement a renderer, generate final binary files,
publish a public URL, upload to SNS, contact customers, create CRM/payment
records, handle secrets, or change KIS/order/risk/prod/deploy surfaces.

`TASK-133` completed `PROMOTION-ASSET-PREVIEW-MANIFEST.json` and `.md` as a
local-only landing/PDF/PPTX/SNS source preview manifest. Final export, public
use, SNS upload, customer contact, CRM/payment activation, external account
action, and legal/tax/securities reliance remain blocked.

## Evidence And Source Notes

- See `agents/research_agent/notes/EVIDENCE-2026-06-19-003-business-plan-admin-agent-research.md`.
- See `agents/project/BUSINESS-ADMIN-REGISTER.md` for current admin and official-source checklist.
- Latest refresh: 2026-06-19T20:03:18+09:00. Official-source review reconfirmed
  the same structure: NTS/Hometax for business registration, Hancom HWPX docs for
  document generation direction, FSC/FSS/law.go.kr for financial-service watch
  items, and K-Startup/MSS for business-plan/form examples.

## Next Version

TASK-093 should produce Business Plan v1 after an Owner interview covering:

- product form
- target user
- pricing
- legal boundary
- first paid pilot scope
- support/refund policy
- marketing tone
- early-user acquisition channel
- whether marketing should stay education/awareness only or include waitlist and
  demo-request capture
- when Sales/Revenue should become a dedicated role rather than a Marketing
  Growth handoff
