"""Shared backend adapter (Mock broker + SQLite by default). — P1.1

KIS_ENV=mock(기본)이면 MockBrokerClient를 쓰므로 증권계좌/API 키 없이 동작한다.
FastAPI/Next.js runtime은 이 어댑터로 화이트리스트/시세/조건/주문로그/엔진/리서치를 연결한다.

Strangler Migration — Phase 5:
  Phase 0의 app.services.backend 원본을 서비스 레이어로 실이동했다.
  Streamlit 뷰는 retired 상태이며 신규 production code는 app.services.backend 또는
  app.services.<domain> 모듈을 사용한다.
"""
from __future__ import annotations

import logging
import threading
from functools import lru_cache

import pandas as pd

from app.agents.research_agent import ConditionProposal, ResearchAgent
from app.brokers.factory import create_broker_client
from app.config.settings import settings
from app.database.repositories import Repository, WhitelistSymbol
from app.database.sqlite_db import initialize_database
from app.engine.live_trading_engine import LiveTradingEngine

_SEED = [
    ("005930", "삼성전자", "LARGE_CAP_TEST"),
    ("069500", "KODEX 200", "ETF_TEST"),
    ("360750", "TIGER 미국S&P500", "LONG_TERM_CANDIDATE"),
]

_LOGGER = logging.getLogger(__name__)

# FastAPI 스레드풀에서 동시에 초기화되는 이중-init 레이스를 방지한다.
# lru_cache 자체는 GIL로 보호되지만 초기화 함수 본체의 재진입은 막지 못한다.
_ctx_lock = threading.Lock()
_holdings_cache_lock = threading.Lock()
_LAST_HOLDINGS_DF: pd.DataFrame | None = None


@lru_cache(maxsize=1)
def _ctx():
    """DB 초기화 + (비어있으면) 샘플 화이트리스트 시드 후 핵심 객체 반환.

    참고: 이 함수는 app/services/ 모든 도메인 모듈에서 재-익스포트된다.
    초기화를 직렬화해 DB 시딩 경쟁을 방지한다 (단일 초기화 보장 아님).
    """
    with _ctx_lock:
        # 락은 초기화를 직렬화해 시딩 경쟁을 방지한다
        # (동시 첫 호출 시 본문이 두 번 실행될 수 있으나 멱등)
        initialize_database(settings.db_path)
        repo = Repository(settings.db_path)
        if not repo.list_whitelist_symbols():
            for sym, name, role in _SEED:
                repo.add_whitelist_symbol(WhitelistSymbol(symbol=sym, name=name, market="KRX", role=role))
        broker = create_broker_client()
        engine = LiveTradingEngine(broker=broker, repo=repo)
        agent = ResearchAgent()
        return repo, broker, engine, agent


def env() -> str:
    return settings.kis_env


def get_flag(key: str) -> bool:
    repo, *_ = _ctx()
    return repo.get_system_state(key, "false") == "true"


def set_flag(key: str, value: bool) -> None:
    repo, *_ = _ctx()
    repo.set_system_state(key, "true" if value else "false")


def list_whitelist() -> pd.DataFrame:
    repo, *_ = _ctx()
    rows = repo.list_whitelist_symbols()
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["symbol", "name", "market", "role", "enabled"])


def add_whitelist(symbol: str, name: str, role: str = "LARGE_CAP_TEST") -> None:
    repo, *_ = _ctx()
    repo.add_whitelist_symbol(WhitelistSymbol(symbol=symbol.strip(), name=name.strip(), market="KRX", role=role))


def symbol_options() -> dict[str, str]:
    df = list_whitelist()
    if df.empty:
        return {}
    return {f"{r['symbol']} · {r['name']}": r["symbol"] for _, r in df.iterrows()}


def price(symbol: str) -> float:
    _, broker, _, _ = _ctx()
    return float(broker.get_current_price(symbol).price)


def fundamental(symbol: str) -> dict:
    """KIS 기본 재무 지표. mock 환경이면 빈 dict."""
    from app.brokers.kis.kis_client import KisClient

    _, broker, _, _ = _ctx()
    if not isinstance(broker, KisClient):
        return {}
    return broker.get_fundamental(symbol)


def positions() -> pd.DataFrame:
    """현재 보유 포지션 (mock 또는 실 KIS 잔고). symbol/quantity/avg_price 컬럼.

    KIS_ENV=mock 이면 MockBrokerClient(빈 잔고로 시작), paper/prod 면 실 잔고조회.
    """
    _, broker, _, _ = _ctx()
    rows = broker.get_positions()
    if not rows:
        return pd.DataFrame(columns=["symbol", "quantity", "avg_price"])
    return pd.DataFrame(
        [{"symbol": p.symbol, "quantity": p.quantity, "avg_price": p.avg_price} for p in rows]
    )


# 포트폴리오 뷰가 기대하는 컬럼(=mock.data.holdings_df 와 동일 스키마).
HOLDINGS_COLUMNS = [
    "종목", "티커", "자산군", "지역", "섹터", "전략", "위험버킷", "수량", "평단", "현재가",
    "평가금액", "평가손익", "손익률", "예상연배당", "배당수익률", "비중",
]
_ROLE_TO_ASSET_CLASS = {"ETF_TEST": "ETF", "LARGE_CAP_TEST": "주식", "LONG_TERM_CANDIDATE": "기타"}
_DEFAULT_SYMBOL_META = {
    "000660": {"name": "SK하이닉스", "asset_class": "주식", "sector": "반도체"},
    "005380": {"name": "현대차", "asset_class": "주식", "sector": "자동차"},
    "005930": {"name": "삼성전자", "asset_class": "주식", "sector": "반도체"},
    "035420": {"name": "NAVER", "asset_class": "주식", "sector": "인터넷"},
    "035720": {"name": "카카오", "asset_class": "주식", "sector": "인터넷"},
    "055550": {"name": "신한지주", "asset_class": "주식", "sector": "금융"},
    "068270": {"name": "셀트리온", "asset_class": "주식", "sector": "바이오"},
    "069500": {"name": "KODEX 200", "asset_class": "ETF", "sector": "국내지수"},
    "102110": {"name": "TIGER 200", "asset_class": "ETF", "sector": "국내지수"},
    "105560": {"name": "KB금융", "asset_class": "주식", "sector": "금융"},
    "114260": {"name": "KODEX 국고채3년", "asset_class": "채권", "sector": "채권"},
}


