# Autofolio Membership Access Plan

Status: draft
Owner: Lead Engineer
Last updated: 2026-06-19T19:46:50+09:00
Related tasks: TASK-087, TASK-098, TASK-099, TASK-100, TASK-101, TASK-102, TASK-103, TASK-104, TASK-105, TASK-106, TASK-107, TASK-108, TASK-109, TASK-110, TASK-111, TASK-112, TASK-113, TASK-114
Related taskset: TASKSET-MEMBERSHIP-ACCESS, TASKSET-MEMBERSHIP-PROD-READINESS

## Purpose

This document defines the v1 membership approval model for Autofolio. It is the
source of truth for signup approval, manual bank-transfer confirmation, and
future code-assisted deposit recognition.

No real bank account number, customer identity data, depositor name, payment
record, API secret, or production credential should be committed here.

## Owner Decision

CTA is not a public waitlist or demo flow.

The v1 CTA is:

```text
검증된 사람만 회원가입 신청 -> 가격/무통장입금 안내 -> 입금 확인 -> 계정 승인
```

## V1 Access Policy

- Only verified people can be approved.
- The initial audience is acquaintances / selected users.
- Account creation can be requested, but access remains inactive until approval.
- Unknown local ID/PW login must not auto-create an active owner account by
  default.
- Server-issued guest demo login is disabled by default. It can be enabled only
  for explicit local/development testing with `AUTOFOLIO_GUEST_DEMO_ENABLED=1`.
- Product read surfaces require an approved app user (`owner` or `member`).
  A signed guest session is not enough to read portfolio, market, analysis,
  trade, engine, agent, stream, manual, account, or profile data.
- Approved local `member` accounts are not Owner/admin accounts. Member
  self-service is limited to session-derived account/profile/acknowledgement
  actions until multi-tenant data isolation exists.
- Local prototype request/approval state is stored in encrypted `.autofolio`
  vault, not in production DB or repository files.
- Payment starts as manual bank-transfer confirmation.
- Code-assisted local recognition can help match pasted bank statement text to
  deposit-pending requests, but final activation stays an explicit Owner action.
- Approved users can manage local LLM/SNS integration token status from their
  own session. Token values are write-only at the API boundary and redacted from
  responses.
- Production secret handling is policy-gated: user-owned LLM/SNS/OAuth/KIS
  token categories are write-only/redacted, and rotation/delete/incident
  operations require audited implementation before launch.
- Payment evidence retention is policy-gated: raw bank statements, full account
  numbers, payment secrets, and unredacted private identifiers are not retained
  by default.

## Account State Machine

| State | Meaning | Who can move it |
|-------|---------|-----------------|
| `requested` | User submitted signup request. | User / system |
| `verification_pending` | Owner needs to verify the person. | Owner |
| `deposit_pending` | User is allowed to see bank-transfer instructions and deposit code. | Owner / system |
| `active` | User can use the service. | Owner or approved recognizer |
| `rejected` | Signup rejected. | Owner |
| `expired` | Request or payment window expired. | Owner / system |

## Signup Flow

1. User submits signup request.
2. System stores request as `requested`.
3. Owner verifies the person.
4. If accepted, system moves user to `deposit_pending` or directly `active` for
   free pilot access.
5. Paid pilot users see price, bank-transfer instructions, and a unique deposit
   code.
6. Owner manually checks the bank app or payment evidence.
7. Owner approves the account.
8. System logs who approved it, when, which evidence type was used, and what
   plan period was granted.

## Deposit Matching

Manual v1:

- Owner compares depositor name, transfer amount, time, and requested deposit
  code.
- Owner activates account through an admin approval action.

Code-assisted local prototype:

- Generate a unique short deposit code per signup request.
- Show the code in deposit instructions.
- Let the Owner paste bank-app or CSV statement text into the admin screen.
- Match by deposit code, amount, applicant name, and contact text.
- Show confidence, match reasons, and a masked excerpt.
- Do not store raw pasted statement text or actual bank payment records.
- If confidence is low, keep the account in `deposit_pending`.

Production recognition later:

- Decide between manual approval, CSV import, open-banking API, PG, or virtual
  account options.
- Store immutable audit evidence only after the production data model,
  retention policy, and privacy boundary are approved.

## UI Requirements

Signup page:

- Show that access is selected/approval-based.
- Show that real access requires Owner approval.
- Do not imply immediate self-serve access.
- Do not offer a default guest/demo login path on the public login screen.

Deposit-pending page:

- Show price.
- Show placeholder-safe bank-transfer instruction fields.
- Show unique deposit code.
- Show approval status.
- Do not show private bank/account data unless it is loaded from runtime/admin
  configuration.

Admin page:

