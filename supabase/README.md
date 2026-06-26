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