def _empty_holdings_df() -> pd.DataFrame:
    return pd.DataFrame(columns=HOLDINGS_COLUMNS)


def _cache_holdings_df(df: pd.DataFrame) -> pd.DataFrame:
    global _LAST_HOLDINGS_DF
    with _holdings_cache_lock:
        _LAST_HOLDINGS_DF = df.copy()
    return df


def _cached_holdings_df() -> pd.DataFrame | None:
    with _holdings_cache_lock:
        if _LAST_HOLDINGS_DF is None:
            return None
        return _LAST_HOLDINGS_DF.copy()


def _fallback_holdings_df_after_error() -> pd.DataFrame:
    cached = _cached_holdings_df()
    if cached is not None:
        _LOGGER.warning("holdings_df live source failed; using cached portfolio holdings", exc_info=True)
        return cached
    _LOGGER.warning("holdings_df live source failed; returning empty portfolio schema", exc_info=True)
    return _empty_holdings_df()


def _fallback_symbol_meta(symbol: str) -> dict:
    return dict(_DEFAULT_SYMBOL_META.get(symbol, {}))


def _build_holdings_df(positions_list, price_of, meta_of, dividend_of=None) -> pd.DataFrame:
    """포지션 + 현재가 + 화이트리스트 메타로 포트폴리오 표를 구성(순수 함수, 테스트 용이).

    price_of(symbol)->float, meta_of(symbol)->dict(name/role 등).
    해외 포지션은 Position.currency/fx_rate/market 값이 있으면 원화 평가금액으로 환산한다.
    dividend_of(symbol)->dict(annual_cash_dividend/latest_dividend_rate) 는 선택.
    """
    if not positions_list:
        return pd.DataFrame(columns=HOLDINGS_COLUMNS)
    dividend_lookup = dividend_of or (lambda symbol: {})
    rows = []
    for p in positions_list:
        fallback_meta = _fallback_symbol_meta(p.symbol)
        meta = {**fallback_meta, **(meta_of(p.symbol) or {})}
        cur_native = float(price_of(p.symbol))
        avg_native = float(p.avg_price) if p.avg_price else 0.0
        currency = str(getattr(p, "currency", "KRW") or "KRW").upper()
        fx_rate = float(getattr(p, "fx_rate", None) or 1.0)
        cur = cur_native * fx_rate if currency != "KRW" else cur_native
        avg = avg_native * fx_rate if currency != "KRW" else avg_native
        market_value = p.quantity * cur
        cost = p.quantity * avg
        dividend = dividend_lookup(p.symbol) or {}
        annual_per_share = float(dividend.get("annual_cash_dividend") or 0.0)
        annual_income = annual_per_share * p.quantity
        dividend_yield = (
            annual_per_share / cur * 100
            if cur
            else float(dividend.get("latest_dividend_rate") or 0.0)
        )
        rows.append({
            "종목": meta.get("name") or p.symbol,
            "티커": p.symbol,
            "자산군": meta.get("asset_class") or _ROLE_TO_ASSET_CLASS.get(meta.get("role"), "주식"),
            "섹터": meta.get("sector") or "",
            "전략": meta.get("strategy") or "",
            "위험버킷": meta.get("risk_bucket") or "",
            "지역": _region_for_market(str(getattr(p, "market", None) or meta.get("market") or "KRX")),
            "수량": p.quantity,
            "평단": round(avg),
            "현재가": round(cur),
            "평가금액": round(market_value),
            "평가손익": round(market_value - cost),
            "손익률": round((cur / avg - 1) * 100, 1) if avg else 0.0,
            "예상연배당": round(annual_income),
            "배당수익률": round(dividend_yield, 2),
        })
    df = pd.DataFrame(rows)
    for column in HOLDINGS_COLUMNS[:-1]:
        if column not in df.columns:
            df[column] = ""
    df = df[HOLDINGS_COLUMNS[:-1]]
    total = df["평가금액"].sum()
    df["비중"] = (df["평가금액"] / total * 100).round(1) if total else 0.0
    return df


def _region_for_market(market: str) -> str:
    value = market.upper()
    if value in {"NASD", "NYSE", "AMEX"}:
        return "US"
    if value == "SEHK":
        return "HK"
    return "KR"


