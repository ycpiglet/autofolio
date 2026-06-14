# TASK-057: KPI 일손익률/누적손익률 실계산 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the hardcoded `0.0` from `kpis()` in `app/ui/backend.py` and replace with real computed values from SQLite `execution_logs`.

**Architecture:** Add two new query helpers to `Repository` (`total_realized_pnl()` and `total_buy_cost_basis()`), then compute `daily_return` and `total_return` inside `kpis()` from those helpers plus the existing `today_realized_pnl()` and holdings unrealized PnL already available in `holdings_df`. No new schema changes.

**Tech Stack:** Python, SQLite (via `app/database/repositories.py`), pytest, existing `create_order_log`/`create_execution_log` repo helpers for test seeding.

---

## Calculation Basis — DOCUMENT BEFORE CODING

### daily_return (일손익률)

**Numerator:** `today_realized_pnl()` (already correct from TASK-063) — today's SELL fills using avg-cost basis.  
**Denominator:** Total buy cost of current holdings = sum of (avg_price × quantity) for all currently-held positions. This approximates "what we have invested today". If holdings are empty (no positions), daily_return = 0.0.

**Simplification honest note:** We do NOT attempt to look up yesterday's closing valuation (no price-series table exists). Using current holdings buy cost as denominator is a reasonable proxy for "invested capital" but will slightly overstate the rate if today's buys add to holdings. This is documented in the code as a comment.

### total_return (누적손익률)

**Numerator:** `total_realized_pnl()` (all-time SELL realized PnL, new helper) + current `holdings_df` unrealized PnL (평가손익 sum).  
**Denominator:** `total_buy_cost_basis()` (new helper) = total cost of ALL BUY fills ever (sum of filled_price × filled_quantity for BUY side). This is the total invested principal over all time.  

**Simplification honest note:** This counts money that was already realized and withdrawn (SELL proceeds) as still "invested". A full TWR would require daily portfolio snapshots. The simple total_buy_cost / net_pnl approach is standard for small portfolio trackers without price history. Documented in code.

---

## Files

| Action | File |
|--------|------|
| Modify | `app/database/repositories.py` — add `total_realized_pnl()` and `total_buy_cost_basis()` |
| Modify | `app/ui/backend.py` — fix `kpis()` to compute real values |
| Modify | `tests/unit/test_backend_kpis.py` — add failing test, update placeholder test |
| Create | `agents/lead_engineer/tasks/units/TASK-057/UNIT-TASK-057-001.md` |
| Modify | `agents/lead_engineer/tasks/TASK-057-fix-kpi-returns-hardcoded-zero.md` — mark 완료 |
| Modify | `agents/lead_engineer/tasks/INDEX.md` — update TASK-057 row to 완료 |
| Regenerate | `agents/lead_engineer/tasks/BACKLOG.md`, `VIEW-*.md`, `tasks.index.json` (via scripts) |

---

## Task 1: Add Repository helpers

**Files:**
- Modify: `app/database/repositories.py` (after `today_realized_pnl()`, around line 375)

- [ ] **Step 1.1: Write the failing test for `total_realized_pnl()`**

Open `tests/unit/test_circuit_breaker.py`. Add this test class after `TestTodayRealizedPnl` (uses same `repo` fixture):

