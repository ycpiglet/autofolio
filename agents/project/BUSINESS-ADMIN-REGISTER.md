# Autofolio Business Admin Register

Status: draft
Owner: Regulatory Admin
Last updated: 2026-06-19T22:31:45+09:00
Related tasks: TASK-092, TASK-094, TASK-127

## Purpose

This register tracks administrative, legal/regulatory, tax, and document-packet
work needed before Autofolio is sold or formally operated as a business.

This is not legal, tax, accounting, or securities advice. It is an official-source
checklist and drafting surface. The Owner must review, sign, submit, and obtain
professional confirmation where required.

## Current Official-Source Findings

Refreshed: 2026-06-19T20:03:18+09:00.

Business registration:

- National Tax Service says business registration is generally per business
  place and should be filed before starting or within 20 days after starting,
  with required documents.
- NTS also states Hometax can support online business-registration application
  and electronic attachment submission when the applicant is set up for Hometax
  authentication.
- Required attachments depend on individual/corporation, lease, permit-required
  business type, partnership, and other facts.

Document format:

- Hancom documents HWP/OWPML public format material.
- HWPX is an XML/ZIP-style open document format based on OWPML, which makes it a
  better target for generated form packets than binary HWP mutation.

Financial-service boundary:

- Paid signals, recommendations, investment advice, robo-advisor claims,
  discretionary management, or automated operation on behalf of users may trigger
  securities-law review.
- FSC interpretation distinguishes advice that is not investment advice in a
  specific no-separate-fee bank context, but that is not a blanket clearance for
  Autofolio sales. Treat the boundary as a professional-review gate.

Business-plan and startup-support forms:

- K-Startup and Ministry of SMEs and Startups notices commonly distribute
  application/business-plan attachments as HWPX/PDF files. Autofolio should keep
  internal business facts in Markdown/YAML first, then render target forms only
  after the exact official form is selected.

Online submission boundary:

- Agents may prepare checklists, placeholders, field maps, draft text, and
  generated document files. Owner-only steps remain login/authentication,
  certificate use, signature, payment, upload, final review, and submission.

## Owner Data Required Before Any Form Draft

- Business owner legal name and identity information.
- Business type: individual business, corporation, or other entity.
- Business address and lease/ownership status.
- Opening date.
- Business name.
- Main business activity and Korean 업태/업종 classification.
- Contact information.
- Permit/license needs, if any.
- Payment method, refund policy, and e-commerce sales channel.
- Whether the product contains advice, recommendations, signals, strategy packs,
  or execution automation for other users.

Do not store sensitive identity numbers, certificates, account credentials,
broker keys, or login secrets in the repo.

## Business Plan V1 Admin Input Map

TASK-093 must produce or confirm these non-sensitive business inputs before
TASK-094 can create an admin/HWPX packet prototype:

| Input | Source | Current status |
|-------|--------|----------------|
| First product form | Owner decision in BUSINESS-PLAN.md | subscription web service selected |
| First customer segment | Owner decision in BUSINESS-PLAN.md | acquaintances / selected users |
| First CTA and pilot flow | Owner decision + MARKETING-BRIEF.md | verified signup request -> bank-transfer instructions -> manual/code-assisted deposit confirmation -> account activation |
| Pricing posture | Owner decision | free pilot or low-price subscription around KRW 20,000 |
| Support/refund scope | Owner decision | web-service account access; exact support/refund terms still open |
| Recommendation/signal boundary | Owner + Compliance Officer review | agent recommendation included; compliance/professional review required |
| Business type candidate | Owner decision + professional review | open |
| Target official form or packet | Regulatory Admin after TASK-093 | blocked |

Additional admin implications from Owner answers:

- Membership-gated web service requires account terms, privacy policy,
  membership approval rules, cancellation/deactivation policy, and support
  boundary.
- Verified signup requires an approval state machine: requested, verification
  pending, deposit pending, active, rejected, expired.
- Bank-transfer approval requires displayed account/price instructions,
  placeholder-safe configuration, unique deposit code or depositor matching,
  manual Owner confirmation, activation audit log, and refund/cancellation
  handling.
- User-owned LLM/SNS token integration requires secret handling, OAuth/token
  storage policy, provider policy review, and user data processing disclosure.
- Low-price paid subscription requires payment, receipt, refund, cancellation,
  and customer-support workflow before live collection.
- Agent recommendation wording requires Compliance Officer plus
  professional/regulator review before public marketing or paid launch.