def holdings_df(*, include_dividends: bool = True) -> pd.DataFrame:
    """라이브 보유 종목 표 (실 KIS 잔고 + 현재가). 포트폴리오 화면 라이브 소스.

    빈 잔고면 빈 DataFrame(HOLDINGS_COLUMNS). 라이브에선 보유종목 수만큼 현재가를 조회한다.
    include_dividends=False 는 빠른 보유/손익 표시 경로에서 종목별 배당 API 호출을 건너뛴다.
    """
    repo, broker, _, _ = _ctx()
    wl = {r["symbol"]: r for r in repo.list_whitelist_symbols()}
    try:
        positions = broker.get_positions()
        if not positions:
            return _cache_holdings_df(_empty_holdings_df())
        symbols = [p.symbol for p in positions]
        if hasattr(broker, "get_prices_batch"):
            price_cache = broker.get_prices_batch(symbols)
            price_of = lambda s: price_cache.get(s) or broker.get_current_price(s).price
        else:
            price_of = lambda s: broker.get_current_price(s).price
        if include_dividends and hasattr(broker, "get_dividend_info"):
            def dividend_of(symbol: str) -> dict:
                try:
                    return broker.get_dividend_info(symbol) or {}
                except Exception:  # noqa: BLE001
                    return {}
        else:
            dividend_of = lambda symbol: {}
        df = _build_holdings_df(positions, price_of, lambda s: wl.get(s, {}), dividend_of)
        return _cache_holdings_df(df)
    except Exception:  # noqa: BLE001 - portfolio read UI must degrade instead of returning 500 on live KIS glitches
        return _fallback_holdings_df_after_error()


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
        # 보유 종목 매수 원가 합계 (분모) — 전일 평가액 대체 (가격 시계열 없음)
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


def recent_fills(limit: int = 10) -> pd.DataFrame:
    """최근 체결 내역 — order_logs에서 FILLED 상태만.

    컬럼: 시각·종목·방향·수량·체결가.
    order_logs.created_at(YYYY-MM-DD HH:MM:SS)에서 HH:MM 부분만 추출한다.
    """
    df = list_order_logs(limit=limit * 10)  # FILLED가 드물 수 있으므로 넉넉히 조회
    if df.empty:
        return pd.DataFrame(columns=["시각", "종목", "방향", "수량", "체결가"])
    filled = df[df["order_status"] == "FILLED"].copy()
    if filled.empty:
        return pd.DataFrame(columns=["시각", "종목", "방향", "수량", "체결가"])
    filled = filled.head(limit)
    timestamp = filled["filled_at"] if "filled_at" in filled.columns else filled["created_at"]
    filled["시각"] = timestamp.fillna(filled["created_at"]).astype(str).str[11:16]
    quantity = filled["filled_quantity"] if "filled_quantity" in filled.columns else filled["quantity"]
    price = filled["filled_price"] if "filled_price" in filled.columns else filled.get("order_price")
    filled["수량"] = quantity.fillna(filled["quantity"]).astype(int)
    if "order_price" in filled.columns:
        price = price.fillna(filled["order_price"])
    if "current_price" in filled.columns:
        price = price.fillna(filled["current_price"])
    filled["체결가"] = price
    result = filled[["시각", "symbol", "side", "수량", "체결가"]].rename(
        columns={"symbol": "종목", "side": "방향"}
    )
    return result.reset_index(drop=True)


# 등록된 조건 표 — 화면에 표시할 핵심 컬럼과 한글 라벨 매핑.
# list_conditions()는 이 7개 컬럼만 반환하므로 메인 표·확장 행 모두 이 컬럼만 보인다.
_CONDITIONS_DISPLAY_COLUMNS: dict[str, str] = {
    "symbol": "종목",
    "side": "구분",
    "target_price": "목표가",
    "quantity": "수량",
    "order_type": "주문유형",
    "status": "상태",
    "created_at": "등록일시",
}


def list_conditions() -> pd.DataFrame:
    """등록된 조건 목록 — 핵심 7개 컬럼만 한글 라벨로 반환.

    원시 snake_case 컬럼(15개)을 그대로 내보내면 DataTable 헤더가 압축·겹쳐
    읽기 어려우므로, 거래 파악에 필요한 핵심 7개 컬럼만 한글 라벨로 골라 반환한다.
    반환되는 컬럼이 곧 화면에 보이는 전부다(메인 표·확장 행 동일). 나머지 원시
    컬럼(rationale·risk_note·cooldown_until 등)은 현재 화면에 노출하지 않는다.
    """
    repo, *_ = _ctx()
    rows = repo.list_conditions()
    if not rows:
        return pd.DataFrame(columns=list(_CONDITIONS_DISPLAY_COLUMNS.values()))
    df = pd.DataFrame(rows)
    # 핵심 컬럼만 선택한 뒤 한글 라벨로 이름 변경
    available = [c for c in _CONDITIONS_DISPLAY_COLUMNS if c in df.columns]
    df = df[available].rename(columns=_CONDITIONS_DISPLAY_COLUMNS)
    return df


def add_condition(symbol: str, side: str, target_price: float, quantity: int,
                  order_type: str = "LIMIT", auto_enabled: bool = False,
                  created_by: str = "USER", rationale: str | None = None,
                  risk_note: str | None = None) -> int:
    repo, *_ = _ctx()
    return repo.add_trade_condition(
        symbol=symbol, side=side, target_price=target_price, quantity=quantity,
        order_type=order_type, auto_enabled=auto_enabled, created_by=created_by,
        rationale=rationale, risk_note=risk_note,
    )


def list_order_logs(limit: int = 200) -> pd.DataFrame:
    repo, *_ = _ctx()
    rows = repo.list_order_logs(limit=limit)
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def run_engine_once() -> list[str]:
    _, _, engine, _ = _ctx()
    return engine.run_once()


def propose(symbol: str, side: str = "BUY") -> ConditionProposal:
    _, broker, _, agent = _ctx()
    cur = broker.get_current_price(symbol).price
    fundamental_data = {}
    if hasattr(broker, "get_fundamental"):
        try:
            fundamental_data = broker.get_fundamental(symbol) or {}
        except Exception:  # noqa: BLE001
            fundamental_data = {}
    return agent.propose_price_condition(
        symbol=symbol,
        current_price=cur,
        side=side,
        fundamental=fundamental_data,
    )


