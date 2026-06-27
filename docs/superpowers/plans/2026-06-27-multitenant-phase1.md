# Multitenant Engine Phase 1 — Repository Query Scoping

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add nullable `user_id` columns to 7 trading tables and make the repository layer tenant-aware behind `AUTOFOLIO_MULTI_TENANT_ENABLED` (default OFF), with byte-identical flag-OFF behavior.

**Architecture:** Schema gets `user_id TEXT` nullable columns (+ indexes) via `schema.sql` for fresh DBs and an idempotent `ALTER TABLE` migration in `sqlite_db.py` for existing DBs. Repository methods gain an optional `user_id=None` parameter; when `flags.multi_tenant_enabled() and user_id is not None`, the SQL adds `WHERE user_id = ?` (or `AND user_id = ?`). When the flag is OFF (default), the new parameter is entirely ignored and the original SQL executes byte-for-byte.

**Tech Stack:** Python 3.10, SQLite (`sqlite3`), `pytest`, feature flag in `app/services/flags.py`

## Global Constraints

- Flag `AUTOFOLIO_MULTI_TENANT_ENABLED` default OFF — flag-OFF path must be byte-identical to pre-change behavior.
- Do NOT change callers (services/engine) to pass user_id — that is Phase 2/3.
- Do NOT set flag ON in any non-test code.
- Do NOT apply Supabase migrations.
- Do NOT touch kill-switch, order approval flow, or risk-gate policy values.
- `order_intents` table does NOT exist in SQLite schema — skip it.
- `system_state` PKC (`key TEXT PRIMARY KEY`) prevents per-user key composite — add column only, no scoping of `get/set_system_state` in Phase 1.
- `risk_limits` scoping is Phase 2 — add column only, no scoping of `get/update_global_risk_limit` in Phase 1.
- Branch: `feat/multitenant-phase1` (already checked out).
- Commit message: `feat(multitenant): Phase 1 — 레포 쿼리 user_id 스코핑(flag-gated, default-OFF byte-identical)`.

---

## File Map

| File | Change |
|------|--------|
| `app/database/schema.sql` | Add `user_id TEXT` columns + indexes to 7 tables |
| `app/database/sqlite_db.py` | Add `_apply_multitenant_migration()` + call from `initialize_database()` |
| `app/database/repositories.py` | Add `user_id=None` to 14 methods; flag-gated scoping |
| `tests/unit/test_multitenant_repository.py` | New: flag-ON scoping tests |

---

### Task 1: Schema — add user_id columns to trading tables

**Files:**
- Modify: `app/database/schema.sql`

**Interfaces:**
- Produces: 7 tables each gain `user_id TEXT` nullable column + `CREATE INDEX IF NOT EXISTS idx_<table>_user_id`

- [ ] **Step 1: Edit `app/database/schema.sql`** — add `user_id TEXT,` as the second column (after `id`) in each of these 7 `CREATE TABLE IF NOT EXISTS` blocks, plus indexes after the table definition.

Tables and additions:
```sql
-- trade_conditions: add after "id INTEGER PRIMARY KEY AUTOINCREMENT,"
    user_id TEXT,

-- order_logs: add after "id INTEGER PRIMARY KEY AUTOINCREMENT,"
    user_id TEXT,

-- execution_logs: add after "id INTEGER PRIMARY KEY AUTOINCREMENT,"
    user_id TEXT,

-- price_alerts: add after "id INTEGER PRIMARY KEY AUTOINCREMENT,"
    user_id TEXT,

-- trade_journal: add after "id INTEGER PRIMARY KEY AUTOINCREMENT,"
    user_id TEXT,

-- system_state: add after "key TEXT PRIMARY KEY,"
    user_id TEXT,

-- risk_limits: add after "id INTEGER PRIMARY KEY AUTOINCREMENT,"
    user_id TEXT,
```

After all existing indexes, add:
```sql
CREATE INDEX IF NOT EXISTS idx_trade_conditions_user_id ON trade_conditions(user_id);
CREATE INDEX IF NOT EXISTS idx_order_logs_user_id ON order_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_execution_logs_user_id ON execution_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_price_alerts_user_id ON price_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_trade_journal_user_id ON trade_journal(user_id);
CREATE INDEX IF NOT EXISTS idx_system_state_user_id ON system_state(user_id);
CREATE INDEX IF NOT EXISTS idx_risk_limits_user_id ON risk_limits(user_id);
```

- [ ] **Step 2: Verify schema is valid** — open a Python REPL and check:
```python
import sqlite3, pathlib
sql = pathlib.Path("app/database/schema.sql").read_text()
conn = sqlite3.connect(":memory:")
conn.executescript(sql)
cols = conn.execute("PRAGMA table_info(trade_conditions)").fetchall()
assert any(c[1] == "user_id" for c in cols), "user_id missing from trade_conditions"
print("Schema OK")
```

