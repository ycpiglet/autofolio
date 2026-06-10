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


def kpis() -> dict:
    """라이브 KPI — 총자산·평가손익·현금비중. holdings_df 기반.

    현금 잔고는 현재 DB/API에서 직접 조회하지 못하므로 0.0 placeholder.
    반환 키: 총자산, 일손익률, 누적손익률, 현금비중, 평가손익.
    """
    df = holdings_df()
    total_market = float(df["평가금액"].sum()) if not df.empty else 0.0
    total_pnl = float(df["평가손익"].sum()) if not df.empty else 0.0
    # 현금 잔고: 현재 Mock 브로커에서는 미지원 → 0.0 placeholder
    cash = 0.0
    total_assets = total_market + cash
    cash_ratio = (cash / total_assets * 100) if total_assets else 0.0
    return {
        "총자산": total_assets,
        "일손익률": 0.0,
        "누적손익률": 0.0,
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
    # created_at 은 'YYYY-MM-DD HH:MM:SS' 형식(SQLite CURRENT_TIMESTAMP)
    filled["시각"] = filled["created_at"].str[11:16]
    result = filled[["시각", "symbol", "side", "quantity", "order_price"]].rename(
        columns={"symbol": "종목", "side": "방향", "quantity": "수량", "order_price": "체결가"}
    )
    return result.reset_index(drop=True)


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
    df = holdings_df()
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
    df = holdings_df()
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

    KIS_ENV=paper/prod: KisClient.get_positions() 시 output2가 있으면 backend._ctx()의
    broker를 통해 KisClient._account_summary()를 호출. mock이면 holdings_df 기반 추정.
    """
    env_name = env()
    if env_name in ("paper", "prod"):
        try:
            _, broker, _, _ = _ctx()
            # KisClient에 account_summary() 메서드가 있으면 사용
            if hasattr(broker, "get_account_summary"):
                return broker.get_account_summary()
        except Exception:  # noqa: BLE001
            pass
    # mock/폴백: holdings_df 기반 추정
    df = holdings_df()
    market_val = float(df["평가금액"].sum()) if not df.empty else 0.0
    return {
        "scts_evlu_amt": market_val,    # 유가증권 평가금액
        "dnca_tot_amt": 0.0,            # 예수금 (mock에선 불명)
        "tot_evlu_amt": market_val,     # 총평가금액
        "nass_amt": market_val,         # 순자산
        "source": "estimated",
    }


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
    rows = []
    for item in wl:
        try:
            import time
            price = broker.get_current_price(item["symbol"]).price
            rows.append({"symbol": item["symbol"], "name": item.get("name", ""), "price": price})
            time.sleep(0.15)  # 레이트리밋 방지
        except Exception:  # noqa: BLE001
            rows.append({"symbol": item["symbol"], "name": item.get("name", ""), "price": None})
    return pd.DataFrame(rows)


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
    df = holdings_df()
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
    df = holdings_df()
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


def asset_curve(days: int = 90) -> pd.DataFrame:
    """누적 자산 곡선 — execution_logs 기반 일별 누적 손익 + 현재 보유 자산.

    컬럼: date (index), 자산 (float).
    체결 내역이 없으면 현재 보유 평가금액 단일 값으로 반환.
    """
    pnl_df = daily_pnl_series()
    holdings = holdings_df()
    base_value = float(holdings["평가금액"].sum()) if not holdings.empty else 0.0

    if pnl_df.empty:
        import datetime as dt
        today = dt.date.today().isoformat()
        return pd.DataFrame({"자산": [base_value]}, index=[today])

    # 최근 days 일치만
    pnl_df = pnl_df.tail(days).copy()
    pnl_df["cumulative_pnl"] = pnl_df["pnl"].cumsum()
    pnl_df["자산"] = base_value + pnl_df["cumulative_pnl"] - pnl_df["cumulative_pnl"].iloc[-1]
    pnl_df.index = pnl_df["date"]
    return pnl_df[["자산"]]