def set_risk_limits(
    *,
    max_order_amount: float | None = None,
    max_daily_amount: float | None = None,
) -> None:
    """리스크 한도를 DB에 저장 (설정 화면 → SafetyChecker 실시간 반영)."""
    repo, *_ = _ctx()
    repo.update_global_risk_limit(
        max_order_amount=max_order_amount,
        max_daily_amount=max_daily_amount,
    )


def attribution_df() -> pd.DataFrame:
    """주문로그 체결 기반 손익 기여 (자산군별 실현손익 합계).

    체결 내역이 없으면 빈 DataFrame 반환.
    holdings_df의 자산군 매핑을 재사용해 미실현 평가손익을 자산군별로 집계.
    """
    df = holdings_df(include_dividends=False)
    if df.empty:
        return pd.DataFrame(columns=["구분", "기여(만원)"])
    grouped = df.groupby("자산군")["평가손익"].sum().reset_index()
    grouped.columns = ["구분", "기여(만원)"]
    grouped["기여(만원)"] = (grouped["기여(만원)"] / 10_000).round(1)
    return grouped.sort_values("기여(만원)", ascending=False).reset_index(drop=True)


def retro_metrics() -> dict:
    """주문로그 기반 회고 지표. 체결 없으면 placeholder 반환."""
    repo, *_ = _ctx()
    logs = repo.list_order_logs(limit=500)
    if not logs:
        return {"승률": 0, "평균R": 0.0, "MDD": 0.0, "규율": 0}
    filled = [l for l in logs if l.get("order_status") == "FILLED"]
    total = len(filled)
    if total == 0:
        return {"승률": 0, "평균R": 0.0, "MDD": 0.0, "규율": 0}
    # 간단 승률: 체결/전체 주문 비율
    win_rate = round(total / len(logs) * 100)
    return {
        "승률": win_rate,
        "평균R": round(total / max(len(logs) - total, 1), 2),
        "MDD": 0.0,   # MDD는 가격 시계열 필요 — 퀀트 엔진 이후
        "규율": min(100, win_rate + 20),
    }


def circuit_breaker_status() -> dict:
    """서킷브레이커 현황 — UI 상단 바에서 경고 표시에 사용한다.

    반환 키:
      triggered (bool)     — 현재 auto_trading_enabled=false 이고 서킷브레이커가 원인일 때 True
      threshold_pct (float) — 일일 손실 트리거 기준(%)
      consecutive_failures (int) — 연속 주문 실패 횟수
      today_pnl (float)    — 오늘 실현 현금흐름 합계
    """
    repo, *_ = _ctx()
    threshold_pct_str = repo.get_system_state("circuit_breaker_threshold_pct", "3.0")
    try:
        threshold_pct = float(threshold_pct_str)
    except (ValueError, TypeError):
        threshold_pct = 3.0

    consecutive_failures_str = repo.get_system_state("consecutive_order_failures", "0")
    try:
        consecutive_failures = int(consecutive_failures_str)
    except (ValueError, TypeError):
        consecutive_failures = 0

    today_pnl = repo.today_realized_pnl()

    auto_enabled = repo.get_system_state("auto_trading_enabled", "false") == "true"
    kill_active = repo.get_system_state("kill_switch_active", "false") == "true"

    # Consider circuit breaker triggered if auto-trading was disabled and either
    # the consecutive failure threshold or the daily-loss threshold is breached.
    loss_tripped = False
    if today_pnl < 0:
        try:
            limit = repo.get_global_risk_limit()
            reference = float(limit["max_daily_amount"])
        except Exception:
            reference = 0.0
        if reference > 0:
            loss_pct = abs(today_pnl) / reference * 100.0
            loss_tripped = loss_pct >= threshold_pct

    triggered = (not auto_enabled) and (not kill_active) and (
        consecutive_failures >= 3 or loss_tripped
    )

    return {
        "triggered": triggered,
        "threshold_pct": threshold_pct,
        "consecutive_failures": consecutive_failures,
        "today_pnl": today_pnl,
    }


def allocation_gap(target: dict | None = None) -> pd.DataFrame:
    """라이브 보유종목 기반 자산배분 vs 목표 갭.

    target: {"주식": 35, "ETF": 30, ...} — None이면 기본값 사용.
    """
    _target = target or {"주식": 35, "ETF": 30, "채권": 15, "원자재": 5, "현금": 15}
    df = holdings_df(include_dividends=False)
    if df.empty:
        return pd.DataFrame([
            {"자산군": k, "목표%": v, "현재%": 0.0, "갭%": -v}
            for k, v in _target.items()
        ])
    current = df.groupby("자산군")["비중"].sum().to_dict()
    rows = []
    for cls, tgt in _target.items():
        cur = round(current.get(cls, 0.0), 1)
        rows.append({"자산군": cls, "목표%": tgt, "현재%": cur, "갭%": round(cur - tgt, 1)})
    return pd.DataFrame(rows)


def account_summary() -> dict:
    """KIS 잔고 output2(계좌 요약) — 총평가금액·예수금·순자산.

    KIS_ENV=paper/prod: KisClient.get_account_summary()를 사용. mock/실패 시
    holdings_df 기반 추정.
    """
    env_name = env()
    if env_name in ("paper", "prod"):
        try:
            _, broker, _, _ = _ctx()
            if hasattr(broker, "get_account_summary"):
                summary = broker.get_account_summary()
                if summary:
                    return summary
        except Exception:  # noqa: BLE001
            pass
    # mock/폴백: holdings_df 기반 추정
    df = holdings_df(include_dividends=False)
    market_val = float(df["평가금액"].sum()) if not df.empty else 0.0
    return {
        "scts_evlu_amt": market_val,    # 유가증권 평가금액
        "dnca_tot_amt": 0.0,            # 예수금 (mock에선 불명)
        "tot_evlu_amt": market_val,     # 총평가금액
        "nass_amt": market_val,         # 순자산
        "source": "estimated",
    }


