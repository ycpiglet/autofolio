# Price Alert Engine Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire the dead `price_alerts` feature so `LiveTradingEngine.run_once()` evaluates active alerts each cycle and notifies via the `Notifier` when price conditions are met.

**Architecture:** Add an `evaluate_price_alerts()` method to `LiveTradingEngine` (called at the end of `run_once()`). It reads all rows with `active=1` from `price_alerts`, fetches the current price from the broker, checks the direction condition, notifies via `self.notifier`, and marks the alert inactive via `repo.trigger_alert(id)`. The `trigger_alert` method already exists in `Repository` — it sets `active=0` and `triggered_at=CURRENT_TIMESTAMP`. No new DB methods are needed. Tests mock the broker price and the notifier; no real network or trading window concerns (alerts fire anytime — independent of the trading window).

**Tech Stack:** Python 3.11+, SQLite (via `app/database/sqlite_db.get_connection`), `pytest`, `unittest.mock`, `app/notification/notifier.Notifier`, `app/engine/live_trading_engine.LiveTradingEngine`, `app/database/repositories.Repository`.

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `app/engine/live_trading_engine.py` | Modify | Add `evaluate_price_alerts()` method; call it from `run_once()` |
| `tests/unit/test_price_alert_engine.py` | Create | TDD tests: condition met, not met, already fired |
| `agents/lead_engineer/tasks/units/TASK-061/UNIT-TASK-061-001.md` | Create | Unit spec record |
| `agents/lead_engineer/tasks/TASK-061-feat-price-alert-engine-loop.md` | Modify | 대기→완료 |
| `agents/lead_engineer/tasks/INDEX.md` | Modify | 대기→완료 |

---

## Key facts (verified in codebase)

