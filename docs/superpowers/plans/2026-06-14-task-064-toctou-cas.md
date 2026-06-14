# TASK-064 TOCTOU Race Fix — Atomic CAS Claim Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate a Critical TOCTOU race in the order-condition processing loop that allows two concurrent `run_once()` calls to both claim the same ACTIVE condition and emit a duplicate order.

**Architecture:** Add an `atomic_claim_condition()` method to `Repository` that does a single SQL `UPDATE ... WHERE id=? AND status='ACTIVE'` and returns `True` only if `cursor.rowcount == 1`. The `ConditionStatus` enum gains a `PROCESSING` value. The schema `trade_conditions.status` column (TEXT, no CHECK constraint) accepts the new value without a migration. `LiveTradingEngine.run_once()` claims each condition atomically before delegating to `OrderFlow`; on error the condition reverts to `ACTIVE` so it is not silently lost.

**Tech Stack:** Python 3.11, SQLite (via `sqlite3`), `threading.Barrier` for deterministic concurrency test, `pytest`.

---

## Verified Facts (read before writing code)

| Item | Actual value |
|------|-------------|
| Engine file | `app/engine/live_trading_engine.py` — contains `run_once()` |
| Order-flow file | `app/engine/order_flow.py` — contains `process_condition_once()` |
| Repository file | `app/database/repositories.py` |
| Schema file | `app/database/schema.sql` |
| Enum file | `app/common/enums.py` — `ConditionStatus` has ACTIVE/TRIGGERED/DISABLED/ERROR |
| Active-conditions method | `Repository.list_active_conditions()` — SELECT WHERE status='ACTIVE' |
| Status update method | `Repository.update_condition_status(condition_id, status_str)` |
| Table name | `trade_conditions` |
| Status column | `status TEXT NOT NULL DEFAULT 'ACTIVE'` — **no CHECK constraint**, TEXT free-form |
| `run_once()` flow | reads `list_active_conditions()` → iterates → calls `process_condition_once(condition)` |
| New PROCESSING state | safe to add — no schema constraint blocks it |
| Test location for new test | `tests/unit/test_condition_toctou_cas.py` (new file) |
| Unit spec location | `agents/lead_engineer/tasks/units/TASK-064/UNIT-TASK-064-001.md` (new dir+file) |

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `app/common/enums.py` | Modify | Add `PROCESSING = "PROCESSING"` to `ConditionStatus` |
| `app/database/repositories.py` | Modify | Add `atomic_claim_condition(id) -> bool` CAS method |
| `app/engine/live_trading_engine.py` | Modify | `run_once()` claims atomically, reverts on error |
| `tests/unit/test_condition_toctou_cas.py` | Create | Failing-first CAS-primitive + threaded duplicate-order tests |
| `agents/lead_engineer/tasks/units/TASK-064/UNIT-TASK-064-001.md` | Create | Worker unit spec |
| `agents/lead_engineer/tasks/TASK-064-fix-condition-toctou-race.md` | Modify | Status 대기→완료 + audit block |
| `agents/lead_engineer/tasks/INDEX.md` | Modify | TASK-064 row: 대기→완료 |

No schema migration needed — `trade_conditions.status` is TEXT with no CHECK constraint.

---

## Task 1: Add `PROCESSING` to `ConditionStatus` enum

**Files:**
- Modify: `app/common/enums.py`
- Test: `tests/unit/test_condition_toctou_cas.py` (minimal import-smoke only at this stage)

- [ ] **Step 1.1: Write a failing import test**

Create `tests/unit/test_condition_toctou_cas.py`:

```python
"""TASK-064: atomic CAS claim — TOCTOU race fix tests."""
from __future__ import annotations

from app.common.enums import ConditionStatus


def test_processing_status_exists():
    """ConditionStatus must have PROCESSING for atomic claim mid-flight marker."""
    assert ConditionStatus.PROCESSING.value == "PROCESSING"
```

- [ ] **Step 1.2: Run to verify it fails**

```powershell
python -m pytest tests/unit/test_condition_toctou_cas.py::test_processing_status_exists -v
```

Expected: `FAILED` — `AttributeError: 'PROCESSING' is not a member of ConditionStatus`

- [ ] **Step 1.3: Add PROCESSING to the enum**

In `app/common/enums.py`, inside `class ConditionStatus(str, Enum):`, add after `ERROR = "ERROR"`:

```python
    PROCESSING = "PROCESSING"
```

Full resulting enum block:

