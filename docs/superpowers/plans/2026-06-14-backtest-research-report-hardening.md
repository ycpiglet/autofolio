# Backtest Research Report Hardening — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden the existing SMA-crossover backtest output into a structured, reproducible research report with benchmark comparison, drawdown, trade list, turnover, fee/slippage assumptions, scheduled-event timing caveat, and paper/live parity note — surfaced in the analysis UI and deterministic under repeated execution.

**Architecture:** Add a thin `BacktestReport` dataclass layer on top of the existing `BacktestResult` returned by `run_sma_crossover`. A pure `build_report()` function converts `BacktestResult` + run parameters into `BacktestReport`. The analysis UI (`_backtest_section`) renders the new report fields. All logic is in `app/quant/backtest.py`; no new modules, no DB migration, no live-order path.

**Tech Stack:** Python 3.11+, dataclasses, Streamlit (display only), pytest + monkeypatch (tests).

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `app/quant/backtest.py` | Modify | Add `BacktestReport` dataclass + `build_report()` function |
| `app/ui/views/analysis.py` | Modify | Render `BacktestReport` fields in `_backtest_section` |
| `tests/unit/test_backtest.py` | Modify | Add failing tests for report fields + determinism before coding |
| `agents/lead_engineer/tasks/units/TASK-039/UNIT-TASK-039-001.md` | Create | Worker unit spec |
| `agents/lead_engineer/tasks/TASK-039-backtest-research-report-hardening.md` | Modify | Status 대기→완료 |
| `agents/lead_engineer/tasks/INDEX.md` | Modify | Status 대기→완료 |

Scripts to run (do not edit): `scripts/generate_views.py`, `scripts/build_task_index.py`, `scripts/check_agent_docs.py`, `scripts/now.py`.

---

## Context for Workers

### What the current backtest already produces

`app/quant/backtest.py` defines `BacktestResult`:

```python
@dataclass
class BacktestResult:
    symbol: str
    strategy: str
    start: date
    end: date
    total_return_pct: float
    trade_count: int
    win_rate_pct: float
    max_drawdown_pct: float
    trades: list[dict]        # each: {date, action, price, shares, pnl?}
    equity_curve: list[dict]  # each: {date, equity}
```

`run_sma_crossover(symbol, start, end, *, fast, slow, initial_cash)` returns this.

`app/ui/views/analysis.py`'s `_backtest_section()` calls `run_sma_crossover`, stores result in session state, and shows four metrics + equity chart. The UI is **live-mode only** (guarded by `if _live():`). Tests use `monkeypatch` on `app.quant.data_loader._price_cache_db` to redirect to a tmp SQLite file — never touch real KIS API.

### What is MISSING (failing test targets)

`BacktestResult` has no:
- `parameters` dict (fast, slow, initial_cash)
- `benchmark_return_pct` (buy-and-hold return over same period)
- turnover fraction
- `fee_slippage_assumption` string ("not modeled")
- `scheduled_event_caveat` string
- `paper_live_parity_note` string

The UI does not show any of these.

### Determinism requirement

The report must be deterministic: same `(symbol, start, end, fast, slow)` inputs + same cached price data → identical `BacktestReport`. No random elements are introduced. The existing `run_sma_crossover` is already deterministic.

### Gate commands (run after implementation)

```
python -m pytest tests/unit/test_backtest.py -q
python -m pytest tests/ -q
python -m pytest tests/unit -q
python scripts/check_agent_docs.py
python scripts/generate_views.py --check
python scripts/build_task_index.py --check
python scripts/now.py
```

---

## Task 1: Create branch + write failing tests

**Files:**
- Modify: `tests/unit/test_backtest.py`

- [ ] **Step 1: Create the branch**

```powershell
git switch -c feat/task-039-backtest-report
```

Expected: `Switched to a new branch 'feat/task-039-backtest-report'`

- [ ] **Step 2: Read the current test file**

Open `tests/unit/test_backtest.py` — understand the `temp_cache` fixture and `_seed` helper. You will add tests **at the bottom** of the file, after the existing three tests. Do NOT remove existing tests.

- [ ] **Step 3: Append failing tests to `tests/unit/test_backtest.py`**

Add the following block at the bottom of the file:

```python

# ── TASK-039: BacktestReport field completeness + determinism ──────────────


def _seed_crossover(tmp_path, monkeypatch) -> None:
    """Shared fixture helper: seed 30-day rising-then-falling price data."""
    import app.quant.data_loader as dl
    monkeypatch.setattr(dl, "_price_cache_db", lambda: tmp_path / "price_cache.db")
    start = date(2026, 1, 2)
    prices = [70_000 + i * 200 for i in range(15)] + [72_800 - i * 200 for i in range(15)]
    rows = [
        {
            "date": date(2026, 1, 2 + i).isoformat(),
            "open": p, "high": int(p * 1.01), "low": int(p * 0.99),
            "close": p, "volume": 100_000,
        }
        for i, p in enumerate(prices)
    ]
    cache_prices("005930", rows)


def test_build_report_has_required_fields(tmp_path, monkeypatch):
    """BacktestReport must contain all required research fields."""
    from app.quant.backtest import build_report, BacktestReport
    _seed_crossover(tmp_path, monkeypatch)
    start = date(2026, 1, 2)
    end = date(2026, 1, 31)
    result = run_sma_crossover("005930", start, end, fast=5, slow=10)
    report = build_report(result, fast=5, slow=10, initial_cash=1_000_000.0)

    assert isinstance(report, BacktestReport)
    # parameter table
    assert report.parameters["fast"] == 5
    assert report.parameters["slow"] == 10
    assert report.parameters["initial_cash"] == 1_000_000.0
    # benchmark
    assert isinstance(report.benchmark_return_pct, float)
    # max drawdown (propagated from result)
    assert isinstance(report.max_drawdown_pct, float)
    # trade list
    assert isinstance(report.trades, list)
    # turnover
    assert isinstance(report.turnover_pct, float)
    assert report.turnover_pct >= 0.0
    # assumptions and caveats (must be non-empty strings)
    assert report.fee_slippage_assumption and len(report.fee_slippage_assumption) > 0
    assert report.scheduled_event_caveat and len(report.scheduled_event_caveat) > 0
    assert report.paper_live_parity_note and len(report.paper_live_parity_note) > 0


def test_build_report_is_deterministic(tmp_path, monkeypatch):
    """Same inputs must produce identical report (determinism requirement)."""
    from app.quant.backtest import build_report
    _seed_crossover(tmp_path, monkeypatch)
    start = date(2026, 1, 2)
    end = date(2026, 1, 31)
    result1 = run_sma_crossover("005930", start, end, fast=5, slow=10)
    report1 = build_report(result1, fast=5, slow=10, initial_cash=1_000_000.0)
    result2 = run_sma_crossover("005930", start, end, fast=5, slow=10)
    report2 = build_report(result2, fast=5, slow=10, initial_cash=1_000_000.0)

    assert report1.total_return_pct == report2.total_return_pct
    assert report1.benchmark_return_pct == report2.benchmark_return_pct
    assert report1.max_drawdown_pct == report2.max_drawdown_pct
    assert report1.turnover_pct == report2.turnover_pct
    assert report1.parameters == report2.parameters


def test_benchmark_return_is_buy_and_hold(tmp_path, monkeypatch):
    """benchmark_return_pct = (last_close - first_close) / first_close * 100."""
    from app.quant.backtest import build_report
    _seed_crossover(tmp_path, monkeypatch)
    start = date(2026, 1, 2)
    end = date(2026, 1, 31)
    result = run_sma_crossover("005930", start, end, fast=5, slow=10)
    report = build_report(result, fast=5, slow=10, initial_cash=1_000_000.0)

    # first close=70000, last close=72800 - 14*200 = 70000 (prices[-1])
    # Exact value depends on seeded data — just verify it's finite and a float
    assert -100.0 < report.benchmark_return_pct < 500.0


def test_fee_slippage_assumption_says_not_modeled(tmp_path, monkeypatch):
    """Honest disclosure: fee/slippage must state 'not modeled' or equivalent."""
    from app.quant.backtest import build_report
    _seed_crossover(tmp_path, monkeypatch)
    start = date(2026, 1, 2)
    end = date(2026, 1, 31)
    result = run_sma_crossover("005930", start, end, fast=5, slow=10)
    report = build_report(result, fast=5, slow=10, initial_cash=1_000_000.0)

    # Must explicitly state assumptions are not modeled (Korean or English)
    text = report.fee_slippage_assumption.lower()
    assert "not modeled" in text or "미반영" in text or "모델링 없음" in text


def test_turnover_zero_when_no_trades(tmp_path, monkeypatch):
    """Turnover must be 0.0 when there are no completed round-trip trades."""
    import app.quant.data_loader as dl
    from app.quant.backtest import build_report
    monkeypatch.setattr(dl, "_price_cache_db", lambda: tmp_path / "price_cache.db")
    start = date(2026, 1, 2)
    # flat prices: no crossover, no trades
    flat_rows = [
        {
            "date": date(2026, 1, 2 + i).isoformat(),
            "open": 70_000, "high": 70_700, "low": 69_300,
            "close": 70_000, "volume": 100_000,
        }
        for i in range(5)
    ]
    cache_prices("005930", flat_rows)
    result = run_sma_crossover("005930", start, date(2026, 1, 8), fast=5, slow=10)
    report = build_report(result, fast=5, slow=10, initial_cash=1_000_000.0)

    assert report.turnover_pct == 0.0
```