---

### Task 2: Idempotent migration for existing DBs

**Files:**
- Modify: `app/database/sqlite_db.py`

**Interfaces:**
- Consumes: `get_connection(db_path)` already defined
- Produces: `_apply_multitenant_migration(conn)` — idempotent, adds `user_id TEXT` to 7 tables if not present; called from `initialize_database()`

- [ ] **Step 1: Write failing test** — add to `tests/unit/test_multitenant_repository.py`:
```python
"""Multitenant Phase 1: schema migration + repository scoping tests."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from app.database.repositories import Repository, WhitelistSymbol
from app.database.sqlite_db import initialize_database, get_connection


@pytest.fixture
def repo(tmp_path):
    db = tmp_path / "test.db"
    initialize_database(db)
    return Repository(db), db


def test_user_id_column_exists_in_all_trading_tables(repo):
    """After initialize_database, all 7 tables must have a user_id column."""
    _, db = repo
    tables = [
        "trade_conditions", "order_logs", "execution_logs",
        "price_alerts", "trade_journal", "system_state", "risk_limits",
    ]
    with get_connection(db) as conn:
        for table in tables:
            info = conn.execute(f"PRAGMA table_info({table})").fetchall()
            col_names = [row[1] for row in info]
            assert "user_id" in col_names, f"user_id missing from {table}"


def test_migration_is_idempotent_on_existing_db(tmp_path):
    """Calling initialize_database twice does not raise (migration is idempotent)."""
    db = tmp_path / "existing.db"
    initialize_database(db)
    initialize_database(db)  # second call — must not raise
    with get_connection(db) as conn:
        info = conn.execute("PRAGMA table_info(trade_conditions)").fetchall()
        col_names = [row[1] for row in info]
        assert "user_id" in col_names
```

- [ ] **Step 2: Run test to confirm failure**:
```bash
python -m pytest tests/unit/test_multitenant_repository.py::test_user_id_column_exists_in_all_trading_tables -v
```
Expected: FAIL (user_id columns not added yet for existing DB path)

- [ ] **Step 3: Implement `_apply_multitenant_migration` in `sqlite_db.py`**:

Add this function BEFORE `initialize_database`:
```python
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
```

And call it in `initialize_database` AFTER `conn.executescript(sql)`:
```python
def initialize_database(db_path: Path | None = None) -> None:
    schema_path = Path(__file__).with_name("schema.sql")
    sql = schema_path.read_text(encoding="utf-8")
    with get_connection(db_path) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.executescript(sql)
        _apply_multitenant_migration(conn)   # <-- add this line
        _seed_system_state(conn)
        _seed_global_risk_limit(conn)
```

- [ ] **Step 4: Run tests to confirm pass**:
```bash
python -m pytest tests/unit/test_multitenant_repository.py::test_user_id_column_exists_in_all_trading_tables tests/unit/test_multitenant_repository.py::test_migration_is_idempotent_on_existing_db -v
```
Expected: PASS

---

### Task 3: Repository — tenant-aware INSERT methods

**Files:**
- Modify: `app/database/repositories.py`

**Interfaces:**
- Consumes: `flags.multi_tenant_enabled()` from `app.services.flags`
- Produces: 5 INSERT methods accept `user_id: str | None = None`; when `flags.multi_tenant_enabled() and user_id is not None`, the INSERT includes the user_id column. Otherwise: byte-identical SQL.

- [ ] **Step 1: Add `flags` import to repositories.py** at the top (after existing imports):
```python
from app.services import flags
```

- [ ] **Step 2: Update `add_trade_condition`** — add `user_id: str | None = None` keyword arg; branch on flag:
```python
def add_trade_condition(
    self,
    *,
    symbol: str,
    side: str,
    target_price: float,
    quantity: int,
    order_type: str = "LIMIT",
    allow_market_fallback: bool = False,
    auto_enabled: bool = False,
    created_by: str = "USER",
    rationale: str | None = None,
    risk_note: str | None = None,
    user_id: str | None = None,
) -> int:
    with get_connection(self.db_path) as conn:
        if flags.multi_tenant_enabled() and user_id is not None:
            cur = conn.execute(
                '''
                INSERT INTO trade_conditions(
                    user_id, symbol, side, target_price, quantity, order_type,
                    allow_market_fallback, auto_enabled, created_by,
                    rationale, risk_note
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    user_id,
                    symbol,
                    side,
                    target_price,
                    quantity,
                    order_type,
                    int(allow_market_fallback),
                    int(auto_enabled),
                    created_by,
                    rationale,
                    risk_note,
                ),
            )
        else:
            cur = conn.execute(
                '''
                INSERT INTO trade_conditions(
                    symbol, side, target_price, quantity, order_type,
                    allow_market_fallback, auto_enabled, created_by,
                    rationale, risk_note
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    symbol,
                    side,
                    target_price,
                    quantity,
                    order_type,
                    int(allow_market_fallback),
                    int(auto_enabled),
                    created_by,
                    rationale,
                    risk_note,
                ),
            )
        return int(cur.lastrowid)
```