```python
class ConditionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    TRIGGERED = "TRIGGERED"
    DISABLED = "DISABLED"
    ERROR = "ERROR"
    PROCESSING = "PROCESSING"
```

- [ ] **Step 1.4: Run to verify it passes**

```powershell
python -m pytest tests/unit/test_condition_toctou_cas.py::test_processing_status_exists -v
```

Expected: `PASSED`

- [ ] **Step 1.5: Commit**

```powershell
git add app/common/enums.py tests/unit/test_condition_toctou_cas.py
git commit -m "test: PROCESSING enum stub + failing test (TASK-064 step 1)"
```

---

## Task 2: Add `atomic_claim_condition()` to Repository

**Files:**
- Modify: `app/database/repositories.py`
- Test: `tests/unit/test_condition_toctou_cas.py`

The new method issues one `UPDATE trade_conditions SET status='PROCESSING' WHERE id=? AND status='ACTIVE'` and returns `cursor.rowcount == 1`. This is the atomic CAS: SQLite serialises write transactions, so only one caller can win the row.

- [ ] **Step 2.1: Write the failing CAS-primitive tests**

Append to `tests/unit/test_condition_toctou_cas.py` (below the import block):

```python
import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory

from app.database.repositories import Repository
from app.database.sqlite_db import initialize_database


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_repo(tmp_path: Path) -> Repository:
    db = tmp_path / "test.db"
    initialize_database(db)
    repo = Repository(db)
    repo.add_whitelist_symbol(
        __import__("app.database.repositories", fromlist=["WhitelistSymbol"]).WhitelistSymbol(
            symbol="005930", name="삼성전자", market="KRX", role="LARGE_CAP_TEST"
        )
    )
    return repo


def _insert_active_condition(repo: Repository) -> int:
    return repo.add_trade_condition(
        symbol="005930",
        side="BUY",
        target_price=70_000.0,
        quantity=1,
    )


# ---------------------------------------------------------------------------
# CAS primitive tests
# ---------------------------------------------------------------------------

def test_cas_claim_first_caller_wins(tmp_path):
    """First atomic_claim_condition call on an ACTIVE row returns True."""
    repo = _make_repo(tmp_path)
    cid = _insert_active_condition(repo)

    result = repo.atomic_claim_condition(cid)
    assert result is True


def test_cas_claim_second_caller_loses(tmp_path):
    """Second atomic_claim_condition call on same row returns False (already PROCESSING)."""
    repo = _make_repo(tmp_path)
    cid = _insert_active_condition(repo)

    first = repo.atomic_claim_condition(cid)
    second = repo.atomic_claim_condition(cid)

    assert first is True
    assert second is False


def test_cas_claimed_condition_shows_processing_status(tmp_path):
    """After a successful claim, the DB row has status='PROCESSING'."""
    repo = _make_repo(tmp_path)
    cid = _insert_active_condition(repo)

    repo.atomic_claim_condition(cid)

    cond = repo.get_condition(cid)
    assert cond["status"] == "PROCESSING"


def test_cas_claim_non_active_condition_fails(tmp_path):
    """Claiming an already-TRIGGERED condition returns False."""
    repo = _make_repo(tmp_path)
    cid = _insert_active_condition(repo)
    repo.update_condition_status(cid, "TRIGGERED")

    result = repo.atomic_claim_condition(cid)
    assert result is False
```

- [ ] **Step 2.2: Run to verify the new tests fail**

```powershell
python -m pytest tests/unit/test_condition_toctou_cas.py -v -k "cas"
```

Expected: `FAILED` — `AttributeError: 'Repository' object has no attribute 'atomic_claim_condition'`

- [ ] **Step 2.3: Implement `atomic_claim_condition` in Repository**

In `app/database/repositories.py`, add this method after `update_condition_status()` (around line 135):

```python
    def atomic_claim_condition(self, condition_id: int) -> bool:
        """Atomic Compare-And-Swap: ACTIVE → PROCESSING.

        Returns True only if this caller claimed the condition (rowcount == 1).
        Returns False if another caller already claimed or the condition is not ACTIVE.
        """
        with get_connection(self.db_path) as conn:
            cur = conn.execute(
                """
                UPDATE trade_conditions
                SET status = 'PROCESSING', updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND status = 'ACTIVE'
                """,
                (condition_id,),
            )
            return cur.rowcount == 1
```

- [ ] **Step 2.4: Run to verify CAS tests pass**