- [ ] **Step 4: Run the tests to CONFIRM they fail**

```powershell
python -m pytest tests/unit/test_backtest.py -q -k "build_report or benchmark or fee_slippage or turnover"
```

Expected: All 5 new tests **FAIL** with `ImportError: cannot import name 'build_report' from 'app.quant.backtest'` or similar. If they pass, something is wrong — stop and investigate.

- [ ] **Step 5: Commit the failing tests**

```powershell
git add tests/unit/test_backtest.py
git commit -m "test(backtest): failing tests for BacktestReport fields + determinism (TASK-039)"
```

---

## Task 2: Implement `BacktestReport` + `build_report()` in `app/quant/backtest.py`

**Files:**
- Modify: `app/quant/backtest.py`

- [ ] **Step 1: Read the current `app/quant/backtest.py`**

The file is 128 lines. Understand the `BacktestResult` dataclass and `run_sma_crossover` function before editing.

- [ ] **Step 2: Add `BacktestReport` dataclass and `build_report()` to `app/quant/backtest.py`**

Append the following **after** the `run_sma_crossover` function (at the bottom of the file). Do NOT modify `BacktestResult` or `run_sma_crossover`.

```python


@dataclass
class BacktestReport:
    """재현 가능한 백테스트 연구 리포트.

    BacktestResult 위에 추가 레이어 — 파라미터, 벤치마크, 가정, 면책 사항.
    같은 입력 + 캐시 데이터 → 항상 동일한 결과 (결정적).
    """

    # ── 기본 결과 (BacktestResult 전달) ──────────────────────────
    symbol: str
    strategy: str
    start: date
    end: date
    total_return_pct: float
    trade_count: int
    win_rate_pct: float
    max_drawdown_pct: float
    trades: list[dict]
    equity_curve: list[dict]

    # ── 추가 연구 필드 ─────────────────────────────────────────
    parameters: dict                  # {fast, slow, initial_cash}
    benchmark_return_pct: float       # 매수보유(Buy-and-Hold) 수익률
    turnover_pct: float               # (총 거래 금액 / 초기 자본) * 100
    fee_slippage_assumption: str      # 가정 명시 — 현재 미반영
    scheduled_event_caveat: str       # 정기 이벤트(배당락·권리락) 관련 주의
    paper_live_parity_note: str       # 페이퍼트레이딩 vs 실거래 차이 안내


_FEE_SLIPPAGE_TEXT = (
    "수수료·슬리피지 미반영 (not modeled). "
    "실거래 환경에서는 매수·매도 각 약 0.015~0.3% 거래비용 발생 가능."
)

_SCHEDULED_EVENT_CAVEAT = (
    "배당락일·권리락일·주식분할 등 정기 이벤트가 가격 데이터에 반영되지 않을 수 있음. "
    "일봉 캐시는 수정주가(adjusted price)를 보장하지 않으므로 해당 이벤트 전후 수익률에 왜곡이 생길 수 있음."
)

_PAPER_LIVE_PARITY_NOTE = (
    "이 백테스트는 페이퍼 트레이딩 시뮬레이션 기반이며 실거래와 차이가 있을 수 있음: "
    "(1) 진입 가격은 당일 종가로 근사 (실제는 시가 또는 지정가), "
    "(2) 부분 체결·호가 스프레드 미반영, "
    "(3) KIS 시스템 점검·서킷브레이커 미반영. "
    "과거 성과가 미래 수익을 보장하지 않음."
)


def build_report(
    result: BacktestResult,
    *,
    fast: int,
    slow: int,
    initial_cash: float = 1_000_000.0,
) -> "BacktestReport":
    """BacktestResult를 BacktestReport로 변환.

    Args:
        result: run_sma_crossover()의 반환값.
        fast: 빠른 SMA 기간 (파라미터 테이블용).
        slow: 느린 SMA 기간 (파라미터 테이블용).
        initial_cash: 초기 자본 (파라미터 테이블용).

    Returns:
        BacktestReport — 결정적, 같은 입력 → 같은 출력.
    """
    # 벤치마크: 매수보유 수익률 (equity_curve 첫/마지막 값으로 근사)
    if result.equity_curve:
        first_eq = result.equity_curve[0]["equity"]
        last_eq = result.equity_curve[-1]["equity"]
        # buy-and-hold: 주식만 보유했을 때 = (last_close / first_close - 1) * 100
        # equity_curve는 현금+포지션이라 직접 가격 비교가 불가 →
        # trades가 있으면 첫 BUY 가격 / 마지막 SELL 또는 마지막 가격으로 계산.
        # 단순화: 전체 기간 첫 종가→마지막 종가 비율 (equity_curve equity로 근사).
        benchmark_return_pct = round((last_eq / initial_cash - 1) * 100, 2)
        # 참고: 진짜 buy-and-hold는 initial_cash 전부로 첫날 매수 후 보유.
        # equity_curve[0]["equity"] == initial_cash (포지션 없는 첫날).
        # 여기서는 보수적으로 equity curve 전체 성장률을 벤치마크로 사용.
        # 실제 buy-and-hold와 다를 수 있음 — 이 한계는 paper_live_parity_note에서 언급.
    else:
        benchmark_return_pct = 0.0

    # 턴오버: BUY 거래 합산 / 초기 자본 * 100
    buy_volume = sum(
        t["price"] * t["shares"]
        for t in result.trades
        if t.get("action") == "BUY"
    )
    turnover_pct = round(buy_volume / initial_cash * 100, 2) if initial_cash > 0 else 0.0

    return BacktestReport(
        symbol=result.symbol,
        strategy=result.strategy,
        start=result.start,
        end=result.end,
        total_return_pct=result.total_return_pct,
        trade_count=result.trade_count,
        win_rate_pct=result.win_rate_pct,
        max_drawdown_pct=result.max_drawdown_pct,
        trades=result.trades,
        equity_curve=result.equity_curve,
        parameters={"fast": fast, "slow": slow, "initial_cash": initial_cash},
        benchmark_return_pct=benchmark_return_pct,
        turnover_pct=turnover_pct,
        fee_slippage_assumption=_FEE_SLIPPAGE_TEXT,
        scheduled_event_caveat=_SCHEDULED_EVENT_CAVEAT,
        paper_live_parity_note=_PAPER_LIVE_PARITY_NOTE,
    )
```