- `app/database/repositories.py:455` — `list_active_alerts()` returns `list[dict]` where each dict has keys: `id`, `symbol`, `target_price`, `direction` (ABOVE|BELOW), `active`, `triggered_at`, `created_at`.
- `app/database/repositories.py:461` — `trigger_alert(alert_id: int)` sets `active=0, triggered_at=CURRENT_TIMESTAMP`. This is the "mark fired" method (TASK-061 stub calls it `mark_alert_fired` — use the REAL name `trigger_alert`).
- `app/engine/live_trading_engine.py:34` — `run_once()` returns `list[str]` messages. `self.notifier` is `Notifier | None`.
- `app/notification/notifier.py:29` — `Notifier.send(text: str) -> None`.
- `app/database/schema.sql:76` — `price_alerts` table: `direction CHECK(direction IN ('ABOVE', 'BELOW'))`.
- `app/brokers/base.py` — `BrokerClient.get_current_price(symbol) -> PriceResult` where `.price` is a float.
- Alert evaluation is independent of the trading window (it's a notification, not an order).

---

### Task 1: Write the failing test (TDD — RED)

**Files:**
- Create: `tests/unit/test_price_alert_engine.py`

- [ ] **Step 1.1: Write the failing test file**

```python
"""TDD tests for price alert evaluation loop in LiveTradingEngine (TASK-061).

These tests were written BEFORE evaluate_price_alerts() existed.
Initial run must show FAIL (AttributeError or condition not met).
"""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock

import pytest

from app.database.repositories import Repository
from app.database.sqlite_db import initialize_database
from app.engine.live_trading_engine import LiveTradingEngine


def _make_engine(tmpdir: Path, price: float):
    """Return (engine, repo, mock_notifier) with broker returning fixed price."""
    db_path = tmpdir / "test.db"
    initialize_database(db_path)
    repo = Repository(db_path)

    mock_broker = MagicMock()
    price_result = MagicMock()
    price_result.price = price
    mock_broker.get_current_price.return_value = price_result

    mock_notifier = MagicMock()

    engine = LiveTradingEngine(broker=mock_broker, repo=repo, notifier=mock_notifier)
    return engine, repo, mock_notifier


# ---------------------------------------------------------------------------
# 1. Condition met (ABOVE): notifier called, alert marked inactive
# ---------------------------------------------------------------------------

def test_alert_above_fires_when_price_meets_condition():
    """ABOVE alert fires when current_price >= target_price."""
    with TemporaryDirectory() as tmpdir:
        engine, repo, notifier = _make_engine(Path(tmpdir), price=55000.0)
        alert_id = repo.add_price_alert("005930", 50000.0, "ABOVE")

        engine.evaluate_price_alerts()

        notifier.send.assert_called_once()
        call_text = notifier.send.call_args[0][0]
        assert "005930" in call_text

        # Alert must be marked inactive
        alerts = repo.list_active_alerts()
        assert not any(a["id"] == alert_id for a in alerts), "Alert should be inactive"


# ---------------------------------------------------------------------------
# 2. Condition NOT met (ABOVE): notifier not called, alert stays active
# ---------------------------------------------------------------------------

def test_alert_above_does_not_fire_when_price_below_target():
    """ABOVE alert does NOT fire when current_price < target_price."""
    with TemporaryDirectory() as tmpdir:
        engine, repo, notifier = _make_engine(Path(tmpdir), price=45000.0)
        alert_id = repo.add_price_alert("005930", 50000.0, "ABOVE")

        engine.evaluate_price_alerts()

        notifier.send.assert_not_called()

        alerts = repo.list_active_alerts()
        assert any(a["id"] == alert_id for a in alerts), "Alert should still be active"


# ---------------------------------------------------------------------------
# 3. Condition met (BELOW): notifier called, alert marked inactive
# ---------------------------------------------------------------------------

def test_alert_below_fires_when_price_meets_condition():
    """BELOW alert fires when current_price <= target_price."""
    with TemporaryDirectory() as tmpdir:
        engine, repo, notifier = _make_engine(Path(tmpdir), price=45000.0)
        alert_id = repo.add_price_alert("005930", 50000.0, "BELOW")

        engine.evaluate_price_alerts()

        notifier.send.assert_called_once()
        call_text = notifier.send.call_args[0][0]
        assert "005930" in call_text

        alerts = repo.list_active_alerts()
        assert not any(a["id"] == alert_id for a in alerts)


# ---------------------------------------------------------------------------
# 4. Condition NOT met (BELOW): notifier not called, alert stays active
# ---------------------------------------------------------------------------

def test_alert_below_does_not_fire_when_price_above_target():
    """BELOW alert does NOT fire when current_price > target_price."""
    with TemporaryDirectory() as tmpdir:
        engine, repo, notifier = _make_engine(Path(tmpdir), price=55000.0)
        alert_id = repo.add_price_alert("005930", 50000.0, "BELOW")

        engine.evaluate_price_alerts()

        notifier.send.assert_not_called()

        alerts = repo.list_active_alerts()
        assert any(a["id"] == alert_id for a in alerts)


# ---------------------------------------------------------------------------
# 5. Already-fired alert (active=0) is not re-sent
# ---------------------------------------------------------------------------

def test_already_fired_alert_not_resent():
    """An alert with active=0 must not be re-evaluated or re-sent."""
    with TemporaryDirectory() as tmpdir:
        engine, repo, notifier = _make_engine(Path(tmpdir), price=55000.0)
        alert_id = repo.add_price_alert("005930", 50000.0, "ABOVE")
        repo.trigger_alert(alert_id)  # pre-fire

        engine.evaluate_price_alerts()

        notifier.send.assert_not_called()


# ---------------------------------------------------------------------------
# 6. run_once() calls evaluate_price_alerts (integration with loop)
# ---------------------------------------------------------------------------

def test_run_once_includes_alert_evaluation():
    """run_once() must trigger alert evaluation; notifier is called for met alerts."""
    with TemporaryDirectory() as tmpdir:
        engine, repo, notifier = _make_engine(Path(tmpdir), price=55000.0)
        repo.add_price_alert("005930", 50000.0, "ABOVE")

        # run_once evaluates conditions (none active) + alerts
        engine.run_once()

        notifier.send.assert_called()


# ---------------------------------------------------------------------------
# 7. No notifier attached: evaluate_price_alerts does not raise
# ---------------------------------------------------------------------------

def test_evaluate_alerts_no_notifier_does_not_raise():
    """evaluate_price_alerts() is safe when self.notifier is None."""
    with TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        initialize_database(db_path)
        repo = Repository(db_path)
        mock_broker = MagicMock()
        price_result = MagicMock()
        price_result.price = 55000.0
        mock_broker.get_current_price.return_value = price_result

        engine = LiveTradingEngine(broker=mock_broker, repo=repo, notifier=None)
        repo.add_price_alert("005930", 50000.0, "ABOVE")

        # Must not raise
        engine.evaluate_price_alerts()

        # Alert should still be marked inactive (logic runs, notify skipped)
        alerts = repo.list_active_alerts()
        assert alerts == []
```

- [ ] **Step 1.2: Run to confirm FAIL**

```
cd C:\Users\ycpig\autofolio
python -m pytest tests/unit/test_price_alert_engine.py -v
```

Expected: `AttributeError: 'LiveTradingEngine' object has no attribute 'evaluate_price_alerts'` — all 7 tests fail.

---

### Task 2: Implement `evaluate_price_alerts()` in `LiveTradingEngine` (GREEN)

**Files:**
- Modify: `app/engine/live_trading_engine.py`

The method goes after `run_once()`. Then `run_once()` calls it at the end.

- [ ] **Step 2.1: Add `evaluate_price_alerts()` and call from `run_once()`**

In `app/engine/live_trading_engine.py`, after the existing `run_once()` block (before the final `return messages`), add a call to `self.evaluate_price_alerts()`. Then add the method.

Change in `run_once()` — before `return messages` (around line 100), add:
```python
        self.evaluate_price_alerts()
```

Add new method after `run_once()`:
```python
    def evaluate_price_alerts(self) -> list[str]:
        """가격 알림 평가 — active 알림 전체를 순회, 조건 충족 시 발송 후 비활성화.

        거래 시간 제한 없이 실행된다 (주문이 아닌 알림이므로).
        """
        alerts = self.repo.list_active_alerts()
        fired: list[str] = []
        for alert in alerts:
            alert_id = alert["id"]
            symbol = alert["symbol"]
            target_price = float(alert["target_price"])
            direction = alert["direction"]
            try:
                current_price = float(self.broker.get_current_price(symbol).price)
            except Exception as exc:  # noqa: BLE001
                log_event(logger, "price_alert_price_fetch_error",
                          alert_id=alert_id, symbol=symbol, error=str(exc))
                continue

            condition_met = (
                (direction == "ABOVE" and current_price >= target_price)
                or (direction == "BELOW" and current_price <= target_price)
            )
            if not condition_met:
                continue

            msg = (
                f"[가격 알림] {symbol} {direction} {target_price:,.0f} — "
                f"현재가 {current_price:,.0f}"
            )
            log_event(logger, "price_alert_fired",
                      alert_id=alert_id, symbol=symbol,
                      direction=direction, target_price=target_price,
                      current_price=current_price)
            if self.notifier:
                self.notifier.send(msg)
            self.repo.trigger_alert(alert_id)
            fired.append(msg)
        return fired
```

- [ ] **Step 2.2: Run failing test suite again — confirm GREEN**

```
python -m pytest tests/unit/test_price_alert_engine.py -v
```

Expected: 7 passed.

- [ ] **Step 2.3: Run full test suite — confirm no regressions**

```
python -m pytest tests/ -q
```

Expected: all previously passing tests still pass.

---

### Task 3: Create Unit spec record

**Files:**
- Create: `agents/lead_engineer/tasks/units/TASK-061/UNIT-TASK-061-001.md`

- [ ] **Step 3.1: Create UNIT-TASK-061-001.md**

Content (fill actual completion time from `python scripts/now.py`):

```markdown
---
unit_id: UNIT-TASK-061-001
task_id: TASK-061
task_set_id: TASKSET-PRODUCT-MATURITY
project_id: PROJECT-AUTOFOLIO
status: completed
horizon: unit
model_tier: worker_standard
escalation_triggers: [high_risk, repeated_failure]
context: "price_alerts 테이블에 저장된 가격 알림이 엔진에서 평가되지 않아 dead feature. LiveTradingEngine.evaluate_price_alerts() 신규 메서드 추가 및 run_once() 호출 연결."
inputs:
  - agents/lead_engineer/tasks/TASK-061-feat-price-alert-engine-loop.md
  - app/engine/live_trading_engine.py
  - app/database/repositories.py
  - app/notification/notifier.py
target_files:
  - app/engine/live_trading_engine.py
  - tests/unit/test_price_alert_engine.py
scope: "LiveTradingEngine.evaluate_price_alerts() 신규 메서드 + run_once() 연결. 주문/거래 기능 변경 금지."
acceptance:
  - "ABOVE 조건 충족 시 notifier.send() 1회 호출 + alert active=0"
  - "ABOVE 조건 미충족 시 notifier.send() 미호출 + alert active=1 유지"
  - "BELOW 조건 충족 시 notifier.send() 1회 호출 + alert active=0"
  - "BELOW 조건 미충족 시 notifier.send() 미호출 + alert active=1 유지"
  - "active=0 사전 발동 알림 재발송 금지"
  - "run_once() 호출 시 evaluate_price_alerts() 실행"
  - "notifier=None 시 예외 없음"
  - "python -m pytest tests/ -q green"
  - "python scripts/check_agent_docs.py 0 error"
verification:
  - "python -m pytest tests/unit/test_price_alert_engine.py -v"
  - "python -m pytest tests/ -q"
  - "python scripts/check_agent_docs.py"
  - "python scripts/work_schema_gate.py --items --check"
  - "python scripts/build_task_index.py --check"
  - "python scripts/generate_views.py --check"
handoff: "변경 파일: live_trading_engine.py (evaluate_price_alerts + run_once 연결), tests/unit/test_price_alert_engine.py (신규 7 테스트). trigger_alert() 기존 메서드 재사용 (mark_alert_fired 별칭 불필요)."
stop_condition: "evaluate_price_alerts() 구현 후 즉시 중단. 주문/거래/리스크 로직 변경 금지."
depends_on: []
---

# UNIT-TASK-061-001 — 가격 알림 엔진 평가 루프 구현

## Context

`Repository.list_active_alerts()` / `trigger_alert()` 는 이미 구현되어 있음.
`LiveTradingEngine.run_once()`가 이를 호출하지 않아 dead feature.

## Target Files

- `app/engine/live_trading_engine.py`
- `tests/unit/test_price_alert_engine.py` (신규)

## Acceptance Criteria

- ABOVE/BELOW 조건 충족/미충족 케이스 정확히 평가
- 충족 시 `self.notifier.send()` 호출 + `repo.trigger_alert(id)` 호출
- `active=0` 알림 재발송 없음
- `run_once()` → `evaluate_price_alerts()` 호출 검증
- `notifier=None` 안전

## 완료 기록

완료 시각: PLACEHOLDER — 실행 시 채워넣기
```

---

### Task 4: Update task records + regenerate views

**Files:**
- Modify: `agents/lead_engineer/tasks/TASK-061-feat-price-alert-engine-loop.md`
- Modify: `agents/lead_engineer/tasks/INDEX.md`

- [ ] **Step 4.1: Update TASK-061 frontmatter and body**

Change `status: 대기` → `status: 완료` in frontmatter AND `상태: 대기` → `상태: 완료` in body. Add completion block at end:

```markdown
## 완료 기록

완료 시각: <output of python scripts/now.py>
검토자: Backend Engineer

## 증거

- `tests/unit/test_price_alert_engine.py`: 7 신규 TDD 테스트 (GREEN)
- `app/engine/live_trading_engine.py`: `evaluate_price_alerts()` 추가, `run_once()` 연결
- `python -m pytest tests/ -q` → all passed
- `python scripts/check_agent_docs.py` → 0 error

## 리뷰

구현 방향:
- 기존 `repo.trigger_alert()` 재사용 (신규 `mark_alert_fired` 별칭 불필요)
- `NotificationBus` 대신 `Notifier` 직접 사용 (엔진 기존 패턴)
- 거래 시간 창 독립 (알림 = 주문 아님)
- `notifier=None` 안전 처리
```

- [ ] **Step 4.2: Update INDEX.md**

Change `| [TASK-061](...) | 대기 | ...` → `| [TASK-061](...) | 완료 | ...|`

- [ ] **Step 4.3: Run generate_views + build_task_index**

```
python scripts/generate_views.py
python scripts/build_task_index.py
```

---

### Task 5: Gate checks + commit

- [ ] **Step 5.1: Run all gates**

```
python -m pytest tests/ -q
python -m pytest tests/unit -q
python scripts/check_agent_docs.py
python scripts/work_schema_gate.py --items --check
python scripts/build_task_index.py --check
python scripts/generate_views.py --check
```

All must pass / 0 errors.

- [ ] **Step 5.2: Commit**

```
git add app/engine/live_trading_engine.py \
        tests/unit/test_price_alert_engine.py \
        agents/lead_engineer/tasks/units/TASK-061/UNIT-TASK-061-001.md \
        agents/lead_engineer/tasks/TASK-061-feat-price-alert-engine-loop.md \
        agents/lead_engineer/tasks/INDEX.md \
        agents/lead_engineer/tasks/BACKLOG.md \
        agents/lead_engineer/tasks/VIEW-by-owner.md \
        agents/lead_engineer/tasks/VIEW-by-priority.md \
        agents/lead_engineer/tasks/VIEW-by-status.md \
        agents/lead_engineer/tasks/VIEW-by-tag.md \
        agents/lead_engineer/tasks/VIEW-by-workload.md \
        tasks.index.json
git commit -m "feat(alerts): 가격 알림 평가 루프 구현 — dead feature 해소 (TASK-061)

- LiveTradingEngine.evaluate_price_alerts() 신규 메서드 추가
- run_once() 루프 끝에서 호출 (거래 시간 독립)
- ABOVE/BELOW 조건 평가 + notifier.send() + repo.trigger_alert()
- notifier=None 안전, 중복 발송 방지 (active=0 건너뜀)
- TDD: 7 신규 테스트 (RED→GREEN 검증 포함)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Self-Review

**Spec coverage:**
- `run_once()` evaluates price_alerts → Task 2 (call at end of run_once)
- `list_active_alerts()` / `mark_alert_fired()` (= `trigger_alert()`) → already exist, confirmed in repo at lines 455, 461
- Notifier connected → `self.notifier.send(msg)` in evaluate_price_alerts
- `fired=True` (active=0) update → `repo.trigger_alert(alert_id)`
- TDD: 7 tests (ABOVE met, ABOVE not met, BELOW met, BELOW not met, already fired, run_once integration, no notifier) → Task 1
- Unit spec record → Task 3
- Status updates + regenerated views → Task 4
- Gate checks → Task 5

**Placeholder scan:** No TBD/TODO in code blocks. All method names use real names from codebase (`trigger_alert`, not `mark_alert_fired`).

**Type consistency:** `evaluate_price_alerts() -> list[str]` used consistently. `alert["id"]`, `alert["symbol"]`, `alert["target_price"]`, `alert["direction"]` match `list_active_alerts()` dict keys (confirmed from schema + repository).
