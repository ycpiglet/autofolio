# Autofolio Membership Production Secret Policy

Status: draft policy, not applied to production
Updated: 2026-06-19T19:27:41+09:00
Related: TASK-087, TASK-107, TASK-108, TASK-109, TASK-112, TASK-114

## Purpose

This policy defines how user-owned LLM, SNS/OAuth, KIS credentials, and
Supabase platform keys must be handled before Autofolio can expose
membership-based production use.

The machine-readable source is
`agents/project/MEMBERSHIP-PRODUCTION-SECRET-POLICY.json`. The local gate is:

```powershell
python scripts/membership_secret_policy_gate.py --check
```

This is not a production secret store. It does not read, write, rotate,
validate, or migrate any real secret value.

## Covered Secret Classes

- Supabase publishable keys, allowed in clients only with RLS and
  least-privilege grants.
- Supabase secret keys and legacy service-role keys, backend-only because they
  bypass RLS.
- OpenAI and Anthropic user-owned API keys.
- Telegram bot tokens.
- Google, Naver, Kakao, and X OAuth tokens.
- KIS app keys, app secrets, and access tokens when a future user-owned broker
  credential flow is explicitly approved.

## API Boundary

Secret values are write-only at the API boundary. A request may submit a secret
value to a server-side route, but responses may only include metadata:

- provider id, kind, and auth type;
- configured/enabled status;
- account label and scopes;
- `secret_set` and a masked `secret_hint`;
- timestamps, status, and non-secret message.

Owner/admin support may inspect redacted metadata only. Routine plaintext
secret readback is forbidden.

## Storage Boundary

Platform secrets belong in server runtime secret stores, deployment-platform
secret variables, or Supabase Edge Function secrets. Tenant provider payloads
may use Supabase Vault or an equivalent KMS, but decrypted access must be
server-only and reviewed. Browser code may read only redacted metadata such as
provider id, enabled state, masked hint, secret reference id, and rotation
timestamps.

## Lifecycle

Production implementation must prove these paths before external users:

- write or replace secret;
- disable without delete;
- delete secret material;
- rotate secret material;
- Owner support read of redacted metadata only.

Each path must be server-side, user-scoped from the authenticated session,
CSRF-protected where browser initiated, and audited.

## Forbidden Exposure

Secret material must not appear in:

- browser storage or browser bundles;
- `NEXT_PUBLIC` or equivalent client-prefixed environment variables;
- URLs, logs, task records, reports, screenshots, or generated artifacts;
- raw OAuth events;
- committed `.env` files;
- provider validation or KIS activation flows that lack explicit Owner
  approval.

## Production Launch Gates

External users remain blocked until the policy gate passes and production
implementation proves secret-store selection, encryption key management,
write/redaction/delete tests, rotation tests, audit event schema, provider
OAuth review, KIS credential-scope review, and incident-response runbook.

This policy intentionally keeps the readiness screen separate: policy can pass
while `production_secret_storage` remains blocked.
