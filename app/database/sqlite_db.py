import sqlite3
from pathlib import Path

from app.config.settings import settings


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or settings.db_path
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database(db_path: Path | None = None) -> None:
    schema_path = Path(__file__).with_name("schema.sql")
    sql = schema_path.read_text(encoding="utf-8")
    with get_connection(db_path) as conn:
        conn.executescript(sql)
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
