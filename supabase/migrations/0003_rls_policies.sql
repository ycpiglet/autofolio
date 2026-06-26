-- TASK-087 A4: RLS policies for all tenant-owned tables
-- Status: NOT APPLIED — staging review file only. Do not apply without Owner/R3 approval.
-- Updated: 2026-06-27T02:18:15+09:00
-- Source contracts:
--   agents/project/MEMBERSHIP-SUPABASE-STAGING-FIELD-MAP.json (policy names + ownership predicates)
--   agents/project/MEMBERSHIP-SUPABASE-STAGING-MIGRATION-RLS-REVIEW.json (review requirements)
-- Policy names match MEMBERSHIP-SUPABASE-STAGING-FIELD-MAP.json entities[*].policies[*].name exactly.
-- No secrets, PII, or real connection strings are present.

-- ---------------------------------------------------------------------------
-- INVARIANTS (enforced by policy structure)
-- • Every member policy combines TO authenticated with (select auth.uid()).
-- • UPDATE policies include both USING and WITH CHECK.
-- • Append-only tables (approval_events, order_intents, order_logs,
--   execution_logs, audit_events) grant no authenticated UPDATE or DELETE.
-- • anon has no tenant table grants; public pre-auth flows use backend routes.
-- • Service role / secret keys remain server-runtime only.
-- ---------------------------------------------------------------------------

-- ===========================================================================
-- 0001 tables — membership core
-- ===========================================================================

-- profiles ---------------------------------------------------------------
alter table public.profiles enable row level security;

create policy profiles_select_own
    on public.profiles
    for select
    to authenticated
    using ((select auth.uid()) = id);

create policy profiles_insert_own
    on public.profiles
    for insert
    to authenticated
    with check ((select auth.uid()) = id);

create policy profiles_update_own
    on public.profiles
    for update
    to authenticated
    using ((select auth.uid()) = id)
    with check ((select auth.uid()) = id);

-- membership_requests ----------------------------------------------------
alter table public.membership_requests enable row level security;

create policy membership_requests_select_own
    on public.membership_requests
    for select
    to authenticated
    using ((select auth.uid()) = user_id);

create policy membership_requests_insert_own
    on public.membership_requests
    for insert
    to authenticated
    with check ((select auth.uid()) = user_id);

-- deposit_instructions ---------------------------------------------------
alter table public.deposit_instructions enable row level security;

create policy deposit_instructions_select_own
    on public.deposit_instructions
    for select
    to authenticated
    using ((select auth.uid()) = user_id);

-- approval_events  (append-only: select only) ----------------------------
alter table public.approval_events enable row level security;

create policy approval_events_select_own
    on public.approval_events
    for select
    to authenticated
    using (
        (select auth.uid()) = target_user_id
        or (select auth.uid()) = actor_user_id
    );

-- subscription_grants ----------------------------------------------------
alter table public.subscription_grants enable row level security;

create policy subscription_grants_select_own
    on public.subscription_grants
    for select
    to authenticated
    using ((select auth.uid()) = user_id);

-- integration_secret_metadata --------------------------------------------
alter table public.integration_secret_metadata enable row level security;

create policy integration_secret_metadata_select_own
    on public.integration_secret_metadata
    for select
    to authenticated
    using ((select auth.uid()) = user_id);

-- payment_evidence -------------------------------------------------------
alter table public.payment_evidence enable row level security;

create policy payment_evidence_select_own
    on public.payment_evidence
    for select
    to authenticated
    using ((select auth.uid()) = target_user_id);

-- portfolio_accounts -----------------------------------------------------
alter table public.portfolio_accounts enable row level security;

create policy portfolio_accounts_select_own
    on public.portfolio_accounts
    for select
    to authenticated
    using ((select auth.uid()) = user_id);

-- holdings_snapshots -----------------------------------------------------
alter table public.holdings_snapshots enable row level security;

create policy holdings_snapshots_select_own
    on public.holdings_snapshots
    for select
    to authenticated
    using ((select auth.uid()) = user_id);

-- risk_settings (select + update with CHECK) -----------------------------
alter table public.risk_settings enable row level security;

create policy risk_settings_select_own
    on public.risk_settings
    for select
    to authenticated
    using ((select auth.uid()) = user_id);

create policy risk_settings_update_own
    on public.risk_settings
    for update
    to authenticated
    using ((select auth.uid()) = user_id)
    with check ((select auth.uid()) = user_id);