def list_portfolio_groups() -> list[dict]:
    repo, *_ = _ctx()
    return repo.list_portfolio_groups()


def create_portfolio_group(**payload) -> dict:
    repo, *_ = _ctx()
    return repo.create_portfolio_group(**payload)


def update_portfolio_group(group_id: str, **payload) -> dict | None:
    repo, *_ = _ctx()
    return repo.update_portfolio_group(group_id, **payload)


def delete_portfolio_group(group_id: str) -> bool:
    repo, *_ = _ctx()
    return repo.delete_portfolio_group(group_id)


def watchlist() -> pd.DataFrame:
    """화이트리스트 종목 현재가 일괄 조회 (와치리스트).

    KIS_ENV=paper/prod: KisClient.get_current_price() 호출 (레이트리밋 주의).
    mock: MockBrokerClient.get_current_price().
    컬럼: symbol, name, price, env.
    """
    repo, broker, _, _ = _ctx()
    wl = repo.list_whitelist_symbols(enabled_only=True)
    if not wl:
        return pd.DataFrame(columns=["symbol", "name", "price"])
    price_cache = {}
    if hasattr(broker, "get_prices_batch"):
        try:
            price_cache = broker.get_prices_batch([item["symbol"] for item in wl])
        except Exception:  # noqa: BLE001
            price_cache = {}
    rows = []
    for item in wl:
        try:
            import time
            price = price_cache.get(item["symbol"])
            if price is None:
                price = broker.get_current_price(item["symbol"]).price
            rows.append({"symbol": item["symbol"], "name": item.get("name", ""), "price": price})
            if not price_cache:
                time.sleep(0.15)  # 레이트리밋 방지
        except Exception:  # noqa: BLE001
            rows.append({"symbol": item["symbol"], "name": item.get("name", ""), "price": None})
    return pd.DataFrame(rows)


def market_indices_df() -> pd.DataFrame:
    """KIS 국내 지수 현재가. mock 환경이면 빈 DataFrame."""
    from app.brokers.kis.constants import KIS_INDEX_CODES
    from app.brokers.kis.kis_client import KisClient

    _, broker, _, _ = _ctx()
    columns = ["name", "code", "price", "change", "change_rate"]
    if not isinstance(broker, KisClient):
        return pd.DataFrame(columns=columns)
    rows = []
    for name, code in KIS_INDEX_CODES.items():
        data = broker.get_index_price(code)
        if not data:
            continue
        rows.append(
            {
                "name": name,
                "code": code,
                "price": data.get("price"),
                "change": data.get("change"),
                "change_rate": data.get("change_rate"),
            }
        )
    return pd.DataFrame(rows, columns=columns)


def sector_performance_df() -> pd.DataFrame:
    """KIS 주요 업종 현재지수. mock 환경이면 빈 DataFrame."""
    from app.brokers.kis.constants import KIS_SECTOR_CODES
    from app.brokers.kis.kis_client import KisClient

    _, broker, _, _ = _ctx()
    columns = ["name", "code", "price", "change", "change_rate", "trading_value"]
    if not isinstance(broker, KisClient):
        return pd.DataFrame(columns=columns)
    rows = []
    for alias in KIS_SECTOR_CODES:
        data = broker.get_sector_price(alias)
        if not data:
            continue
        rows.append(
            {
                "name": data.get("name"),
                "code": data.get("sector_code"),
                "price": data.get("price"),
                "change": data.get("change"),
                "change_rate": data.get("change_rate"),
                "trading_value": data.get("trading_value"),
            }
        )
    return pd.DataFrame(rows, columns=columns)


ORDER_BOOK_COLUMNS = ["level", "ask_price", "ask_quantity", "bid_price", "bid_quantity"]


def order_book_snapshot(symbol: str, market: str = "J") -> dict:
    """KIS 10단계 호가 snapshot. mock 환경이면 빈 dict."""
    from app.brokers.kis.kis_client import KisClient

    _, broker, _, _ = _ctx()
    if not isinstance(broker, KisClient):
        return {}
    return broker.get_order_book(symbol, market=market)


def order_book_levels_df(snapshot: dict) -> pd.DataFrame:
    rows = (snapshot or {}).get("levels") or []
    if not rows:
        return pd.DataFrame(columns=ORDER_BOOK_COLUMNS)
    return pd.DataFrame(rows, columns=ORDER_BOOK_COLUMNS)


def order_book_df(symbol: str, market: str = "J") -> pd.DataFrame:
    """KIS 10단계 호가 테이블. mock 환경이면 빈 DataFrame."""
    return order_book_levels_df(order_book_snapshot(symbol, market=market))


DISCLOSURE_COLUMNS = [
    "date",
    "time",
    "symbol",
    "title",
    "category",
    "severity",
    "block_order",
    "source",
    "serial",
]
_DISCLOSURE_BLOCK_PREFIX = "compliance_disclosure_block:"
_DISCLOSURE_REASON_PREFIX = "compliance_disclosure_reason:"


