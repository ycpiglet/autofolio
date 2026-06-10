"""퀀트 데이터 로더 — KIS 시세 이력 캐시 (일봉·point-in-time). [Autofolio]

설계 원칙 (look-ahead bias 방어):
- 백테스트에 사용하는 데이터는 해당 날짜에 *실제로 알 수 있었던* 값만 사용.
- 일봉 OHLCV를 SQLite에 캐시. 실시간 API 호출 최소화.
- point-in-time: 특정 날짜 이후 데이터는 제공하지 않는다.

KIS API: 국내주식 일자별 주가 조회 (FHKST01010400)
"""
from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from pathlib import Path
from typing import Sequence

from app.config.settings import settings


def _price_cache_db() -> Path:
    return Path(settings.db_path).parent / "price_cache.db"


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS daily_price (
            symbol TEXT NOT NULL,
            date   TEXT NOT NULL,
            open   REAL,
            high   REAL,
            low    REAL,
            close  REAL NOT NULL,
            volume INTEGER,
            PRIMARY KEY (symbol, date)
        )
    """)
    conn.commit()


def load_prices(
    symbol: str,
    start: date,
    end: date,
    *,
    as_of: date | None = None,  # point-in-time cutoff
) -> list[dict]:
    """symbol의 [start, end] 일봉을 반환. as_of 이후 데이터는 제거(look-ahead 방어)."""
    cutoff = min(end, as_of or end)
    path = _price_cache_db()
    with sqlite3.connect(path) as conn:
        conn.row_factory = sqlite3.Row
        _ensure_schema(conn)
        rows = conn.execute(
            "SELECT * FROM daily_price WHERE symbol=? AND date>=? AND date<=? ORDER BY date",
            (symbol, start.isoformat(), cutoff.isoformat()),
        ).fetchall()
    return [dict(r) for r in rows]


def cache_prices(symbol: str, rows: list[dict]) -> int:
    """일봉 데이터를 SQLite 캐시에 upsert. rows: [{date, open, high, low, close, volume}]."""
    path = _price_cache_db()
    with sqlite3.connect(path) as conn:
        _ensure_schema(conn)
        conn.executemany(
            """INSERT OR REPLACE INTO daily_price(symbol,date,open,high,low,close,volume)
               VALUES(:symbol,:date,:open,:high,:low,:close,:volume)""",
            [{"symbol": symbol, **r} for r in rows],
        )
        conn.commit()
    return len(rows)


def fetch_and_cache(symbol: str, start: date, end: date) -> int:
    """KIS API로 일봉을 가져와 캐시에 저장. (KIS_ENV=paper/prod 필요)

    KIS TR: FHKST01010400 (국내주식 일자별 주가)
    장중·실시간 아닌 *종가 기반* 이력이라 look-ahead 안전.
    """
    try:
        from app.config.settings import resolve_settings
        from app.brokers.kis.kis_auth import KisAuth
        import requests

        cfg = resolve_settings()
        token = KisAuth(cfg).get_access_token()
        headers = {
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {token}",
            "appkey": cfg.kis_app_key,
            "appsecret": cfg.kis_app_secret,
            "tr_id": "FHKST01010400",
            "custtype": "P",
        }
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": symbol,
            "FID_INPUT_DATE_1": start.strftime("%Y%m%d"),
            "FID_INPUT_DATE_2": end.strftime("%Y%m%d"),
            "FID_PERIOD_DIV_CODE": "D",
            "FID_ORG_ADJ_PRC": "0",
        }
        url = cfg.kis_base_url.rstrip("/") + "/uapi/domestic-stock/v1/quotations/inquire-daily-price"
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        data = resp.json()
        if str(data.get("rt_cd")) != "0":
            return 0
        rows = []
        for r in data.get("output2") or data.get("output", []):
            d = r.get("stck_bsop_date") or r.get("stck_cntg_hour")
            if not d:
                continue
            rows.append({
                "date": f"{d[:4]}-{d[4:6]}-{d[6:8]}",
                "open": float(r.get("stck_oprc") or 0),
                "high": float(r.get("stck_hgpr") or 0),
                "low": float(r.get("stck_lwpr") or 0),
                "close": float(r.get("stck_clpr") or r.get("stck_prpr") or 0),
                "volume": int(r.get("acml_vol") or 0),
            })
        return cache_prices(symbol, rows) if rows else 0
    except Exception:  # noqa: BLE001 — 데이터 없으면 빈 캐시
        return 0
