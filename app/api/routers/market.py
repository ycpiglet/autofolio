"""Market router — /api/market/*

Endpoints (all require_session):
  GET /market/indices
  GET /market/watchlist
  GET /market/price?symbol=
  GET /market/fundamental?symbol=
  GET /market/order-book?symbol=&market=J
  GET /market/intraday?symbol=&time_unit=1&count=120
  GET /market/sectors
  GET /market/disclosures?symbol=&days=1
"""
from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import require_session
from app.api.schemas import TableResponse
from app.api.serializers import df_records

router = APIRouter(prefix="/market", tags=["market"])

_SYMBOL_MAX_LEN = 20


def _validate_symbol(symbol: str) -> str:
    s = symbol.strip()
    if not s or len(s) > _SYMBOL_MAX_LEN or not s.replace(".", "").isalnum():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid symbol: {symbol!r}",
        )
    return s


@router.get("/indices", response_model=TableResponse)
def indices(
    _session: Annotated[dict[str, Any], Depends(require_session)],
) -> TableResponse:
    from app.ui import backend

    return df_records(backend.market_indices_df())


@router.get("/watchlist", response_model=TableResponse)
def watchlist(
    _session: Annotated[dict[str, Any], Depends(require_session)],
) -> TableResponse:
    from app.ui import backend

    return df_records(backend.watchlist())


@router.get("/price")
def price(
    _session: Annotated[dict[str, Any], Depends(require_session)],
    symbol: str = Query(..., description="종목 코드"),
) -> dict[str, Any]:
    from app.ui import backend

    sym = _validate_symbol(symbol)
    p = backend.price(sym)
    return {"symbol": sym, "price": p}


@router.get("/fundamental")
def fundamental(
    _session: Annotated[dict[str, Any], Depends(require_session)],
    symbol: str = Query(..., description="종목 코드"),
) -> dict[str, Any]:
    from app.ui import backend

    sym = _validate_symbol(symbol)
    return backend.fundamental(sym)


@router.get("/order-book", response_model=TableResponse)
def order_book(
    _session: Annotated[dict[str, Any], Depends(require_session)],
    symbol: str = Query(..., description="종목 코드"),
    market: str = Query(default="J", description="시장 구분 (J=KRX)"),
) -> TableResponse:
    from app.ui import backend

    sym = _validate_symbol(symbol)
    return df_records(backend.order_book_df(sym, market))


@router.get("/intraday", response_model=TableResponse)
def intraday(
    _session: Annotated[dict[str, Any], Depends(require_session)],
    symbol: str = Query(..., description="종목 코드"),
    time_unit: str = Query(default="1", description="분봉 단위 (1/3/5/10/30/60)"),
    count: int = Query(default=120, ge=1, le=400),
) -> TableResponse:
    from app.ui import backend

    sym = _validate_symbol(symbol)
    return df_records(backend.intraday_chart_df(sym, time_unit=time_unit, count=count))


@router.get("/sectors", response_model=TableResponse)
def sectors(
    _session: Annotated[dict[str, Any], Depends(require_session)],
) -> TableResponse:
    from app.ui import backend

    return df_records(backend.sector_performance_df())


@router.get("/disclosures", response_model=TableResponse)
def disclosures(
    _session: Annotated[dict[str, Any], Depends(require_session)],
    symbol: str = Query(..., description="종목 코드"),
    days: int = Query(default=1, ge=1, le=30),
) -> TableResponse:
    from app.ui import backend

    sym = _validate_symbol(symbol)
    return df_records(backend.disclosures_df(sym, days))