def disclosures_df(symbol: str, days: int = 1) -> pd.DataFrame:
    """KIS 종합 시황/공시 제목 조회. mock 환경이면 빈 DataFrame."""
    from app.brokers.kis.kis_client import KisClient

    _, broker, _, _ = _ctx()
    if not isinstance(broker, KisClient):
        return pd.DataFrame(columns=DISCLOSURE_COLUMNS)
    rows = broker.get_disclosures(symbol, days=days)
    if not rows:
        return pd.DataFrame(columns=DISCLOSURE_COLUMNS)
    return pd.DataFrame(rows, columns=DISCLOSURE_COLUMNS)


def disclosure_gate_state(symbol: str) -> dict:
    repo, *_ = _ctx()
    code = str(symbol or "").strip()
    blocked = repo.get_system_state(_DISCLOSURE_BLOCK_PREFIX + code, "false") == "true"
    reason = repo.get_system_state(_DISCLOSURE_REASON_PREFIX + code, "") or ""
    return {"symbol": code, "blocked": blocked, "reason": reason}


def _send_disclosure_notification(notifier, symbol: str, blocked_rows: list[dict]) -> None:
    if notifier is None or not hasattr(notifier, "send") or not blocked_rows:
        return
    first = blocked_rows[0]
    title = first.get("title") or "중대 공시"
    severity = first.get("severity") or "HIGH"
    notifier.send(f"[공시 경고] {symbol} {severity}: {title}")


def refresh_disclosure_gate(
    symbol: str,
    days: int = 1,
    *,
    notify: bool = False,
    notifier=None,
) -> dict:
    """공시 조회 결과로 Compliance 차단 플래그를 갱신한다.

    실제 주문 경로는 수정하지 않고, UI/운영자가 읽을 수 있는 system_state 플래그만 쓴다.
    """
    repo, *_ = _ctx()
    code = str(symbol or "").strip()
    df = disclosures_df(code, days=days)
    if df.empty:
        repo.set_system_state(_DISCLOSURE_BLOCK_PREFIX + code, "false")
        repo.set_system_state(_DISCLOSURE_REASON_PREFIX + code, "")
        return {"symbol": code, "blocked": False, "reason": "", "disclosures": df}

    blocked_df = df[df["block_order"] == True]  # noqa: E712 - pandas boolean mask
    blocked = not blocked_df.empty
    reason = ""
    if blocked:
        first = blocked_df.iloc[0]
        reason = f"{first.get('severity', 'HIGH')} {first.get('category', '')}: {first.get('title', '')}"
    repo.set_system_state(_DISCLOSURE_BLOCK_PREFIX + code, "true" if blocked else "false")
    repo.set_system_state(_DISCLOSURE_REASON_PREFIX + code, reason)

    if blocked and notify:
        if notifier is None:
            from app.notification.notifier import make_notifier_from_env

            notifier = make_notifier_from_env()
        _send_disclosure_notification(notifier, code, blocked_df.to_dict("records"))

    return {"symbol": code, "blocked": blocked, "reason": reason, "disclosures": df}


def intraday_chart_df(
    symbol: str,
    time_unit: str = "1",
    count: int = 120,
) -> pd.DataFrame:
    """KIS 당일 분봉 차트 데이터. mock 환경이면 빈 DataFrame."""
    from app.data.data_loader import load_intraday_chart

    return load_intraday_chart(symbol, time_unit=time_unit, count=count)


def add_price_alert(symbol: str, target_price: float, direction: str = "ABOVE") -> int:
    """가격 알림 조건을 DB에 저장. LiveTradingEngine 실행 시 체크·발송."""
    repo, *_ = _ctx()
    return repo.add_price_alert(symbol, target_price, direction)


def list_journal_entries(limit: int = 100):
    """거래 저널 항목 목록."""
    repo, *_ = _ctx()
    rows = repo.list_journal_entries(limit=limit)
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=[
        "id", "order_log_id", "symbol", "side", "entry_reason",
        "exit_reason", "grade", "lesson", "plan_followed", "emotion_flag", "created_at"
    ])


def add_journal_entry(
    symbol: str, side: str, *,
    order_log_id=None, entry_reason: str = "", exit_reason: str = "",
    grade: str | None = None, lesson: str = "",
    plan_followed: bool = True, emotion_flag: bool = False,
) -> int:
    """거래 저널 항목 추가."""
    repo, *_ = _ctx()
    return repo.add_journal_entry(
        symbol=symbol, side=side, order_log_id=order_log_id,
        entry_reason=entry_reason, exit_reason=exit_reason,
        grade=grade, lesson=lesson,
        plan_followed=plan_followed, emotion_flag=emotion_flag,
    )


_DEFAULT_SCENARIOS: dict = {
    "Bull": {"주식": +15.0, "ETF": +12.0, "채권": +3.0, "원자재": +8.0, "기타": +5.0},
    "Base": {"주식": +5.0, "ETF": +4.0, "채권": +2.0, "원자재": +1.0, "기타": +2.0},
    "Bear": {"주식": -15.0, "ETF": -12.0, "채권": +5.0, "원자재": -5.0, "기타": -8.0},
}


