---
type: evidence
id: EVIDENCE-2026-06-19-004
status: complete
owner: Research Agent
created_at: 2026-06-19T18:31:09+09:00
tags: [membership, supabase, rls, tenant-isolation]
related_tasks: [TASK-087, TASK-109, TASK-114]
---

# EVIDENCE-2026-06-19-004 Membership Tenant Isolation / Supabase RLS

## Question

What local contract should Autofolio require before converting the verified
membership prototype into Supabase-backed multi-tenant access?

## Sources Checked

- Supabase changelog: `https://supabase.com/changelog.md`
- Supabase RLS docs: `https://supabase.com/docs/guides/database/postgres/row-level-security`
- Supabase API security docs: `https://supabase.com/docs/guides/api/securing-your-api`
- Supabase AI prompt guidance for RLS policies:
  `https://supabase.com/docs/guides/ai-tools/ai-prompts/database-rls-policies`
- Supabase API keys docs:
  `https://supabase.com/docs/guides/getting-started/api-keys`

## Findings

1. Supabase's 2026-04-28 changelog says new public-schema tables may not be
   exposed to the Data API automatically. Autofolio should therefore treat API
   exposure and role grants as explicit launch work, not as an implicit side
   effect of creating tables.
2. Supabase RLS guidance maps requests to `anon` or `authenticated` database
   roles, but role membership alone is not tenant authorization. Autofolio
   member policies need ownership predicates using `auth.uid()` against each
   tenant row's user field.
3. API security guidance keeps RLS separate from Data API grants. A granted
   table without RLS policies can expose more than intended, so all tenant-owned
   tables need RLS before staging or production external users.
4. Supabase RLS policy guidance distinguishes SELECT/INSERT/UPDATE/DELETE
   policy shapes. Autofolio's future UPDATE policies should include both
   `USING` and `WITH CHECK` so users cannot reassign rows.
5. Supabase service-role or secret keys bypass RLS and must remain server-side.
   Autofolio should never rely on browser code or client-side filters as the
   isolation boundary.

## Application To Autofolio

- Keep current local membership flow as a prototype only.
- Add a separate tenant-isolation matrix so TASK-087 can be evaluated by route
  group, surface, invariant, and required cross-user test.
- Preserve `can_launch=false` until actual staging Supabase schema/RLS,
  cross-user isolation tests, secret storage, payment evidence, per-user
  engine/safety, KIS/compliance review, and deploy smoke all pass.

## Limitations

This note is not a legal, tax, financial, or production security certification.
No Supabase project was accessed and no migration was applied.
