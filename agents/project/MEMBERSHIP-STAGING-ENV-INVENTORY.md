# Membership Staging Env Inventory

Status: sanitized template only.

This inventory resolves the TASK-119 `.env.example` missing blocker for local
preflight. It does not write environment variables to Vercel, Railway,
Supabase, or any external platform.

## Boundary

- No real secret values.
- No real bank account numbers.
- No OAuth, provider, KIS, Supabase, payment, or Open Banking credentials.
- No deploy, public URL publication, Supabase apply, or platform mutation.
- `KIS_ENV=mock`.
- Guest demo, local auto-register, mock SSO, and KIS WebSocket stay disabled.

## Template

The sanitized template is `.env.example`. Real `.env` remains gitignored.

## Fail-Closed Defaults

| Key | Value | Reason |
|-----|-------|--------|
| `KIS_ENV` | `mock` | no KIS credential activation |
| `AUTOFOLIO_LOCAL_AUTO_REGISTER` | `0` | no automatic local account creation |
| `AUTOFOLIO_GUEST_DEMO_ENABLED` | `0` | public guest/demo remains disabled |
| `AUTOFOLIO_SSO_MOCK_ENABLED` | `0` | mock SSO opt-in only |
| `AUTOFOLIO_KIS_WS_ENABLE` | `0` | no KIS WebSocket activation |
| `AUTOFOLIO_MEMBERSHIP_PRICE_KRW` | `0` | no real pricing/payment signal in repo |

## Remaining Deploy Blockers

- External platform env vars are still not written.
- Railway backend `$PORT` and `/api/health` readiness still needs TASK-121.
- Supabase migration/RLS/advisor/cross-user evidence still needs Owner/R3 lane.
- Persistent storage strategy still needs TASK-122.
- KIS/payment/provider external boundaries remain blocked.

## Gate

Run:

```powershell
python scripts\membership_staging_env_inventory_gate.py --check
```
