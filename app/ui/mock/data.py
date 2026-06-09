"""Mock 데이터 레이어 (P1.0a).

UI를 백엔드와 분리해 독립 구현하기 위한 가짜 데이터.
P1.1에서 이 모듈을 실제 어댑터(KIS·DB·agents)로 교체하면 UI는 그대로 동작한다.
모든 함수는 결정적(seed 고정)이며 KRW 기준으로 평가금액을 환산한다.
"""
from __future__ import annotations

import datetime as dt

import numpy as np
import pandas as pd
import streamlit as st

USD_KRW = 1380.0
_CASH = 2_300_000.0

# (종목, 티커, 자산군, 지역, 수량, 평단, 현재가[현지통화])
_HOLDINGS = [
    ("삼성전자", "005930", "주식", "KR", 30, 71_000, 74_300),
    ("SK하이닉스", "000660", "주식", "KR", 5, 178_000, 195_000),
    ("KODEX 200", "069500", "ETF", "KR", 40, 36_500, 37_800),
    ("TIGER 미국S&P500", "360750", "ETF", "KR(미국)", 60, 17_800, 19_250),
    ("KODEX 국고채10년", "152380", "채권", "KR", 50, 52_000, 51_200),
    ("ACE KRX금현물", "411060", "원자재", "KR", 35, 13_800, 15_100),
    ("Apple", "AAPL", "주식", "US", 8, 205.0, 228.5),
    ("Vanguard S&P500", "VOO", "ETF", "US", 3, 480.0, 521.0),
]

_TARGET_ALLOC = {"주식": 35, "ETF": 30, "채권": 15, "원자재": 5, "현금": 15}


def cash_balance() -> float:
    return _CASH


@st.cache_data
def holdings_df() -> pd.DataFrame:
    rows = []
    for name, ticker, cls, region, qty, avg, cur in _HOLDINGS:
        fx = USD_KRW if region == "US" else 1.0
        market = qty * cur * fx
        cost = qty * avg * fx
        rows.append(
            {
                "종목": name,
                "티커": ticker,
                "자산군": cls,
                "지역": region,
                "수량": qty,
                "평단": avg,
                "현재가": cur,
                "평가금액": round(market),
                "평가손익": round(market - cost),
                "손익률": round((cur / avg - 1) * 100, 1),
            }
        )
    df = pd.DataFrame(rows)
    total = df["평가금액"].sum() + cash_balance()
    df["비중"] = (df["평가금액"] / total * 100).round(1)
    return df


def total_assets() -> float:
    return float(holdings_df()["평가금액"].sum() + cash_balance())


@st.cache_data
def kpis() -> dict:
    df = holdings_df()
    total = total_assets()
    return {
        "총자산": total,
        "일손익률": 0.82,
        "누적손익률": 11.4,
        "현금비중": cash_balance() / total * 100,
        "평가손익": float(df["평가손익"].sum()),
    }


@st.cache_data
def asset_curve(days: int = 90) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    steps = rng.normal(0.0009, 0.011, days)
    series = np.cumprod(1 + steps)
    series = series * (total_assets() / series[-1])  # 끝값을 현재 총자산에 맞춤
    idx = pd.date_range(end=dt.date.today(), periods=days)
    return pd.DataFrame({"자산": series.round()}, index=idx)


@st.cache_data
def allocation_df() -> pd.DataFrame:
    df = holdings_df().groupby("자산군")["평가금액"].sum().reset_index()
    df = pd.concat(
        [df, pd.DataFrame([{"자산군": "현금", "평가금액": cash_balance()}])],
        ignore_index=True,
    )
    df["비중"] = (df["평가금액"] / df["평가금액"].sum() * 100).round(1)
    return df


@st.cache_data
def allocation_gap() -> pd.DataFrame:
    current = allocation_df().set_index("자산군")["비중"].to_dict()
    rows = []
    for cls, target in _TARGET_ALLOC.items():
        cur = round(current.get(cls, 0.0), 1)
        rows.append({"자산군": cls, "목표%": target, "현재%": cur, "갭%": round(cur - target, 1)})
    return pd.DataFrame(rows)


