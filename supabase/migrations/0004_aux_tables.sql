-- TASK: Postgres DDL for SQLite aux tables MISSING from 0001-0003 (auto-trading + investor profile)
-- Status: NOT APPLIED — staging review file only. Do not apply without Owner/R3 approval.
--   The controller applies this via MCP against autofolio-staging and runs the
--   live SQLite/Postgres round-trip verification. The agent does NOT apply it.
-- Updated: 2026-06-27T16:28:25+09:00
-- Source: app/database/schema.sql + app/services/investor_profile.py (SQLite origin),
--         translated to Postgres (INTEGER PK AUTOINCREMENT -> bigserial, REAL -> numeric,
--         TEXT timestamps -> timestamptz, INTEGER bool -> boolean where the writer is portable).
-- No secrets, PII, or real connection strings are present.
--
-- NOTE ON `skips`: the original task list named a `skips` table, but no such
-- table exists in the codebase. That entry came from a comment in schema.sql
-- ("CREATE TABLE IF NOT EXISTS skips the table") that a grep matched as a table
-- name. There is nothing to create; the real missing tables are the five below.
--
-- OWNERSHIP / RLS: these are owner/service-managed config + single-owner
-- personalization tables. They have NO `auth.users` uuid owner column
-- (whitelist is global config; the investor_* tables key on a TEXT `username`,
-- not an auth uuid), so the member-scoped `auth.uid() = user_id` RLS pattern
-- from 0003 does not apply. RLS is ENABLED with no member-facing policies:
-- authenticated/anon get no access; the server-runtime backend connection (the
-- table owner / service role, which is not subject to RLS unless FORCE RLS is
-- set — it is not) manages all reads and writes. This matches the 0003
-- invariant that global / server-only data is server-runtime only.

-- ---------------------------------------------------------------------------
-- whitelist_symbols  (global tradable-universe config)
-- UNIQUE (symbol) is required by the repository's ON CONFLICT(symbol) upsert.
-- `enabled` is boolean: the repository (repositories.py) binds a Python bool
-- and filters with `WHERE enabled`, so boolean is portable here.
-- ---------------------------------------------------------------------------
create table if not exists public.whitelist_symbols (
    id         bigserial   primary key,
    symbol     text        not null unique,
    name       text        not null,
    market     text        not null default 'KRX',
    role       text        not null,
    enabled    boolean     not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

alter table public.whitelist_symbols enable row level security;

-- ---------------------------------------------------------------------------
-- investor_profiles  (single-owner personalization; PK = username TEXT)
-- `completed` and `needs_advanced_survey` are kept as INTEGER (0/1), NOT
-- boolean: their writer (app/services/investor_profile.py) is OUTSIDE this
-- task's touch scope and binds integer literals (`completed = 1`,
-- `int(needs_advanced_survey)`), so integer preserves that unmodified writer.
-- ON CONFLICT(username) (used by the writer) is portable against this PK.
-- ---------------------------------------------------------------------------
create table if not exists public.investor_profiles (
    username                   text        primary key,
    survey_version             text        not null,
    completed                  integer     not null default 0,
    risk_type                  text        not null default '미완료',
    knowledge_level            text        not null default '미확인',
    risk_capacity_score        numeric     not null default 0,
    risk_tolerance_score       numeric     not null default 0,
    knowledge_score            numeric     not null default 0,
    experience_score           numeric     not null default 0,
    time_horizon_score         numeric     not null default 0,
    automation_comfort_score   numeric     not null default 0,
    recommended_max_equity_pct integer     not null default 0,
    recommended_autonomy_level text        not null default 'L0',
    needs_advanced_survey      integer     not null default 0,
    satisfaction_focus         text        not null default '[]',
    last_checkin_at            timestamptz,
    satisfaction_score         integer,
    confidence_score           integer,
    stress_score               integer,
    created_at                 timestamptz not null default now(),
    updated_at                 timestamptz not null default now(),
    completed_at               timestamptz
);

alter table public.investor_profiles enable row level security;

-- ---------------------------------------------------------------------------
-- investor_survey_responses  (append-only survey snapshots)
-- *_json columns stay TEXT: the service stores json.dumps() strings and reads
-- them back with json.loads(), so jsonb would change the round-tripped type.
-- ---------------------------------------------------------------------------
create table if not exists public.investor_survey_responses (
    id             bigserial   primary key,
    username       text        not null,
    survey_version text        not null,
    response_json  text        not null,
    scores_json    text        not null,
    profile_json   text        not null,
    created_at     timestamptz not null default now()
);

create index if not exists idx_investor_survey_responses_user_created
    on public.investor_survey_responses (username, created_at);

alter table public.investor_survey_responses enable row level security;

-- ---------------------------------------------------------------------------
-- investor_override_acknowledgements  (append-only override audit)
-- ---------------------------------------------------------------------------
create table if not exists public.investor_override_acknowledgements (
    id                    bigserial   primary key,
    username              text        not null,
    symbol                text,
    action                text        not null,
    reason                text        not null,
    acknowledgement_text  text        not null,
    profile_version       text        not null,
    profile_snapshot_json text        not null,
    created_at            timestamptz not null default now()
);

create index if not exists idx_investor_override_ack_user_created
    on public.investor_override_acknowledgements (username, created_at);

alter table public.investor_override_acknowledgements enable row level security;

-- ---------------------------------------------------------------------------
-- investor_checkins  (append-only periodic check-ins)
-- ---------------------------------------------------------------------------
create table if not exists public.investor_checkins (
    id                    bigserial   primary key,
    username              text        not null,
    trigger_type          text        not null,
    satisfaction_score    integer     not null,
    confidence_score      integer     not null,
    stress_score          integer     not null,
    automation_adjustment text        not null,
    notes                 text,
    created_at            timestamptz not null default now()
);

create index if not exists idx_investor_checkins_user_created
    on public.investor_checkins (username, created_at);

alter table public.investor_checkins enable row level security;

-- ---------------------------------------------------------------------------
-- system_state upsert support (corrective index for 0002)
-- 0002 created public.system_state with UNIQUE (user_id, key). The repository
-- (Repository.set_system_state) only ever writes GLOBAL rows (user_id stays
-- NULL), and PostgreSQL's default NULLS-DISTINCT unique would treat every such
-- row as unique — so `ON CONFLICT (user_id, key)` would never dedupe global
-- keys and the upsert would silently insert duplicates. This partial unique
-- index makes `key` unique among the global rows the repository writes, and is
-- the arbiter inferred by the PG branch's
-- `ON CONFLICT (key) WHERE user_id IS NULL DO UPDATE` in repositories.py.
-- ---------------------------------------------------------------------------
create unique index if not exists system_state_global_key_key
    on public.system_state (key)
    where user_id is null;
