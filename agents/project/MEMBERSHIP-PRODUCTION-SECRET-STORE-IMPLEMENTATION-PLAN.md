# Autofolio Membership Production Secret Store Implementation Plan

Status: draft implementation plan, not applied to production
Owner: Backend Engineer
Last updated: 2026-06-19T20:34:52+09:00
Related tasks: TASK-087, TASK-107, TASK-108, TASK-112, TASK-118

## Purpose

This document turns the TASK-112 production secret policy into an
implementation plan for staging review. It does not store, read, rotate,
delete, validate, or migrate any real secret. It does not validate OAuth
callbacks, activate KIS credentials, mutate a Supabase project, apply a
production database change, deploy, or write environment variables.

The machine-readable source is
`agents/project/MEMBERSHIP-PRODUCTION-SECRET-STORE-IMPLEMENTATION-PLAN.json`.
The local gate is:

```powershell
python scripts/membership_secret_store_plan_gate.py --check
```

## Official Source Basis

- Supabase changelog checked on 2026-06-19.
- Supabase Vault docs checked: Vault stores secrets encrypted on disk, but
  decrypted values are available through a database view. Autofolio must keep
  decrypted access server-side and reviewed.
- Supabase Edge Function secrets docs checked: `SUPABASE_SECRET_KEYS` and
  legacy service-role keys are safe only in server-side functions and must
  never be used in a browser because they bypass RLS.
- Supabase API key docs checked: API keys identify application components;
  Auth identifies users. Publishable keys can be client-side only with RLS and
  least-privilege grants; secret keys are backend-only.

## Recommended Architecture

Use two lanes:

| Lane | Candidate | Use | Status |
|------|-----------|-----|--------|
| Platform secrets | Deployment runtime secrets or Supabase Edge Function secrets | backend platform keys and function runtime config | not implemented |
| Tenant user-owned secrets | Supabase Vault or equivalent KMS | user-owned LLM/SNS/OAuth/KIS token payloads | not implemented |
| Tenant metadata | `integration_secret_metadata` or equivalent table | provider id, enabled state, masked hint, secret reference, audit id | not implemented |

Supabase Vault is the default staging candidate because it is already in the
Supabase/Postgres path, but its decrypted view means client access must be
explicitly forbidden and server-side access must be reviewed. An external KMS
remains a future option if compliance, audit, or operational separation
requires it.

## Provider Category Map

| Category | Target Store | Metadata | Validation |
|----------|--------------|----------|------------|
| OpenAI API key | Supabase Vault or equivalent KMS | tenant metadata table | forbidden until Owner-approved provider check |
| Anthropic API key | Supabase Vault or equivalent KMS | tenant metadata table | forbidden until Owner-approved provider check |
| Telegram bot token | Supabase Vault or equivalent KMS | tenant metadata table | forbidden until Owner-approved provider check |
| Google/Naver/Kakao/X OAuth tokens | Supabase Vault or equivalent KMS | tenant metadata table | forbidden until Owner-approved OAuth review |
| KIS app key/secret/access token | Supabase Vault or equivalent KMS | tenant metadata table | blocked until KIS terms and scope review |

All categories are write-only at the API boundary. Responses may include
provider id, auth type, enabled state, masked hint, status, timestamps, and
audit event id. Responses may not include plaintext secret material.

## Future API Boundary

| Operation | Route Shape | Rule |
|-----------|-------------|------|
| Write/replace | `POST /api/integrations/{provider}/secret` | own tenant only, CSRF, metadata response only |
| Rotate | `POST /api/integrations/{provider}/secret/rotate` | creates new reference, tombstones old reference, audit required |
| Disable | `PATCH /api/integrations/{provider}/secret` | blocks worker execution without deleting payload |
| Delete | `DELETE /api/integrations/{provider}/secret` | removes payload material, keeps non-sensitive tombstone |
| Owner support read | `GET /api/membership/admin/integrations/{user_id}/metadata` | redacted metadata only, audit required |

Provider calls must not happen during write/rotate/delete. Provider validation
is a separate Owner/R3-approved workflow.

## Rotation/Delete/Audit Checklist

- Create returns metadata only and records an audit event.
- Rotate replaces the secret reference without plaintext readback.
- Disable blocks execution while retaining payload for possible re-enable.
- Delete removes payload material and leaves only a tombstone or non-sensitive
  metadata.
- Owner support can read redacted metadata only.
- Incident response can disable and rotate affected references without secret
  values appearing in reports, logs, task records, screenshots, or artifacts.

## Required Staging Tests

- Member A cannot read or update Member B secret metadata.
- Secret write/rotate/delete responses never include plaintext material.
- Disabled secret blocks worker execution.
- Owner support cannot read plaintext.
- Logs redact Authorization, apikey, token, password, and secret fields.
- Supabase Vault decrypted view is not exposed to `anon` or normal
  authenticated clients.
- KIS categories stay blocked until terms and scope review is recorded.

## R3 Gates Still Required

- Select and provision the actual secret store.
- Apply and review metadata table RLS plus `WITH CHECK` ownership.
- Configure runtime or Edge Function secrets.
- Execute staging write/rotate/disable/delete tests.
- Review audit event schema and incident response runbook.
- Approve OAuth provider validation and KIS credential scope.

`can_launch=false` must remain true until those gates have direct evidence.