```python
class TestTotalRealizedPnl:
    def test_returns_zero_when_no_executions(self, repo):
        assert repo.total_realized_pnl() == 0.0

    def test_accumulates_multiple_sell_days(self, repo):
        """Two SELL fills on different (simulated) days both count."""
        # BUY 2 shares @ 70_000
        for kid in ("B_acc1", "B_acc2"):
            lid = repo.create_order_log(
                condition_id=None, symbol="005930", side="BUY",
                order_type="LIMIT", order_price=70000.0, current_price=70000.0,
                quantity=1, kis_order_id=kid, order_status="FILLED",
            )
            repo.create_execution_log(
                order_log_id=lid, symbol="005930",
                filled_price=70000.0, filled_quantity=1,
            )
        # SELL 1 @ 75_000 (profit 5_000)
        s1 = repo.create_order_log(
            condition_id=None, symbol="005930", side="SELL",
            order_type="LIMIT", order_price=75000.0, current_price=75000.0,
            quantity=1, kis_order_id="S_acc1", order_status="FILLED",
        )
        repo.create_execution_log(
            order_log_id=s1, symbol="005930",
            filled_price=75000.0, filled_quantity=1,
        )
        # total_realized_pnl should be 5_000 (all-time, no date filter)
        assert repo.total_realized_pnl() == pytest.approx(5000.0)


class TestTotalBuyCostBasis:
    def test_returns_zero_when_no_executions(self, repo):
        assert repo.total_buy_cost_basis() == 0.0

    def test_sums_all_buy_fills(self, repo):
        """BUY 2 shares @ 70_000 and 1 share @ 80_000 → total cost = 2*70_000 + 80_000 = 220_000."""
        fills = [(70000.0, 2, "B_cost1"), (80000.0, 1, "B_cost2")]
        for price, qty, kid in fills:
            lid = repo.create_order_log(
                condition_id=None, symbol="005930", side="BUY",
                order_type="LIMIT", order_price=price, current_price=price,
                quantity=qty, kis_order_id=kid, order_status="FILLED",
            )
            repo.create_execution_log(
                order_log_id=lid, symbol="005930",
                filled_price=price, filled_quantity=qty,
            )
        assert repo.total_buy_cost_basis() == pytest.approx(220000.0)
```

- [ ] **Step 1.2: Run tests to verify they FAIL**

```powershell
python -m pytest tests/unit/test_circuit_breaker.py::TestTotalRealizedPnl tests/unit/test_circuit_breaker.py::TestTotalBuyCostBasis -v
```

Expected: `AttributeError: 'Repository' object has no attribute 'total_realized_pnl'` (both classes fail)

- [ ] **Step 1.3: Implement `total_realized_pnl()` and `total_buy_cost_basis()` in `app/database/repositories.py`**

Add immediately after `today_realized_pnl()` (around line 375, before `increment_consecutive_failures`):

```python
def total_realized_pnl(self) -> float:
    """전체 기간 SELL 체결 기준 실현 손익 합계 (누적손익률 분자 사용).

    실현 손익 = Σ (매도체결가 − 종목별 평균매입가) × 매도수량
    평균매입가: 전체 기간 BUY 체결 가중평균 (avg cost basis).
    체결 내역 없으면 0.0 반환.
    today_realized_pnl()과 동일한 로직이나 날짜 필터 없음.
    """
    with get_connection(self.db_path) as conn:
        row = conn.execute(
            '''
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
        ).fetchone()
        return float(row["realized_pnl"] or 0.0)

def total_buy_cost_basis(self) -> float:
    """전체 기간 BUY 체결 원가 합계 (누적손익률 분모 사용).

    투자 원금 = Σ (매수체결가 × 매수수량) for all BUY fills ever.
    체결 내역 없으면 0.0 반환.
    """
    with get_connection(self.db_path) as conn:
        row = conn.execute(
            '''
            SELECT COALESCE(
                SUM(el.filled_price * el.filled_quantity), 0
            ) AS total_cost
            FROM execution_logs el
            JOIN order_logs ol ON el.order_log_id = ol.id
            WHERE ol.side = 'BUY'
              AND el.filled_quantity > 0
            '''
        ).fetchone()
        return float(row["total_cost"] or 0.0)
```

- [ ] **Step 1.4: Run tests to verify they PASS**

```powershell
python -m pytest tests/unit/test_circuit_breaker.py::TestTotalRealizedPnl tests/unit/test_circuit_breaker.py::TestTotalBuyCostBasis -v
```

Expected: 4 passed

- [ ] **Step 1.5: Run full suite to confirm no regressions**

