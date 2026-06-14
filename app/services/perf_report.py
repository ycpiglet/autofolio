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
