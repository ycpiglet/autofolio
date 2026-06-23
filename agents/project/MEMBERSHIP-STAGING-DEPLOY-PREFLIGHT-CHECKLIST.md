# Membership Staging Deploy Preflight Checklist

Status: draft preflight checklist, not deployed
Owner: CI/CD Engineer
Last updated: 2026-06-19T22:16:54+09:00
Related tasks: TASK-087, TASK-115, TASK-116, TASK-117, TASK-118, TASK-119, TASK-120, TASK-121, TASK-122, TASK-123, TASK-124, TASK-125

## Purpose

This checklist prepares the future Autofolio membership staging deployment
without deploying anything. It records required evidence, environment
placeholders, smoke tests, rollback rules, and current repo blockers.

This task did not deploy to Vercel, Railway, Supabase, or any public URL. It
did not create or mutate external projects, write environment variables, read
or write secrets, apply Supabase migrations, or activate KIS/payment providers.

Machine-readable source:

- `agents/project/MEMBERSHIP-STAGING-DEPLOY-PREFLIGHT-CHECKLIST.json`

Local gate:

```powershell
python scripts/membership_staging_deploy_preflight_gate.py --check
```

## Official Source Basis

- Vercel Git deployments: https://vercel.com/docs/git
- Vercel environment variables: https://vercel.com/docs/environment-variables
- Vercel environments: https://vercel.com/docs/deployments/environments
- Railway variables: https://docs.railway.com/variables
- Railway healthchecks: https://docs.railway.com/deployments/healthchecks
- Railway public networking: https://docs.railway.com/public-networking
- Railway Dockerfiles: https://docs.railway.com/builds/dockerfiles
- Supabase CLI: https://supabase.com/docs/reference/cli/introduction
- Supabase API security: https://supabase.com/docs/guides/api/securing-your-api
- Supabase RLS: https://supabase.com/docs/guides/database/postgres/row-level-security
- Supabase database overview: https://supabase.com/docs/guides/database/overview
- Railway volumes: https://docs.railway.com/volumes/reference
- KIS Developers provider guidance: https://apiportal.koreainvestment.com/provider
- KIS Open API affiliate user terms: https://file.koreainvestment.com/updata/namo/09101613%EC%98%A4%ED%94%88API%EC%84%9C%EB%B9%84%EC%8A%A4%EC%9D%B4%EC%9A%A9%EC%95%BD%EA%B4%80_%EC%A0%84%EB%AC%B8.pdf

## Current Repo Blockers

| Blocker | State | Evidence | Required Before Deploy |
|---------|-------|----------|------------------------|
| Env inventory external write | block actual deploy | `.env.example` and `MEMBERSHIP-STAGING-ENV-INVENTORY` now exist with sanitized placeholders only; external platform env vars are still not written | Owner/R3 writes reviewed values in Vercel/Railway/Supabase outside the repository |
| Railway backend external deploy | block actual deploy | Root Dockerfile now uses `${PORT:-8000}` and `/api/health` readiness is recorded in `MEMBERSHIP-RAILWAY-BACKEND-READINESS` | Owner/R3 configures and executes Railway staging deploy outside this repository |
| Supabase migration/RLS review recorded | block actual deploy | `MEMBERSHIP-SUPABASE-STAGING-MIGRATION-RLS-REVIEW` records table groups, owner fields, RLS/Data API review order, and cross-user tests; no migration file or apply exists | Owner/R3 creates and applies staging migration, runs advisors/cross-user tests, and captures evidence |
| Persistent storage decision recorded | block actual deploy | `MEMBERSHIP-STAGING-PERSISTENT-STORAGE-DECISION` selects Supabase Postgres/Auth/RLS for external staging; local vault/SQLite/Railway volume remain internal-smoke or non-tenant only | Owner/R3 selects Supabase staging, applies reviewed migration/RLS, runs advisors/cross-user tests, and reviews backup/restore |
| KIS terms review recorded | block external launch | `MEMBERSHIP-KIS-COMMERCIAL-TERMS-REVIEW-PACKET` records official KIS provider/terms risks and Owner/KIS/legal question set; no KIS/legal clearance exists | Keep `KIS_ENV=mock`; do not activate KIS credentials, market-data display, order API support, or paid KIS integration claims until Owner/KIS/legal confirmation exists |
| Payment boundaries blocked | block external launch | TASK-117 and secret-store plan keep external payment actions gated | Use non-real payment placeholders |

## Service Targets