- [ ] **Step 3: Update `create_order_log`** — add `user_id: str | None = None` keyword arg; branch on flag:
```python
def create_order_log(
    self,
    *,
    condition_id: int | None,
    symbol: str,
    side: str,
    order_type: str,
    order_price: float | None,
    current_price: float | None,
    quantity: int,
    kis_order_id: str | None,
    order_status: str,
    fallback_to_market: bool = False,
    error_message: str | None = None,
    user_id: str | None = None,
) -> int:
    with get_connection(self.db_path) as conn:
        if flags.multi_tenant_enabled() and user_id is not None:
            cur = conn.execute(
                '''
                INSERT INTO order_logs(
                    user_id, condition_id, symbol, side, order_type, order_price,
                    current_price, quantity, kis_order_id, order_status,
                    fallback_to_market, error_message
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    user_id,
                    condition_id,
                    symbol,
                    side,
                    order_type,
                    order_price,
                    current_price,
                    quantity,
                    kis_order_id,
                    order_status,
                    int(fallback_to_market),
                    error_message,
                ),
            )
        else:
            cur = conn.execute(
                '''
                INSERT INTO order_logs(
                    condition_id, symbol, side, order_type, order_price,
                    current_price, quantity, kis_order_id, order_status,
                    fallback_to_market, error_message
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    condition_id,
                    symbol,
                    side,
                    order_type,
                    order_price,
                    current_price,
                    quantity,
                    kis_order_id,
                    order_status,
                    int(fallback_to_market),
                    error_message,
                ),
            )
        return int(cur.lastrowid)
```

- [ ] **Step 4: Update `create_execution_log`** — add `user_id: str | None = None` keyword arg:
```python
def create_execution_log(
    self,
    *,
    order_log_id: int,
    symbol: str,
    filled_price: float | None,
    filled_quantity: int | None,
    raw_status: str | None = None,
    user_id: str | None = None,
) -> int:
    with get_connection(self.db_path) as conn:
        if flags.multi_tenant_enabled() and user_id is not None:
            cur = conn.execute(
                '''
                INSERT INTO execution_logs(
                    user_id, order_log_id, symbol, filled_price, filled_quantity, raw_status
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ''',
                (user_id, order_log_id, symbol, filled_price, filled_quantity, raw_status),
            )
        else:
            cur = conn.execute(
                '''
                INSERT INTO execution_logs(
                    order_log_id, symbol, filled_price, filled_quantity, raw_status
                )
                VALUES (?, ?, ?, ?, ?)
                ''',
                (order_log_id, symbol, filled_price, filled_quantity, raw_status),
            )
        return int(cur.lastrowid)
```

- [ ] **Step 5: Update `add_price_alert`** — add `user_id: str | None = None`:
```python
def add_price_alert(self, symbol: str, target_price: float, direction: str, *, user_id: str | None = None) -> int:
    with get_connection(self.db_path) as conn:
        if flags.multi_tenant_enabled() and user_id is not None:
            cur = conn.execute(
                'INSERT INTO price_alerts(user_id, symbol, target_price, direction) VALUES(?,?,?,?)',
                (user_id, symbol, target_price, direction.upper()),
            )
        else:
            cur = conn.execute(
                'INSERT INTO price_alerts(symbol, target_price, direction) VALUES(?,?,?)',
                (symbol, target_price, direction.upper()),
            )
        return cur.lastrowid
```

- [ ] **Step 6: Update `add_journal_entry`** — add `user_id: str | None = None` keyword arg:
```python
def add_journal_entry(
    self, symbol: str, side: str, *,
    order_log_id: int | None = None,
    entry_reason: str = "",
    exit_reason: str = "",
    grade: str | None = None,
    lesson: str = "",
    plan_followed: bool = True,
    emotion_flag: bool = False,
    user_id: str | None = None,
) -> int:
    with get_connection(self.db_path) as conn:
        if flags.multi_tenant_enabled() and user_id is not None:
            cur = conn.execute(
                """INSERT INTO trade_journal
                    (user_id, order_log_id, symbol, side, entry_reason, exit_reason,
                     grade, lesson, plan_followed, emotion_flag)
                    VALUES(?,?,?,?,?,?,?,?,?,?)""",
                (user_id, order_log_id, symbol, side, entry_reason, exit_reason,
                 grade, lesson, int(plan_followed), int(emotion_flag)),
            )
        else:
            cur = conn.execute(
                """INSERT INTO trade_journal
                    (order_log_id, symbol, side, entry_reason, exit_reason,
                     grade, lesson, plan_followed, emotion_flag)
                    VALUES(?,?,?,?,?,?,?,?,?)""",
                (order_log_id, symbol, side, entry_reason, exit_reason,
                 grade, lesson, int(plan_followed), int(emotion_flag)),
            )
        return cur.lastrowid
```