```powershell
python -m pytest tests/ -q
```

Expected: all previously-passing tests still pass + 4 new pass

- [ ] **Step 1.6: Commit**

```powershell
git add app/database/repositories.py tests/unit/test_circuit_breaker.py
git commit -m "feat(repos): total_realized_pnl + total_buy_cost_basis helpers (TASK-057)"
```

---

## Task 2: Add failing KPI test

**Files:**
- Modify: `tests/unit/test_backend_kpis.py`

- [ ] **Step 2.1: Add the failing test for live daily/total return**

The test must use a real in-process SQLite DB (not mocks) so it exercises `kpis()` through `Repository`. Add a new test class at the bottom of `tests/unit/test_backend_kpis.py`:

```python
# ---------------------------------------------------------------------------
# kpis() daily_return / total_return — integration-style (in-process SQLite)
# ---------------------------------------------------------------------------

class TestKpisReturnRates:
    """kpis() daily_return and total_return must be non-zero when there is
    realized PnL and holdings. Uses a real temp SQLite DB — no network."""

    @pytest.fixture()
    def backend_with_fills(self, tmp_path, monkeypatch):
        """Seed: BUY 1 share @ 70_000, SELL 1 @ 75_000 (profit 5_000).
        Holdings: still hold 1 share with avg_price=70_000, current_price=77_000.
        unrealized PnL = (77_000 - 70_000) * 1 = 7_000.
        total_buy_cost = 2 * 70_000 = 140_000  (two BUY fills total).
        total_realized = 5_000.
        unrealized = 7_000.
        total_return = (5_000 + 7_000) / 140_000 = 8.57...%
        daily_realized = 5_000 (today SELL realized).
        daily_return = 5_000 / (holdings buy cost = 70_000 * 1 remaining) = 7.14...%
        """
        from types import SimpleNamespace

        from app.brokers.base import Position
        from app.database.repositories import Repository, WhitelistSymbol
        from app.database.sqlite_db import initialize_database
        from app.ui import backend

        db_path = tmp_path / "kpi_test.db"
        initialize_database(db_path)
        repo = Repository(db_path)
        repo.add_whitelist_symbol(
            WhitelistSymbol(symbol="005930", name="삼성전자", market="KRX", role="LARGE_CAP_TEST")
        )

        # BUY 1 @ 70_000 (first buy — will be sold)
        buy1 = repo.create_order_log(
            condition_id=None, symbol="005930", side="BUY",
            order_type="LIMIT", order_price=70000.0, current_price=70000.0,
            quantity=1, kis_order_id="B1", order_status="FILLED",
        )
        repo.create_execution_log(
            order_log_id=buy1, symbol="005930",
            filled_price=70000.0, filled_quantity=1,
        )

        # BUY 1 @ 70_000 (second buy — still held)
        buy2 = repo.create_order_log(
            condition_id=None, symbol="005930", side="BUY",
            order_type="LIMIT", order_price=70000.0, current_price=70000.0,
            quantity=1, kis_order_id="B2", order_status="FILLED",
        )
        repo.create_execution_log(
            order_log_id=buy2, symbol="005930",
            filled_price=70000.0, filled_quantity=1,
        )

        # SELL 1 @ 75_000 today (realized = 5_000)
        # Use explicit KST-today timestamp so the test is TZ-independent
        sell1 = repo.create_order_log(
            condition_id=None, symbol="005930", side="SELL",
            order_type="LIMIT", order_price=75000.0, current_price=75000.0,
            quantity=1, kis_order_id="S1", order_status="FILLED",
        )
        # Inject today-KST into filled_at ('+9 hours' = KST; avoids localtime)
        from app.database.sqlite_db import get_connection
        with get_connection(db_path) as conn:
            conn.execute(
                """
                INSERT INTO execution_logs(order_log_id, symbol, filled_price, filled_quantity, filled_at)
                VALUES (?, ?, ?, ?, datetime('now', '+9 hours', 'start of day', '-9 hours', '+1 minute'))
                """,
                (sell1, "005930", 75000.0, 1),
            )

        # Mock holdings: 1 share of 005930 @ avg_price=70_000, current=77_000
        fake_positions = [Position("005930", 1, 70000.0)]
        fake_broker = SimpleNamespace(
            get_positions=lambda: fake_positions,
            get_prices_batch=lambda syms: {"005930": 77000.0},
            get_current_price=lambda s: SimpleNamespace(price=77000.0),
            get_cash_balance=lambda: 0.0,
        )
        wl_data = {"005930": {"name": "삼성전자", "role": "LARGE_CAP_TEST"}}

        monkeypatch.setattr(backend, "_ctx", lambda: (repo, fake_broker, None, None))
        return repo

    def test_daily_return_is_nonzero(self, backend_with_fills, monkeypatch):
        """daily_return must be > 0 when there is today's realized profit.

        Current code returns 0.0 (FAIL before fix).
        """
        from app.ui import backend
        result = backend.kpis()
        assert result["일손익률"] > 0.0, (
            f"Expected daily_return > 0 (got {result['일손익률']}). "
            "Hardcoded 0.0 not yet replaced."
        )

    def test_total_return_is_nonzero(self, backend_with_fills, monkeypatch):
        """total_return must be > 0 when there is realized + unrealized profit.

        Current code returns 0.0 (FAIL before fix).
        """
        from app.ui import backend
        result = backend.kpis()
        assert result["누적손익률"] > 0.0, (
            f"Expected total_return > 0 (got {result['누적손익률']}). "
            "Hardcoded 0.0 not yet replaced."
        )

    def test_return_values_match_formula(self, backend_with_fills, monkeypatch):
        """Verify exact formula output.

        total_buy_cost = 140_000 (2 BUY fills × 70_000).
        total_realized = 5_000. unrealized = 7_000.
        total_return = (5_000 + 7_000) / 140_000 * 100 ≈ 8.57%.
        daily holdings buy cost = 1 × 70_000 = 70_000.
        daily_return = 5_000 / 70_000 * 100 ≈ 7.14%.
        """
        from app.ui import backend
        result = backend.kpis()
        assert result["누적손익률"] == pytest.approx(12000 / 140000 * 100, rel=0.01)
        assert result["일손익률"] == pytest.approx(5000 / 70000 * 100, rel=0.01)
```