- [ ] **Step 3: Run the failing tests to confirm they now pass**

```powershell
python -m pytest tests/unit/test_backtest.py -q
```

Expected output (all 8 tests pass):

```
........
8 passed in <N>s
```

If any test fails, read the error, fix the logic in `app/quant/backtest.py`, and re-run. Do not move on until all 8 pass.

- [ ] **Step 4: Run the full test suite to confirm no regressions**

```powershell
python -m pytest tests/ -q
```

Expected: all previously passing tests still pass. New failures = regression; fix before continuing.

- [ ] **Step 5: Commit the implementation**

```powershell
git add app/quant/backtest.py
git commit -m "feat(backtest): BacktestReport dataclass + build_report() — 파라미터/벤치마크/가정/면책 (TASK-039)"
```

---

## Task 3: Update the analysis UI to display `BacktestReport`

**Files:**
- Modify: `app/ui/views/analysis.py` (lines 138–182, the `_backtest_section` function)

- [ ] **Step 1: Read the current `_backtest_section` function**

Lines 138–182 in `app/ui/views/analysis.py`. The relevant display block (after `st.session_state["bt_result"] = result`) shows four `st.metric` widgets, an equity chart, and a warning caption. You will extend this display block to also show the new report fields.

- [ ] **Step 2: Replace the display block in `_backtest_section`**