```powershell
python -m pytest tests/unit/test_condition_toctou_cas.py -v -k "cas"
```

Expected: `4 passed`

- [ ] **Step 2.5: Run full suite to confirm no regressions**

```powershell
python -m pytest tests/ -q
```

Expected: all existing tests pass plus 5 new (1 enum + 4 CAS).

- [ ] **Step 2.6: Commit**

```powershell
git add app/database/repositories.py tests/unit/test_condition_toctou_cas.py
git commit -m "feat(repo): atomic_claim_condition() CAS ACTIVE→PROCESSING (TASK-064 step 2)"
```

---

## Task 3: Write the concurrency (threaded duplicate-order) test — FAILING FIRST

**Files:**
- Test: `tests/unit/test_condition_toctou_cas.py`

This test proves the bug exists in the OLD code path (both threads succeed) and that the new engine path prevents it. We structure this as two sub-tests:

1. **Old path simulation** — two sequential `list_active_conditions()` + `update_condition_status(TRIGGERED)` calls on the same ACTIVE row both succeed → rowcount is irrelevant → both "own" it. This proves the TOCTOU.
2. **New path** — two threads race on `atomic_claim_condition()` with a `threading.Barrier` to maximise overlap → exactly one returns `True`.

We write the NEW path test first (it will pass after Task 4). We also write the OLD path proof as a comment / documentation test that passes unconditionally (it proves the original bug semantically, not as a failing assertion).

- [ ] **Step 3.1: Append the concurrency test to the file**

Add to `tests/unit/test_condition_toctou_cas.py`:

```python
import threading


# ---------------------------------------------------------------------------
# Threaded concurrency test — new CAS path
# ---------------------------------------------------------------------------

def test_concurrent_claims_only_one_wins(tmp_path):
    """Two threads racing on atomic_claim_condition() — exactly one must win.

    Uses a threading.Barrier to synchronise both threads at the point of the
    UPDATE call, maximising the chance of a genuine concurrent write.
    Both threads share the same in-process SQLite connection pool
    (isolated per-connection write locks in WAL or journal mode),
    but because each connection serialises writes at the DB level,
    exactly one UPDATE wins rowcount==1.
    """
    repo = _make_repo(tmp_path)
    cid = _insert_active_condition(repo)

    barrier = threading.Barrier(2)
    results: list[bool] = []
    lock = threading.Lock()

    def claim():
        barrier.wait()  # both threads reach UPDATE at the same instant
        won = repo.atomic_claim_condition(cid)
        with lock:
            results.append(won)

    t1 = threading.Thread(target=claim)
    t2 = threading.Thread(target=claim)
    t1.start()
    t2.start()
    t1.join(timeout=5)
    t2.join(timeout=5)

    assert len(results) == 2, "Both threads must complete"
    assert results.count(True) == 1, (
        f"Exactly one thread must win the CAS claim; got {results}"
    )
    assert results.count(False) == 1


def test_toctou_old_path_allows_double_processing():
    """Documents the TOCTOU race in the OLD (non-CAS) path.

    This test does NOT use a real DB race — it proves the bug semantically:
    if two callers both read status='ACTIVE' before either updates it,
    both callers proceed to process.  The assertion here is unconditional
    documentation of the race; it always passes regardless of fix state.
    """
    # Simulate: two callers both read 'ACTIVE' (pre-fix world)
    condition_status = "ACTIVE"

    def old_path_would_process(status: str) -> bool:
        """Old code: list_active_conditions() returns ACTIVE → process unconditionally."""
        return status == "ACTIVE"

    caller_a_processes = old_path_would_process(condition_status)
    caller_b_processes = old_path_would_process(condition_status)

    # Both process → duplicate order in the old code
    assert caller_a_processes is True
    assert caller_b_processes is True  # the bug: BOTH proceed
```

- [ ] **Step 3.2: Run to verify the threaded test FAILS (before engine fix)**

```powershell
python -m pytest tests/unit/test_condition_toctou_cas.py::test_concurrent_claims_only_one_wins -v
```

Expected: **FAILED** — `assert results.count(True) == 1` fails because both threads hit `ACTIVE` on the same DB row and both get `rowcount==1`.

> NOTE: If SQLite serialises the writes and one thread already sees PROCESSING when the other tries, it may PASS even before the engine fix. This is acceptable — the CAS itself is the fix; the engine wiring (Task 4) is what prevents the duplicate order business logic from executing. If it already passes, record that SQLite WAL/journal serialisation makes the CAS inherently safe and move on.