| Service | Platform | Path | Target | Required Before Actual Deploy |
|---------|----------|------|--------|-------------------------------|
| Frontend | Vercel | `web/` | Preview or Owner-approved custom staging | `API_INTERNAL_URL`, `AUTOFOLIO_PUBLIC_BASE_URL`, lint/build pass |
| Backend | Railway | repo root | FastAPI container | `$PORT` binding, `/api/health` healthcheck, mock KIS, no guest/autoregister |
| Database/Auth | Supabase | planning artifact | staging project | migration review, RLS, Data API grants, advisors, cross-user tests |

## Environment Inventory Placeholders

Do not put real values in repo.

| Target | Placeholder | Rule |
|--------|-------------|------|
| Vercel | `API_INTERNAL_URL` | Points to approved staging backend before build |
| Vercel | `AUTOFOLIO_PUBLIC_BASE_URL` | Staging frontend URL after platform setup |
| Railway | `AUTOFOLIO_ENV` | Review secure-cookie behavior for external HTTPS staging |
| Railway | `AUTOFOLIO_HOME` | Not a production tenant store; persistence decision required |
| Railway | `KIS_ENV` | Must be `mock` for staging preflight |
| Railway | `AUTOFOLIO_LOCAL_AUTO_REGISTER` | Disabled |
| Railway | `AUTOFOLIO_GUEST_DEMO_ENABLED` | Disabled |
| Railway | `AUTOFOLIO_SSO_ALLOWED_EMAILS` | Owner-approved allowlist only |
| Railway | `AUTOFOLIO_MEMBERSHIP_*` bank values | Non-real placeholders only |
| Railway/Supabase | `SUPABASE_*` | No actual values in repo; server-only secret keys |

## Required Local Checks

- `python -m json.tool agents/project/MEMBERSHIP-STAGING-DEPLOY-PREFLIGHT-CHECKLIST.json`
- `python scripts/membership_staging_deploy_preflight_gate.py --check`
- `python scripts/membership_staging_env_inventory_gate.py --check`
- `python scripts/membership_railway_backend_readiness_gate.py --check`
- `python scripts/membership_staging_storage_decision_gate.py --check`
- `python scripts/membership_supabase_migration_review_gate.py --check`
- `python scripts/membership_supabase_apply_evidence_gate.py --check`
- `python scripts/membership_kis_terms_review_gate.py --check`
- `python -m pytest tests/unit/test_membership_staging_deploy_preflight_gate.py -q`
- `python scripts/membership_contract_gate.py --check`
- `python scripts/membership_supabase_field_map_gate.py --check`
- `python scripts/membership_secret_store_plan_gate.py --check`
- `python scripts/membership_payment_recognition_decision_gate.py --check`
- `python scripts/check_agent_docs.py`

Future deploy readiness should also include backend local `/api/health`, API
membership regression tests, web lint/build, and Playwright smoke against the
staging URL. This checklist does not run or publish a staging URL.

## Staging Smoke Plan

| Smoke | Target | Expected |
|-------|--------|----------|
| Frontend login loads | Vercel preview/custom staging | `/login` loads with no guest demo CTA |
| API health through frontend | Vercel -> Railway proxy | `GET /api/health` returns `200` and `status=ok` |
| Public signup intake | membership public flow | Cannot create active account or session |
| Guest/autoregister fail-closed | auth | Guest demo and unknown local user auto-register are disabled |
| Readiness remains blocked | Owner readiness API | `can_launch=false` until R3 evidence exists |
| No KIS/order activation | trading safety | `KIS_ENV=mock`, no KIS credentials, no live order path |
| No disclosure | logs/API | No secrets, bank account, raw payment evidence, provider token, or PII |
| Persistent storage source of truth | Supabase staging | External/member staging uses Supabase Postgres/Auth/RLS after Owner/R3 apply; local vault, SQLite, Railway volume, and runtime files are not tenant sources of truth |

## Rollback Plan

- Use preview/custom staging only; do not promote to production.
- Configure Railway `/api/health` before actual deploy so unhealthy releases do
  not replace previous traffic.
- Supabase staging migration requires rollback notes and restore/backup plan
  before apply.
- Platform variable changes require an Owner-held previous-value backup outside
  repo.
- Trading remains mock-only; no order or KIS credential activation happens in
  staging smoke.

## Forbidden In This Task

- No Vercel/Railway/Supabase deployment.
- No external project linking, creation, mutation, or public URL publication.
- No environment variable write.
- No `.github/workflows/**` change.
- No Supabase migration creation or apply.
- No secret read/write/rotation/validation.
- No KIS/bank/PG/Open Banking/payment setup.
- No `can_launch=true`.

## Handoff

Actual staging deploy remains blocked until the remaining R3 blockers are
resolved or explicitly waived by Owner/R3 review. Supabase migration/apply,
platform env writes/deploy, KIS commercial/multi-user clearance, market-data
rights, order API support, and payment setup are still Owner/R3 surfaces.
