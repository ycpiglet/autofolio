# supabase/migrations — Staging Review Files (NOT APPLIED)

Status: **NOT APPLIED**. These are reviewable DDL + RLS policy files for Owner/R3 staging review.

No migration has been applied to any Supabase project. `can_launch` remains `false`.

## Files

| File | Contents |
|------|----------|
| `migrations/0001_membership_core.sql` | Membership, account, subscription, integration, payment-evidence, portfolio, engine, and audit entities. |
| `migrations/0002_trading_tenant.sql` | Trading tables (translated from `app/database/schema.sql`) + nullable `user_id` column + `order_intents`. |
| `migrations/0003_rls_policies.sql` | `auth.uid()`-ownership RLS policies, append-only rules, UPDATE USING/WITH CHECK. |

## Apply Gate

Before any apply: Owner/R3 must review this directory and pass the apply-evidence checklist.

```powershell
python scripts/membership_supabase_migration_review_gate.py --check
python scripts/membership_supabase_apply_evidence_gate.py --check
```

## Apply-time backend contract (from A4 RLS review — MUST honor at BUCKET B apply)

RLS ownership predicates use `(select auth.uid()) = user_id`. For rows where
`user_id IS NULL` this evaluates to NULL → treated as FALSE → the row is
INVISIBLE to an `authenticated` session. This is intentional tenant isolation,
but it imposes a backend contract once these migrations are applied:

- **Global/system state reads MUST use the `service_role` credential, not an
  authenticated JWT.** Affected: `system_state` (kill-switch / auto / circuit
  breaker keys), `risk_limits` where `scope = 'GLOBAL'`, and any legacy trading
  row carrying `user_id IS NULL`. Querying these via an authenticated session
  silently returns zero rows.
- **Pre-auth inserts MUST use `service_role`.** Affected: `membership_requests`
  intake (inserted with `user_id IS NULL` before an account exists) — the
  `*_insert_own` WITH CHECK rejects a NULL `user_id` under an authenticated
  session by design.
- The cross-user test `member_a_cannot_read_member_b` does NOT cover the
  authenticated-vs-NULL case; add an explicit "authenticated session cannot see
  user_id IS NULL rows" test in the apply lane.
