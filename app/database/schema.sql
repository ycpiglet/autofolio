CREATE TABLE IF NOT EXISTS whitelist_symbols (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    market TEXT NOT NULL DEFAULT 'KRX',
    role TEXT NOT NULL,
    enabled INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS trade_conditions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,
    target_price REAL NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    order_type TEXT NOT NULL DEFAULT 'LIMIT',
    allow_market_fallback INTEGER NOT NULL DEFAULT 0,
    auto_enabled INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    cooldown_until TEXT,
    created_by TEXT NOT NULL DEFAULT 'USER',
    rationale TEXT,
    risk_note TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    condition_id INTEGER REFERENCES trade_conditions(id) ON DELETE SET NULL,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,
    order_type TEXT NOT NULL,
    order_price REAL,
    current_price REAL,
    quantity INTEGER NOT NULL,
    kis_order_id TEXT,
    order_status TEXT NOT NULL,
    fallback_to_market INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS execution_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    order_log_id INTEGER NOT NULL REFERENCES order_logs(id) ON DELETE CASCADE,
    symbol TEXT NOT NULL,
    filled_price REAL,
    filled_quantity INTEGER,
    filled_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    raw_status TEXT
);

CREATE TABLE IF NOT EXISTS system_state (
    key TEXT PRIMARY KEY,
    user_id TEXT,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS risk_limits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    scope TEXT NOT NULL DEFAULT 'GLOBAL',
    symbol TEXT,
    max_order_amount REAL NOT NULL,
    max_daily_amount REAL NOT NULL,
    max_daily_market_orders INTEGER NOT NULL DEFAULT 1,
    allow_one_share_exception INTEGER NOT NULL DEFAULT 1,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_trade_conditions_symbol ON trade_conditions(symbol);
CREATE INDEX IF NOT EXISTS idx_order_logs_symbol_created ON order_logs(symbol, created_at);

CREATE TABLE IF NOT EXISTS price_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    symbol TEXT NOT NULL,
    target_price REAL NOT NULL,
    direction TEXT NOT NULL CHECK(direction IN ('ABOVE', 'BELOW')),
    active INTEGER NOT NULL DEFAULT 1,
    triggered_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS trade_journal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    order_log_id INTEGER REFERENCES order_logs(id) ON DELETE SET NULL,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,
    entry_reason TEXT,
    exit_reason TEXT,
    grade TEXT CHECK(grade IN ('A','B','C','D','F', NULL)),
    lesson TEXT,
    plan_followed INTEGER NOT NULL DEFAULT 1,
    emotion_flag INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS investor_profiles (
    username TEXT PRIMARY KEY,
    survey_version TEXT NOT NULL,
    completed INTEGER NOT NULL DEFAULT 0,
    risk_type TEXT NOT NULL DEFAULT '미완료',
    knowledge_level TEXT NOT NULL DEFAULT '미확인',
    risk_capacity_score REAL NOT NULL DEFAULT 0,
    risk_tolerance_score REAL NOT NULL DEFAULT 0,
    knowledge_score REAL NOT NULL DEFAULT 0,
    experience_score REAL NOT NULL DEFAULT 0,
    time_horizon_score REAL NOT NULL DEFAULT 0,
    automation_comfort_score REAL NOT NULL DEFAULT 0,
    recommended_max_equity_pct INTEGER NOT NULL DEFAULT 0,
    recommended_autonomy_level TEXT NOT NULL DEFAULT 'L0',
    needs_advanced_survey INTEGER NOT NULL DEFAULT 0,
    satisfaction_focus TEXT NOT NULL DEFAULT '[]',
    last_checkin_at TEXT,
    satisfaction_score INTEGER,
    confidence_score INTEGER,
    stress_score INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS investor_survey_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    survey_version TEXT NOT NULL,
    response_json TEXT NOT NULL,
    scores_json TEXT NOT NULL,
    profile_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_investor_survey_responses_user_created
ON investor_survey_responses(username, created_at);

CREATE TABLE IF NOT EXISTS investor_override_acknowledgements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    symbol TEXT,
    action TEXT NOT NULL,
    reason TEXT NOT NULL,
    acknowledgement_text TEXT NOT NULL,
    profile_version TEXT NOT NULL,
    profile_snapshot_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_investor_override_ack_user_created
ON investor_override_acknowledgements(username, created_at);

CREATE TABLE IF NOT EXISTS investor_checkins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    trigger_type TEXT NOT NULL,
    satisfaction_score INTEGER NOT NULL,
    confidence_score INTEGER NOT NULL,
    stress_score INTEGER NOT NULL,
    automation_adjustment TEXT NOT NULL,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_investor_checkins_user_created
ON investor_checkins(username, created_at);

CREATE INDEX IF NOT EXISTS idx_trade_conditions_user_id ON trade_conditions(user_id);
CREATE INDEX IF NOT EXISTS idx_order_logs_user_id ON order_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_execution_logs_user_id ON execution_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_price_alerts_user_id ON price_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_trade_journal_user_id ON trade_journal(user_id);
CREATE INDEX IF NOT EXISTS idx_system_state_user_id ON system_state(user_id);
CREATE INDEX IF NOT EXISTS idx_risk_limits_user_id ON risk_limits(user_id);
