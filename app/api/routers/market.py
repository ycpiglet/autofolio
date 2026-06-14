"""Market router — /api/market/*

Endpoints (all require_session):
  GET /market/indices
  GET /market/watchlist
"""
from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.api.deps import require_session
from app.api.schemas import TableResponse
from app.api.serializers import df_records

router = APIRouter(prefix="/market", tags=["market"])


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