---

### Task 4: Repository — tenant-aware LIST/AGGREGATE methods

**Files:**
- Modify: `app/database/repositories.py`

**Interfaces:**
- Produces: 9 list/aggregate methods accept `user_id: str | None = None`; when flag ON + user_id, SQL gains `WHERE/AND user_id = ?`. Flag OFF → byte-identical original SQL.

- [ ] **Step 1: Update `list_active_conditions`**:
```python
def list_active_conditions(self, *, user_id: str | None = None) -> list[dict[str, Any]]:
    if flags.multi_tenant_enabled() and user_id is not None:
        sql = "SELECT * FROM trade_conditions WHERE status = 'ACTIVE' AND user_id = ? ORDER BY id"
        params: list[Any] = [user_id]
    else:
        sql = "SELECT * FROM trade_conditions WHERE status = 'ACTIVE' ORDER BY id"
        params = []
    with get_connection(self.db_path) as conn:
        return [dict(row) for row in conn.execute(sql, params).fetchall()]
```

- [ ] **Step 2: Update `list_conditions`**:
```python
def list_conditions(self, *, user_id: str | None = None) -> list[dict[str, Any]]:
    if flags.multi_tenant_enabled() and user_id is not None:
        sql = "SELECT * FROM trade_conditions WHERE user_id = ? ORDER BY id DESC"
        params: list[Any] = [user_id]
    else:
        sql = "SELECT * FROM trade_conditions ORDER BY id DESC"
        params = []
    with get_connection(self.db_path) as conn:
        return [dict(row) for row in conn.execute(sql, params).fetchall()]
```

- [ ] **Step 3: Update `list_order_logs`**:
```python
def list_order_logs(self, limit: int = 100, *, user_id: str | None = None) -> list[dict[str, Any]]:
    scope = flags.multi_tenant_enabled() and user_id is not None
    if scope:
        sql = '''
            SELECT
                ol.*,
                ex.filled_price,
                ex.filled_quantity,
                ex.filled_at
            FROM order_logs ol
            LEFT JOIN (
                SELECT
                    order_log_id,
                    CASE
                        WHEN SUM(COALESCE(filled_quantity, 0)) > 0
                        THEN SUM(COALESCE(filled_price, 0) * COALESCE(filled_quantity, 0))
                             / SUM(COALESCE(filled_quantity, 0))
                        ELSE MAX(filled_price)
                    END AS filled_price,
                    SUM(COALESCE(filled_quantity, 0)) AS filled_quantity,
                    MAX(filled_at) AS filled_at
                FROM execution_logs
                GROUP BY order_log_id
            ) ex ON ex.order_log_id = ol.id
            WHERE ol.user_id = ?
            ORDER BY ol.id DESC LIMIT ?
        '''
        params: list[Any] = [user_id, limit]
    else:
        sql = '''
            SELECT
                ol.*,
                ex.filled_price,
                ex.filled_quantity,
                ex.filled_at
            FROM order_logs ol
            LEFT JOIN (
                SELECT
                    order_log_id,
                    CASE
                        WHEN SUM(COALESCE(filled_quantity, 0)) > 0
                        THEN SUM(COALESCE(filled_price, 0) * COALESCE(filled_quantity, 0))
                             / SUM(COALESCE(filled_quantity, 0))
                        ELSE MAX(filled_price)
                    END AS filled_price,
                    SUM(COALESCE(filled_quantity, 0)) AS filled_quantity,
                    MAX(filled_at) AS filled_at
                FROM execution_logs
                GROUP BY order_log_id
            ) ex ON ex.order_log_id = ol.id
            ORDER BY ol.id DESC LIMIT ?
        '''
        params = [limit]
    with get_connection(self.db_path) as conn:
        return [dict(row) for row in conn.execute(sql, params).fetchall()]
```