-- engine_state -----------------------------------------------------------
alter table public.engine_state enable row level security;

create policy engine_state_select_own
    on public.engine_state
    for select
    to authenticated
    using ((select auth.uid()) = user_id);

-- engine_run_queue (select + insert) ------------------------------------
alter table public.engine_run_queue enable row level security;

create policy engine_run_queue_select_own
    on public.engine_run_queue
    for select
    to authenticated
    using ((select auth.uid()) = user_id);

create policy engine_run_queue_insert_own
    on public.engine_run_queue
    for insert
    to authenticated
    with check ((select auth.uid()) = user_id);

-- notifications ----------------------------------------------------------
alter table public.notifications enable row level security;

create policy notifications_select_own
    on public.notifications
    for select
    to authenticated
    using ((select auth.uid()) = user_id);

-- audit_events  (append-only: select only) -------------------------------
alter table public.audit_events enable row level security;

create policy audit_events_select_own
    on public.audit_events
    for select
    to authenticated
    using (
        (select auth.uid()) = target_user_id
        or (select auth.uid()) = actor_user_id
    );

-- ===========================================================================
-- 0002 tables — trading tenant
-- ===========================================================================

-- trade_conditions (select + insert + update with CHECK) -----------------
alter table public.trade_conditions enable row level security;

create policy trade_conditions_select_own
    on public.trade_conditions
    for select
    to authenticated
    using ((select auth.uid()) = user_id);

create policy trade_conditions_insert_own
    on public.trade_conditions
    for insert
    to authenticated
    with check ((select auth.uid()) = user_id);

create policy trade_conditions_update_own
    on public.trade_conditions
    for update
    to authenticated
    using ((select auth.uid()) = user_id)
    with check ((select auth.uid()) = user_id);

-- order_intents  (append-only: select only — insert via backend risk gate)
alter table public.order_intents enable row level security;

create policy order_intents_select_own
    on public.order_intents
    for select
    to authenticated
    using ((select auth.uid()) = user_id);

-- order_logs  (append-only: select only) ---------------------------------
alter table public.order_logs enable row level security;

create policy order_logs_select_own
    on public.order_logs
    for select
    to authenticated
    using ((select auth.uid()) = user_id);

-- execution_logs  (append-only: select only) -----------------------------
alter table public.execution_logs enable row level security;

create policy execution_logs_select_own
    on public.execution_logs
    for select
    to authenticated
    using ((select auth.uid()) = user_id);

-- price_alerts -----------------------------------------------------------
-- Not in field map entity list; user_id present for future isolation.
-- RLS guards own rows; server controls creation and triggering.
alter table public.price_alerts enable row level security;

create policy price_alerts_select_own
    on public.price_alerts
    for select
    to authenticated
    using ((select auth.uid()) = user_id);

create policy price_alerts_insert_own
    on public.price_alerts
    for insert
    to authenticated
    with check ((select auth.uid()) = user_id);

create policy price_alerts_update_own
    on public.price_alerts
    for update
    to authenticated
    using ((select auth.uid()) = user_id)
    with check ((select auth.uid()) = user_id);

-- trade_journal ----------------------------------------------------------
-- Not in field map entity list; user_id present for future isolation.
alter table public.trade_journal enable row level security;

create policy trade_journal_select_own
    on public.trade_journal
    for select
    to authenticated
    using ((select auth.uid()) = user_id);

create policy trade_journal_insert_own
    on public.trade_journal
    for insert
    to authenticated
    with check ((select auth.uid()) = user_id);

create policy trade_journal_update_own
    on public.trade_journal
    for update
    to authenticated
    using ((select auth.uid()) = user_id)
    with check ((select auth.uid()) = user_id);

-- system_state -----------------------------------------------------------
-- Global (user_id IS NULL) rows are server-only; member can read own-scoped rows.
-- Not in field map entity list; isolation logic deferred.
alter table public.system_state enable row level security;

create policy system_state_select_own
    on public.system_state
    for select
    to authenticated
    using (user_id is not null and (select auth.uid()) = user_id);

-- risk_limits ------------------------------------------------------------
-- Not in field map entity list; user_id present for future isolation.
-- Global SCOPE rows (user_id IS NULL) are server-managed only.
alter table public.risk_limits enable row level security;

create policy risk_limits_select_own
    on public.risk_limits
    for select
    to authenticated
    using (user_id is not null and (select auth.uid()) = user_id);