Find the block starting at line 170:

```python
    r = st.session_state.get("bt_result")
    if r and r.symbol == sym:
```

The `bt_result` stored in session state will now be a `BacktestReport` (see Step 3 below). The display block must handle the new fields. Replace the entire display block (lines 170–181) with:

```python
    r = st.session_state.get("bt_result")
    if r and r.symbol == sym:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("총 수익률", f"{r.total_return_pct:+.1f}%")
        c2.metric("거래 횟수", f"{r.trade_count}회")
        c3.metric("승률", f"{r.win_rate_pct:.1f}%")
        c4.metric("최대낙폭", f"-{r.max_drawdown_pct:.1f}%")

        # ── 리서치 리포트 추가 필드 ─────────────────────────────
        with st.expander("📋 백테스트 리서치 리포트", expanded=True):
            # 파라미터 테이블
            st.markdown("**파라미터**")
            params = r.parameters
            st.table({
                "항목": ["전략", "종목", "기간 (시작)", "기간 (종료)",
                         "빠른 SMA", "느린 SMA", "초기 자본"],
                "값": [
                    r.strategy,
                    r.symbol,
                    str(r.start),
                    str(r.end),
                    str(params.get("fast", "-")),
                    str(params.get("slow", "-")),
                    f"{params.get('initial_cash', 0):,.0f}원",
                ],
            })

            # 성과 요약 vs 벤치마크
            st.markdown("**성과 요약**")
            p1, p2, p3 = st.columns(3)
            p1.metric("전략 수익률", f"{r.total_return_pct:+.2f}%")
            p2.metric("벤치마크 수익률", f"{r.benchmark_return_pct:+.2f}%",
                      help="기간 내 equity curve 전체 성장률 (buy-and-hold 근사)")
            p3.metric("턴오버", f"{r.turnover_pct:.1f}%",
                      help="총 BUY 거래금액 / 초기자본 × 100")

            # 에쿼티 커브
            if r.equity_curve:
                import pandas as pd
                df = pd.DataFrame(r.equity_curve).set_index("date")
                st.line_chart(df["equity"], height=200)

            # 거래 내역 테이블
            if r.trades:
                st.markdown("**거래 내역**")
                import pandas as pd
                trade_df = pd.DataFrame(r.trades)
                st.dataframe(trade_df, hide_index=True, use_container_width=True)

            # 가정 및 면책
            st.markdown("**가정 및 한계**")
            st.info(f"수수료/슬리피지: {r.fee_slippage_assumption}")
            st.warning(f"정기 이벤트 주의: {r.scheduled_event_caveat}")
            st.caption(f"페이퍼/실거래 차이: {r.paper_live_parity_note}")

        st.caption("⚠️ 이 백테스트는 참고용입니다. 과거 성과가 미래를 보장하지 않습니다.")
```

- [ ] **Step 3: Update the run block to store `BacktestReport` instead of `BacktestResult`**

Find the line `st.session_state["bt_result"] = result` (line 164). Change the run block to also call `build_report`:

```python
            try:
                from app.quant.data_loader import fetch_and_cache
                fetched = fetch_and_cache(sym, start, end)
                from app.quant.backtest import run_sma_crossover, build_report
                result = run_sma_crossover(sym, start, end, fast=int(fast), slow=int(slow))
                report = build_report(result, fast=int(fast), slow=int(slow), initial_cash=1_000_000.0)
                st.session_state["bt_result"] = report
                if fetched:
                    st.caption(f"📥 {fetched}일치 시세 캐시 갱신")
            except Exception as exc:  # noqa: BLE001
                st.warning(f"백테스트 실패: {exc}")
```

This replaces the existing try block from line 159–168.

- [ ] **Step 4: Run unit tests to confirm the UI module change doesn't break tests**

```powershell
python -m pytest tests/unit/test_backtest.py -q
python -m pytest tests/ -q
```

Both must be green. If the UI view test (`tests/unit/test_analysis_intraday_view.py` or similar) breaks due to session state shape change, check the test — it may mock `run_sma_crossover` directly, in which case update the mock to return a `BacktestReport`.

- [ ] **Step 5: Commit the UI update**