Agent-drafted documents may use placeholders for business facts, but login,
signature, payment, submission, identity details, certificates, and official
filing actions remain Owner-only.

## Document Packet Model

Each admin packet should contain:

| Field | Meaning |
|-------|---------|
| packet_id | Stable ID such as `DOC-PACKET-YYYY-MM-DD-NNN`. |
| procedure | Business registration, e-commerce filing, policy document, etc. |
| source_urls | Official URLs used and checked date. |
| owner_data | Required facts the Owner must provide. |
| generated_files | Draft md/docx/hwpx/pdf paths. |
| owner_only_steps | Login, signature, payment, submission, certificate auth. |
| review_gate | Attorney, tax accountant, FSC/FSS, or other review if needed. |
| status | draft, owner-review, ready-to-submit, submitted-by-owner, archived. |

## TASK-127 Document Packet Schema Foundation

TASK-127 added a reusable, placeholder-safe document packet schema:

- `agents/project/BUSINESS-ADMIN-DOCUMENT-PACKET-SCHEMA.json`
- `agents/project/BUSINESS-ADMIN-DOCUMENT-PACKET-SCHEMA.md`
- `python scripts/business_admin_document_packet_schema_gate.py --check`

This foundation does not select a final official form and does not generate a
submission-ready HWPX/PDF. It fixes the required packet fields, owner-only
steps, forbidden repo data, and future HWPX fixture requirements so TASK-094 can
start from a deterministic contract when the target form and private-data path
are selected.

TASK-094 remains blocked until:

- Owner chooses individual business, corporation, or another business form;
- Regulatory Admin selects the target official form or filing procedure;
- private identity, certificate, address, payment-account, and submission facts
  have an approved non-repo handling path;
- tax/legal/securities/KIS review boundaries are clear enough for a draft.

### Packet Workflow

1. Regulatory Admin refreshes official source URLs and records the checked date.
2. Business Planner supplies non-sensitive business facts from `BUSINESS-PLAN.md`.
3. Owner supplies private facts outside the repo or through an approved secure
   runtime input path.
4. The packet renders Markdown first, then optional DOCX/PDF/HWPX draft files.
5. Compliance Officer flags investment-advice, recommendation, signal,
   robo-advisor, managed-operation, tax, and refund-policy risk language.
6. Owner reviews, signs, uploads, pays, and submits through the official service.

## HWPX Generation Direction

Preferred architecture:

1. Keep canonical data as structured YAML/JSON with placeholders.
2. Render reviewable Markdown first.
3. Generate HWPX only from a tested template fixture.
4. Diff generated XML and keep a human-readable field map.
5. Never auto-submit generated documents.

Open technical decision:

- Whether to build a minimal HWPX writer in repo, call a Hancom-supported library,
  or generate DOCX/PDF first and convert manually. TASK-094 owns this after
  Business Plan v1 and target forms are selected.

## Watch List

| Topic | Status | Next Gate |
|-------|--------|-----------|
| Business registration | research-backed | Owner chooses business type and business details. |
| E-commerce/telecom sales filing | open | Confirm whether paid online software sales trigger filing. |
| Privacy policy | open | Needed before collecting user data. |
| Terms/refund policy | open | Needed before paid sale. |
| KIS commercial/multi-user terms | blocked | Owner or Legal must verify terms before paid deployment. |
| Investment-advice boundary | blocked | Compliance Officer plus professional/regulator review. |
| HWPX packet generator | planned | TASK-094 after form and data model decision. |

## Source Register

- National Tax Service, business registration application procedure:
  https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?cntntsId=7777&mi=2444
- National Tax Service, required submission documents:
  https://www.nts.go.kr/nts/ad/cntnts/cntntsView.do?mi=2445
- FSC/FSS legal interpretation portal, robo-advisor investment-advice question:
  https://better.fsc.go.kr/fsc_new/replyCase/LawreqDetail.do?lawreqIdx=3790&muGpNo=75&muNo=85&stNo=11
- National Law Information Center, Capital Markets Act:
  https://www.law.go.kr/
- Hancom HWP/OWPML format:
  https://www.hancom.com/support/downloadCenter/hwpOwpml
- Hancom Tech HWPX structure:
  https://tech.hancom.com/hwpxformat/
- K-Startup portal:
  https://www.k-startup.go.kr/
- Ministry of SMEs and Startups sample business-plan attachment page:
  https://www.mss.go.kr/site/smba/ex/bbs/View.do?bcIdx=1029124&cbIdx=310&parentSeq=1029124