- [ ] **Step 2.2: Run tests to verify they FAIL**

```powershell
python -m pytest tests/unit/test_backend_kpis.py::TestKpisReturnRates -v
```

Expected: `FAILED — assert 0.0 > 0` (3 failures — the hardcoded 0.0 is still there)

- [ ] **Step 2.3: Also update the old placeholder test that asserts 0.0**

In `tests/unit/test_backend_kpis.py`, find `test_daily_and_cumulative_pnl_rates_are_placeholder` and replace it with a new test that documents the fix:

Old (around line 117):
```python
def test_daily_and_cumulative_pnl_rates_are_placeholder(self):
    """일손익률 and 누적손익률 are 0.0 placeholders (not yet live)."""
    df = self._make_holdings_df(1_000_000.0, 50_000.0)
    with (
        patch("app.ui.backend.holdings_df", return_value=df),
        patch("app.ui.backend._ctx", return_value=self._no_cash_ctx()),
    ):
        from app.ui import backend
        result = backend.kpis()
    assert result["일손익률"] == 0.0
    assert result["누적손익률"] == 0.0
```

Replace with:
```python
def test_daily_and_cumulative_pnl_rates_zero_when_no_fills(self):
    """일손익률 and 누적손익률 are 0.0 when no execution fills exist.

    With no_cash_ctx the repo mock has no execution_logs → both returns 0.0.
    This is correct behavior (empty portfolio), not a placeholder.
    """
    from types import SimpleNamespace
    from app.database.repositories import Repository
    from app.database.sqlite_db import initialize_database

    # Use a real empty repo so today_realized_pnl() / total_realized_pnl() return 0
    import tempfile, pathlib
    with tempfile.TemporaryDirectory() as td:
        db_path = pathlib.Path(td) / "empty.db"
        initialize_database(db_path)
        empty_repo = Repository(db_path)

        df = self._make_holdings_df(1_000_000.0, 50_000.0)
        fake_broker = SimpleNamespace(get_cash_balance=lambda: 0.0)
        with (
            patch("app.ui.backend.holdings_df", return_value=df),
            patch("app.ui.backend._ctx", return_value=(empty_repo, fake_broker, None, None)),
        ):
            from app.ui import backend
            result = backend.kpis()
    assert result["일손익률"] == 0.0
    assert result["누적손익률"] == 0.0
```