def scenario_analysis(scenarios: dict | None = None) -> pd.DataFrame:
    """보유 포트폴리오에 시나리오 적용 — 주가 변동 효과 계산.

    scenarios: {"Bull": {"주식": +15, "ETF": +12, "채권": +3, "원자재": +8},
                "Base": {"주식": +5, "ETF": +4, "채권": +2, "원자재": +1},
                "Bear": {"주식": -15, "ETF": -12, "채권": +5, "원자재": -5}}
    반환: DataFrame columns = [시나리오, 자산군, 현재금액(원), 변동률(%), 변동액(원), 시나리오후금액(원)]
    포트폴리오 전체 합계 행(자산군="합계")도 포함.
    """
    _scenarios = scenarios or _DEFAULT_SCENARIOS
    df = holdings_df(include_dividends=False)
    if df.empty:
        return pd.DataFrame(columns=["시나리오", "자산군", "현재금액(원)", "변동률(%)", "변동액(원)", "시나리오후금액(원)"])

    # 자산군별 현재 평가금액 합계
    asset_totals = df.groupby("자산군")["평가금액"].sum().to_dict()
    total_current = df["평가금액"].sum()

    rows = []
    for scenario_name, changes in _scenarios.items():
        scenario_total_delta = 0.0
        for asset_cls, pct_change in changes.items():
            current_val = asset_totals.get(asset_cls, 0.0)
            if current_val == 0.0:
                continue  # 해당 자산군 미보유 → 스킵
            delta = current_val * pct_change / 100.0
            new_val = current_val + delta
            scenario_total_delta += delta
            rows.append({
                "시나리오": scenario_name,
                "자산군": asset_cls,
                "현재금액(원)": round(current_val),
                "변동률(%)": round(pct_change, 1),
                "변동액(원)": round(delta),
                "시나리오후금액(원)": round(new_val),
            })
        # 합계 행
        rows.append({
            "시나리오": scenario_name,
            "자산군": "합계",
            "현재금액(원)": round(total_current),
            "변동률(%)": round(scenario_total_delta / total_current * 100, 2) if total_current else 0.0,
            "변동액(원)": round(scenario_total_delta),
            "시나리오후금액(원)": round(total_current + scenario_total_delta),
        })
    return pd.DataFrame(rows, columns=["시나리오", "자산군", "현재금액(원)", "변동률(%)", "변동액(원)", "시나리오후금액(원)"])


def whatif_weight_change(symbol: str, new_weight_pct: float) -> dict:
    """종목 비중을 new_weight_pct%로 변경했을 때 포트폴리오 영향 계산.

    반환: {symbol, current_weight, new_weight, delta_shares, delta_cost,
           new_total_assets_estimated, risk_note}
    delta_shares > 0 이면 추가매수, < 0 이면 일부매도.
    """
    df = holdings_df(include_dividends=False)
    if df.empty:
        return {
            "symbol": symbol,
            "current_weight": 0.0,
            "new_weight": new_weight_pct,
            "delta_shares": 0,
            "delta_cost": 0,
            "new_total_assets_estimated": 0.0,
            "risk_note": "보유 종목 없음 — 포트폴리오가 비어있습니다.",
        }
    total = float(df["평가금액"].sum())
    row = df[df["티커"] == symbol]
    if row.empty:
        # 화이트리스트에는 있지만 미보유 종목
        _, broker, _, _ = _ctx()
        try:
            cur_price = float(broker.get_current_price(symbol).price)
        except Exception:  # noqa: BLE001
            cur_price = 0.0
        current_weight = 0.0
        current_value = 0.0
        current_price = cur_price
        current_shares = 0
    else:
        row = row.iloc[0]
        current_weight = float(row["비중"])
        current_value = float(row["평가금액"])
        current_price = float(row["현재가"])
        current_shares = int(row["수량"])

    target_value = total * new_weight_pct / 100.0
    delta_value = target_value - current_value
    delta_shares = int(delta_value / current_price) if current_price else 0
    delta_cost = delta_shares * current_price

    # 리스크 노트
    risk_notes = []
    if new_weight_pct > 30:
        risk_notes.append(f"단일 종목 비중 {new_weight_pct:.1f}% > 30% — 집중 리스크 주의.")
    if abs(new_weight_pct - current_weight) > 10:
        risk_notes.append(f"비중 변화 {abs(new_weight_pct - current_weight):.1f}%p — 한 번에 집행 시 시장충격 고려.")
    if new_weight_pct == 0 and current_shares > 0:
        risk_notes.append("전량 매도 시나리오 — 세금·수수료 감안 필요.")

    return {
        "symbol": symbol,
        "current_weight": round(current_weight, 2),
        "new_weight": round(new_weight_pct, 2),
        "delta_shares": delta_shares,
        "delta_cost": round(delta_cost),
        "new_total_assets_estimated": round(total + delta_cost),
        "risk_note": " ".join(risk_notes) if risk_notes else "이상 없음.",
    }



def kis_today_orders() -> pd.DataFrame:
    """KIS 당일 주문내역. mock 환경이면 빈 DataFrame."""
    from app.brokers.kis.kis_client import KisClient
    _, broker, _, _ = _ctx()
    if not isinstance(broker, KisClient):
        return pd.DataFrame()
    rows = broker.get_today_orders()
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def kis_order_history(start_date: str, end_date: str) -> pd.DataFrame:
    """KIS 날짜 범위 주문내역. mock 환경이면 빈 DataFrame."""
    from app.brokers.kis.kis_client import KisClient
    _, broker, _, _ = _ctx()
    if not isinstance(broker, KisClient):
        return pd.DataFrame()
    rows = broker.get_order_history(start_date, end_date)
    if not rows:
        return pd.DataFrame()
    _side = {"01": "매도", "02": "매수"}
    result = []
    for r in rows:
        cncl = r.get("cncl_yn", "N").upper() == "Y"
        ccld = int(r.get("tot_ccld_qty") or 0)
        ord_qty = int(r.get("ord_qty") or 0)
        status = "취소" if cncl else ("체결" if ccld >= ord_qty > 0 else "미체결")
        result.append({
            "날짜": r.get("ord_dt", "")[:8],
            "주문번호": r.get("odno", ""),
            "종목": r.get("pdno", ""),
            "구분": _side.get(str(r.get("sll_buy_dvsn_cd", "")), "-"),
            "주문수량": ord_qty,
            "체결수량": ccld,
            "주문가": int(r.get("ord_unpr") or 0),
            "체결평균가": int(float(r.get("avg_prvs") or 0)),
            "상태": status,
        })
    return pd.DataFrame(result)


