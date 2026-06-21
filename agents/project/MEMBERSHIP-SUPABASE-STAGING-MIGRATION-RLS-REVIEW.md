# Membership Supabase Staging Migration/RLS Review

Status: draft review packet, not a migration, not applied
Owner: Backend Engineer
Last updated: 2026-06-19T21:52:56+09:00
Related tasks: TASK-087, TASK-109, TASK-116, TASK-122, TASK-123

## Purpose

This packet turns the TASK-116 field map and TASK-122 persistent storage
decision into a review target for a future Owner/R3 Supabase staging
migration.

It is not a migration file, not executable SQL, and not an applied schema. It
does not connect to Supabase, change Data API grants, edit `schema.sql`, write
environment variables, deploy, or handle secrets or production data.

## Review Decision

Future external/member staging should use Supabase Postgres/Auth/RLS for
structured tenant data. Before that happens, the Owner/R3 apply lane needs to
review:

- table groups and owner fields;
- RLS policy intent and update `WITH CHECK` coverage;
- anon and authenticated Data API grant posture;
- append-only audit and order records;
- secret metadata and payment evidence minimization;
- advisor output, backup/restore posture, and cross-user test evidence.

## Table Groups

| Group | Tables | Review Focus |
|-------|--------|--------------|
| Identity and membership | `profiles`, `membership_requests`, `deposit_instructions`, `approval_events`, `subscription_grants` | account ownership, approval audit, grant visibility |
| Payment and secret metadata | `payment_evidence`, `integration_secret_metadata` | minimal evidence and metadata-only secrets |
| Portfolio runtime | `portfolio_accounts`, `holdings_snapshots`, `risk_settings`, `engine_state`, `engine_run_queue` | tenant-owned runtime and queue scope |
| Trading and audit | `trade_conditions`, `order_intents`, `order_logs`, `execution_logs`, `notifications`, `audit_events` | append-only order/audit and notification isolation |

## RLS Review Requirements

- Every table listed in the packet requires RLS before external users.
- Every member policy must combine `TO authenticated` with user ownership.
- Every update-capable tenant table requires `WITH CHECK` ownership coverage.
- Append-only tables must not grant authenticated update or delete.
- `anon` has no direct tenant table access; public signup/status lookup stays
  backend-mediated.
- Owner/admin cross-tenant operations stay server-side and append audit events.
- Service role or secret keys remain server-runtime only.

## Data API Review Order

1. Confirm table list and owner fields against TASK-116.
2. Confirm RLS policy names and ownership predicates.
3. Confirm `anon` has no tenant table grants.
4. Confirm authenticated grants are least-privilege.
5. Confirm public pre-auth routes do not expose tenant tables directly.
6. Confirm Data API exposure settings after RLS exists.
7. Run security and performance advisors after schema exists.
8. Run cross-user tests before any external user staging.

## Required Cross-User Tests

- `anon_has_no_tenant_table_access`
- `member_a_cannot_read_member_b`
- `member_a_cannot_update_member_b`
- `member_cannot_reassign_user_id`
- `member_cannot_call_owner_admin`
- `owner_admin_routes_create_audit_events`
- `secret_metadata_never_returns_plaintext`
- `payment_evidence_minimized`
- `engine_queue_user_scope`
- `order_intent_append_only`

## Boundary

No migration file, SQL execution, Supabase project mutation, Data API grant
change, `schema.sql` change, external environment write, deploy, secret
handling, production data, real customer data, KIS/payment/provider/order/risk
change, public URL, or `can_launch=true` happened in this task.

