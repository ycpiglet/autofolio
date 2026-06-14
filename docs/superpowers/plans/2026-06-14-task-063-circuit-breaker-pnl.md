# TASK-063 Circuit Breaker PnL Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix `today_realized_pnl()` so it returns true realized PnL (SELL fills minus avg buy cost) instead of net cash flow, eliminating false circuit-breaker trips on buy-heavy days.

**Architecture:** Rewrite the SQL in `Repository.today_realized_pnl()` to sum only SELL fills, computing avg_cost per symbol from all historical BUY fills in `execution_logs`; a day with only BUY fills returns 0. Update existing tests that tested the buggy behavior, add new failing-first TDD tests, update documentation records.

**Tech Stack:** Python 3.10, SQLite (via `app/database/sqlite_db.py`), pytest, `app/risk/safety_checker.py`, `app/database/repositories.py`

---

## File Map

| File | Action | Purpose |
|------|--------|---------|
| `app/database/repositories.py` | Modify lines 334–357 | Replace buggy net-cash-flow SQL with correct realized-PnL SQL |
| `tests/unit/test_circuit_breaker.py` | Modify | Replace tests that asserted buggy behavior; add TDD failing tests first |
| `agents/lead_engineer/tasks/TASK-063-fix-circuit-breaker-pnl-logic.md` | Modify | Update status 대기→완료, add completion audit block |
| `agents/lead_engineer/tasks/units/TASK-063/UNIT-TASK-063-001.md` | Create | Worker unit record |
| `agents/lead_engineer/tasks/INDEX.md` | Modify | TASK-063 → 완료 |

---

## Prerequisite: understand the bug

**Current buggy implementation** (`app/database/repositories.py` lines 334–357):

```sql
SELECT COALESCE(
    SUM(
        CASE WHEN ol.side = 'SELL'
             THEN el.filled_price * el.filled_quantity
             ELSE -el.filled_price * el.filled_quantity
        END
    ), 0
) AS net_pnl
FROM execution_logs el
JOIN order_logs ol ON el.order_log_id = ol.id
WHERE DATE(el.filled_at) = DATE('now')
```

Problems:
1. Returns NET CASH FLOW (SELL=positive, BUY=negative). On a buy-heavy day, returns a large negative → triggers circuit breaker falsely.
2. `DATE(el.filled_at) = DATE('now')` uses UTC — misses KST midnight window (UTC+9). Must use `'+9 hours'` offset.

**Correct formula:**
```
realized_pnl = SUM over today's SELL fills of:
    (sell_filled_price − avg_buy_cost_for_symbol) × sell_filled_quantity

where avg_buy_cost_for_symbol = SUM(buy_price * buy_qty) / SUM(buy_qty)
    from ALL historical BUY fills (execution_logs joined to order_logs where side='BUY')
    for that symbol, up to and including today.
```

Buy-only day → no SELL rows → SUM = 0.