- [ ] **Step 4: Update `today_order_amount`**:
```python
def today_order_amount(self, *, user_id: str | None = None) -> float:
    if flags.multi_tenant_enabled() and user_id is not None:
        sql = '''
            SELECT COALESCE(SUM(COALESCE(order_price, current_price, 0) * quantity), 0) AS amount
            FROM order_logs
            WHERE DATE(created_at, '+9 hours') = DATE('now', '+9 hours')
              AND order_status IN ('REQUESTED', 'FILLED', 'PENDING')
              AND user_id = ?
        '''
        params: list[Any] = [user_id]
    else:
        sql = '''
            SELECT COALESCE(SUM(COALESCE(order_price, current_price, 0) * quantity), 0) AS amount
            FROM order_logs
            WHERE DATE(created_at, '+9 hours') = DATE('now', '+9 hours')
              AND order_status IN ('REQUESTED', 'FILLED', 'PENDING')
        '''
        params = []
    with get_connection(self.db_path) as conn:
        row = conn.execute(sql, params).fetchone()
        return float(row["amount"] or 0.0)
```

- [ ] **Step 5: Update `today_realized_pnl`**:
```python
def today_realized_pnl(self, *, user_id: str | None = None) -> float:
    if flags.multi_tenant_enabled() and user_id is not None:
        sql = '''
            WITH avg_cost AS (
                SELECT
                    el.symbol,
                    SUM(el.filled_price * el.filled_quantity) /
                        SUM(el.filled_quantity) AS avg_buy_price
                FROM execution_logs el
                JOIN order_logs ol ON el.order_log_id = ol.id
                WHERE ol.side = 'BUY'
                  AND el.filled_quantity > 0
                  AND ol.user_id = ?
                GROUP BY el.symbol
            )
            SELECT COALESCE(
                SUM(
                    (el.filled_price - COALESCE(ac.avg_buy_price, el.filled_price))
                    * el.filled_quantity
                ), 0
            ) AS realized_pnl
            FROM execution_logs el
            JOIN order_logs ol ON el.order_log_id = ol.id
            LEFT JOIN avg_cost ac ON ac.symbol = el.symbol
            WHERE ol.side = 'SELL'
              AND el.filled_quantity > 0
              AND DATE(el.filled_at, '+9 hours') = DATE('now', '+9 hours')
              AND ol.user_id = ?
        '''
        params: list[Any] = [user_id, user_id]
    else:
        sql = '''
            WITH avg_cost AS (
                SELECT
                    el.symbol,
                    SUM(el.filled_price * el.filled_quantity) /
                        SUM(el.filled_quantity) AS avg_buy_price
                FROM execution_logs el
                JOIN order_logs ol ON el.order_log_id = ol.id
                WHERE ol.side = 'BUY'
                  AND el.filled_quantity > 0
                GROUP BY el.symbol
            )
            SELECT COALESCE(
                SUM(
                    (el.filled_price - COALESCE(ac.avg_buy_price, el.filled_price))
                    * el.filled_quantity
                ), 0
            ) AS realized_pnl
            FROM execution_logs el
            JOIN order_logs ol ON el.order_log_id = ol.id
            LEFT JOIN avg_cost ac ON ac.symbol = el.symbol
            WHERE ol.side = 'SELL'
              AND el.filled_quantity > 0
              AND DATE(el.filled_at, '+9 hours') = DATE('now', '+9 hours')
        '''
        params = []
    with get_connection(self.db_path) as conn:
        row = conn.execute(sql, params).fetchone()
        return float(row["realized_pnl"] or 0.0)
```

- [ ] **Step 6: Update `total_realized_pnl`**:
```python
def total_realized_pnl(self, *, user_id: str | None = None) -> float:
    if flags.multi_tenant_enabled() and user_id is not None:
        sql = '''
            WITH avg_cost AS (
                SELECT
                    el.symbol,
                    SUM(el.filled_price * el.filled_quantity) /
                        SUM(el.filled_quantity) AS avg_buy_price
                FROM execution_logs el
                JOIN order_logs ol ON el.order_log_id = ol.id
                WHERE ol.side = 'BUY'
                  AND el.filled_quantity > 0
                  AND ol.user_id = ?
                GROUP BY el.symbol
            )
            SELECT COALESCE(
                SUM(
                    (el.filled_price - COALESCE(ac.avg_buy_price, el.filled_price))
                    * el.filled_quantity
                ), 0
            ) AS realized_pnl
            FROM execution_logs el
            JOIN order_logs ol ON el.order_log_id = ol.id
            LEFT JOIN avg_cost ac ON ac.symbol = el.symbol
            WHERE ol.side = 'SELL'
              AND el.filled_quantity > 0
              AND ol.user_id = ?
        '''
        params: list[Any] = [user_id, user_id]
    else:
        sql = '''
            WITH avg_cost AS (
                SELECT
                    el.symbol,
                    SUM(el.filled_price * el.filled_quantity) /
                        SUM(el.filled_quantity) AS avg_buy_price
                FROM execution_logs el
                JOIN order_logs ol ON el.order_log_id = ol.id
                WHERE ol.side = 'BUY'
                  AND el.filled_quantity > 0
                GROUP BY el.symbol
            )
            SELECT COALESCE(
                SUM(
                    (el.filled_price - COALESCE(ac.avg_buy_price, el.filled_price))
                    * el.filled_quantity
                ), 0
            ) AS realized_pnl
            FROM execution_logs el
            JOIN order_logs ol ON el.order_log_id = ol.id
            LEFT JOIN avg_cost ac ON ac.symbol = el.symbol
            WHERE ol.side = 'SELL'
              AND el.filled_quantity > 0
        '''
        params = []
    with get_connection(self.db_path) as conn:
        row = conn.execute(sql, params).fetchone()
        return float(row["realized_pnl"] or 0.0)
```

