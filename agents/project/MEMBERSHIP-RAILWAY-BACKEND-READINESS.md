# Membership Railway Backend Readiness

Status: local readiness only, not deployed.

TASK-121 reduces the Railway backend blocker from TASK-119 by making the local
container start command honor a platform-provided `PORT` while preserving the
local fallback port.

## Boundary

- No Railway project mutation.
- No Railway environment variable write.
- No deploy, public URL, domain, or service creation.
- No secret, Supabase apply, KIS, payment, order, or risk behavior change.

## Local Readiness

| Item | Value |
|------|-------|
| Dockerfile | `Dockerfile` |
| Host binding | `0.0.0.0` |
| Port binding | `${PORT:-8000}` |
| Healthcheck path | `/api/health` |
| Healthcheck expected body | `{"status":"ok"}` |

## Remaining Blockers

- External platform env values are still not written.
- Supabase migration/RLS/advisor/cross-user evidence remains Owner/R3.
- Persistent storage decision remains TASK-122.
- KIS/payment/provider external boundaries remain blocked.

## Gate

Run:

```powershell
python scripts\membership_railway_backend_readiness_gate.py --check
```