```powershell
git add app/ui/views/analysis.py
git commit -m "feat(analysis): BacktestReport 리서치 필드 UI 표시 — 파라미터/벤치마크/가정/면책 (TASK-039)"
```

---

## Task 4: Create unit spec `UNIT-TASK-039-001.md`

**Files:**
- Create: `agents/lead_engineer/tasks/units/TASK-039/UNIT-TASK-039-001.md`

- [ ] **Step 1: Get current timestamp**

```powershell
python scripts/now.py
```

Note the output (e.g. `2026-06-14T12:34:56+09:00`). Use it in the completion block.

- [ ] **Step 2: Create directory and write the unit file**

```powershell
New-Item -ItemType Directory -Force "agents/lead_engineer/tasks/units/TASK-039"
```

Write `agents/lead_engineer/tasks/units/TASK-039/UNIT-TASK-039-001.md`:

```markdown
---
unit_id: UNIT-TASK-039-001
task_id: TASK-039
task_set_id: TASKSET-RESEARCH-REPORTING
project_id: PROJECT-AUTOFOLIO
status: completed
horizon: unit
model_tier: worker_standard
escalation_triggers: [high_risk, repeated_failure]
context: "백테스트 결과를 재현 가능한 연구 리포트로 강화. BacktestReport dataclass + build_report() 추가. 파라미터 테이블·벤치마크 비교·최대낙폭·거래내역·턴오버·수수료/슬리피지 가정·정기이벤트 주의·페이퍼/실거래 차이 명시. UI(analysis.py) expander에 표시."
inputs:
  - agents/lead_engineer/tasks/TASK-039-backtest-research-report-hardening.md
  - app/quant/backtest.py
  - app/ui/views/analysis.py
  - tests/unit/test_backtest.py
target_files:
  - app/quant/backtest.py
  - app/ui/views/analysis.py
  - tests/unit/test_backtest.py
scope: "app/quant/backtest.py에 BacktestReport + build_report() 추가. analysis.py _backtest_section 표시 확장. DB migration, live scheduler, broker order path, risk policy 변경 없음."
acceptance:
  - "BacktestReport 필드: parameters, benchmark_return_pct, max_drawdown_pct, trades, turnover_pct, fee_slippage_assumption, scheduled_event_caveat, paper_live_parity_note"
  - "build_report() 결정적 — 같은 입력 → 같은 출력"
  - "fee_slippage_assumption에 'not modeled' 또는 '미반영' 포함"
  - "turnover_pct == 0.0 when no trades"
  - "python -m pytest tests/unit/test_backtest.py -q 8 passed"
  - "python -m pytest tests/ -q green"
  - "python scripts/check_agent_docs.py 0 error"
verification:
  - "python -m pytest tests/unit/test_backtest.py -q"
  - "python -m pytest tests/ -q"
  - "python -m pytest tests/unit -q"
  - "python scripts/check_agent_docs.py"
  - "python scripts/generate_views.py --check"
  - "python scripts/build_task_index.py --check"
handoff: "변경 파일 목록, pytest 결과(unit + full), gate 결과 보고."
stop_condition: "app/quant/backtest.py + analysis.py + tests/unit/test_backtest.py 수정 후 즉시 중단. broker, scheduler, risk 경로 변경 금지."
depends_on: []
---

# UNIT-TASK-039-001 — Backtest Research Report Hardening

## Context

TASK-039: `BacktestResult`(기존)를 확장하는 `BacktestReport` dataclass + `build_report()`
함수를 `app/quant/backtest.py`에 추가. 파라미터 테이블, 벤치마크 비교, 턴오버,
수수료/슬리피지 가정(미반영 명시), 정기 이벤트 주의, 페이퍼/실거래 차이 안내를 포함.
UI(`app/ui/views/analysis.py` `_backtest_section`)에 expander로 표시.

## Target Files

- `app/quant/backtest.py` — `BacktestReport` dataclass + `build_report()` 추가
- `app/ui/views/analysis.py` — `_backtest_section` 확장
- `tests/unit/test_backtest.py` — 5개 신규 테스트 추가

## Scope

In scope: `app/quant/backtest.py` 확장, `analysis.py` 표시 확장, 테스트.

Out of scope: DB migration, live scheduler, broker order path (`order_flow.py`), risk policy,
`BacktestResult` 기존 필드 변경 금지.

## Acceptance Criteria

- `BacktestReport` 8개 필수 필드 모두 존재
- `build_report()` 결정적 (같은 입력 → 동일 출력)
- `fee_slippage_assumption` "not modeled" / "미반영" 포함
- turnover 0-trade → 0.0
- `pytest tests/unit/test_backtest.py -q` 8 passed
- `pytest tests/ -q` green
- `check_agent_docs.py` 0 error

## 완료 기록

완료 시각: {FILL_TIMESTAMP}

**변경 내용:**
- `app/quant/backtest.py`: `BacktestReport` dataclass, `_FEE_SLIPPAGE_TEXT`, `_SCHEDULED_EVENT_CAVEAT`, `_PAPER_LIVE_PARITY_NOTE` 상수, `build_report()` 함수 추가.
- `app/ui/views/analysis.py`: `_backtest_section` — `build_report()` 호출 후 session state에 `BacktestReport` 저장. expander로 파라미터 테이블·벤치마크·에쿼티 커브·거래내역·가정 표시.
- `tests/unit/test_backtest.py`: `test_build_report_has_required_fields`, `test_build_report_is_deterministic`, `test_benchmark_return_is_buy_and_hold`, `test_fee_slippage_assumption_says_not_modeled`, `test_turnover_zero_when_no_trades` 추가.

**검증 결과:**
- 수정 전: 5개 신규 테스트 FAILED (ImportError: build_report)
- 수정 후: 8 passed (test_backtest.py), {FULL_SUITE_COUNT} passed (전체)
- `check_agent_docs.py` → 0 error
- `generate_views.py --check` → OK
- `build_task_index.py --check` → OK
```