def daily_pnl_series() -> "pd.DataFrame":
    """일별 실현손익 시계열 (execution_logs 기반).

    컬럼: date (YYYY-MM-DD), pnl (원).
    """
    repo, *_ = _ctx()
    from app.database.sqlite_db import get_connection
    with get_connection(repo.db_path) as conn:
        rows = conn.execute(
            """
            SELECT DATE(el.filled_at) AS date,
                   SUM(CASE WHEN ol.side='SELL'
                            THEN el.filled_price * el.filled_quantity
                            ELSE -el.filled_price * el.filled_quantity END) AS pnl
            FROM execution_logs el
            JOIN order_logs ol ON el.order_log_id = ol.id
            GROUP BY DATE(el.filled_at)
            ORDER BY date
            """
        ).fetchall()
    return pd.DataFrame([dict(r) for r in rows]) if rows else pd.DataFrame(columns=["date", "pnl"])


# ── 데모 자산추이 생성 ────────────────────────────────────────────────────────
# mock/demo 환경에서 체결 내역 없이 0원이 반환될 때 사용하는 시드값 및 초기 자본.
# 이 값들은 DEMO 전용이며 실거래/실계정 경로에 영향을 주지 않는다.
_DEMO_RNG_SEED: int = 7          # 결정적 재현성 보장 (numpy.random.default_rng)
_DEMO_INITIAL_CAPITAL: float = 1_500_000.0  # 데모 시작 자본 (₩150만)
_DEMO_MIN_REAL_POINTS: int = 14  # 실데이터 포인트가 이 값 이상이면 데모 미발동 (≈ 2주)


def _generate_demo_asset_curve(days: int, end_value: float) -> pd.DataFrame:
    """데모 전용 — 결정적(고정 시드) 일별 자산추이를 생성한다.

    실거래·실계정 경로에서는 절대 호출되지 않는다.
    시작값은 _DEMO_INITIAL_CAPITAL, 끝값은 end_value(0이면 _DEMO_INITIAL_CAPITAL) 에 맞춘다.
    일별 수익률은 뮤 0.09% / 시그마 1.1% 의 정규분포 (KOSPI 장기 일평균 근사).
    """
    import datetime as dt
    import numpy as np

    target_end = end_value if end_value > 0 else _DEMO_INITIAL_CAPITAL
    rng = np.random.default_rng(_DEMO_RNG_SEED)
    steps = rng.normal(0.0009, 0.011, days)
    series = np.cumprod(1 + steps)
    # 시작값을 _DEMO_INITIAL_CAPITAL, 끝값을 target_end에 고정
    series = series / series[0] * _DEMO_INITIAL_CAPITAL
    series = series * (target_end / series[-1])
    idx = pd.date_range(end=dt.date.today(), periods=days, name="date")
    return pd.DataFrame({"자산": series.round()}, index=idx)


def asset_curve(days: int = 90) -> pd.DataFrame:
    """누적 자산 곡선 — execution_logs 기반 일별 누적 손익 + 현재 보유 자산.

    컬럼: date (index, name="date"), 자산 (float).
    df.attrs["is_demo"] = True 이면 합성 데모 곡선(라벨 필수).

    폴백 우선순위:
    1. prod 환경(KIS_ENV=prod) → 항상 실 경로(데모 미발동).
    2. 비-prod(mock/paper) + 실 포인트 < _DEMO_MIN_REAL_POINTS → 데모 시드 곡선.
       base_value > 0이면 끝점을 실 현재총액에 고정(현재 상태는 진실).
       base_value == 0이면 nominal(₩150만) 유지 (기존 mock-empty 동작).
    3. 비-prod + 실 포인트 >= _DEMO_MIN_REAL_POINTS → 실 누적 손익 경로.
    4. prod + 실 포인트 >= 1 → 실 누적 손익 경로.
    5. prod + 체결 내역 없음 + base_value > 0 → 단일 관측값.
    """
    pnl_df = daily_pnl_series()
    holdings = holdings_df(include_dividends=False)
    base_value = float(holdings["평가금액"].sum()) if not holdings.empty else 0.0

    # real_points: 이용 가능한 실 데이터 포인트 수
    real_points = len(pnl_df.tail(days)) if not pnl_df.empty else 0

    is_non_prod = env() in {"mock", "paper"}
    sparse = real_points < _DEMO_MIN_REAL_POINTS

    if is_non_prod and sparse:
        # 비-prod sparse → 데모 곡선 (끝점을 실 현재총액에 앵커)
        df = _generate_demo_asset_curve(days, end_value=base_value)
        df.attrs["is_demo"] = True
        return df

    if pnl_df.empty:
        # prod + 체결 내역 없음 + base_value > 0 → 단일 관측값
        import datetime as dt
        today = dt.date.today().isoformat()
        df = pd.DataFrame({"자산": [base_value]}, index=pd.Index([today], name="date"))
        df.attrs["is_demo"] = False
        return df

    # 실 누적 손익 경로 (비-prod 충분한 데이터 또는 prod)
    pnl_df = pnl_df.tail(days).copy()
    pnl_df["cumulative_pnl"] = pnl_df["pnl"].cumsum()
    pnl_df["자산"] = base_value + pnl_df["cumulative_pnl"] - pnl_df["cumulative_pnl"].iloc[-1]
    pnl_df.index = pd.Index(pnl_df["date"], name="date")
    df = pnl_df[["자산"]]
    df.attrs["is_demo"] = False
    return df
