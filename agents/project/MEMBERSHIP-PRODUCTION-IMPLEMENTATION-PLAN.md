# Autofolio Membership Production Implementation Plan

Status: draft implementation plan, no production action
Owner: Lead Engineer
Last updated: 2026-06-19T22:14:24+09:00
Related tasks: TASK-087, TASK-109, TASK-111, TASK-112, TASK-113, TASK-114, TASK-115, TASK-116, TASK-117, TASK-118, TASK-119, TASK-120, TASK-121, TASK-122, TASK-123, TASK-124, TASK-125, TASK-126
Related taskset: TASKSET-MEMBERSHIP-PROD-IMPLEMENTATION-PLANNING

## Purpose

This document turns the completed local membership readiness contracts into a
production implementation plan. It is a planning artifact only. It does not
apply Supabase schema, create migrations, deploy services, read or write
secrets, call payment/bank APIs, activate KIS credentials, or change
OrderFlow/SafetyChecker/KIS/risk behavior.

## Current Inputs

The no-Owner R2 readiness slice is complete:

- `MEMBERSHIP-PRODUCTION-CONTRACT.json`: production entity/RLS/secret/payment/engine contract.
- `MEMBERSHIP-PAYMENT-EVIDENCE-POLICY.json`: minimal payment evidence policy.
- `MEMBERSHIP-TENANT-ISOLATION-MATRIX.json`: route/surface/user isolation matrix.
- `MEMBERSHIP-PRODUCTION-SECRET-POLICY.json`: user-owned token/secret policy.
- `MEMBERSHIP-ENGINE-SAFETY-CONTRACT.json`: per-user engine/safety contract.
- `MEMBERSHIP-SUPABASE-STAGING-FIELD-MAP.json`: Supabase staging entity/RLS/Data API field map.
- `MEMBERSHIP-PAYMENT-RECOGNITION-DECISION-PACKET.json`: payment recognition MVP decision and upgrade path.
- `MEMBERSHIP-PRODUCTION-SECRET-STORE-IMPLEMENTATION-PLAN.json`: production secret store candidate, API boundary, and rotation/delete/audit plan.
- `MEMBERSHIP-STAGING-DEPLOY-PREFLIGHT-CHECKLIST.json`: Vercel/Railway/Supabase staging deploy preflight checklist, smoke plan, rollback plan, and current blocker register.
- `MEMBERSHIP-STAGING-ENV-INVENTORY.json`: sanitized env inventory template and fail-closed defaults.
- `MEMBERSHIP-RAILWAY-BACKEND-READINESS.json`: Railway backend local `$PORT` and `/api/health` readiness evidence.
- `MEMBERSHIP-STAGING-PERSISTENT-STORAGE-DECISION.json`: external/member staging storage source-of-truth decision.
- `MEMBERSHIP-SUPABASE-STAGING-MIGRATION-RLS-REVIEW.json`: review packet for future staging migration/RLS apply.
- `MEMBERSHIP-SUPABASE-STAGING-APPLY-EVIDENCE-CHECKLIST.json`: required future Owner/R3 apply evidence.
- `app/services/membership_readiness.py`: Owner-visible readiness surface now reflects these R2 artifacts while keeping R3 blockers explicit.

These artifacts are implementation inputs, not launch approval.

## Remaining Work Split

| Area | R2 planning allowed now | R3 action gate |
|------|-------------------------|----------------|
| Supabase schema/RLS | Field map, policy names, staging test matrix, migration review checklist | Create/apply migration, touch production DB, connect live Supabase project |
| Payment recognition | Option decision packet, data retention field map, manual/CSV/API/PG comparison | Bank/Open Banking/PG account setup, API credentials, real payment records |
| Secret store | Implementation design, provider category mapping, rotation/delete test plan | Store real secrets, validate OAuth/provider token, rotate/delete live credentials |
| Per-user engine safety | Worker context design, order-intent lifecycle plan, staging dry-run checklist | Change OrderFlow, SafetyChecker, risk gate, KIS broker, live/member execution |
| Deploy | Environment inventory, preflight checklist, smoke-test plan | Vercel/Railway/Supabase deploy, public URL, production env mutation |
| Persistent storage | Storage source-of-truth decision, local-vs-Supabase boundary, staging tests | Supabase project selection, migration/RLS apply, advisors, backup/restore, external users |
| Compliance | Question list and evidence packet | Legal/tax/securities conclusion, KIS terms acceptance, commercial launch |