- [ ] **Step 2.4: Commit the failing tests**

```powershell
git add tests/unit/test_backend_kpis.py
git commit -m "test(kpis): failing tests for daily/total return (TASK-057 TDD red)"
```

---

## Task 3: Fix `kpis()` in `app/ui/backend.py`

**Files:**
- Modify: `app/ui/backend.py` — `kpis()` function (lines 199-222)

- [ ] **Step 3.1: Implement real daily_return and total_return in `kpis()`**

Replace the current `kpis()` implementation with:

```python
def kpis() -> dict:
    """라이브 KPI — 총자산·평가손익·일손익률·누적손익률·현금비중.

    반환 키: 총자산, 일손익률, 누적손익률, 현금비중, 평가손익.

    ## 계산 기준 (Basis Notes)

    ### 일손익률 (daily_return)
    분자: today_realized_pnl() — 당일 SELL 기준 실현 손익 (TASK-063 수정 완료).
    분모: 현재 보유 종목의 매수 원가 합계 = Σ(평단 × 수량).
    단순화: 전일 종가 기준 평가액 대신 현재 보유 원가를 분모로 사용.
    이유: 일별 가격 시계열 테이블이 없어 전일 평가액 조회 불가.

    ### 누적손익률 (total_return)
    분자: total_realized_pnl() + 현재 보유 미실현 평가손익 합계.
    분모: total_buy_cost_basis() — 전체 기간 BUY 체결 원가 합계 (투자 원금).
    단순화: 매도 후 회수된 원금도 분모에 포함 → 실제 TWR보다 보수적 수치.
    이유: 일별 포트폴리오 스냅샷 테이블 없음.

    실패 시 0.0 폴백 (화면 안정성 유지).
    """
    repo, broker, _, _ = _ctx()
    df = holdings_df(include_dividends=False)
    total_market = float(df["평가금액"].sum()) if not df.empty else 0.0
    total_pnl = float(df["평가손익"].sum()) if not df.empty else 0.0

    try:
        cash = float(broker.get_cash_balance()) if hasattr(broker, "get_cash_balance") else 0.0
    except Exception:
        cash = 0.0

    total_assets = total_market + cash
    cash_ratio = (cash / total_assets * 100) if total_assets else 0.0

    # --- daily_return ---
    try:
        today_realized = repo.today_realized_pnl()
        # 보유 종목 평수 원가 합계 (분모)
        holdings_cost = float((df["평단"] * df["수량"]).sum()) if not df.empty else 0.0
        daily_return = (today_realized / holdings_cost * 100) if holdings_cost else 0.0
    except Exception:
        daily_return = 0.0

    # --- total_return ---
    try:
        total_realized = repo.total_realized_pnl()
        total_cost = repo.total_buy_cost_basis()
        total_net_pnl = total_realized + total_pnl  # 실현 + 미실현
        total_return = (total_net_pnl / total_cost * 100) if total_cost else 0.0
    except Exception:
        total_return = 0.0

    return {
        "총자산": total_assets,
        "일손익률": daily_return,
        "누적손익률": total_return,
        "현금비중": cash_ratio,
        "평가손익": total_pnl,
    }
```

