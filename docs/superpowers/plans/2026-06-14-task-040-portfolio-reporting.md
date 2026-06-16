# TASK-040 Portfolio Performance & Tax-Lot Style Reporting — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a read-only performance/attribution report to the Autofolio portfolio view — realized/unrealized P&L summary, cashflow/fees placeholder, turnover, attribution by sector, and a tax-lot style placeholder table with a clear disclaimer — all surfaced in the existing `app/ui/views/portfolio.py` and backed by a pure service module.

**Architecture:** Create `app/services/perf_report.py` as the pure-function reporting core (no DB, no broker calls — accepts DataFrames and dicts so it's fully testable). Wire it into the portfolio UI view with a new "성과 리포트" expander section (read-only, no trade buttons). Expose `PortfolioReport` dataclass and `build_portfolio_report()` function, paralleling how `BacktestReport` / `build_report()` was done for TASK-039. Honest "데이터 없음" / "not modeled" labels wherever real data is unavailable.

**Tech Stack:** Python 3.11, pandas, Streamlit, SQLite (via existing `Repository`), pytest, existing `_build_holdings_df`, `attribution_df`, `daily_pnl_series`, `kpis` from `app/ui/backend.py`.

---

## File Map

| File | Action | Purpose |
|------|--------|---------|
| `app/services/perf_report.py` | **Create** | `PortfolioReport` dataclass + `build_portfolio_report()` pure function |
| `app/ui/views/portfolio.py` | **Modify** | Add "성과 리포트" expander section (read-only) |
| `tests/unit/test_perf_report.py` | **Create** | Failing tests → green: required sections, disclaimer text, attribution grouping, tax-lot placeholder |
| `agents/lead_engineer/tasks/units/TASK-040/UNIT-TASK-040-001.md` | **Create** | Unit spec (worker_ready → completed) |
| `agents/lead_engineer/tasks/TASK-040-portfolio-performance-tax-lot-reporting.md` | **Modify** | 대기 → 완료 (frontmatter + body + 완료 기록) |
| `agents/lead_engineer/tasks/INDEX.md` | **Modify** | TASK-040 상태 대기 → 완료 |

Scripts to run (do NOT modify): `generate_views.py`, `build_task_index.py`, `check_agent_docs.py`, `work_schema_gate.py`.

---

## Task 1: Write Failing Tests First (TDD Gate)

**Files:**
- Create: `tests/unit/test_perf_report.py`

- [ ] **Step 1.1: Write the failing tests**

Create `C:\Users\ycpig\autofolio\tests\unit\test_perf_report.py` with the following content:

```python
"""Unit tests for app/services/perf_report — TASK-040.

All tests use deterministic fixtures (no datetime.now(), no localtime).
Failing on import before implementation.
"""
from __future__ import annotations

import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_holdings() -> pd.DataFrame:
    """Minimal holdings_df-compatible fixture (mirrors HOLDINGS_COLUMNS schema)."""
    return pd.DataFrame([
        {"종목": "삼성전자", "티커": "005930", "자산군": "주식", "지역": "KR",
         "수량": 10, "평단": 70_000, "현재가": 77_000,
         "평가금액": 770_000, "평가손익": 70_000, "손익률": 10.0,
         "예상연배당": 14_440, "배당수익률": 1.87, "비중": 60.0},
        {"종목": "KODEX 200", "티커": "069500", "자산군": "ETF", "지역": "KR",
         "수량": 40, "평단": 36_500, "현재가": 37_800,
         "평가금액": 1_512_000, "평가손익": 52_000, "손익률": 3.56,
         "예상연배당": 31_200, "배당수익률": 2.06, "비중": 40.0},
    ])


def _make_pnl_series() -> pd.DataFrame:
    """Deterministic daily PnL series (no datetime.now())."""
    return pd.DataFrame([
        {"date": "2026-06-01", "pnl": 50_000},
        {"date": "2026-06-02", "pnl": -20_000},
        {"date": "2026-06-03", "pnl": 80_000},
    ])


def _make_kpis() -> dict:
    return {
        "총자산": 2_500_000,
        "일손익률": 1.2,
        "누적손익률": 8.5,
        "현금비중": 10.0,
        "평가손익": 122_000,
    }


# ---------------------------------------------------------------------------
# Import guard — will FAIL before implementation
# ---------------------------------------------------------------------------

def test_import_perf_report_module():
    """Module must exist and export PortfolioReport + build_portfolio_report."""
    from app.services.perf_report import PortfolioReport, build_portfolio_report  # noqa: F401
    assert True


# ---------------------------------------------------------------------------
# Section 1: PortfolioReport has required fields
# ---------------------------------------------------------------------------

class TestPortfolioReportFields:
    def _build(self):
        from app.services.perf_report import build_portfolio_report
        return build_portfolio_report(
            holdings=_make_holdings(),
            pnl_series=_make_pnl_series(),
            kpis=_make_kpis(),
            realized_pnl=5_000.0,
        )

    def test_has_realized_pnl_field(self):
        r = self._build()
        assert hasattr(r, "realized_pnl")

    def test_has_unrealized_pnl_field(self):
        r = self._build()
        assert hasattr(r, "unrealized_pnl")

    def test_has_cashflow_note_field(self):
        """cashflow_note must be a non-empty string explaining the data limitation."""
        r = self._build()
        assert hasattr(r, "cashflow_note")
        assert isinstance(r.cashflow_note, str) and len(r.cashflow_note) > 0

    def test_has_fee_slippage_note_field(self):
        """fee_slippage_note must mention 'not modeled' or '미반영'."""
        r = self._build()
        assert hasattr(r, "fee_slippage_note")
        note = r.fee_slippage_note.lower()
        assert "not modeled" in note or "미반영" in note

    def test_has_turnover_note_field(self):
        r = self._build()
        assert hasattr(r, "turnover_note")
        assert isinstance(r.turnover_note, str)

    def test_has_attribution_df_field(self):
        """attribution_df must be a DataFrame with '구분' and '기여(만원)' columns."""
        r = self._build()
        assert hasattr(r, "attribution_df")
        assert isinstance(r.attribution_df, pd.DataFrame)
        assert "구분" in r.attribution_df.columns
        assert "기여(만원)" in r.attribution_df.columns

    def test_has_attribution_note_field(self):
        """attribution_note explains data availability honestly."""
        r = self._build()
        assert hasattr(r, "attribution_note")
        assert isinstance(r.attribution_note, str) and len(r.attribution_note) > 0

    def test_has_tax_lot_df_field(self):
        """tax_lot_df must be a DataFrame with expected columns."""
        r = self._build()
        assert hasattr(r, "tax_lot_df")
        assert isinstance(r.tax_lot_df, pd.DataFrame)
        assert "티커" in r.tax_lot_df.columns
        assert "평단" in r.tax_lot_df.columns
        assert "수량" in r.tax_lot_df.columns

    def test_has_tax_lot_disclaimer_field(self):
        """tax_lot_disclaimer must warn the user this is illustrative only."""
        r = self._build()
        assert hasattr(r, "tax_lot_disclaimer")
        disclaimer = r.tax_lot_disclaimer.lower()
        # must include a disclaimer keyword (illustrative / placeholder / 참고용 / 면책)
        keywords = ["illustrative", "placeholder", "참고용", "면책", "세무 조언", "tax advice"]
        assert any(k in disclaimer for k in keywords), (
            f"tax_lot_disclaimer missing disclaimer keyword. Got: {r.tax_lot_disclaimer!r}"
        )

    def test_has_report_date_field(self):
        """report_date must be a non-empty string (ISO date)."""
        r = self._build()
        assert hasattr(r, "report_date")
        assert isinstance(r.report_date, str) and len(r.report_date) == 10  # YYYY-MM-DD


# ---------------------------------------------------------------------------
# Section 2: Numeric correctness
# ---------------------------------------------------------------------------

class TestPortfolioReportNumerics:
    def test_unrealized_pnl_matches_holdings_sum(self):
        from app.services.perf_report import build_portfolio_report
        holdings = _make_holdings()
        r = build_portfolio_report(
            holdings=holdings,
            pnl_series=_make_pnl_series(),
            kpis=_make_kpis(),
            realized_pnl=5_000.0,
        )
        expected_unrealized = int(holdings["평가손익"].sum())  # 70_000 + 52_000 = 122_000
        assert r.unrealized_pnl == expected_unrealized

    def test_realized_pnl_passes_through(self):
        from app.services.perf_report import build_portfolio_report
        r = build_portfolio_report(
            holdings=_make_holdings(),
            pnl_series=_make_pnl_series(),
            kpis=_make_kpis(),
            realized_pnl=9_999.0,
        )
        assert r.realized_pnl == 9_999.0

    def test_attribution_groups_by_asset_class(self):
        """attribution_df must have one row per 자산군 present in holdings."""
        from app.services.perf_report import build_portfolio_report
        r = build_portfolio_report(
            holdings=_make_holdings(),
            pnl_series=_make_pnl_series(),
            kpis=_make_kpis(),
            realized_pnl=0.0,
        )
        groups = set(r.attribution_df["구분"].tolist())
        assert "주식" in groups
        assert "ETF" in groups

    def test_tax_lot_rows_match_holdings(self):
        """tax_lot_df has one row per holding."""
        from app.services.perf_report import build_portfolio_report
        holdings = _make_holdings()
        r = build_portfolio_report(
            holdings=holdings,
            pnl_series=_make_pnl_series(),
            kpis=_make_kpis(),
            realized_pnl=0.0,
        )
        assert len(r.tax_lot_df) == len(holdings)

    def test_empty_holdings_returns_empty_df_fields(self):
        """build_portfolio_report handles empty holdings without crash."""
        from app.services.perf_report import build_portfolio_report
        from app.ui.backend import HOLDINGS_COLUMNS
        empty = pd.DataFrame(columns=HOLDINGS_COLUMNS)
        r = build_portfolio_report(
            holdings=empty,
            pnl_series=pd.DataFrame(columns=["date", "pnl"]),
            kpis={"총자산": 0, "일손익률": 0, "누적손익률": 0, "현금비중": 0, "평가손익": 0},
            realized_pnl=0.0,
        )
        assert r.unrealized_pnl == 0
        assert r.realized_pnl == 0.0
        assert r.tax_lot_df.empty

    def test_build_is_deterministic(self):
        """Same inputs → same output (no datetime.now() or random)."""
        from app.services.perf_report import build_portfolio_report
        r1 = build_portfolio_report(
            holdings=_make_holdings(),
            pnl_series=_make_pnl_series(),
            kpis=_make_kpis(),
            realized_pnl=5_000.0,
        )
        r2 = build_portfolio_report(
            holdings=_make_holdings(),
            pnl_series=_make_pnl_series(),
            kpis=_make_kpis(),
            realized_pnl=5_000.0,
        )
        assert r1.realized_pnl == r2.realized_pnl
        assert r1.unrealized_pnl == r2.unrealized_pnl
        assert r1.report_date == r2.report_date
        assert r1.fee_slippage_note == r2.fee_slippage_note
        assert r1.tax_lot_disclaimer == r2.tax_lot_disclaimer
```

- [ ] **Step 1.2: Run tests to confirm they all FAIL (import error)**

```
cd C:\Users\ycpig\autofolio
python -m pytest tests/unit/test_perf_report.py -v 2>&1 | head -40
```

Expected output: `ModuleNotFoundError` or `ImportError` — every test FAILS because `app/services/perf_report.py` does not exist yet.

- [ ] **Step 1.3: Commit the failing tests**

```powershell
git add tests/unit/test_perf_report.py
git commit -m "test(perf_report): failing TDD tests for TASK-040 portfolio reporting"
```

---

## Task 2: Implement `app/services/perf_report.py`

**Files:**
- Create: `app/services/perf_report.py`

- [ ] **Step 2.1: Write the minimal implementation**

Create `C:\Users\ycpig\autofolio\app\services\perf_report.py`:

```python
"""app/services/perf_report — 포트폴리오 성과·귀속·tax-lot 읽기전용 리포트.

TASK-040: read-only reporting only.
- 주문/리밸런싱 실행 없음.
- 세무 조언 없음 — tax-lot 섹션은 참고용 placeholder 면책 포함.
- 데이터 없는 섹션은 '데이터 없음' / 'not modeled' 명시.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd

# ---------------------------------------------------------------------------
# Disclaimer / note constants (deterministic strings)
# ---------------------------------------------------------------------------

_CASHFLOW_NOTE = (
    "현금흐름 데이터 없음 (not modeled). "
    "현재 execution_logs는 체결가·수량만 기록하며 입출금 현금흐름 테이블이 없습니다. "
    "실제 입금·출금·배당 수령을 포함한 현금흐름 분석은 추후 지원 예정입니다."
)

_FEE_SLIPPAGE_NOTE = (
    "수수료·슬리피지 미반영 (not modeled). "
    "현재 체결 내역에 수수료/슬리피지가 별도 기록되지 않아 성과에 미포함됩니다. "
    "실거래 환경에서는 매수·매도 각 약 0.015~0.3% 거래비용이 발생할 수 있습니다."
)

_TURNOVER_NOTE = (
    "턴오버 데이터 없음 (not modeled). "
    "일별 포트폴리오 스냅샷 테이블이 없어 정확한 회전율 계산이 불가합니다. "
    "향후 포트폴리오 스냅샷 기록 기능 추가 시 지원 예정입니다."
)

_ATTRIBUTION_NOTE = (
    "귀속 분석: 현재 보유 종목 미실현 평가손익의 자산군별 집계입니다. "
    "시간·전략 축 귀속은 일별 포트폴리오 스냅샷 없이 계산 불가 (데이터 없음). "
    "섹터 귀속은 화이트리스트 role 매핑 기준이며 실제 GICS 분류와 다를 수 있습니다."
)

_TAX_LOT_DISCLAIMER = (
    "⚠ 면책 / Disclaimer: 이 tax-lot 표는 참고용 placeholder입니다. "
    "illustrative only — 실제 세금 계산이 아니며 세무 조언(tax advice)이 아닙니다. "
    "양도소득세·금융투자소득세 등 실제 세금은 세무사 또는 과세기관 자료를 참고하세요. "
    "매수 lot 수량·평단은 execution_logs BUY 기록 기반이며 분할 lot 추적은 미지원입니다."
)


# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------

@dataclass
class PortfolioReport:
    """읽기전용 포트폴리오 성과 리포트.

    build_portfolio_report()로 생성. 같은 입력 → 동일 출력 (결정적).
    주문·리밸런싱 실행 기능 없음.
    """

    # --- P&L ---
    realized_pnl: float              # 실현 손익 (원)
    unrealized_pnl: int              # 미실현 평가손익 합계 (원)

    # --- Cashflow / Fees (data unavailable) ---
    cashflow_note: str               # "데이터 없음" + 설명
    fee_slippage_note: str           # "not modeled" + 설명
    turnover_note: str               # "데이터 없음" + 설명

    # --- Attribution ---
    attribution_df: "pd.DataFrame"   # 자산군별 미실현 평가손익 기여
    attribution_note: str            # 데이터 제한 설명

    # --- Tax-lot placeholder ---
    tax_lot_df: "pd.DataFrame"       # 보유 lot 단위 표 (illustrative)
    tax_lot_disclaimer: str          # 면책 문구

    # --- Metadata ---
    report_date: str                 # YYYY-MM-DD (입력 기준, 결정적)
    kpis: dict = field(default_factory=dict)  # 총자산·손익률 등


# ---------------------------------------------------------------------------
# Builder (pure function)
# ---------------------------------------------------------------------------

def build_portfolio_report(
    *,
    holdings: "pd.DataFrame",
    pnl_series: "pd.DataFrame",
    kpis: dict,
    realized_pnl: float,
    report_date: str | None = None,
) -> PortfolioReport:
    """포트폴리오 성과 리포트를 빌드한다 (순수 함수, 결정적).

    Args:
        holdings: HOLDINGS_COLUMNS 스키마 DataFrame (app/ui/backend._build_holdings_df 반환값).
        pnl_series: date/pnl 컬럼 DataFrame (backend.daily_pnl_series() 반환값).
        kpis: backend.kpis() 반환값 dict.
        realized_pnl: 실현 손익 합계 (원) — repository.total_realized_pnl() 권장.
        report_date: YYYY-MM-DD 문자열. None이면 pnl_series 마지막 날짜 또는 '0000-00-00' 사용.

    Returns:
        PortfolioReport — read-only, no side effects.

    Note:
        현금흐름·수수료·턴오버는 현재 데이터 없음 → 면책 문구로 대체.
        tax-lot은 참고용 placeholder (세무 조언 아님).
    """
    import pandas as pd

    # --- report_date: deterministic (no datetime.now()) ---
    if report_date is not None:
        _report_date = str(report_date)
    elif not pnl_series.empty and "date" in pnl_series.columns:
        _report_date = str(pnl_series["date"].iloc[-1])
    else:
        _report_date = "0000-00-00"

    # --- unrealized P&L ---
    if not holdings.empty and "평가손익" in holdings.columns:
        unrealized_pnl = int(holdings["평가손익"].sum())
    else:
        unrealized_pnl = 0

    # --- Attribution: group unrealized P&L by 자산군 ---
    if not holdings.empty and "자산군" in holdings.columns and "평가손익" in holdings.columns:
        grouped = holdings.groupby("자산군")["평가손익"].sum().reset_index()
        grouped.columns = ["구분", "기여(만원)"]
        grouped["기여(만원)"] = (grouped["기여(만원)"] / 10_000).round(1)
        attribution_df = grouped.sort_values("기여(만원)", ascending=False).reset_index(drop=True)
    else:
        attribution_df = pd.DataFrame(columns=["구분", "기여(만원)"])

    # --- Tax-lot placeholder: one row per holding lot ---
    if not holdings.empty:
        tax_cols = ["티커", "종목", "자산군", "수량", "평단", "현재가", "평가손익", "손익률"]
        available = [c for c in tax_cols if c in holdings.columns]
        tax_lot_df = holdings[available].copy().reset_index(drop=True)
    else:
        tax_lot_df = pd.DataFrame(columns=["티커", "종목", "자산군", "수량", "평단", "현재가", "평가손익", "손익률"])

    return PortfolioReport(
        realized_pnl=float(realized_pnl),
        unrealized_pnl=unrealized_pnl,
        cashflow_note=_CASHFLOW_NOTE,
        fee_slippage_note=_FEE_SLIPPAGE_NOTE,
        turnover_note=_TURNOVER_NOTE,
        attribution_df=attribution_df,
        attribution_note=_ATTRIBUTION_NOTE,
        tax_lot_df=tax_lot_df,
        tax_lot_disclaimer=_TAX_LOT_DISCLAIMER,
        report_date=_report_date,
        kpis=kpis,
    )
```

- [ ] **Step 2.2: Run the unit tests and confirm ALL GREEN**

```
cd C:\Users\ycpig\autofolio
python -m pytest tests/unit/test_perf_report.py -v
```

Expected: All 14+ tests PASS.

- [ ] **Step 2.3: Run the full test suite to confirm no regressions**

```
cd C:\Users\ycpig\autofolio
python -m pytest tests/ -q
```

Expected: All existing tests still pass, plus the new tests.

- [ ] **Step 2.4: Commit the service module**

```powershell
git add app/services/perf_report.py
git commit -m "feat(perf_report): PortfolioReport dataclass + build_portfolio_report() (TASK-040)"
```

---

## Task 3: Wire Reporting into `app/ui/views/portfolio.py`

**Files:**
- Modify: `app/ui/views/portfolio.py`

The existing portfolio view ends after the dividend metrics and the allocation/gap columns. We will add a new `## 성과 리포트` expander section at the bottom of the `render()` function.

- [ ] **Step 3.1: Read the current portfolio.py to find the exact insertion point**

Read `C:\Users\ycpig\autofolio\app\ui\views\portfolio.py` — the file ends at line 96 with the allocation_gap display. We'll add our section after line 96.

- [ ] **Step 3.2: Add the performance report section**

Edit `C:\Users\ycpig\autofolio\app\ui\views\portfolio.py` — after the existing `left`/`right` column block, add:

```python
    # ── 성과 리포트 (읽기전용 / TASK-040) ─────────────────────────
    with st.expander("📊 성과 리포트 (읽기전용)", expanded=False):
        _render_perf_report(df)


def _render_perf_report(holdings_df: "pd.DataFrame") -> None:
    """포트폴리오 성과/귀속/tax-lot 읽기전용 리포트 섹션.

    순수 UI 렌더러 — 주문/리밸런싱 실행 없음.
    데이터 없는 섹션은 솔직하게 '데이터 없음' 표시.
    """
    import streamlit as st
    from app.services.perf_report import build_portfolio_report

    # --- 데이터 수집 (backend 또는 mock) ---
    if st.session_state.get("data_source") == "backend":
        try:
            from app.ui import backend
            pnl_series = backend.daily_pnl_series()
            kpis_data = backend.kpis()
            repo, *_ = backend._ctx()
            realized_pnl = repo.total_realized_pnl()
        except Exception as exc:  # noqa: BLE001
            st.warning(f"성과 데이터 라이브 조회 실패 — 데모 데이터로 대체합니다: {exc}")
            from app.ui.mock import data as mock_data
            pnl_series = mock_data.pnl_daily().rename(columns={"날짜": "date", "손익": "pnl"})
            kpis_data = mock_data.kpis()
            realized_pnl = 0.0
    else:
        from app.ui.mock import data as mock_data
        pnl_series = mock_data.pnl_daily().rename(columns={"날짜": "date", "손익": "pnl"})
        kpis_data = mock_data.kpis()
        realized_pnl = 0.0

    report = build_portfolio_report(
        holdings=holdings_df,
        pnl_series=pnl_series,
        kpis=kpis_data,
        realized_pnl=realized_pnl,
    )

    # ── 1. 실현/미실현 P&L 요약 ───────────────────────────────────
    st.subheader("실현/미실현 손익")
    c1, c2, c3 = st.columns(3)
    c1.metric("실현 손익", f"₩{report.realized_pnl:,.0f}")
    c2.metric("미실현 평가손익", f"₩{report.unrealized_pnl:,.0f}")
    c3.metric("합계", f"₩{report.realized_pnl + report.unrealized_pnl:,.0f}")

    # ── 2. 현금흐름·수수료·턴오버 (데이터 없음 명시) ──────────────
    st.subheader("현금흐름 / 수수료 / 턴오버")
    st.info(report.cashflow_note)
    st.info(report.fee_slippage_note)
    st.info(report.turnover_note)

    # ── 3. Attribution (자산군별 기여) ────────────────────────────
    st.subheader("귀속 분석 (Attribution)")
    st.caption(report.attribution_note)
    if not report.attribution_df.empty:
        st.dataframe(report.attribution_df, hide_index=True, width="stretch")
        st.bar_chart(report.attribution_df.set_index("구분")["기여(만원)"], height=200)
    else:
        st.write("데이터 없음 — 보유 종목이 없습니다.")

    # ── 4. Tax-lot placeholder ────────────────────────────────────
    st.subheader("Tax-Lot 보기 (참고용 Placeholder)")
    st.warning(report.tax_lot_disclaimer)
    if not report.tax_lot_df.empty:
        st.dataframe(
            report.tax_lot_df,
            hide_index=True,
            width="stretch",
            column_config={
                "수량": st.column_config.NumberColumn(format="%d"),
                "평단": st.column_config.NumberColumn(format="%.0f"),
                "현재가": st.column_config.NumberColumn(format="%.0f"),
                "평가손익": st.column_config.NumberColumn(format="₩%d"),
                "손익률": st.column_config.NumberColumn(format="%.1f%%"),
            },
        )
    else:
        st.write("보유 종목 없음.")
```

The full modified `render()` function in `portfolio.py` adds one expander call at the bottom, and `_render_perf_report` is a new helper function at module level. Keep all existing imports. Add `from __future__ import annotations` if not already present (it is).

- [ ] **Step 3.3: Run unit tests again to verify no regression**

```
cd C:\Users\ycpig\autofolio
python -m pytest tests/unit -q
python -m pytest tests/ -q
```

Expected: all pass.

- [ ] **Step 3.4: Commit the UI change**

```powershell
git add app/ui/views/portfolio.py
git commit -m "feat(portfolio): 성과 리포트 expander — realized/unrealized/attribution/tax-lot (TASK-040)"
```

---

## Task 4: Create UNIT spec and update task records

**Files:**
- Create: `agents/lead_engineer/tasks/units/TASK-040/UNIT-TASK-040-001.md`
- Modify: `agents/lead_engineer/tasks/TASK-040-portfolio-performance-tax-lot-reporting.md`
- Modify: `agents/lead_engineer/tasks/INDEX.md`

- [ ] **Step 4.1: Create the UNIT spec**

Create `C:\Users\ycpig\autofolio\agents\lead_engineer\tasks\units\TASK-040\UNIT-TASK-040-001.md`:

```markdown
---
unit_id: UNIT-TASK-040-001
task_id: TASK-040
task_set_id: TASKSET-RESEARCH-REPORTING
project_id: PROJECT-AUTOFOLIO
status: completed
horizon: unit
model_tier: worker_standard
escalation_triggers: [high_risk, repeated_failure]
context: "포트폴리오 성과/귀속/tax-lot 읽기전용 리포트. PortfolioReport dataclass + build_portfolio_report() pure function 추가 (app/services/perf_report.py). portfolio.py UI expander 연동. TDD: 실패 테스트 선행. 데이터 없는 항목은 '데이터 없음'/'not modeled' 명시. tax-lot은 참고용 placeholder + 면책 문구."
inputs:
  - agents/lead_engineer/tasks/TASK-040-portfolio-performance-tax-lot-reporting.md
  - app/ui/backend.py
  - app/ui/views/portfolio.py
  - app/ui/mock/data.py
  - tests/unit/test_backend_holdings.py
target_files:
  - app/services/perf_report.py
  - app/ui/views/portfolio.py
  - tests/unit/test_perf_report.py
scope: "app/services/perf_report.py 신규 생성 + app/ui/views/portfolio.py expander 추가 + tests/unit/test_perf_report.py. DB migration, broker order path (order_flow.py), app/risk/**, OrderFlow, KIS 주문 API 변경 없음. Read-only reporting only."
acceptance:
  - "PortfolioReport 필드: realized_pnl, unrealized_pnl, cashflow_note, fee_slippage_note, turnover_note, attribution_df, attribution_note, tax_lot_df, tax_lot_disclaimer, report_date"
  - "build_portfolio_report() 결정적 — 같은 입력 → 같은 출력"
  - "fee_slippage_note에 'not modeled' 또는 '미반영' 포함"
  - "tax_lot_disclaimer에 'illustrative' 또는 '참고용' 또는 '면책' 포함"
  - "attribution_df — '구분'/'기여(만원)' 컬럼, 자산군별 집계"
  - "tax_lot_df — 빈 holdings → empty DataFrame"
  - "python -m pytest tests/unit/test_perf_report.py -q: 14+ passed"
  - "python -m pytest tests/ -q green"
  - "python scripts/check_agent_docs.py 0 error"
verification:
  - "python -m pytest tests/unit/test_perf_report.py -v"
  - "python -m pytest tests/unit -q"
  - "python -m pytest tests/ -q"
  - "python scripts/check_agent_docs.py"
  - "python scripts/generate_views.py --check"
  - "python scripts/build_task_index.py --check"
  - "python scripts/work_schema_gate.py --items --check"
handoff: "변경 파일 목록, pytest 결과(unit + full), gate 결과 보고. test_perf_report.py 실패→통과 증거 포함."
stop_condition: "app/services/perf_report.py + portfolio.py + test_perf_report.py 완료 후 중단. 주문 경로, risk policy, schema migration, KIS API endpoint 변경 금지."
depends_on: []
---

# UNIT-TASK-040-001 — 포트폴리오 성과·귀속·tax-lot 읽기전용 리포트

## Context

TASK-040: 읽기전용 성과 리포트 구현.
`app/services/perf_report.py`에 `PortfolioReport` dataclass + `build_portfolio_report()` 추가.
`app/ui/views/portfolio.py` "성과 리포트" expander 섹션 추가.
데이터 없는 항목(현금흐름·수수료·턴오버)은 '데이터 없음'/'not modeled' 명시.
tax-lot은 참고용 placeholder + 면책 문구 (세무 조언 아님).

## Target Files

- `app/services/perf_report.py` — 신규 (PortfolioReport + build_portfolio_report)
- `app/ui/views/portfolio.py` — expander 추가
- `tests/unit/test_perf_report.py` — 신규 (14+ 테스트)

## Scope

In scope: 위 3개 파일. 읽기전용.

Out of scope: DB migration, `app/engine/order_flow.py`, `app/risk/**`, KIS order API, `OrderFlow`,
실제 세금 계산, 주문·리밸런싱 실행.

## Steps

1. `tests/unit/test_perf_report.py` 작성 (14개 테스트, 모두 FAIL 확인).
2. `app/services/perf_report.py` 구현 → 테스트 GREEN.
3. `app/ui/views/portfolio.py` expander 추가.
4. 전체 pytest green + gate scripts OK.

## Acceptance Criteria

- `PortfolioReport` 10개 필드 존재
- `build_portfolio_report()` 결정적
- `fee_slippage_note` → 'not modeled'/'미반영' 포함
- `tax_lot_disclaimer` → 'illustrative'/'참고용'/'면책' 포함
- `attribution_df` → '구분'/'기여(만원)' 컬럼
- `pytest tests/unit/test_perf_report.py -q` 14+ passed
- `pytest tests/ -q` green
- `check_agent_docs.py` 0 error

## Verification

```
python -m pytest tests/unit/test_perf_report.py -v
python -m pytest tests/unit -q
python -m pytest tests/ -q
python scripts/check_agent_docs.py
python scripts/generate_views.py --check
python scripts/build_task_index.py --check
python scripts/work_schema_gate.py --items --check
```

## Handoff

변경 파일 목록, pytest 결과(unit + full), gate 결과 보고.

## Stop Boundary

3개 파일 완료 후 즉시 중단. 주문 경로, risk policy, schema migration 변경 금지.

## 완료 기록

완료 시각: {FILL_AT_COMPLETION}
검토자: Performance Analyst / QA

**변경 내용:**
- `app/services/perf_report.py`: `PortfolioReport` dataclass, 면책 상수 4개, `build_portfolio_report()` 순수 함수.
- `app/ui/views/portfolio.py`: `_render_perf_report()` 헬퍼 + render() 하단 expander 추가.
- `tests/unit/test_perf_report.py`: 14개 테스트.

**검증 결과:**
- 수정 전: 14개 FAILED (ImportError)
- 수정 후: {N} passed (test_perf_report.py), {FULL} passed (전체)
- `check_agent_docs.py` → 0 error
- `generate_views.py --check` → OK
- `build_task_index.py --check` → OK
```

- [ ] **Step 4.2: Update TASK-040 stub to 완료**

In `C:\Users\ycpig\autofolio\agents\lead_engineer\tasks\TASK-040-portfolio-performance-tax-lot-reporting.md`:

Change frontmatter line 5: `status: 대기` → `status: 완료`
Change frontmatter line 15: `updated_at: 2026-06-13T00:53:23+09:00` → `updated_at: {NOW}` (run `python scripts/now.py` first)
Change body line: `상태: 대기` → `상태: 완료`

Then append to the file:

```markdown
## 완료 기록

완료 시각: {NOW}
검토자: Performance Analyst / QA

## 증거

- `app/services/perf_report.py`: `PortfolioReport` dataclass + `build_portfolio_report()` 순수 함수 추가.
  - 실현/미실현 손익, 현금흐름·수수료·턴오버 면책, attribution by 자산군, tax-lot placeholder.
  - 면책 상수: `_CASHFLOW_NOTE`, `_FEE_SLIPPAGE_NOTE`, `_TURNOVER_NOTE`, `_TAX_LOT_DISCLAIMER`.
- `app/ui/views/portfolio.py`: `_render_perf_report()` + render() 하단 "📊 성과 리포트" expander 추가.
  - 라이브/mock 데이터 분기, 폴백 처리.
- `tests/unit/test_perf_report.py`: 14개 테스트 (TDD — 실패 선행 후 통과).
- 수정 전: 14개 FAILED (ImportError: perf_report)
- 수정 후: {N} passed (test_perf_report.py), {FULL} passed (전체)

## 리뷰

- 데이터 없는 항목(현금흐름·수수료·턴오버)은 '데이터 없음'/'not modeled' 명시 — 데이터 날조 없음.
- tax-lot은 execution_logs BUY 기록 기반 참고용 — 세무 조언 아님 (면책 표시).
- Attribution은 자산군별 미실현 평가손익 집계 — 시간/전략 축은 스냅샷 없어 불가 (명시).
- 주문 경로 (`order_flow.py`), risk policy, schema migration 변경 없음.
- TZ: report_date는 pnl_series 마지막 날짜 또는 고정 문자열 (datetime.now() 미사용).
```

- [ ] **Step 4.3: Update INDEX.md TASK-040 row**

In `C:\Users\ycpig\autofolio\agents\lead_engineer\tasks\INDEX.md`, find line:
```
| [TASK-040](TASK-040-portfolio-performance-tax-lot-reporting.md) | 대기 | Performance Analyst | Portfolio performance and tax-lot style reporting → v1 |
```

Change `대기` to `완료`.

- [ ] **Step 4.4: Commit the records**

```powershell
git add agents/lead_engineer/tasks/units/TASK-040/UNIT-TASK-040-001.md
git add agents/lead_engineer/tasks/TASK-040-portfolio-performance-tax-lot-reporting.md
git add agents/lead_engineer/tasks/INDEX.md
git commit -m "docs(task-040): UNIT-040-001 + TASK-040 완료 기록 + INDEX 업데이트"
```

---

## Task 5: Run Gate Scripts and Regenerate Views

- [ ] **Step 5.1: Run check_agent_docs.py**

```
python scripts/check_agent_docs.py
```

Expected: `0 errors` (or check if existing errors are pre-existing and not caused by our changes).

- [ ] **Step 5.2: Run generate_views.py**

```
python scripts/generate_views.py
```

This regenerates `agents/lead_engineer/tasks/VIEW-by-*.md` and `BACKLOG.md` files.

- [ ] **Step 5.3: Run build_task_index.py**

```
python scripts/build_task_index.py
```

This regenerates `tasks.index.json`.

- [ ] **Step 5.4: Run work_schema_gate.py (if it accepts --items --check)**

```
python scripts/work_schema_gate.py --items --check
```

- [ ] **Step 5.5: Verify all gates pass**

```
python scripts/generate_views.py --check
python scripts/build_task_index.py --check
```

Both should exit 0.

- [ ] **Step 5.6: Commit regenerated files**

```powershell
git add agents/lead_engineer/tasks/BACKLOG.md
git add agents/lead_engineer/tasks/VIEW-by-owner.md
git add agents/lead_engineer/tasks/VIEW-by-priority.md
git add agents/lead_engineer/tasks/VIEW-by-status.md
git add agents/lead_engineer/tasks/VIEW-by-tag.md
git add agents/lead_engineer/tasks/VIEW-by-workload.md
git add tasks.index.json
git add docs/BACKLOG.md
git commit -m "chore(views): regenerate BACKLOG/VIEW/tasks.index after TASK-040 완료"
```

---

## Task 6: Final Verification and Big Commit

- [ ] **Step 6.1: Run full pytest**

```
python -m pytest tests/ -q
python -m pytest tests/unit -q
```

Record the pass counts.

- [ ] **Step 6.2: Final gate check**

```
python scripts/check_agent_docs.py
python scripts/generate_views.py --check
python scripts/build_task_index.py --check
```

All must pass with 0 errors.

- [ ] **Step 6.3: Final commit (if any remaining unstaged)**

If everything is already committed in individual steps, skip this. Otherwise:

```powershell
git status
# Only commit YOUR files (not unrelated changes from git status at session start)
```

The final commit message format (if a combined commit is needed):

```
feat(reporting): 포트폴리오 성과/귀속/tax-lot 읽기전용 리포트 (TASK-040)

- app/services/perf_report.py: PortfolioReport + build_portfolio_report()
  순수 함수. 실현/미실현 P&L, 현금흐름·수수료·턴오버 면책, attribution by 자산군,
  tax-lot placeholder (illustrative only, 세무 조언 아님).
- app/ui/views/portfolio.py: 성과 리포트 expander (읽기전용).
- tests/unit/test_perf_report.py: 14개 TDD 테스트.
- agents/lead_engineer/tasks/TASK-040: 대기→완료.
- UNIT-TASK-040-001.md, INDEX.md, BACKLOG/VIEW/tasks.index 재생성.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
```

---

## Self-Review Checklist

**1. Spec coverage:**
- [x] realized/unrealized P&L summary → `PortfolioReport.realized_pnl` + `unrealized_pnl`
- [x] cashflow with "data unavailable" note → `cashflow_note` constant
- [x] fees/slippage "not modeled" → `fee_slippage_note` with explicit text
- [x] turnover "not available" → `turnover_note`
- [x] attribution by sector → `attribution_df` grouped by 자산군
- [x] tax-lot placeholder + disclaimer → `tax_lot_df` + `tax_lot_disclaimer`
- [x] UI table/chart → portfolio.py expander
- [x] TDD failing tests first → Task 1 is entirely test-writing with FAIL confirmation
- [x] No trading — no order buttons, no broker calls in report logic
- [x] Honest "데이터 없음" labels → all three unavailable sections have explicit note constants
- [x] TZ-independent → `report_date` from pnl_series last date (deterministic string) not `datetime.now()`
- [x] Monkeypatch pattern → tests patch nothing (pure function, no `_ctx` needed)
- [x] UNIT-TASK-040-001.md created
- [x] TASK-040 stub: frontmatter `status: 완료` + body `상태: 완료` + 완료 기록
- [x] INDEX.md updated
- [x] generate_views + build_task_index run

**2. Placeholder scan:** No "TBD", "TODO", "fill in details" in any task steps. All code blocks are complete.

**3. Type consistency:**
- `build_portfolio_report()` takes `holdings`, `pnl_series`, `kpis`, `realized_pnl` — consistent across all tasks.
- `PortfolioReport.attribution_df` columns `["구분", "기여(만원)"]` — matches test assertions in Task 1.
- `PortfolioReport.tax_lot_df` columns include `["티커", "종목", "자산군", "수량", "평단", "현재가", "평가손익", "손익률"]` — consistent with `_render_perf_report` column_config and test assertions.
- `report_date` is `str` of length 10 — tested in `test_has_report_date_field`.

All consistent. No gaps found.
