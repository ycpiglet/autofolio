"""Portfolio router — /api/portfolio/*

Endpoints (all require_session):
  GET /portfolio/holdings
  GET /portfolio/kpis
  GET /portfolio/asset-curve?days=90
  GET /portfolio/allocation-gap
"""
from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query

from app.api.deps import require_session
from app.api.schemas import TableResponse
from app.api.serializers import df_records

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/holdings", response_model=TableResponse)
def holdings(
    _session: Annotated[dict[str, Any], Depends(require_session)],
) -> TableResponse:
    from app.ui import backend

    return df_records(backend.holdings_df())


@router.get("/kpis")
def kpis(
    _session: Annotated[dict[str, Any], Depends(require_session)],
) -> dict[str, Any]:
    from app.ui import backend

    return backend.kpis()


@router.get("/asset-curve", response_model=TableResponse)
def asset_curve(
    _session: Annotated[dict[str, Any], Depends(require_session)],
    days: int = Query(default=90, ge=1, le=3650),
) -> TableResponse:
    from app.ui import backend

    return df_records(backend.asset_curve(days))


@router.get("/allocation-gap", response_model=TableResponse)
def allocation_gap(
    _session: Annotated[dict[str, Any], Depends(require_session)],
) -> TableResponse:
    from app.ui import backend

    return df_records(backend.allocation_gap())
