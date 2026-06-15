"""Settings router — /api/settings/*

Phase 3 state-changing endpoints (all require_owner_csrf):
  PUT /settings/risk-limits  — persist max_order_amount / max_daily_amount to DB
"""
from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.api.deps import require_owner_csrf
from app.api.schemas import RiskLimitsRequest, RiskLimitsResponse

router = APIRouter(prefix="/settings", tags=["settings"])


@router.put("/risk-limits", response_model=RiskLimitsResponse)
def risk_limits(
    body: RiskLimitsRequest,
    _session: Annotated[dict[str, Any], Depends(require_owner_csrf)],
) -> RiskLimitsResponse:
    """Persist risk limits to DB (SafetyChecker picks them up on next run)."""
    from app.ui import backend

    backend.set_risk_limits(
        max_order_amount=body.max_order_amount,
        max_daily_amount=body.max_daily_amount,
    )
    return RiskLimitsResponse(status="saved")
