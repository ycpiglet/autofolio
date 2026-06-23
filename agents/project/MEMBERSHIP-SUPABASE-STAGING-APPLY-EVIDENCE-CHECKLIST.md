# Membership Supabase Staging Apply Evidence Checklist

Status: draft evidence checklist, not applied
Owner: Backend Engineer
Last updated: 2026-06-19T22:02:58+09:00
Related tasks: TASK-087, TASK-119, TASK-122, TASK-123, TASK-124

## Purpose

This checklist defines the evidence a future Owner/R3 Supabase staging apply
lane must capture before external/member staging proceeds.

It did not connect to Supabase, create migrations, execute SQL, download
backups, restore data, run advisors, change Data API grants, write external
environment variables, deploy, publish a URL, or handle secrets.

## Evidence Stages

| Stage | Required Evidence |
|-------|-------------------|
| Pre-apply review | staging project selected, backup/restore plan reviewed, migration/RLS review packet passed, rollback notes reviewed, external env values ready outside repo |
| Apply execution | approved migration created in R3 lane, apply log captured, migration status captured, `can_launch=false` preserved |
| Post-apply security | security advisor output, performance advisor output, Data API grant review, service role server-only review |
| Post-apply isolation | cross-user membership request, integration metadata, anon tenant access, append-only order/audit tests |
| Deploy smoke prerequisite | Railway/Vercel env writes by Owner, backend/frontend health smoke ready, no real KIS/payment activation |

## Boundary

All entries are future evidence names. No external project, database, backup,
advisor, environment, deploy, public URL, secret, production data, KIS/payment/
provider/order/risk boundary was touched.