## Taskset Plan

`TASKSET-MEMBERSHIP-PROD-IMPLEMENTATION-PLANNING` keeps the next cycle in the
safe lane:

1. `TASK-115`: create this implementation plan and R2/R3 split.
2. `TASK-116`: Supabase staging schema/RLS field map, no migration apply.
3. `TASK-117`: payment recognition option decision packet, no external account/API.
4. `TASK-118`: production secret store implementation plan, no secret handling.
5. `TASK-119`: staging deploy preflight checklist, no deploy.

## Invariants

- `can_launch=false` remains true until every R3 blocker has direct evidence.
- Planning records must distinguish design readiness from implementation
  readiness.
- Do not create migration files or change `app/database/schema.sql` in this
  planning taskset.
- Do not store real bank account numbers, payment records, customer PII,
  provider tokens, KIS keys, OAuth secrets, or production environment values in
  repository files.
- Do not change engine/order/risk/KIS behavior without explicit Owner approval.

## TASK-116 Result

`TASK-116` created `MEMBERSHIP-SUPABASE-STAGING-FIELD-MAP.json`/`.md`.
It maps membership, integration, payment evidence, portfolio, engine, trading,
notification, and audit surfaces to Supabase Auth-owned RLS targets. It also
records Data API exposure order, policy naming, UPDATE `USING`/`WITH CHECK`
requirements, staging cross-user tests, and advisor checklist.
`scripts/membership_supabase_field_map_gate.py` validates the local JSON field
map only; it does not connect to Supabase or apply schema.

It is still not a migration and was not applied to any Supabase project.

## TASK-118 Result

`TASK-118` created
`MEMBERSHIP-PRODUCTION-SECRET-STORE-IMPLEMENTATION-PLAN.json`/`.md`.
It maps TASK-112 policy into a production secret-store staging review target:
deployment runtime secrets and Supabase Edge Function secrets for platform
backend keys, Supabase Vault or equivalent KMS for tenant user-owned provider
payloads, and a tenant metadata table for redacted status, masked hints,
rotation/delete timestamps, and audit event ids.
`scripts/membership_secret_store_plan_gate.py` validates the local plan only.
It fails if the plan marks stores implemented, allows plaintext provider
responses, omits rotation/delete tests, or introduces raw secret key names.

It is still not a secret store implementation and no secret value was read,
written, rotated, deleted, or validated.

## TASK-117 Result

`TASK-117` created
`MEMBERSHIP-PAYMENT-RECOGNITION-DECISION-PACKET.json`/`.md`.
It selects manual bank-app confirmation plus the existing code-assisted deposit
match as the MVP payment recognition path, with explicit Owner/admin activation
still required. CSV import remains a near-term staff-tool candidate only after
retention/delete/redaction tests. PG virtual account or provider receipt
reference handling is reserved for scale after Owner approval, provider setup,
webhook source verification, idempotency/retry tests, and refund/receipt/tax
and privacy review. Direct Open Banking transaction inquiry is explicitly not
an MVP path because it needs participation approval, security/function checks,
credentials, consent, and operational controls.
`scripts/membership_payment_recognition_decision_gate.py` validates the local
decision packet only.

It is still not a payment implementation and no bank, PG, virtual account, Open
Banking, credential, API call, or real payment data boundary was crossed.

## TASK-119 Result

`TASK-119` created
`MEMBERSHIP-STAGING-DEPLOY-PREFLIGHT-CHECKLIST.json`/`.md`.
It defines Vercel frontend, Railway backend, and Supabase staging service
targets; environment inventory placeholders; required local checks; staging
smoke plan; rollback plan; forbidden actions; and launch gates.
It also records current blockers: README references `.env.example` but that
file was absent, the root Dockerfile starts uvicorn on fixed port `8000` rather
than a reviewed Railway `$PORT` binding, Supabase migration/RLS has not been
created or applied, persistent storage is still local-vault/runtime based, and
KIS/payment external boundaries remain blocked.
`scripts/membership_staging_deploy_preflight_gate.py` validates the local
checklist only.