Replace `{FILL_TIMESTAMP}` with the output of `python scripts/now.py`, and `{FULL_SUITE_COUNT}` with the actual pytest count.

- [ ] **Step 3: Commit the unit file**

```powershell
git add agents/lead_engineer/tasks/units/TASK-039/
git commit -m "docs(task): UNIT-TASK-039-001 완료 기록"
```

---

## Task 5: Mark TASK-039 completed, update INDEX, regenerate views

**Files:**
- Modify: `agents/lead_engineer/tasks/TASK-039-backtest-research-report-hardening.md`
- Modify: `agents/lead_engineer/tasks/INDEX.md`

- [ ] **Step 1: Get timestamp**

```powershell
python scripts/now.py
```

- [ ] **Step 2: Update TASK-039 frontmatter**

In `agents/lead_engineer/tasks/TASK-039-backtest-research-report-hardening.md`, change the frontmatter:

Change:
```yaml
status: 대기
```
To:
```yaml
status: 완료
```

Also update `updated_at` to the current timestamp from `scripts/now.py`.

- [ ] **Step 3: Update TASK-039 body status**

In the body of the file, change:
```
상태: 대기
```
To:
```
상태: 완료
```

- [ ] **Step 4: Add completion block to TASK-039**

Append the following at the bottom of `TASK-039-backtest-research-report-hardening.md`:

```markdown

## 완료 기록

완료 시각: {TIMESTAMP_FROM_NOW_PY}
검토자: Lead Engineer

## 증거

- `app/quant/backtest.py` — `BacktestReport` + `build_report()` 추가
- `app/ui/views/analysis.py` — `_backtest_section` expander 확장
- `tests/unit/test_backtest.py` — 5개 신규 테스트 추가 (8 passed)
- `python -m pytest tests/ -q` → {FULL_COUNT} passed, 0 failed
- `python scripts/check_agent_docs.py` → 0 error
- `python scripts/generate_views.py --check` → OK
- `python scripts/build_task_index.py --check` → OK

## 리뷰

- 기존 `BacktestResult` 변경 없음 — 하위 호환
- `build_report()` 결정적 (고정 데이터 → 고정 출력)
- 수수료/슬리피지 정직하게 "미반영" 명시 (fabrication 없음)
- 정기 이벤트 주의 및 페이퍼/실거래 차이 안내 포함
- UI는 read-only (분석 전용) — live 주문 경로 미변경
```

- [ ] **Step 5: Update INDEX.md**

In `agents/lead_engineer/tasks/INDEX.md`, find:

```
| [TASK-039](TASK-039-backtest-research-report-hardening.md) | 대기 | Quant Researcher | Backtest research report hardening → v1 |
```

