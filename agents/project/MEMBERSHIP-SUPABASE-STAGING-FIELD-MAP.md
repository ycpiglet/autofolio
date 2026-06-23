# Autofolio Membership Supabase Staging Field Map

Status: draft field map, not applied to Supabase
Owner: Backend Engineer
Last updated: 2026-06-19T20:20:16+09:00
Related tasks: TASK-087, TASK-109, TASK-111, TASK-112, TASK-113, TASK-114, TASK-115, TASK-116
Related taskset: TASKSET-MEMBERSHIP-PROD-IMPLEMENTATION-PLANNING

## Purpose

This document maps the existing membership production contracts into a
reviewable Supabase staging schema/RLS target. It is not a migration and does
not apply anything to Supabase.

Machine-readable source:

- `agents/project/MEMBERSHIP-SUPABASE-STAGING-FIELD-MAP.json`

## Boundaries

This task does not:

- create a SQL migration;
- edit `app/database/schema.sql`;
- connect to or mutate a Supabase project;
- change Data API exposure settings;
- deploy a service;
- store customer PII, real payment records, bank account numbers, provider
  tokens, OAuth secrets, KIS keys, or runtime secrets.

`can_launch=false` remains correct. This map only gives the future migration and
staging-test task a concrete review target.

## Supabase Guidance Applied

Checked on 2026-06-19 from official Supabase sources:

- Supabase changelog includes the 2026-04-28 Data/API exposure change: new
  public-schema tables are not automatically exposed to Data/GraphQL APIs for
  new projects.
- RLS policies should use policy `TO` clauses such as `TO authenticated` and
  ownership predicates based on `(select auth.uid())`.
- UPDATE policies need both `USING` and `WITH CHECK`.
- Client-editable user metadata must not be used for authorization.
- Service role or secret keys must remain server-side only.

Sources:

- `https://supabase.com/changelog.md`
- `https://supabase.com/docs/guides/database/postgres/row-level-security.md`
- `https://supabase.com/docs/guides/api/securing-your-api.md`
- `https://supabase.com/docs/guides/security/product-security.md`

## Data API Rule

Default stance for tenant tables:

1. Design table fields and ownership fields.
2. Enable RLS.
3. Add ownership policies.
4. Add staging cross-user tests.
5. Review Data API exposure settings.
6. Grant least privilege to `authenticated` only where the app needs direct
   Data API access.
7. Keep `anon` away from tenant tables; public pre-auth flows go through backend
   routes.
8. Run Supabase security and performance advisors before launch.

Data API grants do not replace RLS. They only decide whether the role can reach
the table/function at all.

## Entity Map

| Table | Owner field | Data class | Member access | Admin/server path |
|-------|-------------|------------|---------------|-------------------|
| `profiles` | `id` | tenant_private | select/insert/update own row | server-audited support action |
| `membership_requests` | `user_id` | tenant_private | select/insert own row after auth or controlled intake | owner review/transition route |
| `deposit_instructions` | `user_id` | payment_instruction | select own instruction | owner issuance/update route; no bank values in repo |
| `approval_events` | `target_user_id`, `actor_user_id` | tenant_audit | select own target/actor events | append-only owner/admin event writer |
| `subscription_grants` | `user_id` | tenant_private | select own grant | grant/revoke route |
| `integration_secret_metadata` | `user_id` | secret_metadata | select own redacted metadata | backend write/rotate/delete; no plaintext response |
| `payment_evidence` | `target_user_id`, `actor_user_id` | payment_evidence | select own minimized evidence | owner approval route; no automatic activation |
| `portfolio_accounts` | `user_id` | tenant_financial | select own account | support/ingestion route |
| `holdings_snapshots` | `user_id` | tenant_financial | select own snapshots | ingestion/support route |
| `risk_settings` | `user_id` | tenant_control | select/update own allowed limits | backend validation; audited override |
| `engine_state` | `user_id` | tenant_control | select own engine state | backend worker/admin validation |
| `engine_run_queue` | `user_id` | tenant_control | select/insert own requested run | worker claim includes user_id |
| `trade_conditions` | `user_id` | tenant_trading | select/insert/update own condition | backend safety validation |
| `order_intents` | `user_id` | tenant_trading | select own intents | insert only through backend risk gate |
| `order_logs` | `user_id` | trading_audit | select own logs | append-only worker log |
| `execution_logs` | `user_id` | trading_audit | select own executions | append-only worker log |
| `notifications` | `user_id` | tenant_product | select own notifications | destination from same user's integration metadata |
| `audit_events` | `target_user_id`, `actor_user_id` | tenant_audit | select own target/actor events | append-only audit writer |

## RLS Policy Pattern

Self-owned SELECT:

```sql
create policy "<table>_select_own"
on public.<table>
for select
to authenticated
using ((select auth.uid()) = user_id);
```

Self-owned INSERT:

```sql
create policy "<table>_insert_own"
on public.<table>
for insert
to authenticated
with check ((select auth.uid()) = user_id);
```

Self-owned UPDATE:

```sql
create policy "<table>_update_own"
on public.<table>
for update
to authenticated
using ((select auth.uid()) = user_id)
with check ((select auth.uid()) = user_id);
```

Tables whose ownership field is `id`, `target_user_id`, or another explicit
field must adapt the predicate. Do not use a request-body `user_id` as authority.

## Public Pre-Auth Boundary

Public signup and applicant status lookup are not direct table exposure. They
remain backend routes that:

- create or read only the minimal pre-auth request surface;
- require request id plus original contact for applicant status lookup;
- strip Owner notes, internal events, account grants, subscription grants,
  product rows, and private payment evidence.

## Owner/Admin Boundary

Owner/admin cross-tenant operations must be server-audited. The browser never
receives a Supabase service role key, secret key, direct privileged SQL channel,
or unlogged cross-tenant mutation path.

If a later implementation proposes `SECURITY DEFINER`, it needs a separate
review and must stay outside public API schemas, set an explicit `search_path`,
check the authenticated actor, and be covered by Supabase advisors.

## Required Staging Tests

- Anonymous callers cannot reach tenant-owned tables through Data API.
- Member A cannot read Member B rows for every tenant-owned table.
- Member A cannot update Member B rows.
- Member cannot reassign `user_id` or `target_user_id` on UPDATE.
- Member cannot call Owner/admin membership, grant, engine override, or support
  paths.
- Owner/admin cross-tenant actions append `audit_events`.
- Secret metadata writes never return plaintext.
- Payment evidence rows contain only the retained allowlist fields.
- Engine queue claims are user-scoped.
- `order_intents`, `order_logs`, and `execution_logs` stay append-only.

## Handoff

Next implementation step, still before any launch:

1. Draft a reviewed staging migration from this map.
2. Apply it only to a staging Supabase project after Owner/R3 boundary review.
3. Add cross-user RLS tests.
4. Run Supabase security/performance advisors.
5. Keep production launch blocked until all evidence exists.