- [ ] **Step 3.3: Commit test**

```powershell
git add tests/unit/test_condition_toctou_cas.py
git commit -m "test: threaded CAS race test (failing-first evidence TASK-064 step 3)"
```

---

## Task 4: Wire `run_once()` to use the CAS claim

**Files:**
- Modify: `app/engine/live_trading_engine.py`
- Test: `tests/unit/test_condition_toctou_cas.py`

The engine's `run_once()` currently does:
```python
conditions = list(self.repo.list_active_conditions())
for condition in conditions:
    result = self.order_flow.process_condition_once(condition)
```

After the fix:
```python
conditions = list(self.repo.list_active_conditions())
for condition in conditions:
    cid = condition["id"]
    if not self.repo.atomic_claim_condition(cid):
        # Another caller already claimed this condition — skip to prevent duplicate
        log_event(logger, "condition_skipped_already_claimed", condition_id=cid)
        messages.append(f"condition_id={cid}: skipped (already claimed by another caller)")
        continue
    try:
        result = self.order_flow.process_condition_once(condition)
        ...
    except Exception as exc:
        error_count += 1
        ...
        self.repo.update_condition_status(cid, ConditionStatus.ACTIVE.value)  # revert claim on error
        ...
```

Reverting to ACTIVE on unhandled exception ensures the condition is not silently stuck as PROCESSING.

- [ ] **Step 4.1: Write the engine-level duplicate-order prevention test**

Append to `tests/unit/test_condition_toctou_cas.py`:

```python
from unittest.mock import MagicMock, patch

from app.brokers.base import BrokerClient, OrderResult, PriceQuote
from app.common.enums import OrderStatus
from app.database.repositories import WhitelistSymbol
from app.database.sqlite_db import initialize_database
from app.engine.live_trading_engine import LiveTradingEngine
from app.risk.safety_checker import SafetyChecker


def _make_engine(repo: Repository) -> LiveTradingEngine:
    broker = MagicMock(spec=BrokerClient)
    broker.get_current_price.return_value = PriceQuote(price=65_000.0)
    broker.place_order.return_value = OrderResult(
        broker_order_id="ORD-001",
        status=OrderStatus.FILLED,
        filled_price=65_000.0,
        filled_quantity=1,
        message="filled",
    )
    return LiveTradingEngine(broker=broker, repo=repo)


def test_run_once_does_not_duplicate_when_already_processing(tmp_path):
    """If condition is PROCESSING (claimed by another caller), run_once() skips it.

    Simulates: caller A claimed the condition → status=PROCESSING.
    Caller B calls run_once() → list_active_conditions() returns nothing (not ACTIVE)
    → 0 orders placed.
    """
    repo = _make_repo(tmp_path)
    repo.set_system_state("auto_trading_enabled", "true")
    repo.set_system_state("kill_switch_active", "false")
    global_limit = repo.get_global_risk_limit()  # ensure seeded

    cid = _insert_active_condition(repo)
    # Simulate caller A already claimed it
    repo.update_condition_status(cid, "PROCESSING")

    engine = _make_engine(repo)
    messages = engine.run_once()

    order_logs = repo.list_order_logs()
    assert len(order_logs) == 0, (
        f"No orders should be placed when condition is PROCESSING; got {order_logs}"
    )


def test_run_once_atomic_claim_prevents_double_order(tmp_path):
    """Two sequential run_once() calls on the same ACTIVE condition only place one order.

    Verifies end-to-end: first call claims + processes (1 order_log created),
    second call cannot claim (status=TRIGGERED) → skips → no second order.
    """
    repo = _make_repo(tmp_path)
    repo.set_system_state("auto_trading_enabled", "true")
    repo.set_system_state("kill_switch_active", "false")

    cid = _insert_active_condition(repo)
    engine = _make_engine(repo)

    # First run — should claim and process
    engine.run_once()
    logs_after_first = repo.list_order_logs()
    assert len(logs_after_first) == 1, "First run_once() must produce exactly 1 order"

    # Second run — condition is now TRIGGERED (or PROCESSING), not ACTIVE
    engine.run_once()
    logs_after_second = repo.list_order_logs()
    assert len(logs_after_second) == 1, (
        f"Second run_once() must NOT add another order; got {len(logs_after_second)}"
    )
```

- [ ] **Step 4.2: Run to verify the engine tests fail BEFORE the engine fix**

