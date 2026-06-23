---
type: evidence
id: EVIDENCE-2026-06-19-003
title: Business plan, admin filing, HWPX, and regulatory role research
created_at: 2026-06-19T00:04:30+09:00
owner: Research Agent
related_task: TASK-092
tags: [business-plan, admin, regulatory, hwpx, marketing, official-sources]
status: pass
redaction: no secrets, identity numbers, certificates, account numbers, broker keys, or production data recorded
---

# Business plan, admin filing, HWPX, and regulatory role research

## Question

What agent/skill surface should Autofolio add so business planning, later formal
business registration/admin documents, HWPX-style document packets, and marketing
materials can be managed from a single business context?

## Sources Checked

Official and primary sources:

- National Tax Service, business registration application procedure:
  https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7777&mi=2444
- National Tax Service, business registration submission documents:
  https://www.nts.go.kr/nts/ad/cntnts/cntntsView.do?mi=2445
- FSC/FSS legal interpretation portal, robo-advisor investment-advice question:
  https://better.fsc.go.kr/fsc_new/replyCase/LawreqDetail.do?lawreqIdx=3790&muGpNo=75&muNo=85&stNo=11
- National Law Information Center, Capital Markets Act:
  https://www.law.go.kr/
- Hancom, HWP/OWPML format:
  https://www.hancom.com/support/downloadCenter/hwpOwpml
- Hancom Tech, HWPX format structure:
  https://tech.hancom.com/hwpxformat/
- K-Startup:
  https://www.k-startup.go.kr/
- Ministry of SMEs and Startups example page with business-plan attachments:
  https://www.mss.go.kr/site/smba/ex/bbs/View.do?bcIdx=1029124&cbIdx=310&parentSeq=1029124

## Findings

1. Business registration and filing requirements are fact-specific.
   NTS guidance separates business-registration procedure from required
   attachments. Required documents vary by individual/corporation, lease status,
   permit-required business, partnership, and other facts.

2. Online filing is plausible but Owner-only.
   NTS guidance describes online business-registration application and electronic
   attachment submission through Hometax when authentication is available. Agents
   can prepare packets, but login, authentication, signing, and submission must
   remain Owner actions.

3. HWPX is the better automation target than binary HWP.
   Hancom describes HWPX as OWPML/XML-based and easier to inspect than binary HWP
   formats. A generator should keep structured data, template fixtures, XML diff,
   and reviewable Markdown/PDF outputs before any Owner submission.

4. Business-plan templates are commonly distributed as HWP/DOCX attachments.
   K-Startup and MSS surfaces show that startup support and application flows
   often use official portals and downloadable business-plan forms. Autofolio
   should keep a business-plan SSoT that can be transformed into forms later.

5. Autofolio has a securities/regulatory boundary.
   A paid product that includes individualized advice, paid signals, robo-advisor
   claims, or operation on behalf of users may require legal/regulatory review.
   A single FSC interpretation about no-separate-fee ancillary bank advice is
   useful context but not blanket clearance for Autofolio.

## Recommendation

Create a business lane with three repo-visible roles:

- Business Planner: owns vision, business model, plan, milestones, and Owner
  decision list.
- Regulatory Admin: owns official-source procedure research, admin checklists,
  legal/regulatory watch list, and document-packet/HWPX planning.
- Marketing Growth: turns approved plan sections into safe marketing briefs and
  claim banks.

Keep Compliance Officer focused on trade/legal/tax gates and involve it for
investment-advice, robo-advisor, public performance, paid signal, or automated
trading-service claims.

## Uncertainties

- Exact business type, 업태/업종, address, opening date, sales model, refund
  policy, and target customer are Owner decisions.
- KIS OpenAPI commercial/multi-user terms still need direct review.
- HWPX generation implementation should wait until the target form and data
  model are selected.

## Refresh — 2026-06-19T20:03:18+09:00

Current-source check:

- NTS business-registration procedure page still supports the register-first or
  within-20-days framing and online Hometax application/electronic attachment
  possibility when the applicant has the required authentication.
- Hometax exposes business-registration application and submission-document
  guidance, but actual application remains an authenticated Owner action.
- Hancom Tech describes HWPX as an OWPML/XML-based ZIP package, so the repo
  should generate HWPX from structured data and fixtures rather than mutate
  binary HWP files.
- MSS/K-Startup surfaces continue to publish startup/business-plan notices and
  attachments as HWPX/PDF-style files; this supports a transform-from-SSoT
  approach.
- FSC materials continue to show robo-advisor and delegated operation as a
  regulated financial-service boundary. Autofolio should keep public
  recommendation, paid signal, model portfolio, and managed-operation claims
  behind Compliance Officer plus professional/regulator review.

Applied repo decision:

- Keep Business Planner, Regulatory Admin, Compliance Officer, and Marketing
  Growth as separate roles.
- Keep `BUSINESS-PLAN.md` as the source for product/vision facts,
  `BUSINESS-ADMIN-REGISTER.md` as the source for official-source admin packets,
  and `MARKETING-BRIEF.md` as the source for claim banks and promotional drafts.
- Do not automate login, certification, official submission, payment, public
  posting, customer contact, or legal/tax/securities final advice from this lane.