It is still not a deploy and no Vercel, Railway, Supabase, environment,
public URL, secret, migration, KIS, or payment boundary was crossed.

## TASK-120 Result

`TASK-120` created `.env.example` plus
`MEMBERSHIP-STAGING-ENV-INVENTORY.json`/`.md`.

The repo now has a sanitized environment template with local URLs, fail-closed
defaults, and empty secret/account/provider placeholders. The local gate rejects
secret-like values and fail-open defaults. This resolves the local missing
`.env.example` blocker but does not write any external platform environment
variables.

## TASK-121 Result

`TASK-121` updated the root `Dockerfile` command to bind uvicorn to
`${PORT:-8000}` and created `MEMBERSHIP-RAILWAY-BACKEND-READINESS.json`/`.md`.

The local gate validates that the backend binds `0.0.0.0`, uses the platform
`PORT` fallback pattern, exposes unauthenticated `/api/health`, and remains
not deployed. This resolves the local Railway fixed-port readiness blocker but
does not configure Railway, write platform env vars, deploy, or publish a URL.

## TASK-122 Result

`TASK-122` created
`MEMBERSHIP-STAGING-PERSISTENT-STORAGE-DECISION.json`/`.md`.

It selects Supabase Postgres/Auth/RLS as the source of truth for any external
or member-facing staging. Local encrypted vault, SQLite, Railway volume, and
runtime filesystem storage remain local/internal-smoke or non-tenant-artifact
only, not account, membership, payment evidence, integration-secret metadata,
portfolio/engine/trading, or audit-event sources of truth.
`scripts/membership_staging_storage_decision_gate.py` validates the local
decision only.

It is still not a migration or storage implementation and no Supabase project,
Railway volume, external environment value, public URL, secret, or production
data was created or changed.

## TASK-123 Result

`TASK-123` created
`MEMBERSHIP-SUPABASE-STAGING-MIGRATION-RLS-REVIEW.json`/`.md`.

It records table groups, owner fields, authenticated grants, append-only rules,
update `WITH CHECK` requirements, Data API review order, cross-user tests, and
rollback/apply review checklist for future Supabase staging work.
`scripts/membership_supabase_migration_review_gate.py` validates the local
review packet only.

It is still not a migration file or executable SQL and no Supabase project,
Data API grant, schema file, external environment value, deploy target, secret,
or production data was created or changed.

## TASK-124 Result

`TASK-124` created
`MEMBERSHIP-SUPABASE-STAGING-APPLY-EVIDENCE-CHECKLIST.json`/`.md`.

It records the evidence a future Owner/R3 apply lane must capture: selected
staging project, backup/restore plan, migration apply log/status, advisors,
Data API grant review, service-role review, cross-user tests, and deploy-smoke
prerequisites. `scripts/membership_supabase_apply_evidence_gate.py` validates
the local checklist only.

It is still not an apply lane and no Supabase project, backup, migration,
advisor, Data API grant, external environment value, deploy target, secret, or
production data was created or changed.

## TASK-125 Result

`TASK-125` created
`MEMBERSHIP-KIS-COMMERCIAL-TERMS-REVIEW-PACKET.json`/`.md`.

It records KIS/FSC/FSS official-source findings and the Owner/KIS/legal
question set for hosted multi-user/commercial Open API use, market-data
display, order API support, credential handling, and paid integration claims.
`scripts/membership_kis_terms_review_gate.py` validates the local packet only.

It is still not KIS/legal clearance and no KIS login, KIS credential, external
contact, app/brokers/kis change, order/risk change, deploy, or launch
clearance happened.

## TASK-126 Result

`TASK-126` updated `app/services/membership_readiness.py` and focused API tests.

The Owner-visible readiness API now reports TASK-116 through TASK-125 R2
artifacts as pass items while keeping Supabase schema/RLS, production secret
storage, payment recognition, per-user engine/safety, KIS terms, and external
deploy as block/watch items. `can_launch=false` remains the invariant.

It is still not launch approval and no external platform, Supabase, secret,
payment, KIS, order, risk, deploy, or production data boundary was crossed.

## Next Candidate

No additional no-Owner R2 follow-up is currently identified inside this plan.
Actual migration creation/apply, external deploy, env writes, real secrets,
public URL publication, external users, and production readiness remain
Owner/R3 unless a new explicitly-scoped local task is registered.