- [ ] **Step 3.2: Run the failing tests — verify they now PASS**

```powershell
python -m pytest tests/unit/test_backend_kpis.py::TestKpisReturnRates -v
```

Expected: 3 passed

- [ ] **Step 3.3: Run the full kpis test file**

```powershell
python -m pytest tests/unit/test_backend_kpis.py -v
```

Expected: all tests pass (including the updated placeholder test)

- [ ] **Step 3.4: Run full test suite**

```powershell
python -m pytest tests/ -q
```

Expected: all previously-passing tests still pass + new tests pass

- [ ] **Step 3.5: Commit**

```powershell
git add app/ui/backend.py tests/unit/test_backend_kpis.py
git commit -m "fix(correctness): KPI 일/누적 손익률 실계산 — 0.0 하드코딩 제거 (TASK-057)"
```

---

## Task 4: Create UNIT spec and update task records

**Files:**
- Create: `agents/lead_engineer/tasks/units/TASK-057/UNIT-TASK-057-001.md`
- Modify: `agents/lead_engineer/tasks/TASK-057-fix-kpi-returns-hardcoded-zero.md`
- Modify: `agents/lead_engineer/tasks/INDEX.md`

- [ ] **Step 4.1: Create the UNIT spec file**

Create `agents/lead_engineer/tasks/units/TASK-057/UNIT-TASK-057-001.md`:

```markdown
---
unit_id: UNIT-TASK-057-001
task_id: TASK-057
task_set_id: TASKSET-PRODUCT-MATURITY
project_id: PROJECT-AUTOFOLIO
status: completed
horizon: unit
model_tier: worker_standard
escalation_triggers: [high_risk, repeated_failure]
context: "backend.kpis()의 일손익률/누적손익률이 0.0 하드코딩 → 홈 KPI 카드 항상 0.00% 표시. repositories.py에 total_realized_pnl()/total_buy_cost_basis() 헬퍼 추가 후 kpis() 실계산."
inputs:
  - agents/lead_engineer/tasks/TASK-057-fix-kpi-returns-hardcoded-zero.md
  - app/ui/backend.py
  - app/database/repositories.py
  - tests/unit/test_backend_kpis.py
target_files:
  - app/database/repositories.py
  - app/ui/backend.py
  - tests/unit/test_backend_kpis.py
  - tests/unit/test_circuit_breaker.py
scope: "kpis() 함수 일손익률/누적손익률 실계산. 신규 repo 헬퍼 2개. 다른 화면/API 변경 금지."
acceptance:
  - "kpis() 일손익률 > 0 when today SELL realized profit exists"
  - "kpis() 누적손익률 > 0 when total realized + unrealized profit exists"
  - "empty holdings/fills → both return 0.0 (graceful)"
  - "python -m pytest tests/ -q green"
  - "python scripts/check_agent_docs.py 0 error"
verification:
  - "python -m pytest tests/unit/test_backend_kpis.py -v"
  - "python -m pytest tests/ -q"
  - "python scripts/check_agent_docs.py"
handoff: "변경 파일 목록, 계산 기준 요약, pytest 결과, check_agent_docs 결과 보고."
stop_condition: "kpis() 수정 완료 후 즉시 중단. 인접 뷰·다른 백엔드 함수 확장 금지."
depends_on: [TASK-063]
---

# UNIT-TASK-057-001 — KPI 일손익률/누적손익률 실계산

## Context

`backend.kpis()`의 `일손익률`/`누적손익률`이 `0.0` 하드코딩.
`execution_logs`·`order_logs` 기반 실계산 필요.

## Target Files

- `app/database/repositories.py` — `total_realized_pnl()`, `total_buy_cost_basis()` 추가
- `app/ui/backend.py` — `kpis()` 실계산 구현
- `tests/unit/test_backend_kpis.py` — 실패 테스트 선행, 통과 확인
- `tests/unit/test_circuit_breaker.py` — 신규 repo 헬퍼 단위테스트

## Calculation Basis

### daily_return
- 분자: `repo.today_realized_pnl()` (당일 SELL 실현 손익, TASK-063 수정 완료)
- 분모: `Σ(평단 × 수량)` of current holdings (보유 원가)
- 단순화: 전일 종가 평가액 없음 → 보유 원가를 분모로 대체. 코드 주석에 명시.

### total_return
- 분자: `repo.total_realized_pnl()` + `holdings_df 평가손익 합계`
- 분모: `repo.total_buy_cost_basis()` (전체 BUY 체결 원가 합계)
- 단순화: 매도 회수분 포함 분모 → TWR보다 보수적. 코드 주석에 명시.

## 완료 기록

완료 시각: (실행 시점에 기입)
검토자: Backend Engineer / QA
```

