-- TASK-087 A4: Trading tenant tables (Postgres DDL — translated from app/database/schema.sql)
-- Status: NOT APPLIED — staging review file only. Do not apply without Owner/R3 approval.
-- Updated: 2026-06-27T02:18:15+09:00
-- Source contracts:
--   app/database/schema.sql (SQLite origin, translated to Postgres)
--   agents/project/MEMBERSHIP-SUPABASE-STAGING-FIELD-MAP.json
--   agents/project/MEMBERSHIP-ENGINE-SAFETY-CONTRACT.json
-- user_id columns are NULLABLE — non-breaking addition for future per-tenant isolation.
-- The actual isolation enforcement is a SEPARATE future initiative; no isolation
-- logic is implemented here beyond column presence and index.
-- No secrets, PII, or real connection strings are present.

-- ---------------------------------------------------------------------------
-- trade_conditions
-- Owner field: user_id (nullable — future isolation initiative)
-- ---------------------------------------------------------------------------
create table public.trade_conditions (
    id                   bigserial   primary key,
    user_id              uuid        references auth.users (id) on delete set null,
    symbol               text        not null,
    side                 text        not null,
    target_price         numeric     not null,
    quantity             int         not null default 1,
    order_type           text        not null default 'LIMIT',
    allow_market_fallback boolean    not null default false,
    auto_enabled         boolean     not null default false,
    status               text        not null default 'ACTIVE',
    cooldown_until       timestamptz,
    created_by           text        not null default 'USER',
    rationale            text,
    risk_note            text,
    created_at           timestamptz not null default now(),
    updated_at           timestamptz not null default now()
);

create index idx_trade_conditions_symbol  on public.trade_conditions (symbol);
create index idx_trade_conditions_user_id on public.trade_conditions (user_id);

-- ---------------------------------------------------------------------------
-- order_intents  (append-only, insert via backend risk gate only)
-- Owner field: user_id (nullable — future isolation initiative)
-- Source: MEMBERSHIP-SUPABASE-STAGING-FIELD-MAP.json tenant_trading entity
-- ---------------------------------------------------------------------------
create table public.order_intents (
    id                  uuid        not null default gen_random_uuid() primary key,
    user_id             uuid        references auth.users (id) on delete set null,
    trade_condition_id  bigint      references public.trade_conditions (id) on delete set null,
    symbol              text        not null,
    side                text        not null,
    order_type          text        not null,
    target_price        numeric,
    quantity            int         not null,
    intent_status       text        not null default 'PENDING',
    created_at          timestamptz not null default now()
);

create index idx_order_intents_user_id on public.order_intents (user_id);

-- ---------------------------------------------------------------------------
-- order_logs  (append-only)
-- Owner field: user_id (nullable — future isolation initiative)
-- ---------------------------------------------------------------------------
create table public.order_logs (
    id                bigserial   primary key,
    user_id           uuid        references auth.users (id) on delete set null,
    order_intent_id   uuid        references public.order_intents (id) on delete set null,
    condition_id      bigint      references public.trade_conditions (id) on delete set null,
    symbol            text        not null,
    side              text        not null,
    order_type        text        not null,
    order_price       numeric,
    current_price     numeric,
    quantity          int         not null,
    kis_order_id      text,
    order_status      text        not null,
    fallback_to_market boolean    not null default false,
    error_message     text,
    created_at        timestamptz not null default now()
);

create index idx_order_logs_symbol_created on public.order_logs (symbol, created_at);
create index idx_order_logs_user_id        on public.order_logs (user_id);

-- ---------------------------------------------------------------------------
-- execution_logs  (append-only)
-- Owner field: user_id (nullable — future isolation initiative)
-- ---------------------------------------------------------------------------
create table public.execution_logs (
    id              bigserial   primary key,
    user_id         uuid        references auth.users (id) on delete set null,
    order_log_id    bigint      not null references public.order_logs (id) on delete cascade,
    symbol          text        not null,
    filled_price    numeric,
    filled_quantity int,
    filled_at       timestamptz not null default now(),
    raw_status      text
);

create index idx_execution_logs_user_id on public.execution_logs (user_id);

-- ---------------------------------------------------------------------------
-- price_alerts
-- Owner field: user_id (nullable — future isolation initiative)
-- ---------------------------------------------------------------------------
create table public.price_alerts (
    id           bigserial   primary key,
    user_id      uuid        references auth.users (id) on delete set null,
    symbol       text        not null,
    target_price numeric     not null,
    direction    text        not null check (direction in ('ABOVE', 'BELOW')),
    active       boolean     not null default true,
    triggered_at timestamptz,
    created_at   timestamptz not null default now()
);

create index idx_price_alerts_user_id on public.price_alerts (user_id);

-- ---------------------------------------------------------------------------
-- trade_journal
-- Owner field: user_id (nullable — future isolation initiative)
-- ---------------------------------------------------------------------------
create table public.trade_journal (
    id           bigserial   primary key,
    user_id      uuid        references auth.users (id) on delete set null,
    order_log_id bigint      references public.order_logs (id) on delete set null,
    symbol       text        not null,
    side         text        not null,
    entry_reason text,
    exit_reason  text,
    grade        text        check (grade in ('A', 'B', 'C', 'D', 'F')),
    lesson       text,
    plan_followed boolean    not null default true,
    emotion_flag  boolean    not null default false,
    created_at   timestamptz not null default now(),
    updated_at   timestamptz not null default now()
);

create index idx_trade_journal_user_id on public.trade_journal (user_id);

-- ---------------------------------------------------------------------------
-- system_state  (global key-value store for engine flags)
-- Owner field: user_id (nullable — future per-tenant isolation)
-- Rows with user_id IS NULL are global/system-level; access is server-only.
-- ---------------------------------------------------------------------------
create table public.system_state (
    id         bigserial   primary key,
    user_id    uuid        references auth.users (id) on delete set null,
    key        text        not null,
    value      text        not null,
    updated_at timestamptz not null default now(),
    unique (user_id, key)
);

create index idx_system_state_user_id on public.system_state (user_id);

-- ---------------------------------------------------------------------------
-- risk_limits  (global/scoped risk caps — translated from SQLite)
-- Owner field: user_id (nullable — future isolation initiative)
-- Distinct from risk_settings (per-user tenant table in 0001).
-- ---------------------------------------------------------------------------
create table public.risk_limits (
    id                      bigserial   primary key,
    user_id                 uuid        references auth.users (id) on delete set null,
    scope                   text        not null default 'GLOBAL',
    symbol                  text,
    max_order_amount        numeric     not null,
    max_daily_amount        numeric     not null,
    max_daily_market_orders int         not null default 1,
    allow_one_share_exception boolean   not null default true,
    updated_at              timestamptz not null default now()
);

create index idx_risk_limits_user_id on public.risk_limits (user_id);
