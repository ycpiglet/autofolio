-- TASK-087 A4: Membership core entities (Postgres DDL)
-- Status: NOT APPLIED — staging review file only. Do not apply without Owner/R3 approval.
-- Updated: 2026-06-27T02:18:15+09:00
-- Source contracts:
--   agents/project/MEMBERSHIP-PRODUCTION-CONTRACT.json
--   agents/project/MEMBERSHIP-SUPABASE-STAGING-FIELD-MAP.json
--   agents/project/MEMBERSHIP-SUPABASE-STAGING-MIGRATION-RLS-REVIEW.json
--   agents/project/MEMBERSHIP-PAYMENT-EVIDENCE-POLICY.json
--   agents/project/MEMBERSHIP-ENGINE-SAFETY-CONTRACT.json
-- No secrets, PII, real bank values, or connection strings are present.

-- ---------------------------------------------------------------------------
-- profiles
-- Owner field: id (references auth.users)
-- ---------------------------------------------------------------------------
create table public.profiles (
    id          uuid        not null references auth.users (id) on delete cascade,
    display_name text,
    avatar_url  text,
    created_at  timestamptz not null default now(),
    updated_at  timestamptz not null default now(),
    primary key (id)
);

-- ---------------------------------------------------------------------------
-- membership_requests
-- Owner field: user_id
-- Pre-auth intake stays a backend route; user_id nullable for controlled intake.
-- ---------------------------------------------------------------------------
create table public.membership_requests (
    id              uuid        not null default gen_random_uuid() primary key,
    user_id         uuid        references auth.users (id) on delete set null,
    contact_email   text,
    contact_name    text,
    deposit_code    text,
    status          text        not null default 'pending',
    requested_at    timestamptz not null default now(),
    created_at      timestamptz not null default now(),
    updated_at      timestamptz not null default now()
);

create index idx_membership_requests_user_id on public.membership_requests (user_id);

-- ---------------------------------------------------------------------------
-- deposit_instructions
-- Owner field: user_id
-- Real bank account values are runtime/server config, never stored here.
-- ---------------------------------------------------------------------------
create table public.deposit_instructions (
    id            uuid        not null default gen_random_uuid() primary key,
    user_id       uuid        not null references auth.users (id) on delete cascade,
    deposit_code  text        not null,
    amount_krw    bigint      not null,
    currency      text        not null default 'KRW',
    issued_at     timestamptz not null default now(),
    expires_at    timestamptz,
    status        text        not null default 'active',
    created_at    timestamptz not null default now(),
    updated_at    timestamptz not null default now()
);

create index idx_deposit_instructions_user_id on public.deposit_instructions (user_id);

-- ---------------------------------------------------------------------------
-- approval_events  (append-only)
-- Owner fields: target_user_id, actor_user_id
-- ---------------------------------------------------------------------------
create table public.approval_events (
    id                    uuid        not null default gen_random_uuid() primary key,
    target_user_id        uuid        not null references auth.users (id),
    actor_user_id         uuid        not null references auth.users (id),
    event_type            text        not null,
    membership_request_id uuid,
    note                  text,
    occurred_at           timestamptz not null default now()
);

create index idx_approval_events_target_user_id on public.approval_events (target_user_id);
create index idx_approval_events_actor_user_id  on public.approval_events (actor_user_id);

-- ---------------------------------------------------------------------------
-- subscription_grants
-- Owner field: user_id
-- ---------------------------------------------------------------------------
create table public.subscription_grants (
    id          uuid        not null default gen_random_uuid() primary key,
    user_id     uuid        not null references auth.users (id) on delete cascade,
    plan        text        not null,
    granted_by  uuid        references auth.users (id),
    valid_from  timestamptz not null default now(),
    valid_until timestamptz,
    status      text        not null default 'active',
    created_at  timestamptz not null default now(),
    updated_at  timestamptz not null default now()
);

create index idx_subscription_grants_user_id on public.subscription_grants (user_id);

-- ---------------------------------------------------------------------------
-- integration_secret_metadata
-- Owner field: user_id
-- CONSTRAINT: No plaintext secret values are stored. Backend writes metadata only.
-- ---------------------------------------------------------------------------
create table public.integration_secret_metadata (
    id               uuid        not null default gen_random_uuid() primary key,
    user_id          uuid        not null references auth.users (id) on delete cascade,
    integration_type text        not null,
    label            text,
    enabled          boolean     not null default false,
    masked_hint      text,
    last_rotated_at  timestamptz,
    created_at       timestamptz not null default now(),
    updated_at       timestamptz not null default now()
);

create index idx_integration_secret_metadata_user_id on public.integration_secret_metadata (user_id);