- [ ] **Step 4.2: Update TASK-057 stub — mark 완료 in BOTH frontmatter and body**

In `agents/lead_engineer/tasks/TASK-057-fix-kpi-returns-hardcoded-zero.md`:

Change frontmatter line 3: `status: 대기` → `status: 완료`  
Change frontmatter `updated_at` to current KST time.

In the body, change:
`상태: 대기` → `상태: 완료`

Append a completion block at the end of the file:

```markdown
## 완료 기록

완료 시각: (run `python scripts/now.py` and insert result)
검토자: Backend Engineer / QA

## 증거

- `app/database/repositories.py`: `total_realized_pnl()` 추가 (날짜 필터 없는 전체 기간 실현손익).
  `total_buy_cost_basis()` 추가 (전체 BUY 체결 원가 합계 = 투자 원금 근사).
- `app/ui/backend.py` `kpis()`:
  - `일손익률` = `today_realized_pnl() / holdings_cost * 100`
  - `누적손익률` = `(total_realized + unrealized_pnl) / total_buy_cost * 100`
  - 실패 시 0.0 폴백 유지 (화면 안정성).
- `tests/unit/test_backend_kpis.py`: `TestKpisReturnRates` 추가 (3 tests).
  TDD — 실패 테스트 선행 → 구현 후 통과 확인.
- `tests/unit/test_circuit_breaker.py`: `TestTotalRealizedPnl`, `TestTotalBuyCostBasis` 추가 (4 tests).
- 수정 전: `test_daily_return_is_nonzero` FAILED (일손익률 == 0.0).
- 수정 후: 전체 passed.

## 리뷰

- 계산 기준 단순화:
  - 일손익률 분모: 전일 평가액 대신 현재 보유 원가. 이유: 일별 가격 시계열 없음.
  - 누적손익률 분모: 전체 BUY 원가 합계 (TWR보다 보수적). 이유: 포트폴리오 스냅샷 없음.
  - 두 단순화 모두 코드 docstring에 명시.
- TZ: `today_realized_pnl()` TASK-063 수정분 (`'+9 hours'`) 그대로 재사용.
- mock.data.kpis() 미변경 (하드코딩 데모값 유지).

실측 비용 (시간): (실행 후 기입)
실측 비용 (LLM 토큰): (실행 후 기입)

## Independent Audit

(검토 후 기입)
```

- [ ] **Step 4.3: Update INDEX.md**

In `agents/lead_engineer/tasks/INDEX.md`, find:
```
| [TASK-057](TASK-057-fix-kpi-returns-hardcoded-zero.md) | 대기 | Backend Engineer | fix: 일손익률/누적손익률 KPI 0.0 하드코딩 → v1 |
```

Replace with:
```
| [TASK-057](TASK-057-fix-kpi-returns-hardcoded-zero.md) | 완료 | Backend Engineer | fix: 일손익률/누적손익률 KPI 0.0 하드코딩 → v1 |
```

- [ ] **Step 4.4: Commit records**