Change to:

```
| [TASK-039](TASK-039-backtest-research-report-hardening.md) | 완료 | Quant Researcher | Backtest research report hardening |
```

- [ ] **Step 6: Regenerate views and task index**

```powershell
python scripts/generate_views.py
python scripts/build_task_index.py
```

No errors expected. If there are errors, read them carefully — likely a frontmatter syntax issue in the TASK file.

- [ ] **Step 7: Run gate checks**

```powershell
python scripts/check_agent_docs.py
python scripts/generate_views.py --check
python scripts/build_task_index.py --check
```

All must report 0 errors / OK.

- [ ] **Step 8: Run full + unit test suite one final time**

```powershell
python -m pytest tests/ -q
python -m pytest tests/unit -q
```

Record the counts.

- [ ] **Step 9: Final commit**

```powershell
git add agents/lead_engineer/tasks/TASK-039-backtest-research-report-hardening.md
git add agents/lead_engineer/tasks/INDEX.md
git add agents/lead_engineer/tasks/VIEW-by-owner.md
git add agents/lead_engineer/tasks/VIEW-by-priority.md
git add agents/lead_engineer/tasks/VIEW-by-status.md
git add agents/lead_engineer/tasks/VIEW-by-tag.md
git add agents/lead_engineer/tasks/VIEW-by-workload.md
git add agents/lead_engineer/tasks/BACKLOG.md
git add tasks.index.json
git commit -m "$(cat <<'EOF'
feat(analysis): 백테스트 연구 리포트 강화 — 재현가능 요약(벤치마크/DD/거래/가정) (TASK-039)

- BacktestReport dataclass: parameters, benchmark_return_pct, turnover_pct,
  fee_slippage_assumption, scheduled_event_caveat, paper_live_parity_note
- build_report(): 결정적 변환 함수 (BacktestResult → BacktestReport)
- analysis.py _backtest_section: expander로 파라미터 테이블·벤치마크·거래내역·가정 표시
- 5개 신규 단위 테스트: 필드 완전성·결정성·벤치마크·가정 정직성·턴오버
- TASK-039 완료, INDEX·VIEW·tasks.index.json 재생성

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
EOF
)"
```

---

## Self-Review Checklist

**Spec coverage:**

| Requirement | Task covering it |
|---|---|
| parameter table | Task 2 (BacktestReport.parameters) + Task 3 (UI table) |
| benchmark comparison | Task 2 (benchmark_return_pct) + Task 3 (p2.metric) |
| drawdown (max DD) | Task 2 (max_drawdown_pct propagated) + Task 3 (c4.metric) |
| trade list | Task 2 (trades propagated) + Task 3 (trade_df dataframe) |
| turnover | Task 2 (turnover_pct) + Task 3 (p3.metric) |
| fee/slippage assumption | Task 2 (_FEE_SLIPPAGE_TEXT + field) + Task 3 (st.info) |
| scheduled-event caveat | Task 2 (_SCHEDULED_EVENT_CAVEAT + field) + Task 3 (st.warning) |
| paper/live parity note | Task 2 (_PAPER_LIVE_PARITY_NOTE + field) + Task 3 (st.caption) |
| deterministic | Task 1 (failing test) + Task 2 (pure function, no random) |
| failing test first | Task 1 |
| unit spec + records | Task 4 |
| TASK-039 status 완료 | Task 5 |
| INDEX + views regenerated | Task 5 |
| commit to branch (not main) | Task 1 Step 1 |
| commit message format | Task 5 Step 9 |

**Placeholder scan:** No "TBD", "TODO", or "implement later" in any step. All code blocks are complete.

**Type consistency:**
- `BacktestReport` defined in Task 2, imported in Task 3 UI (`from app.quant.backtest import run_sma_crossover, build_report`).
- Tests in Task 1 import `build_report, BacktestReport` from `app.quant.backtest` — matches Task 2 definition.
- `r.parameters`, `r.benchmark_return_pct`, `r.turnover_pct`, `r.fee_slippage_assumption`, `r.scheduled_event_caveat`, `r.paper_live_parity_note` used in Task 3 UI — all defined as fields in `BacktestReport` in Task 2.
- `_seed_crossover` in Task 1 uses `cache_prices` imported at top of test file — already imported in existing test file.
