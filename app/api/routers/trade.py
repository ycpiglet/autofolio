"""Trade router — /api/trade/* (read-only in Phase 1+2).

Endpoints (all require_session):
  GET /trade/fills/recent?limit=10
  GET /trade/conditions
  GET /trade/orders?limit=200

SAFETY: No POST /trade/orders or any direct order endpoint is defined here.
        All order execution goes through run-once → OrderFlow → SafetyChecker.
"""
from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query

from app.api.deps import require_session
from app.api.schemas import TableResponse
from app.api.serializers import df_records

router = APIRouter(prefix="/trade", tags=["trade"])


@router.get("/fills/recent", response_model=TableResponse)
def recent_fills(
    _session: Annotated[dict[str, Any], Depends(require_session)],
    limit: int = Query(default=10, ge=1, le=200),
) -> TableResponse:
    from app.ui import backend

    return df_records(backend.recent_fills(limit))


@router.get("/conditions", response_model=TableResponse)
def conditions(
    _session: Annotated[dict[str, Any], Depends(require_session)],
) -> TableResponse:
    from app.ui import backend

    return df_records(backend.list_conditions())


@router.get("/orders", response_model=TableResponse)
def orders(
    _session: Annotated[dict[str, Any], Depends(require_session)],
    limit: int = Query(default=200, ge=1, le=1000),
) -> TableResponse:
    from app.ui import backend

    return df_records(backend.list_order_logs(limit))
