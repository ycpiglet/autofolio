"""실제 백엔드 어댑터 (증권 키 불필요: Mock 브로커 + SQLite). — P1.1

KIS_ENV=mock(기본)이면 MockBrokerClient를 쓰므로 증권계좌/API 키 없이 동작한다.
UI의 '라이브' 모드에서 이 어댑터로 화이트리스트/시세/조건/주문로그/엔진/리서치를 실연결한다.
"""
from __future__ import annotations

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


@lru_cache(maxsize=1)
def _ctx():
    """DB 초기화 + (비어있으면) 샘플 화이트리스트 시드 후 핵심 객체 반환."""
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
HOLDINGS_COLUMNS = ["종목", "티커", "자산군", "지역", "수량", "평단", "현재가",
                    "평가금액", "평가손익", "손익률", "비중"]
_ROLE_TO_ASSET_CLASS = {"ETF_TEST": "ETF", "LARGE_CAP_TEST": "주식", "LONG_TERM_CANDIDATE": "기타"}


def _build_holdings_df(positions_list, price_of, meta_of) -> pd.DataFrame:
    """포지션 + 현재가 + 화이트리스트 메타로 포트폴리오 표를 구성(순수 함수, 테스트 용이).

    price_of(symbol)->float, meta_of(symbol)->dict(name/role 등). KRX 보유라 지역=KR.
    """
    if not positions_list:
        return pd.DataFrame(columns=HOLDINGS_COLUMNS)
    rows = []
    for p in positions_list:
        meta = meta_of(p.symbol) or {}
        cur = float(price_of(p.symbol))
        avg = float(p.avg_price) if p.avg_price else 0.0
        market = p.quantity * cur
        cost = p.quantity * avg
        rows.append({
            "종목": meta.get("name") or p.symbol,
            "티커": p.symbol,
            "자산군": _ROLE_TO_ASSET_CLASS.get(meta.get("role"), "주식"),
            "지역": "KR",
            "수량": p.quantity,
            "평단": round(avg),
            "현재가": round(cur),
            "평가금액": round(market),
            "평가손익": round(market - cost),
            "손익률": round((cur / avg - 1) * 100, 1) if avg else 0.0,
        })
    df = pd.DataFrame(rows, columns=HOLDINGS_COLUMNS[:-1])
    total = df["평가금액"].sum()
    df["비중"] = (df["평가금액"] / total * 100).round(1) if total else 0.0
    return df


def holdings_df() -> pd.DataFrame:
    """라이브 보유 종목 표 (실 KIS 잔고 + 현재가). 포트폴리오 화면 라이브 소스.

    빈 잔고면 빈 DataFrame(HOLDINGS_COLUMNS). 라이브에선 보유종목 수만큼 현재가를 조회한다.
    """
    repo, broker, _, _ = _ctx()
    wl = {r["symbol"]: r for r in repo.list_whitelist_symbols()}
    return _build_holdings_df(
        broker.get_positions(),
        lambda s: broker.get_current_price(s).price,
        lambda s: wl.get(s, {}),
    )


def list_conditions() -> pd.DataFrame:
    repo, *_ = _ctx()
    rows = repo.list_conditions()
    return pd.DataFrame(rows) if rows else pd.DataFrame()


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
    return agent.propose_price_condition(symbol=symbol, current_price=cur, side=side)
