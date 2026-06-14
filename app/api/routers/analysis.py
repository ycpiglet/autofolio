"""Analysis router — /api/analysis/*

Endpoints (all require_session; guest allowed):
  GET /analysis/attribution
  GET /analysis/retro
  GET /analysis/daily-pnl

SAFETY: READ-ONLY. No state-changing endpoint is defined here.
        Errors propagate as non-200 responses (fail-loud, no silent empty 200).
"""
from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.api.deps import require_session
from app.api.schemas import TableResponse
from app.api.serializers import df_records

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/attribution", response_model=TableResponse)
def attribution(
    _session: Annotated[dict[str, Any], Depends(require_session)],
) -> TableResponse:
    from app.ui import backend

    return df_records(backend.attribution_df())


@router.get("/retro")
def retro(
    _session: Annotated[dict[str, Any], Depends(require_session)],
) -> dict[str, Any]:
    from app.ui import backend

    return backend.retro_metrics()


@router.get("/daily-pnl", response_model=TableResponse)
def daily_pnl(
    _session: Annotated[dict[str, Any], Depends(require_session)],
) -> TableResponse:
    from app.ui import backend

    return df_records(backend.daily_pnl_series())