- List requested, verification-pending, deposit-pending, active, rejected, and
  expired users.
- Allow Owner to approve, reject, expire, or extend access.
- Record reason/evidence type.

Implemented local prototype:

- Public `/signup` submits `POST /api/membership/requests`.
- Owner-only API can list requests and move them through verification,
  deposit-pending, active, rejected, or expired states.
- Deposit instructions include price and unique deposit code. Bank account
  display fields are loaded from runtime environment variables only.
- `/settings` includes an Owner-facing `회원 승인` tab over the local prototype
  APIs. It lists requests and exposes manual state transitions for verification,
  deposit guidance, bank-app confirmation, rejection, and expiry.
- On local `active` transition, the Owner can provide a login ID and temporary
  password. The server creates/resets a local approved `member` account and a
  subscription grant without returning or storing the plaintext password.
- Owner-only local deposit recognition can scan pasted bank-app/CSV text for
  deposit-pending requests by deposit code, amount, applicant name, and contact.
  It returns confidence/reasons/masked excerpts without storing the raw pasted
  statement. High-confidence matches can be used as
  `code_assisted_deposit_match` evidence during explicit Owner activation.
- Authorization gates are split: `require_owner` / `require_owner_csrf` protect
  Owner/admin global controls, while `require_app_user` /
  `require_app_user_csrf` protect approved-user self-service routes. Member
  password/profile/acknowledgement mutations derive their target from the
  session and do not grant engine/trading/admin control.
- Guest demo login issuance is fail-closed by default. `/api/auth/login` rejects
  `guest=true` unless `AUTOFOLIO_GUEST_DEMO_ENABLED=1`, and the public login UI
  no longer exposes a guest/demo entry point. Static preview content can remain
  as non-interactive product context.
- Product read APIs are app-user gated. Anonymous callers receive 401, guest
  sessions receive 403, and approved `member` or `owner` sessions can read.
  This is still local authorization only; it does not replace future user_id
  data isolation.
- `/settings > 계정/연결` includes a local user-owned integration section for
  LLM/SNS providers. The local prototype stores provider records in the
  encrypted vault and returns only configured/disabled/masked status. It does
  not validate tokens, call provider APIs, perform OAuth, or activate KIS
  broker credentials.
- `/settings > 회원 승인` includes an Owner-only production-readiness panel.
  It keeps launch blocked while Supabase/RLS, production secret storage,
  payment recognition, per-user engine/safety isolation, KIS terms, and deploy
  evidence are missing.
- Supabase/RLS production architecture is captured in
  `MEMBERSHIP-PRODUCTION-CONTRACT.json` and
  `MEMBERSHIP-PRODUCTION-CONTRACT.md`. `scripts/membership_contract_gate.py`
  validates required tenant entities, `auth.uid()` ownership, RLS invariants,
  secret redaction, server-audited admin operations, minimal payment evidence,
  and per-user engine/safety launch gates. This is a contract only; it does not
  apply a DB migration or prove production isolation.
- Public `/signup` includes applicant status lookup. A user can enter request id
  and the original contact to view an applicant-safe response. After Owner moves
  the request to `deposit_pending`, the applicant can see price, deposit code,
  runtime-configured bank name/account holder/account number, and due date.
  Public lookup strips Owner events/notes, account grant, and subscription
  grant internals.
- Payment evidence retention is captured in
  `MEMBERSHIP-PAYMENT-EVIDENCE-POLICY.json` and
  `MEMBERSHIP-PAYMENT-EVIDENCE-POLICY.md`. The local gate
  `scripts/membership_payment_policy_gate.py` validates allowed evidence
  sources, forbidden raw/private evidence, retained field allowlist, redaction
  rules, audit invariants, and launch gates. This is a policy only; it does not
  store real payment evidence or approve a production payment method.
- Production secret handling is captured in
  `MEMBERSHIP-PRODUCTION-SECRET-POLICY.json` and
  `MEMBERSHIP-PRODUCTION-SECRET-POLICY.md`. The local gate
  `scripts/membership_secret_policy_gate.py` validates user-owned
  LLM/SNS/OAuth/KIS token categories, forbidden exposure, metadata-only
  responses, lifecycle operations, redaction, audit invariants, and launch
  gates. This is a policy only; it does not read/write secrets or enable
  provider/OAuth/KIS execution.
- Per-user engine/safety readiness is captured in
  `MEMBERSHIP-ENGINE-SAFETY-CONTRACT.json` and
  `MEMBERSHIP-ENGINE-SAFETY-CONTRACT.md`. The local gate
  `scripts/membership_engine_safety_gate.py` validates engine state, queue,
  kill switch, safety flags, risk limits, circuit breakers, append-only order
  intents, order/execution logs, notification scope, worker context, and launch
  gates. This is a contract only; it does not change OrderFlow, SafetyChecker,
  KIS broker behavior, risk gates, production DB, deploy, or live execution.