@st.cache_data
def proposals() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"id": "P-101", "종목": "TIGER 미국S&P500", "방향": "매수", "목표가": 18_900, "수량": 20,
             "에이전트": "kr-etf-specialist", "확신도": "중", "근거": "분할매수 2차, 환율 부담 분산"},
            {"id": "P-102", "종목": "삼성전자", "방향": "매수", "목표가": 72_000, "수량": 10,
             "에이전트": "kr-equity-specialist", "확신도": "상", "근거": "반도체 업황 반등 + 밸류업 기대"},
            {"id": "P-103", "종목": "KODEX 국고채10년", "방향": "매수", "목표가": 51_000, "수량": 30,
             "에이전트": "kr-fixed-income-specialist", "확신도": "중", "근거": "인하 사이클 듀레이션 확대"},
        ]
    )


@st.cache_data
def recent_fills() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"시각": "09:12", "종목": "삼성전자", "방향": "매수", "수량": 10, "체결가": 71_800},
            {"시각": "10:35", "종목": "ACE KRX금현물", "방향": "매수", "수량": 15, "체결가": 15_050},
            {"시각": "13:02", "종목": "KODEX 200", "방향": "매도", "수량": 10, "체결가": 37_950},
        ]
    )


@st.cache_data
def open_orders() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"종목": "삼성전자", "방향": "매수", "유형": "지정가", "수량": 10, "지정가": 72_000, "상태": "미체결"},
            {"종목": "TIGER 미국S&P500", "방향": "매수", "유형": "지정가", "수량": 20, "지정가": 18_900, "상태": "미체결"},
        ]
    )


@st.cache_data
def history_df() -> pd.DataFrame:
    rng = np.random.default_rng(11)
    names = ["삼성전자", "KODEX 200", "TIGER 미국S&P500", "ACE KRX금현물", "SK하이닉스"]
    base = {"삼성전자": 72_000, "KODEX 200": 37_000, "TIGER 미국S&P500": 18_500,
            "ACE KRX금현물": 14_500, "SK하이닉스": 185_000}
    rows = []
    today = dt.date.today()
    for i in range(14):
        name = names[int(rng.integers(0, len(names)))]
        side = "매수" if rng.random() > 0.4 else "매도"
        qty = int(rng.integers(1, 20))
        price = int(base[name] * (1 + rng.normal(0, 0.02)))
        amount = qty * price
        fee = round(amount * 0.00015)
        tax = round(amount * 0.0018) if side == "매도" else 0
        rows.append(
            {"날짜": str(today - dt.timedelta(days=int(rng.integers(0, 30)))),
             "종목": name, "구분": side, "수량": qty, "체결가": price,
             "거래금액": amount, "수수료": fee, "세금": tax}
        )
    return pd.DataFrame(rows).sort_values("날짜", ascending=False).reset_index(drop=True)


@st.cache_data
def pnl_daily() -> pd.DataFrame:
    rng = np.random.default_rng(5)
    idx = pd.date_range(end=dt.date.today(), periods=20)
    pnl = rng.normal(15_000, 90_000, len(idx)).round()
    return pd.DataFrame({"날짜": [d.strftime("%m-%d") for d in idx], "손익": pnl})


@st.cache_data
def dividends() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"지급일": "2026-05-15", "종목": "삼성전자", "배당금": 10_830, "세후": 9_162},
            {"지급일": "2026-04-30", "종목": "KODEX 200", "배당금": 4_200, "세후": 3_553},
            {"지급일": "2026-03-20", "종목": "Vanguard S&P500", "배당금": 6_120, "세후": 5_202},
        ]
    )


@st.cache_data
def watchlist() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"종목": "삼성전자", "현재가": 74_300, "등락률": 1.78},
            {"종목": "NAVER", "현재가": 168_500, "등락률": -0.65},
            {"종목": "TIGER 2차전지소재", "현재가": 12_450, "등락률": 2.40},
            {"종목": "KODEX 인버스", "현재가": 4_120, "등락률": -1.10},
            {"종목": "Apple", "현재가": 228.5, "등락률": 0.90},
        ]
    )


@st.cache_data
def alerts_feed() -> list[dict]:
    return [
        {"t": "13:02", "유형": "체결", "msg": "KODEX 200 10주 매도 체결 @37,950", "level": "info"},
        {"t": "11:20", "유형": "가격", "msg": "삼성전자 목표가 72,000 근접 (현재 74,300)", "level": "info"},
        {"t": "10:35", "유형": "체결", "msg": "ACE KRX금현물 15주 매수 체결 @15,050", "level": "info"},
        {"t": "09:30", "유형": "리스크", "msg": "미국 노출 28% — 통화 리스크 점검 권고", "level": "warn"},
        {"t": "09:05", "유형": "시스템", "msg": "장 시작. 자동매매 OFF(L1) 상태", "level": "info"},
    ]


