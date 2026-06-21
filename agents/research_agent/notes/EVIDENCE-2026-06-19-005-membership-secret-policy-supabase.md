---
type: evidence
id: EVIDENCE-2026-06-19-005
status: complete
owner: Research Agent
created_at: 2026-06-19T19:29:22+09:00
tags: [membership, supabase, secrets, production-readiness]
related_tasks: [TASK-087, TASK-107, TASK-109, TASK-112]
---

# EVIDENCE-2026-06-19-005 Membership Secret Policy / Supabase

## Question

What local policy should Autofolio require before converting the local
user-owned LLM/SNS/KIS token harness into production secret storage?

## Sources Checked

- Supabase changelog: `https://supabase.com/changelog`
- Supabase API keys docs:
  `https://supabase.com/docs/guides/getting-started/api-keys`
- Supabase Edge Functions environment variables:
  `https://supabase.com/docs/guides/functions/secrets`
- Supabase Vault docs: `https://supabase.com/docs/guides/database/vault`
- Supabase API security docs:
  `https://supabase.com/docs/guides/api/securing-your-api`
- Supabase product security index:
  `https://supabase.com/docs/guides/security/product-security`
- Supabase platform access control:
  `https://supabase.com/docs/guides/platform/access-control`

## Findings

1. Supabase publishable keys can be exposed in public clients only when RLS and
   least-privilege grants protect exposed data. They identify the app component,
   not the user.
2. Supabase secret keys and legacy service-role keys are backend-only because
   they grant elevated access and bypass RLS. They must not be in browser code,
   source control, public docs, URLs, or logs.
3. Supabase Edge Functions expose secret/service keys as server-side runtime
   secrets, but the same docs state these keys must never be used in a browser.
4. Supabase Vault stores encrypted secrets in Postgres and exposes decrypted
   values through a view. Autofolio must therefore treat decrypted view access
   as a server-only, reviewed path rather than a member-readable table.
5. Supabase platform access control shows that dashboard/API roles can view or
   manage API keys and Edge Function secrets. Production use needs role review,
   not just application code review.

## Application To Autofolio

- Keep current local integration token harness as prototype only.
- Add a separate production secret policy so TASK-087 can distinguish policy
  readiness from actual secret store implementation.
- Require write-only APIs, metadata-only responses, masked hints, no routine
  plaintext admin readback, user-scoped metadata, audited rotation/delete, and
  server-only decrypted access.
- Preserve `can_launch=false` until actual production storage, staging RLS,
  rotation/delete tests, provider/OAuth review, KIS terms review, and deploy
  smoke all pass.

## Limitations

This note is not legal, tax, financial, or production security certification.
No Supabase project was accessed, no secret was read or written, and no
provider/OAuth/KIS call was made.