- Tenant isolation is captured in
  `MEMBERSHIP-TENANT-ISOLATION-MATRIX.json` and
  `MEMBERSHIP-TENANT-ISOLATION-MATRIX.md`. The local gate
  `scripts/membership_tenant_isolation_gate.py` validates public/member/owner/
  worker route groups, tenant surfaces, `auth.uid()` ownership, secret
  redaction, applicant lookup non-disclosure, and required staging tests. This
  is a matrix only; it does not apply Supabase schema/RLS or prove production
  cross-user isolation.

## Data Model Direction

Required entities:

| Entity | Required fields |
|--------|-----------------|
| membership_request | user id, requested email, status, requested_at, verified_at, expires_at |
| deposit_instruction | request id, plan, price, currency, deposit_code, due_at |
| approval_event | actor, action, previous_status, next_status, evidence_type, note, created_at |
| subscription_grant | user id, plan, starts_at, ends_at, source_event |

Do not store bank credentials or private payment records in plaintext repo files.

## Safety Boundaries

- No automatic public signup.
- No committed bank account number.
- No production payment integration without a separate task.
- No external bank API/OAuth setup without Owner approval.
- No public marketing that implies guaranteed access, guaranteed returns, or
  investment advice.
- No KIS/order/risk/prod/secret changes in this planning task.

## Follow-Up Implementation Gates

- TASK-087 owns the broader web deploy and membership-gating implementation.
- TASK-099 made local auto-registration fail-closed; first-run/dev opt-in
  remains possible only with `AUTOFOLIO_LOCAL_AUTO_REGISTER=1`.
- TASK-100 added local encrypted-vault signup request and Owner approval-state
  prototype. It does not create login accounts or subscription grants.
- TASK-101 added a local Owner admin approval UI in `/settings`.
- TASK-102 added local active membership -> login account/subscription grant.
  It is encrypted-vault only and does not provide production DB or multi-tenant
  isolation.
- TASK-103 added stateless local pasted statement/CSV deposit recognition as an
  Owner approval aid. It does not integrate a real bank API, store raw payment
  records, or auto-activate accounts.
- TASK-104 split local member self-service from Owner/admin authorization.
  Members can complete their own account/profile/acknowledgement setup but
  cannot mutate global engine/trading/admin controls before user_id isolation.
- TASK-105 made server-issued guest demo sessions explicit dev opt-in and
  removed the guest demo CTA from the login surface. Internal signed guest
  fixtures may remain for legacy read-only/mock tests, but public access is
  approval-based by default.
- TASK-106 moved product read APIs from session-only to approved app-user
  access. This closes guest read access in the local prototype, while production
  RLS/user_id isolation remains future work.
- TASK-107 added a local approved-user LLM/SNS integration token harness. Token
  values are request-only and redacted in API responses; actual provider calls,
  OAuth, production secret management, and KIS per-user broker credential
  activation remain future work.
- TASK-108 added an Owner-visible production-readiness gate. It does not launch
  or configure production; it makes remaining R3 blockers visible in API/UI.
- TASK-109 added a Supabase/RLS production contract asset and local contract
  gate. It gives TASK-087 a concrete acceptance map but does not create or apply
  any production schema.
- TASK-110 added applicant-facing request status and deposit-instruction lookup
  on `/signup`. It completes the local applicant side of the manual
  bank-transfer loop without storing real payment records or applying production
  DB changes.
- TASK-111 added a local payment evidence retention policy and validation gate.
  It narrows the production payment-evidence gap but does not choose a bank/PG
  method, store real payment records, or settle refund/receipt/tax handling.
- TASK-112 added a local production secret policy and validation gate. It
  narrows the production secret-management gap but does not implement a secret
  store, rotate/delete real secrets, validate provider OAuth, activate KIS
  credentials, or apply Supabase changes.
- TASK-113 added a local per-user engine/safety contract and validation gate.
  It narrows the engine isolation gap but does not change OrderFlow,
  SafetyChecker, KIS broker behavior, risk gates, production DB, deploy, or
  live execution.
- TASK-114 added a local tenant-isolation matrix and validation gate. It
  narrows the production user_id/RLS gap but does not apply Supabase schema/RLS
  or prove staging cross-user isolation.
- A future implementation task should decide the production auth/database schema,
  multi-tenant isolation, and deploy path.
- A future payment-recognition task should compare manual approval, CSV upload,
  open-banking API, and PG/virtual-account options.
- Production deployment, real account numbers, payment collection, and external
  bank integration remain Owner-managed boundaries.
