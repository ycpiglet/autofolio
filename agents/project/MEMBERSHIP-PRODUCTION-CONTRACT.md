# Autofolio Membership Production Contract

Status: draft contract, not applied to production
Updated: 2026-06-19T19:46:50+09:00
Related: TASK-087, TASK-108, TASK-109, TASK-111, TASK-112, TASK-113, TASK-114

## Purpose

This is the asset that turns the membership/product launch discussion into a
checkable production contract. It is intentionally not a database migration.
No Supabase project, production DB, bank account, provider API, OAuth callback,
KIS credential, or deploy target is changed by this document.

The machine-readable source is
`agents/project/MEMBERSHIP-PRODUCTION-CONTRACT.json`. The local gate is:

```powershell
python scripts/membership_contract_gate.py --check
```

## Launch Rule

External users cannot be launched until all production gates pass. The current
local prototype may be used for flow testing, but it is not production
multi-tenant security.

Required before external users:

- Supabase staging project exists and schema migration is reviewed/applied in
  staging.
- RLS is enabled on every tenant-owned table.
- Tenant-isolation tests prove member A cannot read or mutate member B data.
- Service role or secret keys exist only in server-side runtime.
- User-owned LLM/SNS/KIS secrets have rotation, deletion, redaction, and audit
  behavior.
- Payment evidence retention is approved and minimal.
- Engine state, queues, kill switch, risk limits, and order intents are
  user-scoped.
- KIS terms and recommendation/compliance boundaries are recorded.
- Staging deploy smoke tests pass.

## Data Ownership

Every tenant-owned row must have a `user_id`, `target_user_id`, or equivalent
field referencing `auth.users(id)`. Member self-access uses `auth.uid()` against
that user field. Owner/admin actions affecting another user must go through a
server-side audited route or a reviewed private `SECURITY DEFINER` function.

Core production entities:

- `profiles`
- `membership_requests`
- `deposit_instructions`
- `approval_events`
- `subscription_grants`
- `integration_secrets`
- `portfolio_accounts`
- `holdings_snapshots`
- `risk_settings`
- `engine_state`
- `order_intents`
- `audit_events`

## RLS And Admin Boundary

RLS must be enabled for all tenant-owned tables before staging or production.
Member policies are self-scoped. Owner/admin operations are not browser-side
bypasses; they are server audited operations.

Service role or Supabase secret keys are forbidden in browser code, logs,
reports, or repository files. If `SECURITY DEFINER` is used, it must live
outside public API schemas, set an explicit `search_path`, and stay small enough
to review.

## Secret And Payment Boundary

LLM/SNS/KIS token values are write-only at the API boundary. Responses can show
metadata, enabled/disabled state, and masked hints, but never raw secrets.

Payment evidence stores only minimal masked evidence, deposit code, amount,
source type, and audit event references. Raw pasted bank statements and private
bank records are not persisted by default.

Payment evidence retention is further constrained by
`agents/project/MEMBERSHIP-PAYMENT-EVIDENCE-POLICY.json` and the local gate:

```powershell
python scripts/membership_payment_policy_gate.py --check
```

Production secret handling is further constrained by
`agents/project/MEMBERSHIP-PRODUCTION-SECRET-POLICY.json` and the local gate:

```powershell
python scripts/membership_secret_policy_gate.py --check
```

Tenant isolation is further constrained by
`agents/project/MEMBERSHIP-TENANT-ISOLATION-MATRIX.json` and the local gate:

```powershell
python scripts/membership_tenant_isolation_gate.py --check
```

Per-user engine and safety isolation is further constrained by
`agents/project/MEMBERSHIP-ENGINE-SAFETY-CONTRACT.json` and the local gate:

```powershell
python scripts/membership_engine_safety_gate.py --check
```

## Recommendation Boundary

Autofolio can provide the harness, agent personalities, workflow, safety gates,
and audit surfaces. Public claims for recommendation, paid signal, model
portfolio, personalized advice, or performance remain compliance-gated until a
separate professional/regulator review exists.

## What This Unlocks

This contract lets the readiness screen distinguish between:

- local flow implemented;
- production architecture contract exists;
- tenant isolation matrix exists;
- production secret handling policy exists;
- per-user engine/safety contract exists;
- production schema/RLS/secret/payment/engine/deploy evidence still missing.

It also gives the next implementation task a concrete acceptance target without
silently crossing the production DB or deployment boundary.