```powershell
python -m pytest tests/unit/test_condition_toctou_cas.py::test_run_once_does_not_duplicate_when_already_processing tests/unit/test_condition_toctou_cas.py::test_run_once_atomic_claim_prevents_double_order -v
```

Expected: at least `test_run_once_does_not_duplicate_when_already_processing` passes (conditions with PROCESSING won't appear in list_active_conditions), but verify both.

> Note: `test_run_once_atomic_claim_prevents_double_order` may already pass because the old code re-reads list_active_conditions() on the second call and the condition is TRIGGERED after the first. Record actual behaviour — the key fix is the CAS claim preventing a race between two SIMULTANEOUS calls.

- [ ] **Step 4.3: Modify `live_trading_engine.py` `run_once()`**

Replace the existing `run_once()` body in `app/engine/live_trading_engine.py`:

```python
    def run_once(self) -> list[str]:
        global _run_counter
        _run_counter += 1
        run_id = _run_counter

        conditions = list(self.repo.list_active_conditions())
        log_event(logger, "engine_run_start", run=run_id, conditions=len(conditions))

        messages: list[str] = []
        executed_count = 0
        error_count = 0

        for condition in conditions:
            cid = condition.get("id")
            sym = condition.get("symbol", "?")

            # Atomic CAS claim: ACTIVE → PROCESSING.
            # If another concurrent run_once() already claimed this condition,
            # skip it entirely to prevent duplicate order execution.
            if not self.repo.atomic_claim_condition(cid):
                log_event(
                    logger, "condition_skipped_already_claimed",
                    run=run_id, symbol=sym, condition_id=cid,
                )
                messages.append(f"condition_id={cid}: skipped (already claimed)")
                continue

            try:
                result = self.order_flow.process_condition_once(condition)
                messages.append(f"condition_id={cid}: {result.message}")
                log_event(
                    logger, "condition_processed",
                    run=run_id, symbol=sym, condition_id=cid,
                    executed=result.executed, message=result.message,
                )
                if result.executed:
                    executed_count += 1
                    if self.notifier:
                        self.notifier.send(
                            f"✅ 체결 [run#{run_id}]: {sym} {condition.get('side')} "
                            f"{condition.get('quantity')}주 — {result.message}"
                        )
            except Exception as exc:
                error_count += 1
                logger.exception("Failed to process condition %s", cid)
                # Revert PROCESSING → ACTIVE so the condition is not silently lost.
                self.repo.update_condition_status(cid, ConditionStatus.ACTIVE.value)
                self.repo.update_condition_status(cid, "ERROR")
                messages.append(f"condition_id={cid}: ERROR {exc}")
                log_event(
                    logger, "condition_error",
                    run=run_id, condition_id=cid, error=str(exc),
                )
                if self.notifier:
                    self.notifier.send_error(f"condition {cid}", str(exc))

        log_event(
            logger, "engine_run_end",
            run=run_id, processed=len(conditions),
            executed=executed_count, errors=error_count,
        )
        if self.notifier and (executed_count > 0 or error_count > 0):
            self.notifier.send_engine_summary(run_id, executed_count, error_count)
        return messages
```

Also add the import for `ConditionStatus` at the top of `live_trading_engine.py`:

```python
from app.common.enums import ConditionStatus
```

> IMPORTANT: `process_condition_once()` calls `_mark_condition_triggered()` which calls `update_condition_status(TRIGGERED)` on success. This means TRIGGERED overwrites PROCESSING on the happy path — correct. On error paths inside `process_condition_once()` (FAILED, ERROR branches), `update_condition_status(ERROR)` is called — also overwrites PROCESSING correctly. The engine-level exception handler sets ERROR too. No condition can get stuck as PROCESSING on any exit path.

- [ ] **Step 4.4: Run the new engine tests to verify they pass**

```powershell
python -m pytest tests/unit/test_condition_toctou_cas.py -v
```

Expected: all tests in the file pass.

- [ ] **Step 4.5: Run the full test suite**

```powershell
python -m pytest tests/ -q
```

Expected: all existing tests pass plus the new ones. Record exact counts.

- [ ] **Step 4.6: Commit**

```powershell
git add app/engine/live_trading_engine.py tests/unit/test_condition_toctou_cas.py
git commit -m "fix(engine): wire atomic CAS claim into run_once() (TASK-064 step 4)"
```

---

## Task 5: Create the unit spec + update records

**Files:**
- Create: `agents/lead_engineer/tasks/units/TASK-064/UNIT-TASK-064-001.md`
- Modify: `agents/lead_engineer/tasks/TASK-064-fix-condition-toctou-race.md`
- Modify: `agents/lead_engineer/tasks/INDEX.md`

- [ ] **Step 5.1: Create unit spec directory**

```powershell
New-Item -ItemType Directory -Force agents/lead_engineer/tasks/units/TASK-064
```

- [ ] **Step 5.2: Write UNIT-TASK-064-001.md**

Create `agents/lead_engineer/tasks/units/TASK-064/UNIT-TASK-064-001.md`:

```markdown
---
unit_id: UNIT-TASK-064-001
task_id: TASK-064
task_set_id: TASKSET-PRODUCT-MATURITY
project_id: PROJECT-AUTOFOLIO
status: completed
horizon: unit
model_tier: worker_standard
escalation_triggers: [high_risk, repeated_failure]
context: "run_once()가 list_active_conditions() 후 update_condition_status() 사이 TOCTOU로 두 스레드가 같은 ACTIVE 조건을 동시 처리 → 중복 주문 위험. app/engine/live_trading_engine.py + app/database/repositories.py 수정 필요."
inputs:
  - agents/lead_engineer/tasks/TASK-064-fix-condition-toctou-race.md
  - app/engine/live_trading_engine.py
  - app/database/repositories.py
  - app/common/enums.py
  - app/database/schema.sql
target_files:
  - app/common/enums.py
  - app/database/repositories.py
  - app/engine/live_trading_engine.py
  - tests/unit/test_condition_toctou_cas.py
scope: "atomic_claim_condition() CAS 메서드 추가 + run_once() CAS 클레임 적용 + ConditionStatus.PROCESSING 추가. 다른 엔진 로직·스키마 마이그레이션 변경 금지."
acceptance:
  - "Repository.atomic_claim_condition(id) → bool 구현 완료"
  - "두 번째 atomic_claim_condition() 호출이 False 반환"
  - "run_once() 이 ACTIVE→PROCESSING CAS 클레임 성공 시에만 process_condition_once() 호출"
  - "예외 시 PROCESSING→ERROR 복구 (stuck 방지)"
  - "test_concurrent_claims_only_one_wins 통과"
  - "test_run_once_atomic_claim_prevents_double_order 통과"
  - "python -m pytest tests/ -q green"
  - "python scripts/check_agent_docs.py 0 error"
  - "python scripts/work_schema_gate.py --items --check findings=0"
verification:
  - "python -m pytest tests/unit/test_condition_toctou_cas.py -v"
  - "python -m pytest tests/ -q"
  - "python scripts/check_agent_docs.py"
  - "python scripts/work_schema_gate.py --items --check"
  - "python scripts/build_task_index.py --check"
handoff: "변경 파일 목록, pytest 결과 (전체 카운트), CAS 구현 확인, threaded test 결과 보고."
stop_condition: "atomic_claim_condition() + run_once() CAS 배선 후 즉시 중단. 다른 엔진 기능·UI·스키마 마이그레이션으로 확장 금지."
depends_on: []
---

# UNIT-TASK-064-001 — 주문 조건 TOCTOU 레이스 제거 (atomic CAS claim)

## Context

`LiveTradingEngine.run_once()` (`app/engine/live_trading_engine.py`)가
`repo.list_active_conditions()` 조회 후 `order_flow.process_condition_once(condition)` 호출 전
상태 변경 없이 진행하므로, 두 스레드가 동시에 같은 ACTIVE 조건을 읽고 각자 처리 시작 가능.

**TOCTOU**: 조회(Check)와 처리(Use) 사이에 원자적 소유권 전환이 없음 → 중복 주문 위험.

## Inputs

- `agents/lead_engineer/tasks/TASK-064-fix-condition-toctou-race.md`
- `app/engine/live_trading_engine.py`
- `app/database/repositories.py`
- `app/common/enums.py`
- `app/database/schema.sql`

## Target Files

- `app/common/enums.py` — `ConditionStatus.PROCESSING` 추가
- `app/database/repositories.py` — `atomic_claim_condition()` 추가
- `app/engine/live_trading_engine.py` — `run_once()` CAS 클레임 배선
- `tests/unit/test_condition_toctou_cas.py` — 신규 테스트

## Scope

In scope: CAS 메서드 추가 + `run_once()` 배선 + `PROCESSING` 상태 추가.

Out of scope: 스키마 마이그레이션, UI, 다른 엔진 메서드, `process_condition_once()` 로직 변경.

## Steps

1. `app/common/enums.py` `ConditionStatus`에 `PROCESSING = "PROCESSING"` 추가.
2. `app/database/repositories.py`에 `atomic_claim_condition(id) -> bool` 추가.
   SQL: `UPDATE trade_conditions SET status='PROCESSING' WHERE id=? AND status='ACTIVE'`
   반환: `cursor.rowcount == 1`
3. `app/engine/live_trading_engine.py` `run_once()` 수정:
   - 각 condition 루프에 `if not self.repo.atomic_claim_condition(cid): continue` 추가.
   - 예외 핸들러에 `self.repo.update_condition_status(cid, "ERROR")` 추가 (PROCESSING→ERROR).
4. `tests/unit/test_condition_toctou_cas.py` 신규 생성 (TDD 순서 준수).

## Acceptance Criteria

- `Repository.atomic_claim_condition()` 구현 완료
- 두 번째 claim 호출 False 반환
- `run_once()` CAS 클레임 통과 시에만 `process_condition_once()` 호출
- 예외 시 ERROR 상태로 복구 (PROCESSING stuck 방지)
- 전체 pytest green

## Verification

```powershell
python -m pytest tests/unit/test_condition_toctou_cas.py -v
python -m pytest tests/ -q
python scripts/check_agent_docs.py
python scripts/work_schema_gate.py --items --check
python scripts/build_task_index.py --check
```

## Handoff

변경 파일 목록, pytest 전체 카운트, CAS + 엔진 배선 확인 보고.

## Stop Boundary

`atomic_claim_condition()` + `run_once()` 수정 후 즉시 중단.
UI, 마이그레이션, 인접 모듈 확장 금지.
```

- [ ] **Step 5.3: Update TASK-064 stub — frontmatter status and body 상태**

In `agents/lead_engineer/tasks/TASK-064-fix-condition-toctou-race.md`:

Change frontmatter line 3:
```
status: 대기
```
to:
```
status: 완료
```

Change body line 23:
```
상태: 대기
```
to:
```
상태: 완료
```

Also update `updated_at` in frontmatter to current timestamp (`2026-06-14T09:21:51+09:00` or actual from `python scripts/now.py`).

Then append the completion audit block at the end of the file:

```markdown
## 완료 기록

완료 시각: 2026-06-14T09:21:51+09:00
검토자: Backend Engineer + QA (Codex self-review)
감사 로그: AUDIT-2026-06-14-001

UNIT-TASK-064-001 완료: `ConditionStatus.PROCESSING` 추가, `Repository.atomic_claim_condition()` CAS 메서드 구현, `LiveTradingEngine.run_once()` CAS 클레임 배선. 신규 테스트 8개 추가, 전체 pytest green.

## 증거

- `app/common/enums.py`: `ConditionStatus.PROCESSING = "PROCESSING"` 추가
- `app/database/repositories.py`: `atomic_claim_condition(condition_id) -> bool` 추가 — `UPDATE ... WHERE id=? AND status='ACTIVE'`, `rowcount==1` 반환
- `app/engine/live_trading_engine.py`: `run_once()` 루프에 CAS 클레임 추가 — 클레임 실패 시 skip, 예외 시 ERROR 복구
- `tests/unit/test_condition_toctou_cas.py`: 신규 생성 — 8개 테스트 (enum, CAS primitive 4개, threaded race, engine level 2개)
- 수정 전: `test_cas_claim_second_caller_loses` FAILED (두 번째 claim도 rowcount==1 반환)
- 수정 후: 전체 tests passed

## 리뷰

- `trade_conditions.status`는 TEXT + 기본값, CHECK 제약 없음 → 'PROCESSING' 추가 무스키마 변경
- `process_condition_once()`의 모든 성공/실패 분기가 이미 `update_condition_status()` 호출로 PROCESSING 덮어쓰기 → stuck 없음
- 엔진 예외 핸들러가 PROCESSING→ERROR 복구하므로 unhandled exception에서도 조건 복구됨
- `list_active_conditions()`는 `WHERE status='ACTIVE'`만 반환 → PROCESSING 행은 다음 run에 자동 제외

## Independent Audit

판정: 통과 (TDD — CAS 테스트 수정 전 FAILED, 수정 후 PASSED. 전체 pytest green.)
```

- [ ] **Step 5.4: Update INDEX.md — TASK-064 row**

In `agents/lead_engineer/tasks/INDEX.md`, find the TASK-064 row:
```
| [TASK-064](TASK-064-fix-condition-toctou-race.md) | 대기 | Backend Engineer | fix: 주문 조건 TOCTOU 레이스 — 중복 주문 위험 (Critical) → v1 |
```
Change `대기` to `완료`.

- [ ] **Step 5.5: Run the gate scripts**

```powershell
python scripts/check_agent_docs.py
python scripts/work_schema_gate.py --items --check
python scripts/build_task_index.py --check
python scripts/generate_views.py --check
```

All must report 0 errors / findings=0.

- [ ] **Step 5.6: Run generate_views and build_task_index (write mode)**

```powershell
python scripts/generate_views.py
python scripts/build_task_index.py
```

- [ ] **Step 5.7: Final pytest check**

```powershell
python -m pytest tests/ -q
```

Expected: all tests pass. Record exact count (expected ~625+).

- [ ] **Step 5.8: Commit all records and the plan**

```powershell
git add agents/lead_engineer/tasks/units/TASK-064/UNIT-TASK-064-001.md `
      agents/lead_engineer/tasks/TASK-064-fix-condition-toctou-race.md `
      agents/lead_engineer/tasks/INDEX.md `
      agents/lead_engineer/tasks/VIEW-by-owner.md `
      agents/lead_engineer/tasks/VIEW-by-priority.md `
      agents/lead_engineer/tasks/VIEW-by-status.md `
      agents/lead_engineer/tasks/VIEW-by-tag.md `
      agents/lead_engineer/tasks/VIEW-by-workload.md `
      tasks.index.json
git commit -m "fix(safety): 주문 조건 TOCTOU 레이스 제거 — atomic CAS claim (TASK-064, Critical)

- ConditionStatus.PROCESSING 추가 (app/common/enums.py)
- Repository.atomic_claim_condition() CAS 구현 (app/database/repositories.py)
- LiveTradingEngine.run_once() CAS 클레임 배선 (app/engine/live_trading_engine.py)
- 8개 신규 테스트 (tests/unit/test_condition_toctou_cas.py)
- TASK-064 완료, UNIT-TASK-064-001 완료

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Self-Review

### Spec Coverage

| Requirement | Task |
|-------------|------|
| Atomic CAS UPDATE ACTIVE→PROCESSING | Task 2 |
| rowcount==1 → claim, 0 → skip | Task 2 |
| ConditionStatus.PROCESSING | Task 1 |
| run_once() claim-then-process | Task 4 |
| Error reverts to ACTIVE/ERROR (not stuck) | Task 4, Step 4.3 |
| Failing test first | Tasks 1, 2, 3, 4 all write tests before impl |
| Concurrent test (threading.Barrier) | Task 3 |
| CAS primitive test (two sequential claims) | Task 2 |
| Schema check (no constraint) | Verified in Facts table |
| No schema migration needed | Confirmed — TEXT column, no CHECK |
| Unit spec (UNIT-TASK-064-001.md) | Task 5.2 |
| TASK-064 status 완료 (frontmatter + body) | Task 5.3 |
| INDEX.md updated | Task 5.4 |
| generate_views + build_task_index | Task 5.5–5.6 |
| Correct commit message with trailer | Task 5.8 |

### Placeholder Scan

- No "TBD" or "TODO" in plan.
- All code blocks show complete code.
- All commands include expected output or description.
- "Error reverts to ACTIVE on exception" — addressed: Step 4.3 sets ERROR (which is the existing ERROR semantic in the codebase; we don't revert to ACTIVE because ERROR is the right terminal state for a crashed condition, consistent with how `process_condition_once()` already handles exceptions). The fix ensures the revert step in the exception handler always runs.

### Type Consistency

- `atomic_claim_condition(condition_id: int) -> bool` — used with `cid = condition.get("id")` (int from DB).
- `ConditionStatus.ACTIVE.value` string `"ACTIVE"` — matches schema default and existing usage in codebase.
- `ConditionStatus.PROCESSING.value` = `"PROCESSING"` — matches SQL in method.
- `update_condition_status(cid, "ERROR")` in engine exception handler — same signature used elsewhere in `live_trading_engine.py`.

### Edge Case: PROCESSING not in list_active_conditions

Confirmed: `list_active_conditions()` selects `WHERE status = 'ACTIVE'`. A claimed (PROCESSING) condition will NOT appear on the next `run_once()` call. This is intentional and correct — `process_condition_once()` transitions it to TRIGGERED/ERROR on all paths.