```powershell
git add agents/lead_engineer/tasks/units/TASK-057/UNIT-TASK-057-001.md
git add agents/lead_engineer/tasks/TASK-057-fix-kpi-returns-hardcoded-zero.md
git add agents/lead_engineer/tasks/INDEX.md
git commit -m "docs(task): TASK-057 완료 기록 + UNIT 스펙 생성"
```

---

## Task 5: Regenerate views and final verification

**Files:**
- Regenerate: `agents/lead_engineer/tasks/BACKLOG.md`, `VIEW-*.md`, `tasks.index.json`

- [ ] **Step 5.1: Run generate_views.py**

```powershell
python scripts/generate_views.py
```

Expected: No errors. `BACKLOG.md` and `VIEW-*.md` files updated.

- [ ] **Step 5.2: Run build_task_index.py**

```powershell
python scripts/build_task_index.py
```

Expected: `tasks.index.json` updated.

- [ ] **Step 5.3: Run check gates**

```powershell
python scripts/check_agent_docs.py
```

Expected: `0 error(s)`

```powershell
python scripts/work_schema_gate.py --items --check
python scripts/build_task_index.py --check
python scripts/generate_views.py --check
```

Expected: all gates pass (exit code 0)

- [ ] **Step 5.4: Run full pytest**

```powershell
python -m pytest tests/ -q
```

Expected: green (all pass)

- [ ] **Step 5.5: Commit regenerated files**

```powershell
git add agents/lead_engineer/tasks/BACKLOG.md
git add agents/lead_engineer/tasks/VIEW-by-owner.md
git add agents/lead_engineer/tasks/VIEW-by-priority.md
git add agents/lead_engineer/tasks/VIEW-by-status.md
git add agents/lead_engineer/tasks/VIEW-by-tag.md
git add agents/lead_engineer/tasks/VIEW-by-workload.md
git add tasks.index.json
git commit -m "chore(views): BACKLOG + VIEW-* + tasks.index.json 재생성 (TASK-057 완료 반영)"
```

- [ ] **Step 5.6: Final combined commit (squash-optional)**

Create the canonical combined commit with the required message:

```powershell
git log --oneline -5  # verify commits look right
```

If you need a single canonical commit instead of the task commits above, amend or rebase. Otherwise the individual commits from Tasks 1–4 plus the views commit form the complete change set.

The final git log should include a commit with subject:
```
fix(correctness): KPI 일/누적 손익률 실계산 — 0.0 하드코딩 제거 (TASK-057)
```
with body and trailer:
```
Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
```

---

## Self-Review

**Spec coverage check:**

| Spec requirement | Covered by |
|---|---|
| Find real `kpis()` location | Verified in `app/ui/backend.py` lines 199-222 |
| `daily_return` real computation | Task 3 — uses `today_realized_pnl() / holdings_cost` |
| `total_return` real computation | Task 3 — uses `(total_realized + unrealized) / total_buy_cost` |
| Repository query helpers | Task 1 — `total_realized_pnl()`, `total_buy_cost_basis()` |
| TDD: failing test first | Task 2 — fails before Task 3 |
| TZ-independent date handling | `'+9 hours'` used in SELL fixture insert (Task 2 Step 1) |
| Keep mock kpis unchanged | `app/ui/mock/data.py` not in file list — not touched |
| UNIT spec created | Task 4 Step 1 |
| TASK-057 frontmatter+body both updated | Task 4 Step 2 — both `status:` and `상태:` |
| INDEX.md updated | Task 4 Step 3 |
| BACKLOG + VIEW-* regenerated | Task 5 Steps 1–2 |
| `check_agent_docs.py` 0 errors | Task 5 Step 3 |
| Commit message format | Task 5 Step 6 |

**Placeholder scan:** No TBD/TODO/placeholder language found.

**Type consistency:** `today_realized_pnl()` → `float`, `total_realized_pnl()` → `float`, `total_buy_cost_basis()` → `float`. All consistent across Tasks 1 and 3.
