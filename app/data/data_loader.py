"""데이터 로더 — 시세 이력 조회.

KIS_ENV=paper/prod → KisClient 실데이터.
KIS_ENV=mock       → 빈 DataFrame 반환 (테스트/개발용).
"""
from __future__ import annotations


def load_price_history(symbol: str, period: str = "D", count: int = 100):
    """일봉(D)/주봉(W)/월봉(M) OHLCV DataFrame 반환.

    KIS_ENV=paper/prod → KisClient 실데이터.
    mock → 빈 DataFrame 반환.

    컬럼: date(datetime), open, high, low, close(float), volume(int).
    날짜 오름차순 정렬.
    """
    import pandas as pd
    from app.brokers.factory import create_broker_client
    from app.brokers.kis.kis_client import KisClient

    broker = create_broker_client()
    if not isinstance(broker, KisClient):
        return pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])
    rows = broker.get_price_history(symbol, period=period, count=count)
    if not rows:
        return pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
    return df.sort_values("date").reset_index(drop=True)


def load_intraday_chart(symbol: str, time_unit: str = "1", count: int = 100):
    """당일 분봉 OHLCV DataFrame 반환.

    KIS_ENV=paper/prod → KisClient.get_intraday_chart.
    mock → 빈 DataFrame 반환.

    컬럼: datetime(datetime), open, high, low, close(float), volume(int).
    시간 오름차순 정렬.
    """
    import pandas as pd
    from app.brokers.factory import create_broker_client
    from app.brokers.kis.kis_client import KisClient

    columns = ["datetime", "open", "high", "low", "close", "volume"]
    broker = create_broker_client()
    if not isinstance(broker, KisClient):
        return pd.DataFrame(columns=columns)
    rows = broker.get_intraday_chart(symbol, time_unit=time_unit, count=count)
    if not rows:
        return pd.DataFrame(columns=columns)
    df = pd.DataFrame(rows, columns=columns)
    df["datetime"] = pd.to_datetime(df["datetime"], format="%Y%m%d %H%M%S")
    return df.sort_values("datetime").reset_index(drop=True)
