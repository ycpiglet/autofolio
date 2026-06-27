-- 0005_seed_global_config.sql
-- Purpose  : Seed global config + tradable universe that SQLite initialize_database() provides
--            but was MISSING on Postgres (PG schema comes from supabase/migrations/, which
--            only contained DDL — no seed data).  This migration brings a fresh PG DB to
--            parity with a fresh SQLite DB seeded by app/database/sqlite_db.py.
-- Status   : NOT APPLIED by the agent. The controller applies this via MCP.
-- Updated  : 2026-06-27T23:01:29+09:00
-- No secrets, PII, or real connection strings are present.
--
-- SQLite parity sources
--   app/database/sqlite_db._seed_system_state()   → system_state rows
--   app/database/sqlite_db._seed_global_risk_limit() → risk_limits GLOBAL row
--   app/services/backend._SEED (30 entries)       → whitelist_symbols rows
--   app/config/settings  default_max_order_amount=100000.0 / default_max_daily_amount=300000.0
--
-- Idempotency
--   whitelist_symbols   : ON CONFLICT (symbol) DO NOTHING  (UNIQUE symbol)
--   system_state        : ON CONFLICT (key) WHERE user_id IS NULL DO NOTHING
--                         (uses partial index system_state_global_key_key from 0004)
--   risk_limits GLOBAL  : INSERT … SELECT … WHERE NOT EXISTS (no unique constraint; mirrors
--                         the SQLite guard: "if existing: return")

-- ---------------------------------------------------------------------------
-- 1. whitelist_symbols  (30 symbols — source: app/services/backend._SEED)
--    All rows: market='KRX', enabled=true, role per _SEED tuple element 3.
-- ---------------------------------------------------------------------------
insert into public.whitelist_symbols (symbol, name, market, role, enabled)
values
    -- KR 대형주 (25 종목)
    ('005930', '삼성전자',       'KRX', 'LARGE_CAP', true),
    ('000660', 'SK하이닉스',     'KRX', 'LARGE_CAP', true),
    ('005380', '현대차',         'KRX', 'LARGE_CAP', true),
    ('005490', 'POSCO홀딩스',    'KRX', 'LARGE_CAP', true),
    ('035420', 'NAVER',          'KRX', 'LARGE_CAP', true),
    ('035720', '카카오',         'KRX', 'LARGE_CAP', true),
    ('051910', 'LG화학',         'KRX', 'LARGE_CAP', true),
    ('006400', '삼성SDI',        'KRX', 'LARGE_CAP', true),
    ('068270', '셀트리온',       'KRX', 'LARGE_CAP', true),
    ('000270', '기아',           'KRX', 'LARGE_CAP', true),
    ('105560', 'KB금융',         'KRX', 'LARGE_CAP', true),
    ('055550', '신한지주',       'KRX', 'LARGE_CAP', true),
    ('086790', '하나금융지주',   'KRX', 'LARGE_CAP', true),
    ('012330', '현대모비스',     'KRX', 'LARGE_CAP', true),
    ('028260', '삼성물산',       'KRX', 'LARGE_CAP', true),
    ('066570', 'LG전자',         'KRX', 'LARGE_CAP', true),
    ('096770', 'SK이노베이션',   'KRX', 'LARGE_CAP', true),
    ('034730', 'SK',             'KRX', 'LARGE_CAP', true),
    ('015760', '한국전력',       'KRX', 'LARGE_CAP', true),
    ('017670', 'SK텔레콤',       'KRX', 'LARGE_CAP', true),
    ('009150', '삼성전기',       'KRX', 'LARGE_CAP', true),
    ('010130', '고려아연',       'KRX', 'LARGE_CAP', true),
    ('207940', '삼성바이오로직스', 'KRX', 'LARGE_CAP', true),
    ('373220', 'LG에너지솔루션', 'KRX', 'LARGE_CAP', true),
    ('000810', '삼성화재',       'KRX', 'LARGE_CAP', true),
    -- ETF (5 종목)
    ('069500', 'KODEX 200',          'KRX', 'ETF', true),
    ('102110', 'TIGER 200',          'KRX', 'ETF', true),
    ('360750', 'TIGER 미국S&P500',   'KRX', 'ETF', true),
    ('114260', 'KODEX 국고채3년',    'KRX', 'ETF', true),
    ('133690', 'TIGER 미국나스닥100','KRX', 'ETF', true)
on conflict (symbol) do nothing;

-- ---------------------------------------------------------------------------
-- 2. risk_limits  (GLOBAL row — source: sqlite_db._seed_global_risk_limit)
--    user_id=NULL identifies the GLOBAL scope (mirrors SQLite: no user_id col).
--    Guard: WHERE NOT EXISTS replicates SQLite's "if existing: return" check.
--    Default values from app/config/settings:
--      default_max_order_amount = 100000.0
--      default_max_daily_amount = 300000.0
-- ---------------------------------------------------------------------------
insert into public.risk_limits (
    scope,
    symbol,
    max_order_amount,
    max_daily_amount,
    max_daily_market_orders,
    allow_one_share_exception
)
select
    'GLOBAL',
    null,
    100000.0,
    300000.0,
    1,
    true
where not exists (
    select 1 from public.risk_limits
    where scope = 'GLOBAL' and user_id is null
);

-- ---------------------------------------------------------------------------
-- 3. system_state  (global default keys — source: sqlite_db._seed_system_state)
--    user_id=NULL = global/system rows (same pattern as 0002 + 0004).
--    Conflict target: partial index system_state_global_key_key (0004).
--    Keys seeded (SQLite _seed_system_state defaults):
--      auto_trading_enabled  = 'false'
--      kill_switch_active    = 'false'
--      kis_env               = 'paper'  (settings.kis_env default)
-- ---------------------------------------------------------------------------
insert into public.system_state (user_id, key, value)
values
    (null, 'auto_trading_enabled', 'false'),
    (null, 'kill_switch_active',   'false'),
    (null, 'kis_env',              'paper')
on conflict (key) where user_id is null do nothing;
