---
unit_id: UNIT-TASK-060-001
task_id: TASK-060
task_set_id: TASKSET-PRODUCT-MATURITY
project_id: PROJECT-AUTOFOLIO
status: completed
horizon: unit
model_tier: worker_standard
escalation_triggers: [high_risk, repeated_failure]
context: "SQLite FK enforcement is per-connection (not persistent) — PRAGMA foreign_keys=ON must be set in get_connection(). WAL mode is persistent per-DB — set once in initialize_database(). schema.sql lacks FK declarations for execution_logs.order_log_id → order_logs.id and order_logs.condition_id → trade_conditions.id. Two test fixtures insert orphan condition_id=1 rows that break with FK=ON."
inputs:
  - agents/lead_engineer/tasks/TASK-060-sqlite-wal-fk-enforcement.md
  - app/database/sqlite_db.py
  - app/database/schema.sql
  - tests/unit/test_repository_edge_cases.py
  - tests/unit/test_safety_critical_boundaries.py
target_files:
  - app/database/sqlite_db.py
  - app/database/schema.sql
  - tests/unit/test_sqlite_wal_fk.py
  - tests/unit/test_repository_edge_cases.py
  - tests/unit/test_safety_critical_boundaries.py
scope: "get_connection() FK pragma, initialize_database() WAL pragma, schema.sql FK declarations, test fixture repairs, new TDD test file."
acceptance:
  - "PRAGMA foreign_keys=ON on every get_connection() call"
  - "PRAGMA journal_mode=WAL in initialize_database()"
  - "execution_logs.order_log_id REFERENCES order_logs(id)"
  - "order_logs.condition_id REFERENCES trade_conditions(id) ON DELETE SET NULL"
  - "trade_journal.order_log_id REFERENCES order_logs(id) ON DELETE SET NULL"
  - "IntegrityError raised on orphan execution_log insert"
  - "python -m pytest tests/unit/test_sqlite_wal_fk.py -q: 8 passed"
  - "python -m pytest tests/ -q: 675 passed, 1 pre-existing failure unrelated to FK"
  - "check_agent_docs.py 0 errors"
verification:
  - "python -m pytest tests/unit/test_sqlite_wal_fk.py -v"
  - "python -m pytest tests/ -q"
  - "python scripts/check_agent_docs.py"
  - "python scripts/work_schema_gate.py --items --check"
  - "python scripts/build_task_index.py --check"
  - "python scripts/generate_views.py --check"
handoff: "변경 파일: sqlite_db.py (get_connection FK + initialize_database WAL), schema.sql (FK 선언 3개), tests/unit/test_sqlite_wal_fk.py (신규 8 테스트), test_repository_edge_cases.py (fixture 수정), test_safety_critical_boundaries.py (fixture + INSERT 수정)"
stop_condition: "모든 파일 변경 및 pytest green 확인 후 중단. 다른 모듈로 확장 금지."
depends_on: []
---

# UNIT-TASK-060-001 — SQLite WAL 모드 + FK 제약 적용

## Context

`app/database/sqlite_db.py`의 `get_connection()`에 `PRAGMA foreign_keys=ON`이 없고,
`initialize_database()`에 `PRAGMA journal_mode=WAL`이 없음.
`app/database/schema.sql`의 `execution_logs`, `order_logs`, `trade_journal`에 FK 선언 없음.

## Target Files

- `app/database/sqlite_db.py`
- `app/database/schema.sql`
- `tests/unit/test_sqlite_wal_fk.py` (신규)
- `tests/unit/test_repository_edge_cases.py` (fixture 수정)
- `tests/unit/test_safety_critical_boundaries.py` (fixture + INSERT 수정)

## Acceptance Criteria

- `PRAGMA foreign_keys=ON` on every `get_connection()` return
- `PRAGMA journal_mode=WAL` in `initialize_database()`
- `execution_logs.order_log_id` REFERENCES `order_logs(id)` ON DELETE CASCADE
- `order_logs.condition_id` REFERENCES `trade_conditions(id)` ON DELETE SET NULL
- `trade_journal.order_log_id` REFERENCES `order_logs(id)` ON DELETE SET NULL
- IntegrityError raised on orphan insert (proved by TDD tests)
- `python -m pytest tests/ -q` → 675 passed (1 pre-existing time-gated failure unrelated)

## 완료 기록

완료 시각: 2026-06-14T15:35:45+09:00

**변경 내용:**

- `app/database/sqlite_db.py`:
  - `get_connection()`: `conn.execute("PRAGMA foreign_keys=ON")` 추가 (per-connection)
  - `initialize_database()`: `conn.execute("PRAGMA journal_mode=WAL")` 추가 (persistent)
- `app/database/schema.sql`:
  - `order_logs.condition_id`: `REFERENCES trade_conditions(id) ON DELETE SET NULL` 추가
  - `execution_logs.order_log_id`: `REFERENCES order_logs(id) ON DELETE CASCADE` 추가
  - `trade_journal.order_log_id`: `REFERENCES order_logs(id) ON DELETE SET NULL` 추가
- `tests/unit/test_sqlite_wal_fk.py` (신규): WAL + FK 검증 8개 TDD 테스트
- `tests/unit/test_repository_edge_cases.py`: `repo` fixture에 trade_condition pre-seed, `_insert_order_log()` condition_id 파라미터화
- `tests/unit/test_safety_critical_boundaries.py`: `_make_env()`에 trade_condition pre-seed, 날것 INSERT에 `?` 바인딩 적용

**깨진 테스트 현황:**
- `test_repository_edge_cases.py`: condition_id=1 하드코딩 → pre-seed 후 동적 ID 사용으로 수정
- `test_safety_critical_boundaries.py`: condition_id=1 하드코딩 → pre-seed 후 `(repo._test_condition_id,)` 바인딩으로 수정

**검증 결과:**
- `test_sqlite_wal_fk.py`: 8 passed
- 전체: 675 passed, 1 failed (pre-existing: `test_run_once_atomic_claim_prevents_double_order` — trading window 외 시간대 시간의존 버그, FK 무관)
- `check_agent_docs.py`: 0 error
- `work_schema_gate --check`: pass
- `build_task_index --check`: OK
- `generate_views --check`: OK
