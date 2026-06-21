# Autofolio Membership Tenant Isolation Matrix

Status: draft matrix, not applied to Supabase
Updated: 2026-06-19T18:31:09+09:00
Related: TASK-087, TASK-109, TASK-114

## Purpose

This matrix narrows TASK-087's production membership risk into a checkable
tenant-isolation contract. It does not apply a migration, connect to Supabase,
read secrets, deploy, or certify production security.

The machine-readable source is
`agents/project/MEMBERSHIP-TENANT-ISOLATION-MATRIX.json`. The local gate is:

```powershell
python scripts/membership_tenant_isolation_gate.py --check
```

## Current Boundary

Local Autofolio now blocks anonymous and guest product access and separates
member self-service from Owner/admin controls. That is useful local gating, but
it is not production tenant isolation. Production isolation still requires
Supabase Auth subjects, tenant-owned rows, RLS policies, explicit API exposure
decisions, and cross-user tests.

## Route Groups

| Group | Allowed | Forbidden |
|-------|---------|-----------|
| `public_pre_auth` | signup request, request-id/contact lookup, provider availability | product data, session grants, Owner notes/events |
| `app_user_self_service` | own account/profile/acknowledgement/integration metadata | admin settings, approval transitions, global engine/trading control |
| `app_user_product_read` | own product rows only | other user's rows, admin queue, raw secrets |
| `owner_admin` | membership review, transitions, support action | browser service key, unlogged cross-tenant edit |
| `engine_worker` | per-user queue, safety, risk gate | single global owner state for members |

## Production Rule

Tenant-private, financial, product, control, trading, secret-metadata, and
audit rows must have a Supabase Auth-owned user field and RLS enabled before
external users. Member policies must be ownership policies, not role-only
checks. Owner/admin cross-tenant actions must go through server-audited routes.

Public applicant lookup remains a special pre-auth flow. It is keyed by request
id plus original contact and must not expose Owner notes, internal events,
account grants, subscription grants, or product rows.

## Required Staging Tests

- Anonymous callers cannot read product surfaces.
- Guest sessions receive 403 on product surfaces.
- Member A cannot read or mutate Member B tenant rows.
- Member cannot call Owner/admin membership or engine control routes.
- Owner cross-tenant membership transitions create immutable audit events.
- Secret/token writes never return plaintext values.
- Engine state, kill switch, risk settings, and order intent queues are
  user-scoped.
- Applicant status lookup requires request id plus original contact and strips
  internal fields.

## What This Unlocks

This lets the readiness screen distinguish between:

- local app-user gating completed;
- production contract exists;
- tenant isolation matrix exists;
- real Supabase schema/RLS/apply and cross-user tests still missing.

`can_launch=false` remains correct until staging evidence proves the matrix.
