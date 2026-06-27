import sqlite3
from pathlib import Path

from app.config.settings import settings
from app.database.pg_db import is_postgres_url


def get_connection(db_path: Path | None = None):
    """Return the database connection for the configured backend.

    When ``settings.database_url`` is a Postgres URL → the psycopg adapter
    (``app.database.pg_db``). Otherwise (the default; unset/empty) → the
    SQLite path below, byte-identical to the pre-existing behaviour.
    """
    if is_postgres_url(settings.database_url):
        from app.database import pg_db

        return pg_db.connect(settings.database_url)

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
    SQLite ALTER TABLE does not support IF NOT EXISTS, so we run ADD COLUMN
    and swallow ONLY the "duplicate column name" OperationalError to make this
    re-entrant. Any other OperationalError (e.g. "no such table", disk full)
    is re-raised — silently masking those would leave the columns absent with
    no trace, which is exactly the failure this migration exists to prevent.

    Columns are added unconditionally, regardless of
    AUTOFOLIO_MULTI_TENANT_ENABLED. This is a non-breaking additive change:
    the columns are nullable and no code reads or writes them while the flag
    is OFF, so flag-OFF query results stay byte-identical. Only the schema
    shape (PRAGMA table_info) changes.

    The matching indexes are created HERE, after the columns exist — not in
    schema.sql. On an existing pre-multitenant DB, CREATE TABLE IF NOT EXISTS
    skips the table, so an index DDL referencing user_id in schema.sql would
    crash with "no such column" before this migration could add the column.
    """
    for table, column, col_type in _MULTITENANT_COLUMNS:
        try:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
        except sqlite3.OperationalError as exc:
            if "duplicate column name" not in str(exc).lower():
                raise  # genuine error (missing table, disk full, …) — do not mask
            # column already exists — safe to ignore (re-entrant call)

    # Indexes are created only after every user_id column is guaranteed present.
    for table, column, _col_type in _MULTITENANT_COLUMNS:
        conn.execute(
            f"CREATE INDEX IF NOT EXISTS idx_{table}_{column} ON {table}({column})"
        )


def initialize_database(db_path: Path | None = None) -> None:
    if is_postgres_url(settings.database_url):
        # The Postgres schema is owned by the pre-applied supabase/migrations/*.sql
        # (assume the DB is already migrated). Do NOT run the SQLite-dialect
        # schema.sql / PRAGMA / executescript / ALTER-based migration here.
        return
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
