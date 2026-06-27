# Membership Staging Deploy — Evidence & Remaining Runbook (TASK-087 BUCKET B)

Recorded: 2026-06-27T11:19:52+09:00 · Owner-approved staging execution (mock, non-public, no payment).

## ✅ Executed this session (Supabase DB tier — real, applied)

A NEW Supabase project was created for Autofolio (the existing INACTIVE project
`xkkbgjvywtbwyaoyvwmq` — from the predecessor STAR-TEAM/tag_manual work — was **NOT
touched**, per the Owner's "신규 프로젝트" choice and to avoid data loss).

| Item | Value |
|------|-------|
| Project name | `autofolio-staging` |
| Project ref/id | `rpdophwfgrwctaochewf` |
| Region | `ap-northeast-2` (Seoul) |
| API URL | `https://rpdophwfgrwctaochewf.supabase.co` |
| Status | ACTIVE_HEALTHY |

Migrations applied (from `supabase/migrations/`, in order):
- `0001_membership_core` — 14 membership/account/subscription/integration/payment/audit tables
- `0002_trading_tenant` — 8 trading tables (nullable `user_id`)
- `0003_rls_policies` — RLS on all tenant tables

**Verification (live, on the project):**
- `22 tables`, `22 RLS-enabled`, `33 RLS policies`, **`0` RLS tables without a policy** (no lockout, no gap).
- Supabase **security advisors: 0 lints** (no missing-RLS / exposed-table findings).

### Public (safe-to-share) env values for the frontend
These are PUBLIC keys (RLS protects data); they belong in frontend env, not secret stores:
```
NEXT_PUBLIC_SUPABASE_URL=https://rpdophwfgrwctaochewf.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon legacy JWT — public; fetch via Supabase dashboard or get_publishable_keys>
# or the modern publishable key: sb_publishable_qaEkSEal78GU51n7wZ1x3A_m8z58O9c
```

### Secret (server-only) — NOT stored in repo
- `SUPABASE_SERVICE_ROLE_KEY` — server-runtime only (Railway/backend env). NEVER place in
  Vercel public scope or the browser bundle (it bypasses RLS). Fetch from the Supabase
  dashboard → Project Settings → API. Required by the backend for global-state reads
  (`system_state`, `risk_limits` scope=GLOBAL) and pre-auth `membership_requests` inserts
  (see `supabase/README.md` apply-time service_role contract).

## ⛔ Remaining for a working app staging (NOT done — blockers found during execution)

The Supabase DB tier is live, but an end-to-end app staging needs two prerequisites that
are outside this session's safe/available scope:

1. **Backend host (FastAPI + paper-worker).** No Railway access is available here (no MCP, no
   token; tag_manual deployed a static site + Supabase, never Railway). The backend needs a
   host (Railway/Render Starter) the Owner provisions once. Config is ready: root `Dockerfile`
   binds `0.0.0.0:$PORT` + `/api/health`; `railway.json` is committed.
2. **App-to-Supabase wiring.** The app currently uses **SQLite + a single-owner model**;
   the repositories are NOT yet pointed at this Supabase Postgres, and tenant isolation is
   not enforced in app code. Wiring the app to this DB (per-user `user_id` scoping) is the
   deliberately-split **`INIT-MULTITENANT-ENGINE`** initiative (default-OFF
   `AUTOFOLIO_MULTI_TENANT_ENABLED`, 4 phases, characterization-tested before flip). Until
   that lands, deploying the backend would run on SQLite/single-tenant and would NOT use this
   Supabase project.

### Frontend (Vercel) — ready to deploy from `web/`
`web/vercel.json` (security headers) is committed. Deploy with the Vercel root directory set
to `web/` (this is a monorepo; the repo root is not the Next app). The Vercel MCP
`deploy_to_vercel` is parameterless and could not be reliably targeted at `web/` from here —
deploy via the Vercel dashboard/CLI with root = `web/`, env = the public Supabase values
above + `API_INTERNAL_URL`/`NEXT_PUBLIC_API_URL` pointing at the backend host from (1).

## Runbook (Owner/next session)
1. Provision the backend host (Railway/Render); set env: `KIS_ENV=mock`, `AUTOFOLIO_OWNER_EMAIL=<owner>`,
   `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` (server-only), all capability flags = `0`.
2. Land `INIT-MULTITENANT-ENGINE` so the app reads/writes this Supabase project per-user.
3. Deploy `web/` to Vercel (root=`web/`) with the public Supabase env + backend URL; keep it
   non-indexed (preview), `can_launch=false`.
4. BUCKET C (legal) gates any PUBLIC commercial launch: KIS commercial/multi-user terms,
   비조치의견서 (유사투자자문 경계), 사업자등록 + 통신판매업, payment/privacy review.

## Boundaries honored
No secrets committed (only public URL/anon key). Existing STAR-TEAM Supabase project untouched.
KIS_ENV stays mock. No real orders, no payment collection, no public commercial launch.
`can_launch` remains false.
