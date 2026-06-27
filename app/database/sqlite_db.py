import sqlite3
from pathlib import Path

from app.config.settings import settings


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or settings.db_path
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    # FK enforcement is per-connection in SQLite — must be set on EVERY connection.
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


_MULTITENANT_COLUMNS: tuple[tuple[str, str, str], ...] = (
    ("trade_conditions", "user_id", "TEXT"),
    ("order_logs",       "user_id", "TEXT"),
    ("execution_logs",   "user_id", "TEXT"),
    ("price_alerts",     "user_id", "TEXT"),
    ("trade_journal",    "user_id", "TEXT"),
    ("system_state",     "user_id", "TEXT"),
    ("risk_limits",      "user_id", "TEXT"),
)


def _apply_multitenant_migration(conn: sqlite3.Connection) -> None:
    """Add user_id columns to trading tables for multi-tenant support.

    Idempotent: safe to call on both fresh and existing databases.
    SQLite ALTER TABLE does not support IF NOT EXISTS; we catch
    OperationalError ('duplicate column name') to make this re-entrant.
    """
    for table, column, col_type in _MULTITENANT_COLUMNS:
        try:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
        except sqlite3.OperationalError:
            pass  # column already exists — safe to ignore


def initialize_database(db_path: Path | None = None) -> None:
    schema_path = Path(__file__).with_name("schema.sql")
    sql = schema_path.read_text(encoding="utf-8")
    with get_connection(db_path) as conn:
        # WAL mode is persistent (survives reconnect); ignored gracefully for :memory: DBs.
        conn.execute("PRAGMA journal_mode=WAL")
        conn.executescript(sql)
        _apply_multitenant_migration(conn)
        _seed_system_state(conn)
        _seed_global_risk_limit(conn)


def _seed_system_state(conn: sqlite3.Connection) -> None:
    defaults = {
        "auto_trading_enabled": "false",
        "kill_switch_active": "false",
        "kis_env": settings.kis_env,
    }
    for key, value in defaults.items():
        conn.execute(
            "INSERT OR IGNORE INTO system_state(key, value) VALUES (?, ?)",
            (key, value),
        )


def _seed_global_risk_limit(conn: sqlite3.Connection) -> None:
    existing = conn.execute(
        "SELECT id FROM risk_limits WHERE scope = 'GLOBAL' LIMIT 1"
    ).fetchone()
    if existing:
        return

    conn.execute(
        '''
        INSERT INTO risk_limits(
            scope, symbol, max_order_amount, max_daily_amount,
            max_daily_market_orders, allow_one_share_exception
        )
        VALUES ('GLOBAL', NULL, ?, ?, 1, 1)
        ''',
        (settings.default_max_order_amount, settings.default_max_daily_amount),
    )
