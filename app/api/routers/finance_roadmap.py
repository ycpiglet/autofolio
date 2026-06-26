"""Finance Roadmap router — /api/finance-roadmap/*

Endpoints (all require_app_user):
  GET /finance-roadmap/goal-gap

Read-only planning preview. No order, no action, no advice wording.
All candidates are for Owner review only (action_permitted_now=False).
"""
from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.api.deps import require_app_user
from app.services.finance_roadmap import FinanceRoadmapResponse

router = APIRouter(prefix="/finance-roadmap", tags=["finance-roadmap"])


@router.get(
    "/goal-gap",
    response_model=FinanceRoadmapResponse,
    summary="Read-only finance roadmap goal-gap preview",
    description=(
        "Returns planned vs expected, gap, allocation drift, data-quality flags, "
        "and timeline candidates. All candidates are for Owner review only. "
        "No order, no trade instruction, no advice. Preview only."
    ),
)
def goal_gap(
    _session: Annotated[dict[str, Any], Depends(require_app_user)],
) -> FinanceRoadmapResponse:
    """Read-only finance roadmap goal-gap preview.

    Derives: planned vs expected, gap, allocation drift, data-quality flags,
    timeline candidates, review candidates. All marked Owner-review only.
    No order path. No trade instruction. No advice wording.
    """
    from app.services.finance_roadmap import compute_goal_gap, load_contract

    return compute_goal_gap(load_contract())
