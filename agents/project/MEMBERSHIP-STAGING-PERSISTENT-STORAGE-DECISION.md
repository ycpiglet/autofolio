# Membership Staging Persistent Storage Decision

Status: draft decision packet, not applied to staging
Owner: Backend Engineer
Last updated: 2026-06-19T21:42:53+09:00
Related tasks: TASK-087, TASK-109, TASK-112, TASK-116, TASK-118, TASK-119, TASK-122

## Purpose

This packet decides where membership, account, payment-evidence, integration,
portfolio, engine, trading, and audit state should persist before external
staging users are allowed.

It is a local planning and validation artifact. It did not create Supabase,
Railway, Vercel, database, storage bucket, or volume resources. It did not
write environment variables, create or apply migrations, read or write secrets,
publish a URL, or mark the service launch-ready.

## Decision

Use `supabase_postgres_auth_rls` as the source of truth for any external or
member-facing staging.

The current local encrypted vault, SQLite file, Railway volume, and runtime
filesystem are not selected as tenant data sources of truth. They can only be
used for single-operator internal smoke with no external users, no real
customer data, and `can_launch=false`.

Railway volumes may be useful later for non-tenant runtime artifacts, but not
for Autofolio membership identity, request state, subscription grants, payment
evidence, integration-secret metadata, portfolio/engine/trading state, or audit
events.

Supabase Storage buckets are a future file-artifact option, not the structured
membership MVP data store.

## Source Basis

Official sources used for this packet:

- Supabase database overview:
  https://supabase.com/docs/guides/database/overview
- Supabase Row Level Security:
  https://supabase.com/docs/guides/database/postgres/row-level-security
- Supabase database backups:
  https://supabase.com/docs/guides/platform/backups
- Supabase Storage:
  https://supabase.com/docs/guides/storage
- Railway volumes:
  https://docs.railway.com/volumes/reference
- Railway variables:
  https://docs.railway.com/variables

## Option Matrix

| Option | Decision | Allowed Scope | Isolation | Gate |
|--------|----------|---------------|-----------|------|
| Local encrypted vault | Local/dev only | Single-operator internal smoke | App convention only | Not external staging source of truth |
| SQLite file | Local/runtime only | Local regression and internal smoke | App convention only | Not membership staging source of truth |
| Railway volume | Not tenant data source | Non-tenant artifacts only after Owner setup | Service filesystem | Not account/payment/secret metadata store |
| Supabase Postgres/Auth/RLS | Selected | External/member staging after migration/RLS/advisors/tests | Auth owner fields plus RLS | Owner/R3 apply required |
| Supabase Storage buckets | Future file artifacts | Uploads/exports after bucket policy review | Bucket policy | Not structured MVP data store |

## Storage Surfaces

| Surface | Current Local Surface | Selected Target | Required Before External Users |
|---------|-----------------------|-----------------|--------------------------------|
| Auth identity/profile | `vault.users` | Supabase Auth plus profile table | Project selected, migration review, profile RLS, session tests |
| Membership requests | `vault.membership_requests` | Supabase membership request table | Applicant lookup policy, approval events, cross-user tests |
| Subscription grants | Vault nested grant | Supabase subscription grant table | Grant RLS, Owner/admin override, expiry tests |
| Payment evidence | Membership event fields | Supabase payment evidence table | TASK-111 fields only, redaction, non-disclosure, retention/delete |
| Integration secret metadata | `vault.user_integrations` | Supabase metadata plus secret-store payload | Metadata RLS, secret-store plan, rotation/delete/audit tests |
| Portfolio/engine/trading state | SQLite/local runtime | Supabase tenant-owned runtime tables after engine review | Tenant isolation, per-user worker context, order-intent isolation |
| Audit events | Local events/logs | Supabase append-only audit event table | Append-only policy and actor/subject/event timestamp tests |

## Required Staging Tests

- `scripts/membership_staging_storage_decision_gate.py --check` passes.
- Local vault is not the external staging source of truth.
- Railway volume is not the tenant data source of truth.
- Supabase migration review packet exists.
- RLS is enabled on membership and secret metadata tables.
- Cross-user membership request reads are blocked.
- Cross-user integration metadata reads are blocked.
- Applicant lookup requires request id plus contact.
- Service role or secret key is server-only.
- Backup and restore plan is reviewed by Owner.
- No external users are allowed until Supabase apply and cross-user tests pass.
- `can_launch=false` remains true until R3 evidence exists.

## Owner-Only Actions

- Select or create the Supabase staging project outside this repository.
- Approve and apply any Supabase migration, RLS policy, grant, storage bucket,
  backup, or advisor remediation.
- Write platform environment variables outside git.
- Approve whether Railway volumes are needed for non-tenant artifacts.
- Approve any staging use with external users or real customer data.

## Boundary

This packet did not create resources, mutate external projects, write platform
environment variables, create or apply migrations, handle secrets, publish a
URL, or change KIS/payment/order/risk behavior.