- [ ] **Step 7: Update `total_buy_cost_basis`**:
```python
def total_buy_cost_basis(self, *, user_id: str | None = None) -> float:
    if flags.multi_tenant_enabled() and user_id is not None:
        sql = '''
            SELECT COALESCE(
                SUM(el.filled_price * el.filled_quantity), 0
            ) AS total_cost
            FROM execution_logs el
            JOIN order_logs ol ON el.order_log_id = ol.id
            WHERE ol.side = 'BUY'
              AND el.filled_quantity > 0
              AND ol.user_id = ?
        '''
        params: list[Any] = [user_id]
    else:
        sql = '''
            SELECT COALESCE(
                SUM(el.filled_price * el.filled_quantity), 0
            ) AS total_cost
            FROM execution_logs el
            JOIN order_logs ol ON el.order_log_id = ol.id
            WHERE ol.side = 'BUY'
              AND el.filled_quantity > 0
        '''
        params = []
    with get_connection(self.db_path) as conn:
        row = conn.execute(sql, params).fetchone()
        return float(row["total_cost"] or 0.0)
```

- [ ] **Step 8: Update `list_active_alerts`**:
```python
def list_active_alerts(self, *, user_id: str | None = None) -> list:
    if flags.multi_tenant_enabled() and user_id is not None:
        sql = 'SELECT * FROM price_alerts WHERE active=1 AND user_id=? ORDER BY id'
        params: list[Any] = [user_id]
    else:
        sql = 'SELECT * FROM price_alerts WHERE active=1 ORDER BY id'
        params = []
    with get_connection(self.db_path) as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]
```

- [ ] **Step 9: Update `list_journal_entries`**:
```python
def list_journal_entries(self, limit: int = 100, *, user_id: str | None = None) -> list:
    if flags.multi_tenant_enabled() and user_id is not None:
        sql = "SELECT * FROM trade_journal WHERE user_id=? ORDER BY created_at DESC LIMIT ?"
        params: list[Any] = [user_id, limit]
    else:
        sql = "SELECT * FROM trade_journal ORDER BY created_at DESC LIMIT ?"
        params = [limit]
    with get_connection(self.db_path) as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]
```

---

### Task 5: Flag-ON scoping tests

**Files:**
- Modify: `tests/unit/test_multitenant_repository.py`

**Interfaces:**
- Consumes: all 14 scoped methods from Tasks 3-4