**Cost basis approach:** Average cost from ALL historical BUY fills (not just today's). The schema has no positions table, so we compute from `execution_logs JOIN order_logs WHERE side='BUY'` for all time. This matches what the mock broker does (running weighted average).

---

## Task 1: Write failing TDD tests FIRST

**Files:**
- Modify: `tests/unit/test_circuit_breaker.py`

- [ ] **Step 1: Replace the existing tests that assert the buggy behavior**

The current `TestTodayRealizedPnl.test_sell_positive_buy_negative` (lines 57–101) explicitly asserts:
```python
pnl = repo.today_realized_pnl()
assert pnl == pytest.approx(-70000.0)  # ← this is WRONG/buggy behavior
```

And `TestSafetyCheckerCircuitBreaker.test_daily_loss_trips_when_loss_exceeds_threshold` (lines 156–182) inserts only a BUY fill to trigger the breaker — which is the false-trip bug.

Replace `TestTodayRealizedPnl` class and update `test_daily_loss_trips_when_loss_exceeds_threshold` in `tests/unit/test_circuit_breaker.py`.

Open `tests/unit/test_circuit_breaker.py` and replace the entire `TestTodayRealizedPnl` class (lines 53–101) with:

```python
class TestTodayRealizedPnl:
    def test_returns_zero_when_no_executions(self, repo):
        assert repo.today_realized_pnl() == 0.0

    def test_buy_only_day_returns_zero(self, repo):
        """BUG REGRESSION: BUY-only day must return 0 (not a large negative)."""
        buy_log_id = repo.create_order_log(
            condition_id=None,
            symbol="005930",
            side="BUY",
            order_type="LIMIT",
            order_price=70000.0,
            current_price=70000.0,
            quantity=10,
            kis_order_id="B1",
            order_status="FILLED",
        )
        repo.create_execution_log(
            order_log_id=buy_log_id,
            symbol="005930",
            filled_price=70000.0,
            filled_quantity=10,
        )
        # No SELL fills → realized PnL must be 0, not -700_000
        assert repo.today_realized_pnl() == pytest.approx(0.0)

    def test_sell_after_buy_profit(self, repo):
        """BUY at 70_000, SELL at 75_000 → realized = (75_000 − 70_000) × 1 = 5_000."""
        buy_log_id = repo.create_order_log(
            condition_id=None,
            symbol="005930",
            side="BUY",
            order_type="LIMIT",
            order_price=70000.0,
            current_price=70000.0,
            quantity=1,
            kis_order_id="B1",
            order_status="FILLED",
        )
        repo.create_execution_log(
            order_log_id=buy_log_id,
            symbol="005930",
            filled_price=70000.0,
            filled_quantity=1,
        )
        sell_log_id = repo.create_order_log(
            condition_id=None,
            symbol="005930",
            side="SELL",
            order_type="LIMIT",
            order_price=75000.0,
            current_price=75000.0,
            quantity=1,
            kis_order_id="S1",
            order_status="FILLED",
        )
        repo.create_execution_log(
            order_log_id=sell_log_id,
            symbol="005930",
            filled_price=75000.0,
            filled_quantity=1,
        )
        assert repo.today_realized_pnl() == pytest.approx(5000.0)

    def test_sell_after_buy_loss(self, repo):
        """BUY at 70_000, SELL at 65_000 → realized = (65_000 − 70_000) × 1 = −5_000."""
        buy_log_id = repo.create_order_log(
            condition_id=None,
            symbol="005930",
            side="BUY",
            order_type="LIMIT",
            order_price=70000.0,
            current_price=70000.0,
            quantity=1,
            kis_order_id="B2",
            order_status="FILLED",
        )
        repo.create_execution_log(
            order_log_id=buy_log_id,
            symbol="005930",
            filled_price=70000.0,
            filled_quantity=1,
        )
        sell_log_id = repo.create_order_log(
            condition_id=None,
            symbol="005930",
            side="SELL",
            order_type="LIMIT",
            order_price=65000.0,
            current_price=65000.0,
            quantity=1,
            kis_order_id="S2",
            order_status="FILLED",
        )
        repo.create_execution_log(
            order_log_id=sell_log_id,
            symbol="005930",
            filled_price=65000.0,
            filled_quantity=1,
        )
        assert repo.today_realized_pnl() == pytest.approx(-5000.0)

    def test_avg_cost_weighted_correctly(self, repo):
        """Two BUYs at different prices → avg cost used for SELL realized PnL.

        BUY 1 share @ 60_000, BUY 1 share @ 80_000 → avg_cost = 70_000.
        SELL 1 share @ 75_000 → realized = (75_000 − 70_000) × 1 = 5_000.
        """
        for price, kid in [(60000.0, "B3a"), (80000.0, "B3b")]:
            lid = repo.create_order_log(
                condition_id=None,
                symbol="005930",
                side="BUY",
                order_type="LIMIT",
                order_price=price,
                current_price=price,
                quantity=1,
                kis_order_id=kid,
                order_status="FILLED",
            )
            repo.create_execution_log(
                order_log_id=lid,
                symbol="005930",
                filled_price=price,
                filled_quantity=1,
            )
        sell_lid = repo.create_order_log(
            condition_id=None,
            symbol="005930",
            side="SELL",
            order_type="LIMIT",
            order_price=75000.0,
            current_price=75000.0,
            quantity=1,
            kis_order_id="S3",
            order_status="FILLED",
        )
        repo.create_execution_log(
            order_log_id=sell_lid,
            symbol="005930",
            filled_price=75000.0,
            filled_quantity=1,
        )
        assert repo.today_realized_pnl() == pytest.approx(5000.0)
```

- [ ] **Step 2: Update `test_daily_loss_trips_when_loss_exceeds_threshold`**

The current test (lines 156–182) inserts a BUY-only fill to trip the circuit breaker — that's the bug scenario. Replace it to use a SELL fill at a loss instead:

Find and replace the method body of `test_daily_loss_trips_when_loss_exceeds_threshold` inside `TestSafetyCheckerCircuitBreaker`:

```python
    def test_daily_loss_trips_when_loss_exceeds_threshold(self, repo, monkeypatch):
        """당일 실현 손실이 max_daily_amount 의 threshold_pct% 이상이면 트립.

        SELL at a loss that exceeds threshold — NOT a BUY fill.
        BUY fills never realize PnL (regression guard).
        """
        import app.risk.safety_checker as sc_mod
        monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)

        checker = SafetyChecker(repo)
        condition = _make_condition(repo)

        # threshold 3%, max_daily_amount 1_000_000 → trip if loss >= 30_000
        repo.set_system_state("circuit_breaker_threshold_pct", "3.0")
        repo.update_global_risk_limit(max_daily_amount=1_000_000.0)

        # BUY 1 share @ 40_000 (avg cost = 40_000)
        buy_lid = repo.create_order_log(
            condition_id=None, symbol="005930", side="BUY",
            order_type="LIMIT", order_price=40000.0, current_price=40000.0,
            quantity=1, kis_order_id="CB_B1", order_status="FILLED",
        )
        repo.create_execution_log(
            order_log_id=buy_lid, symbol="005930",
            filled_price=40000.0, filled_quantity=1,
        )

        # SELL 1 share @ 0 (extreme loss: realized = (0 − 40_000) × 1 = −40_000 = 4% of 1M)
        sell_lid = repo.create_order_log(
            condition_id=None, symbol="005930", side="SELL",
            order_type="LIMIT", order_price=0.0, current_price=0.0,
            quantity=1, kis_order_id="CB_S1", order_status="FILLED",
        )
        repo.create_execution_log(
            order_log_id=sell_lid, symbol="005930",
            filled_price=0.0, filled_quantity=1,
        )

        result = checker.check(condition=condition, current_price=69900.0)
        assert not result.allowed
        assert "circuit breaker" in result.reason.lower()
        assert repo.get_system_state("auto_trading_enabled") == "false"
```

Also add a new regression test class at the bottom of `TestSafetyCheckerCircuitBreaker`:

```python
    def test_buy_only_day_does_not_trip_circuit_breaker(self, repo, monkeypatch):
        """BUG REGRESSION: buy-heavy day must NOT trip the daily-loss circuit breaker."""
        import app.risk.safety_checker as sc_mod
        monkeypatch.setattr(sc_mod, "is_within_trading_window", lambda *a, **kw: True)

        checker = SafetyChecker(repo)
        condition = _make_condition(repo)

        repo.set_system_state("circuit_breaker_threshold_pct", "3.0")
        repo.update_global_risk_limit(max_daily_amount=1_000_000.0)

        # Large BUY fills — old code would return −800_000 PnL and trip (80% of 1M)
        for i in range(10):
            lid = repo.create_order_log(
                condition_id=None, symbol="005930", side="BUY",
                order_type="LIMIT", order_price=80000.0, current_price=80000.0,
                quantity=1, kis_order_id=f"BIG_B{i}", order_status="FILLED",
            )
            repo.create_execution_log(
                order_log_id=lid, symbol="005930",
                filled_price=80000.0, filled_quantity=1,
            )

        result = checker.check(condition=condition, current_price=69900.0)
        assert result.allowed, f"Circuit breaker falsely tripped on buy-only day: {result.reason}"
```

- [ ] **Step 3: Run tests to verify they FAIL on current code**

```powershell
cd C:\Users\ycpig\autofolio
python -m pytest tests/unit/test_circuit_breaker.py -q -x 2>&1 | tail -20
```

Expected: FAIL — `test_buy_only_day_returns_zero` fails because current code returns -700_000, and `test_sell_after_buy_profit` fails because current code returns 5_000 - 70_000 = -65_000, and `test_buy_only_day_does_not_trip_circuit_breaker` fails.

---

## Task 2: Implement the fix in `today_realized_pnl()`

**Files:**
- Modify: `app/database/repositories.py` lines 334–357

- [ ] **Step 1: Replace the SQL in `today_realized_pnl()`**

Find the method at line 334. Replace the entire method with:

```python
    def today_realized_pnl(self) -> float:
        """오늘 SELL 체결 기준 실현 손익 합계.

        실현 손익 = Σ (매도체결가 − 종목별 평균매입가) × 매도수량
        - SELL 체결만 집계 (BUY 체결은 실현 손익 없음 → 0).
        - 평균매입가: execution_logs 전체 BUY 체결의 가중평균 (포지션 테이블 없음).
        - KST 당일 필터: DATE(filled_at, '+9 hours') = DATE('now', '+9 hours').
        - 체결 내역 없으면 0.0 반환.

        Cost basis: 전체 기간 BUY 체결 가중평균 (average cost basis).
        SELL 체결이 없으면 realized PnL = 0 (매수만인 날 서킷브레이커 오발동 방지).
        """
        with get_connection(self.db_path) as conn:
            row = conn.execute(
                '''
                WITH avg_cost AS (
                    -- 종목별 전체 기간 BUY 체결 가중평균 매입가
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
            ).fetchone()
            return float(row["realized_pnl"] or 0.0)
```

Key design decisions:
- **`WITH avg_cost` CTE**: computes per-symbol weighted-average buy price from ALL historical BUY fills. No positions table exists.
- **SELL filter**: Only SELL rows from today contribute to realized PnL; BUY-only day → SUM over empty SELL set → 0.
- **`DATE(el.filled_at, '+9 hours') = DATE('now', '+9 hours')`**: KST-aware, same pattern as `today_order_amount()`. No `'localtime'` — TZ-independent.
- **`COALESCE(ac.avg_buy_price, el.filled_price)`**: if no historical BUY exists for a symbol (e.g., manual/external position), use the SELL price itself → 0 realized (safe fallback, no false trip).
- **`filled_quantity > 0`**: guards against NULL or zero-quantity rows.

- [ ] **Step 2: Run the new tests to verify they PASS**

```powershell
cd C:\Users\ycpig\autofolio
python -m pytest tests/unit/test_circuit_breaker.py -q 2>&1 | tail -20
```

Expected: all tests pass.

- [ ] **Step 3: Run full test suite to verify no regressions**

```powershell
cd C:\Users\ycpig\autofolio
python -m pytest tests/ -q 2>&1 | tail -20
```

Expected: all tests green (no failures).

---

## Task 3: Create UNIT-TASK-063-001.md

**Files:**
- Create: `agents/lead_engineer/tasks/units/TASK-063/UNIT-TASK-063-001.md`

- [ ] **Step 1: Create directory and unit file**

```powershell
New-Item -ItemType Directory -Force "C:\Users\ycpig\autofolio\agents\lead_engineer\tasks\units\TASK-063"
```

Write the file at `agents/lead_engineer/tasks/units/TASK-063/UNIT-TASK-063-001.md`:

```markdown
---
unit_id: UNIT-TASK-063-001
task_id: TASK-063
task_set_id: TASKSET-PRODUCT-MATURITY
project_id: PROJECT-AUTOFOLIO
status: completed
horizon: unit
model_tier: worker_standard
escalation_triggers: [high_risk, repeated_failure]
context: "today_realized_pnl()가 순 현금흐름(SELL 양수, BUY 음수)을 반환하여 매수만 있는 날 대규모 음수값 → 일손실 서킷브레이커 오발동. app/database/repositories.py line 334 수정 필요. 평균매입가: execution_logs 전체 BUY 체결 가중평균."
inputs:
  - agents/lead_engineer/tasks/TASK-063-fix-circuit-breaker-pnl-logic.md
  - app/database/repositories.py
  - tests/unit/test_circuit_breaker.py
target_files:
  - app/database/repositories.py
  - tests/unit/test_circuit_breaker.py
scope: "app/database/repositories.py today_realized_pnl() 메서드만 수정. 서킷브레이커 임계치·다른 risk 로직 변경 금지."
acceptance:
  - "BUY-only day: today_realized_pnl() == 0.0"
  - "BUY then SELL at profit: realized == (sell_price - avg_cost) * qty > 0"
  - "BUY then SELL at loss: realized == (sell_price - avg_cost) * qty < 0"
  - "BUY-only day does NOT trip circuit breaker"
  - "python -m pytest tests/ -q green"
  - "python scripts/check_agent_docs.py 0 error"
verification:
  - "python -m pytest tests/unit/test_circuit_breaker.py -q"
  - "python -m pytest tests/ -q"
  - "python scripts/check_agent_docs.py"
handoff: "변경 파일 목록, pytest 결과, cost basis 방식, TZ 처리 방식 보고."
stop_condition: "today_realized_pnl() 수정 후 즉시 중단. 다른 repositories.py 메서드나 인접 모듈로 확장 금지."
depends_on: []
---

# UNIT-TASK-063-001 — 서킷브레이커 실현손익 계산 수정

## Context

`Repository.today_realized_pnl()` (`app/database/repositories.py` line 334)가
순 현금흐름(SELL 양수, BUY 음수)을 반환한다.

매수 주문이 많은 날 SELL 체결 없이 BUY만 발생하면 대규모 음수값 →
일손실 서킷브레이커 임계치 초과 → 정상 거래 중단.

## Target Files

- `app/database/repositories.py`
- `tests/unit/test_circuit_breaker.py`

## Scope

In scope: `today_realized_pnl()` SQL 로직 수정, 관련 단위테스트 재작성.

Out of scope: 서킷브레이커 임계치, 다른 서비스 레이어, 마이그레이션, UI 코드.

## Cost Basis Approach

DB에 포지션/평균단가 테이블 없음. `execution_logs JOIN order_logs WHERE side='BUY'`
전체 기간 가중평균으로 종목별 avg_buy_price 계산. SQL WITH CTE 사용.

## TZ 처리

`DATE(el.filled_at, '+9 hours') = DATE('now', '+9 hours')` — KST-aware, OS 무관 ('+9 hours' 고정).
`'localtime'` 미사용.

## Acceptance Criteria

- `today_realized_pnl()` BUY-only day → 0.0
- SELL at profit → positive realized
- SELL at loss → negative realized
- `test_buy_only_day_does_not_trip_circuit_breaker` PASS
- `python -m pytest tests/ -q` green
- `python scripts/check_agent_docs.py` 0 error

## 완료 기록

완료 시각: (실행 시 기입)

**변경 내용:** (실행 시 기입)

**검증 결과:** (실행 시 기입)
```

---

## Task 4: Update TASK-063 stub to 완료 + add audit block

**Files:**
- Modify: `agents/lead_engineer/tasks/TASK-063-fix-circuit-breaker-pnl-logic.md`

- [ ] **Step 1: Update frontmatter and body status**

In `agents/lead_engineer/tasks/TASK-063-fix-circuit-breaker-pnl-logic.md`:

1. Frontmatter line 3: `status: 대기` → `status: 완료`
2. Body line `상태: 대기` → `상태: 완료`

- [ ] **Step 2: Append completion audit block at end of file**

```markdown

## 완료 기록

완료 시각: (python scripts/now.py 결과 기입)
검토자: Backend Engineer / QA

## 증거

- `app/database/repositories.py` `today_realized_pnl()`: 순현금흐름 SQL → SELL 체결 기준 실현손익 SQL로 수정.
  - WITH CTE로 종목별 avg_buy_price 계산 (전체 기간 BUY 가중평균).
  - KST 필터: `DATE(el.filled_at, '+9 hours') = DATE('now', '+9 hours')` — OS TZ 무관.
- `tests/unit/test_circuit_breaker.py`: 버그 행동을 assert하던 테스트 교체.
  - 신규: `test_buy_only_day_returns_zero` (버그 재현 → 수정 증거).
  - 신규: `test_buy_only_day_does_not_trip_circuit_breaker` (서킷브레이커 오발동 재현 → 수정 증거).
  - `test_sell_after_buy_profit`, `test_sell_after_buy_loss`, `test_avg_cost_weighted_correctly` 추가.
  - `test_daily_loss_trips_when_loss_exceeds_threshold`: BUY fill → SELL fill로 교체.
- 수정 전: `test_buy_only_day_returns_zero` FAILED (반환값 -700_000).
- 수정 후: 전체 테스트 green.

## 리뷰

- 평균단가 근거: execution_logs 전체 BUY 기록 가중평균 (positions 테이블 없음).
- 안전 폴백: 매입 기록 없는 종목 SELL → avg_price = sell_price → realized = 0 (오발동 방지).
- TZ: `'+9 hours'` 고정, `'localtime'` 미사용.
```

---

## Task 5: Update INDEX.md and run generate_views + build_task_index

**Files:**
- Modify: `agents/lead_engineer/tasks/INDEX.md`

- [ ] **Step 1: Find TASK-063 entry in INDEX.md and change status to 완료**

```powershell
cd C:\Users\ycpig\autofolio
Select-String -Path "agents\lead_engineer\tasks\INDEX.md" -Pattern "TASK-063" -Context 1,1
```

Then edit the `| 대기 |` cell in that row to `| 완료 |`.

- [ ] **Step 2: Run view generators**

```powershell
cd C:\Users\ycpig\autofolio
python scripts/generate_views.py 2>&1 | tail -5
python scripts/build_task_index.py 2>&1 | tail -5
```

Expected: no errors.

---

## Task 6: Final verification gates

- [ ] **Step 1: Run full pytest**

```powershell
cd C:\Users\ycpig\autofolio
python -m pytest tests/ -q 2>&1 | tail -10
```

Expected: all green, 0 failures.

- [ ] **Step 2: check_agent_docs**

```powershell
cd C:\Users\ycpig\autofolio
python scripts/check_agent_docs.py 2>&1 | tail -10
```

Expected: 0 error(s).

- [ ] **Step 3: gate checks**

```powershell
cd C:\Users\ycpig\autofolio
python scripts/work_schema_gate.py --items --check 2>&1 | tail -5
python scripts/build_task_index.py --check 2>&1 | tail -5
python scripts/generate_views.py --check 2>&1 | tail -5
```

Expected: OK / 0 errors each.

---

## Task 7: Commit

- [ ] **Step 1: Stage only changed files**

```powershell
cd C:\Users\ycpig\autofolio
git add app/database/repositories.py
git add tests/unit/test_circuit_breaker.py
git add agents/lead_engineer/tasks/TASK-063-fix-circuit-breaker-pnl-logic.md
git add agents/lead_engineer/tasks/units/TASK-063/UNIT-TASK-063-001.md
git add agents/lead_engineer/tasks/INDEX.md
git add agents/lead_engineer/tasks/VIEW-by-status.md
git add agents/lead_engineer/tasks/VIEW-by-priority.md
git add agents/lead_engineer/tasks/VIEW-by-owner.md
git add agents/lead_engineer/tasks/VIEW-by-tag.md
git add agents/lead_engineer/tasks/VIEW-by-workload.md
git add tasks.index.json
```

Do NOT `git add .` or `git add -A` — there are many unrelated modified files in the working tree.

- [ ] **Step 2: Create commit**

```powershell
cd C:\Users\ycpig\autofolio
git commit -m @'
fix(safety): 서킷브레이커 실현손익 정확 계산 — 매수過多日 오발동 제거 (TASK-063)

today_realized_pnl()이 순현금흐름(BUY=음수)을 반환해
매수만 있는 날 일손실 서킷브레이커가 오발동하는 버그를 수정한다.

수정 내용:
- today_realized_pnl(): SELL 체결 기준 실현손익 계산으로 변경
  (sell_price - avg_buy_cost) * sell_qty; BUY-only → 0
- 평균매입가: execution_logs 전체 BUY 가중평균 (WITH CTE)
- KST 필터: DATE(filled_at, '+9 hours') — OS TZ 무관
- 테스트: 버그 재현→수정 증거 (test_buy_only_day_returns_zero,
  test_buy_only_day_does_not_trip_circuit_breaker)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
'@
```

---

## Self-Review

**Spec coverage check:**

| Requirement | Task |
|-------------|------|
| BUY-only day → realized = 0 | Task 1 `test_buy_only_day_returns_zero`, Task 2 SQL |
| SELL at profit → positive realized | Task 1 `test_sell_after_buy_profit` |
| SELL at loss → negative realized | Task 1 `test_sell_after_buy_loss` |
| Weighted avg cost | Task 1 `test_avg_cost_weighted_correctly`, Task 2 CTE |
| Circuit breaker buy-only day no trip | Task 1 `test_buy_only_day_does_not_trip_circuit_breaker` |
| Circuit breaker SELL loss trips | Task 1 updated `test_daily_loss_trips_when_loss_exceeds_threshold` |
| TZ-independent KST filter | Task 2 `'+9 hours'` |
| UNIT record created | Task 3 |
| TASK-063 stub 대기→완료 | Task 4 |
| INDEX.md updated | Task 5 |
| generate_views + build_task_index | Task 5 |
| Gates pass | Task 6 |
| Commit with correct message | Task 7 |

**Placeholder scan:** No TBD or TODO in plan. All SQL and Python code is complete.

**Type consistency:** `today_realized_pnl()` returns `float` throughout. `repo.create_order_log()` and `repo.create_execution_log()` signatures match existing tests. `repo.update_global_risk_limit()` called with keyword arg `max_daily_amount=` — matches `app/database/repositories.py` line 300.