@st.cache_data
def connections() -> dict:
    return {
        "sso": [
            {"provider": "Google", "status": "연결", "detail": "ycpiglet@gmail.com"},
            {"provider": "Kakao", "status": "미연결", "detail": ""},
            {"provider": "Naver", "status": "미연결", "detail": ""},
        ],
        "channels": [
            {"채널": "Telegram", "status": "연결", "detail": "@autofolio_bot"},
            {"채널": "KakaoTalk(나에게)", "status": "미연결", "detail": ""},
            {"채널": "Notion", "status": "연결", "detail": "Autofolio Journal DB"},
            {"채널": "Discord", "status": "미연결", "detail": ""},
            {"채널": "Email", "status": "연결", "detail": "ycpiglet@gmail.com"},
        ],
        "brokers": [
            {"별칭": "내 KIS(실전)", "증권사": "한국투자증권", "환경": "실전", "상태": "연동", "기본": True},
            {"별칭": "모의계좌", "증권사": "한국투자증권", "환경": "모의", "상태": "연동", "기본": False},
        ],
    }


@st.cache_data
def agents_tree() -> dict:
    return {
        "개발팀 · 리더십": ["ceo", "owner", "managing-partner", "lead-engineer"],
        "개발팀 · 엔지니어링": ["backend-engineer", "cicd-engineer", "uiux-designer", "kis-api-engineer"],
        "개발팀 · 품질": ["qa", "beta-tester", "independent-auditor"],
        "개발팀 · 지원/프로세스": ["requirements-interviewer", "research-agent", "doc-steward", "scribe", "secretary", "timeline-agent"],
        "자산팀 · Leadership": ["cio", "portfolio-manager", "macro-strategist", "risk-manager"],
        "자산팀 · Korea Desk": ["kr-equity-specialist", "kr-etf-specialist", "kr-fund-specialist", "kr-fixed-income-specialist"],
        "자산팀 · US Desk": ["us-equity-specialist", "us-etf-specialist", "us-fixed-income-specialist"],
        "자산팀 · Global Desk": ["commodities-specialist", "futures-specialist", "options-specialist", "fx-specialist"],
        "퀀트팀 (설계)": ["quant-researcher", "backtest-engineer", "data-engineer", "optimization-quant"],
        "거버넌스 (설계)": ["devils-advocate", "performance-analyst", "execution-trader", "compliance-officer"],
    }


def symbol_options() -> list[str]:
    return [f"{r['종목']} ({r['티커']})" for _, r in holdings_df().iterrows()]


# --- 분석 탭 ---
@st.cache_data
def backtest_curve(days: int = 120) -> pd.DataFrame:
    rng = np.random.default_rng(3)
    strat = np.cumprod(1 + rng.normal(0.0011, 0.010, days))
    bench = np.cumprod(1 + rng.normal(0.0007, 0.011, days))
    idx = pd.date_range(end=dt.date.today(), periods=days)
    return pd.DataFrame({"전략": (strat * 100).round(1), "벤치마크(KOSPI)": (bench * 100).round(1)}, index=idx)


@st.cache_data
def attribution() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"구분": "국내주식", "기여(만원)": 48},
            {"구분": "미국ETF", "기여(만원)": 71},
            {"구분": "원자재(금)", "기여(만원)": 33},
            {"구분": "채권", "기여(만원)": -6},
            {"구분": "현금/기타", "기여(만원)": 2},
        ]
    )


@st.cache_data
def retro_metrics() -> dict:
    return {"승률": 58, "평균R": 1.4, "MDD": -9.2, "규율": 82}


@st.cache_data
def scenarios() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"시나리오": "Base", "가정": "금리 동결·완만 성장", "포트폴리오 영향": "+3 ~ +6%", "확률": "50%"},
            {"시나리오": "Bull", "가정": "인하 + 반도체 업턴", "포트폴리오 영향": "+10 ~ +15%", "확률": "25%"},
            {"시나리오": "Bear", "가정": "침체 + 위험회피", "포트폴리오 영향": "-12 ~ -20%", "확률": "25%"},
        ]
    )