- [ ] **Step 1: Write the flag-ON scoping test suite** — add to `tests/unit/test_multitenant_repository.py`:
```python
# ---- Helpers ----

def _seed_whitelist(repo_obj, symbol="005930"):
    repo_obj.add_whitelist_symbol(
        WhitelistSymbol(symbol=symbol, name="테스트", market="KRX", role="TEST")
    )


def _insert_filled_sell(repo_obj, user_id, symbol="005930", price=75_000.0, qty=1):
    """Insert a complete BUY+SELL cycle for realized PnL testing."""
    # BUY order
    buy_cid = repo_obj.add_trade_condition(
        symbol=symbol, side="BUY", target_price=price,
        quantity=qty, user_id=user_id,
    )
    buy_order_id = repo_obj.create_order_log(
        condition_id=buy_cid, symbol=symbol, side="BUY",
        order_type="LIMIT", order_price=price, current_price=price,
        quantity=qty, kis_order_id=None, order_status="FILLED",
        user_id=user_id,
    )
    repo_obj.create_execution_log(
        order_log_id=buy_order_id, symbol=symbol,
        filled_price=price, filled_quantity=qty,
        user_id=user_id,
    )
    # SELL order
    sell_cid = repo_obj.add_trade_condition(
        symbol=symbol, side="SELL", target_price=price + 1000,
        quantity=qty, user_id=user_id,
    )
    sell_order_id = repo_obj.create_order_log(
        condition_id=sell_cid, symbol=symbol, side="SELL",
        order_type="LIMIT", order_price=price + 1000, current_price=price + 1000,
        quantity=qty, kis_order_id=None, order_status="FILLED",
        user_id=user_id,
    )
    repo_obj.create_execution_log(
        order_log_id=sell_order_id, symbol=symbol,
        filled_price=price + 1000, filled_quantity=qty,
        user_id=user_id,
    )
    return buy_order_id, sell_order_id


# ---- Flag-ON scoping tests ----

@pytest.fixture
def mt_repo(tmp_path, monkeypatch):
    """Repo fixture with AUTOFOLIO_MULTI_TENANT_ENABLED=1."""
    monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
    db = tmp_path / "mt_test.db"
    initialize_database(db)
    return Repository(db), db


def test_flagoff_is_default(tmp_path):
    """With no env var set, multi_tenant_enabled() returns False."""
    from app.services.flags import multi_tenant_enabled
    import os
    os.environ.pop("AUTOFOLIO_MULTI_TENANT_ENABLED", None)
    assert multi_tenant_enabled() is False


class TestConditionScoping:
    def test_list_conditions_scoped_to_user(self, mt_repo, monkeypatch):
        monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
        repo, _ = mt_repo
        _seed_whitelist(repo)
        repo.add_trade_condition(
            symbol="005930", side="BUY", target_price=70_000, quantity=1, user_id="user_a"
        )
        repo.add_trade_condition(
            symbol="005930", side="SELL", target_price=75_000, quantity=1, user_id="user_b"
        )
        rows_a = repo.list_conditions(user_id="user_a")
        rows_b = repo.list_conditions(user_id="user_b")
        assert len(rows_a) == 1 and rows_a[0]["side"] == "BUY"
        assert len(rows_b) == 1 and rows_b[0]["side"] == "SELL"

    def test_list_active_conditions_scoped(self, mt_repo, monkeypatch):
        monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
        repo, _ = mt_repo
        _seed_whitelist(repo)
        repo.add_trade_condition(
            symbol="005930", side="BUY", target_price=70_000, quantity=1, user_id="user_a"
        )
        repo.add_trade_condition(
            symbol="005930", side="SELL", target_price=75_000, quantity=1, user_id="user_b"
        )
        active_a = repo.list_active_conditions(user_id="user_a")
        assert len(active_a) == 1
        assert active_a[0]["side"] == "BUY"

    def test_null_user_id_row_not_returned_in_scoped_query(self, mt_repo, monkeypatch):
        """Legacy row with NULL user_id must NOT be returned to a scoped query."""
        monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
        repo, _ = mt_repo
        _seed_whitelist(repo)
        # Insert without user_id → NULL user_id
        repo.add_trade_condition(
            symbol="005930", side="BUY", target_price=70_000, quantity=1
        )
        # Scoped query for user_a should not return the legacy row
        rows = repo.list_conditions(user_id="user_a")
        assert rows == []


class TestOrderLogScoping:
    def test_list_order_logs_scoped(self, mt_repo, monkeypatch):
        monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
        repo, _ = mt_repo
        _seed_whitelist(repo)
        cid_a = repo.add_trade_condition(
            symbol="005930", side="BUY", target_price=70_000, quantity=1, user_id="user_a"
        )
        cid_b = repo.add_trade_condition(
            symbol="005930", side="BUY", target_price=70_000, quantity=1, user_id="user_b"
        )
        repo.create_order_log(
            condition_id=cid_a, symbol="005930", side="BUY",
            order_type="LIMIT", order_price=70_000, current_price=70_000,
            quantity=1, kis_order_id="A001", order_status="FILLED",
            user_id="user_a",
        )
        repo.create_order_log(
            condition_id=cid_b, symbol="005930", side="BUY",
            order_type="LIMIT", order_price=70_000, current_price=70_000,
            quantity=1, kis_order_id="B001", order_status="FILLED",
            user_id="user_b",
        )
        logs_a = repo.list_order_logs(user_id="user_a")
        assert len(logs_a) == 1 and logs_a[0]["kis_order_id"] == "A001"


class TestAggregateScoping:
    def test_today_order_amount_scoped(self, mt_repo, monkeypatch):
        monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
        repo, _ = mt_repo
        _seed_whitelist(repo)
        cid_a = repo.add_trade_condition(
            symbol="005930", side="BUY", target_price=70_000, quantity=1, user_id="user_a"
        )
        cid_b = repo.add_trade_condition(
            symbol="005930", side="BUY", target_price=70_000, quantity=1, user_id="user_b"
        )
        repo.create_order_log(
            condition_id=cid_a, symbol="005930", side="BUY",
            order_type="LIMIT", order_price=70_000, current_price=70_000,
            quantity=2, kis_order_id=None, order_status="FILLED",
            user_id="user_a",
        )
        repo.create_order_log(
            condition_id=cid_b, symbol="005930", side="BUY",
            order_type="LIMIT", order_price=90_000, current_price=90_000,
            quantity=3, kis_order_id=None, order_status="FILLED",
            user_id="user_b",
        )
        amt_a = repo.today_order_amount(user_id="user_a")
        amt_b = repo.today_order_amount(user_id="user_b")
        assert amt_a == pytest.approx(140_000.0)  # 70000 * 2
        assert amt_b == pytest.approx(270_000.0)  # 90000 * 3

    def test_total_buy_cost_basis_scoped(self, mt_repo, monkeypatch):
        monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
        repo, _ = mt_repo
        _seed_whitelist(repo)
        cid_a = repo.add_trade_condition(
            symbol="005930", side="BUY", target_price=70_000, quantity=1, user_id="user_a"
        )
        order_a = repo.create_order_log(
            condition_id=cid_a, symbol="005930", side="BUY",
            order_type="LIMIT", order_price=70_000, current_price=70_000,
            quantity=1, kis_order_id=None, order_status="FILLED",
            user_id="user_a",
        )
        repo.create_execution_log(
            order_log_id=order_a, symbol="005930",
            filled_price=70_000, filled_quantity=1,
            user_id="user_a",
        )
        cid_b = repo.add_trade_condition(
            symbol="005930", side="BUY", target_price=80_000, quantity=1, user_id="user_b"
        )
        order_b = repo.create_order_log(
            condition_id=cid_b, symbol="005930", side="BUY",
            order_type="LIMIT", order_price=80_000, current_price=80_000,
            quantity=1, kis_order_id=None, order_status="FILLED",
            user_id="user_b",
        )
        repo.create_execution_log(
            order_log_id=order_b, symbol="005930",
            filled_price=80_000, filled_quantity=1,
            user_id="user_b",
        )
        assert repo.total_buy_cost_basis(user_id="user_a") == pytest.approx(70_000.0)
        assert repo.total_buy_cost_basis(user_id="user_b") == pytest.approx(80_000.0)


class TestAlertScoping:
    def test_list_active_alerts_scoped(self, mt_repo, monkeypatch):
        monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
        repo, _ = mt_repo
        repo.add_price_alert("005930", 70_000, "ABOVE", user_id="user_a")
        repo.add_price_alert("000660", 80_000, "BELOW", user_id="user_b")
        alerts_a = repo.list_active_alerts(user_id="user_a")
        assert len(alerts_a) == 1 and alerts_a[0]["symbol"] == "005930"


class TestJournalScoping:
    def test_list_journal_entries_scoped(self, mt_repo, monkeypatch):
        monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
        repo, _ = mt_repo
        repo.add_journal_entry("005930", "BUY", entry_reason="value", user_id="user_a")
        repo.add_journal_entry("000660", "SELL", entry_reason="momentum", user_id="user_b")
        entries_a = repo.list_journal_entries(user_id="user_a")
        assert len(entries_a) == 1 and entries_a[0]["symbol"] == "005930"
```