-- ---------------------------------------------------------------------------
-- payment_evidence
-- Owner fields: target_user_id, actor_user_id
-- Fields restricted to retained_fields allowlist per MEMBERSHIP-PAYMENT-EVIDENCE-POLICY.json.
-- Raw bank statements and PII are NOT stored.
-- ---------------------------------------------------------------------------
create table public.payment_evidence (
    id                    uuid        not null default gen_random_uuid() primary key,
    membership_request_id uuid,
    target_user_id        uuid        not null references auth.users (id),
    actor_user_id         uuid        not null references auth.users (id),
    approval_event_id     uuid,
    evidence_type         text        not null,
    deposit_code          text,
    amount_krw            bigint,
    currency              text        not null default 'KRW',
    source_type           text        not null,
    source_reference      text,
    masked_excerpt        text,
    confidence            text,
    recorded_at           timestamptz not null default now()
);

create index idx_payment_evidence_target_user_id on public.payment_evidence (target_user_id);

-- ---------------------------------------------------------------------------
-- portfolio_accounts
-- Owner field: user_id
-- ---------------------------------------------------------------------------
create table public.portfolio_accounts (
    id           uuid        not null default gen_random_uuid() primary key,
    user_id      uuid        not null references auth.users (id) on delete cascade,
    account_alias text,
    broker       text,
    account_type text,
    created_at   timestamptz not null default now(),
    updated_at   timestamptz not null default now()
);

create index idx_portfolio_accounts_user_id on public.portfolio_accounts (user_id);

-- ---------------------------------------------------------------------------
-- holdings_snapshots
-- Owner field: user_id
-- ---------------------------------------------------------------------------
create table public.holdings_snapshots (
    id              uuid        not null default gen_random_uuid() primary key,
    user_id         uuid        not null references auth.users (id) on delete cascade,
    account_id      uuid        references public.portfolio_accounts (id) on delete set null,
    snapshot_at     timestamptz not null default now(),
    holdings_json   jsonb       not null default '[]',
    total_value_krw bigint,
    created_at      timestamptz not null default now()
);

create index idx_holdings_snapshots_user_id on public.holdings_snapshots (user_id);

-- ---------------------------------------------------------------------------
-- risk_settings
-- Owner field: user_id
-- Per-user risk limits; backend validates allowed changes; override is audited.
-- ---------------------------------------------------------------------------
create table public.risk_settings (
    id                      uuid        not null default gen_random_uuid() primary key,
    user_id                 uuid        not null references auth.users (id) on delete cascade unique,
    max_order_amount        bigint      not null default 1000000,
    max_daily_amount        bigint      not null default 5000000,
    max_daily_market_orders int         not null default 1,
    allow_one_share_exception boolean   not null default true,
    automation_level        text        not null default 'L0',
    updated_at              timestamptz not null default now()
);

create index idx_risk_settings_user_id on public.risk_settings (user_id);

-- ---------------------------------------------------------------------------
-- engine_state
-- Owner field: user_id
-- Per-user engine flags; no global auto_trading_enabled shared across users.
-- ---------------------------------------------------------------------------
create table public.engine_state (
    id                        uuid        not null default gen_random_uuid() primary key,
    user_id                   uuid        not null references auth.users (id) on delete cascade unique,
    auto_trading_enabled      boolean     not null default false,
    kill_switch_active        boolean     not null default false,
    global_mode               text        not null default 'PAPER',
    consecutive_order_failures int        not null default 0,
    last_run_at               timestamptz,
    updated_at                timestamptz not null default now()
);

create index idx_engine_state_user_id on public.engine_state (user_id);

-- ---------------------------------------------------------------------------
-- engine_run_queue
-- Owner field: user_id
-- Worker claim includes user_id; queue items are not cross-user readable.
-- ---------------------------------------------------------------------------
create table public.engine_run_queue (
    id           uuid        not null default gen_random_uuid() primary key,
    user_id      uuid        not null references auth.users (id) on delete cascade,
    requested_at timestamptz not null default now(),
    claimed_at   timestamptz,
    completed_at timestamptz,
    status       text        not null default 'pending',
    triggered_by text,
    created_at   timestamptz not null default now()
);

create index idx_engine_run_queue_user_id on public.engine_run_queue (user_id);

-- ---------------------------------------------------------------------------
-- notifications
-- Owner field: user_id
-- Destination resolved from same user's integration_secret_metadata.
-- ---------------------------------------------------------------------------
create table public.notifications (
    id                uuid        not null default gen_random_uuid() primary key,
    user_id           uuid        not null references auth.users (id) on delete cascade,
    notification_type text        not null,
    title             text,
    body              text,
    read              boolean     not null default false,
    created_at        timestamptz not null default now()
);

create index idx_notifications_user_id on public.notifications (user_id);

-- ---------------------------------------------------------------------------
-- audit_events  (append-only)
-- Owner fields: target_user_id, actor_user_id
-- All owner/admin cross-tenant actions must append here.
-- ---------------------------------------------------------------------------
create table public.audit_events (
    id              uuid        not null default gen_random_uuid() primary key,
    target_user_id  uuid        not null references auth.users (id),
    actor_user_id   uuid        not null references auth.users (id),
    event_type      text        not null,
    resource_type   text,
    resource_id     uuid,
    detail_json     jsonb,
    occurred_at     timestamptz not null default now()
);

create index idx_audit_events_target_user_id on public.audit_events (target_user_id);
create index idx_audit_events_actor_user_id  on public.audit_events (actor_user_id);
