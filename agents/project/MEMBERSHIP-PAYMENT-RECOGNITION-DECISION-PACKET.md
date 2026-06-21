# Membership Payment Recognition Decision Packet

Status: draft decision packet, not applied to production
Owner: Regulatory Admin
Last updated: 2026-06-19T20:47:06+09:00
Related tasks: TASK-087, TASK-111, TASK-117

## Purpose

This packet decides the payment-recognition path for the verified-signup
membership MVP without creating bank, PG, virtual-account, or Open Banking
accounts and without handling real payment data.

It is not legal, tax, accounting, securities, banking, or payment-provider
advice. It is a local planning and validation artifact.

## Decision

Use `manual_bank_app_check` plus the existing
`code_assisted_deposit_match` helper for MVP.

- The Owner checks the actual bank app or bank site outside Autofolio.
- Autofolio may assist by matching pasted bank-app/CSV text against deposit
  code, amount, applicant name, and contact.
- The match is advisory only; account activation still requires explicit
  Owner/admin action.
- Raw bank statements, full account numbers, unredacted private identifiers,
  provider payloads, and real customer payment records are not stored in repo
  artifacts.

The near-term optional improvement is `csv_import_review`, but only after
retention, delete, and redaction tests are written.

The scale upgrade is `pg_virtual_account_webhook` or provider receipt/reference
reconciliation after Owner approval, provider setup, webhook verification,
idempotency/retry tests, refund/receipt/tax review, and privacy review.

Direct `open_banking_transaction_inquiry` is not an MVP path. It requires
official Open Banking participation, approval/security/function checks, API
credentials, consent handling, logging, and operational controls. That crosses
the Owner/R3 gate.

## Source Basis

Official and primary sources used for this packet:

- Financial Services Commission Open Banking status:
  https://www.fsc.go.kr/no010101/83750?curPage=&srchBeginDt=&srchCtgry=&srchEndDt=&srchKey=&srchText=
- Korea Financial Telecommunications and Clearings Institute Open Banking
  portal: https://www.openbanking.or.kr/
- Financial Services Commission Open Banking security/approval note:
  https://www.fsc.go.kr/no010101/74024?curPage=344&srchBeginDt=2022-12-&srchCtgry=&srchEndDt=&srchKey=sj&srchText=
- National Tax Service Hometax cash receipt service:
  https://hometax.go.kr/websquare/websquare.html?tm2lIdx=4606010000&tm3lIdx=4606010600&tmIdx=46&w2xPath=%2Fui%2Fpp%2Findex_pp.xml
- Personal Information Protection Commission consent/minimization guide:
  https://www.privacy.go.kr/front/bbs/bbsView.do?bbsNo=BBSMSTR_000000000049&bbscttNo=13156
- Toss Payments virtual-account webhook documentation:
  https://docs.tosspayments.com/blog/virtual-account-webhook
- PortOne virtual-account notification documentation:
  https://developers.portone.io/opi/ko/integration/virtual-account/readme?v=v2
- KG Inicis notification service documentation:
  https://manual.inicis.com/pay/etc-noti.html

## Option Matrix

| Option | Decision | Cost | Ops | Privacy | Audit | Gate |
|--------|----------|------|-----|---------|-------|------|
| Manual bank app check | Selected MVP | Lowest | Manual per payment | Low if masked evidence only | Adequate at low volume | Owner checks bank app outside system |
| Code-assisted deposit match | Selected MVP helper | Lowest | Owner paste/review | Medium if raw text mishandled, low if stateless | Adequate with explicit activation | Raw pasted text must not persist |
| CSV import review | Near-term candidate | Low | Batch review | Medium until delete/redaction tests pass | Stronger reconciliation | Retention/delete/redaction tests first |
| Provider receipt reference | Scale candidate | Provider dependent | Lower after setup | Medium | Strong if verified/idempotent | Provider contract/setup required |
| PG virtual-account webhook | Scale candidate | PG contract/fee dependent | Lower after setup | Medium | Strong with source verification/retry handling | Owner approval, PG setup, webhook tests |
| Open Banking transaction inquiry | Blocked R3, not MVP | Onboarding/control dependent | High | High | Strong only after approval/consent/security | Open Banking participation and security/function checks |

## Retained Evidence

Retain only the TASK-111 payment evidence policy fields:

- `membership_request_id`
- `target_user_id`
- `actor_user_id`
- `approval_event_id`
- `evidence_type`
- `deposit_code`
- `amount_krw`
- `currency`
- `source_type`
- `source_reference`
- `masked_excerpt`
- `confidence`
- `recorded_at`

## Owner-Only Actions

- Choose and manage the live receiving bank account outside repository files.
- Check actual deposits in the bank app or bank website.
- Decide whether and when cash receipt, refund, tax, and accounting workflows
  are needed.
- Approve any PG, virtual-account, or Open Banking provider setup.
- Approve any production payment evidence retention/deletion policy.

## Required Staging Tests

- Public applicant lookup hides payment evidence.
- Raw bank statements are not persisted.
- Code-assisted match requires Owner activation.
- CSV import discards raw source after review.
- Provider webhook requires signature or source verification.
- Provider webhook is idempotent.
- Provider webhook handles delayed or corrected notification.
- Open Banking remains disabled without approval.
- Refund, receipt, and tax boundary remains `watch`.

## Launch Gates

- `scripts/membership_payment_recognition_decision_gate.py --check` passes.
- `scripts/membership_payment_policy_gate.py --check` passes.
- Payment method is selected for the current stage.
- Retention period and delete path are reviewed.
- Refund, receipt, and tax boundary has professional review before commercial
  launch.
- Privacy notice and consent wording are reviewed.
- PG contract or Open Banking approval exists if those paths are used.
- Staging non-disclosure tests pass.
- `can_launch=false` remains true until direct R3 evidence exists.

## Boundary

This packet did not create accounts, log in to providers, request credentials,
call bank/PG/Open Banking APIs, store real payment data, apply Supabase schema,
deploy, or mark the service launch-ready.