- [ ] **Step 2: Run all new tests**:
```bash
python -m pytest tests/unit/test_multitenant_repository.py -v
```
Expected: All PASS

- [ ] **Step 3: Run the full characterization suite** (flag-OFF = default):
```bash
python -m pytest tests/unit/ tests/integration/ -q --tb=short
```
Expected: Same pass count as baseline (no regressions).

---

### Task 6: Commit and report

**Files:**
- Create: `.superpowers/sdd/multitenant-p1-report.md`

- [ ] **Step 1: Write report to `.superpowers/sdd/multitenant-p1-report.md`** with: schema changes, migration approach, methods scoped, scoping rule, characterization result, flag-ON test evidence, files changed.

- [ ] **Step 2: Commit** (do NOT git-add the report file):
```bash
git add app/database/schema.sql app/database/sqlite_db.py app/database/repositories.py tests/unit/test_multitenant_repository.py
git commit -m "$(cat <<'EOF'
feat(multitenant): Phase 1 — 레포 쿼리 user_id 스코핑(flag-gated, default-OFF byte-identical)

- app/database/schema.sql: 7개 거래 테이블에 user_id TEXT nullable + 인덱스 추가
- app/database/sqlite_db.py: _apply_multitenant_migration() — 기존 DB idempotent ALTER
- app/database/repositories.py: 14개 메서드 user_id=None 파라미터 + flag-gated 스코핑
- tests/unit/test_multitenant_repository.py: flag-ON 격리 테스트 + 마이그레이션 테스트

flag OFF(기본값) 경로는 기존 SQL과 byte-identical.
AUTOFOLIO_MULTI_TENANT_ENABLED=1 + user_id 전달 시에만 WHERE user_id = ? 적용.
서비스/엔진 레이어 변경 없음(Phase 2/3 예정).

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```
