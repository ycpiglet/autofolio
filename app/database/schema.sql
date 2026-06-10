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
    condition_id INTEGER,
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
    order_log_id INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    filled_price REAL,
    filled_quantity INTEGER,
    filled_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    raw_status TEXT
);

CREATE TABLE IF NOT EXISTS system_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS risk_limits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    symbol TEXT NOT NULL,
    target_price REAL NOT NULL,
    direction TEXT NOT NULL CHECK(direction IN ('ABOVE', 'BELOW')),
    active INTEGER NOT NULL DEFAULT 1,
    triggered_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS trade_journal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_log_id INTEGER,
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
