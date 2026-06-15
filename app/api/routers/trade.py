"""Trade router — /api/trade/*

Endpoints (all require_session for reads):
  GET  /trade/fills/recent?limit=10
  GET  /trade/conditions
  GET  /trade/orders?limit=200

Phase 3 state-changing (require_owner_csrf):
  POST /trade/conditions  — gate-checked condition save (2-step ack_token)

SAFETY: No POST /trade/orders or any direct order endpoint is defined here.
        All order execution goes through run-once → OrderFlow → SafetyChecker.
"""
from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.api.deps import require_owner_csrf, require_session
from app.api.schemas import (
    ConditionRequest,
    ConditionSavedResponse,
    TableResponse,
)
from app.api.serializers import df_records
from app.api.security import decode_ack_token, encode_ack_token

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


@router.post("/conditions")
def create_condition(
    body: ConditionRequest,
    http_response: Response,
    _session: Annotated[dict[str, Any], Depends(require_owner_csrf)],
) -> Any:
    """Gate-checked condition save.

    Gate mapping (GateResult.status → HTTP):
      saved                  → 201  ConditionSavedResponse
      blocked_disclosure     → 422  {"detail": {"status": ..., "message": ...}}
      rejected               → 422  {"detail": {"status": ..., "message": ...}}
      needs_acknowledgement  → 409  {"detail": {"status": ..., "verdict": ..., "ack_token": ...}}
      error                  → 500  fail-closed

    ack_token 2-step:
      - On needs_acknowledgement, server issues a short-lived itsdangerous-signed
        token binding {symbol, side, target_price, quantity}.
      - Re-submit includes the same body + ack_token. Server verifies the token
        decodes AND its payload exactly matches the current request body.
        Any mismatch/expiry/tamper → treat as caution_acknowledged=False
        (fail-closed, re-runs gate, likely 409 again with a fresh token).
    """
    from app.services.trading import save_condition_with_gates

    # Determine caution_acknowledged from ack_token (fail-closed on any anomaly)
    caution_acknowledged = False
    if body.ack_token:
        decoded = decode_ack_token(body.ack_token)
        if decoded is not None:
            expected = {
                "symbol": body.symbol,
                "side": body.side,
                "target_price": body.target_price,
                "quantity": body.quantity,
            }
            if decoded == expected:
                caution_acknowledged = True
        # Any other case (tampered, expired, mismatched) → stays False

    result = save_condition_with_gates(
        symbol=body.symbol,
        side=body.side,
        target_price=body.target_price,
        qty=body.quantity,
        auto=body.auto,
        caution_acknowledged=caution_acknowledged,
    )

    if result.status == "saved":
        http_response.status_code = status.HTTP_201_CREATED
        return ConditionSavedResponse(
            status="saved",
            message=result.message,
            condition_id=result.condition_id,
        )
    elif result.status in ("blocked_disclosure", "rejected"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"status": result.status, "message": result.message},
        )
    elif result.status == "needs_acknowledgement":
        ack_payload = {
            "symbol": body.symbol,
            "side": body.side,
            "target_price": body.target_price,
            "quantity": body.quantity,
        }
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "status": "needs_acknowledgement",
                "verdict": result.message,
                "ack_token": encode_ack_token(ack_payload),
            },
        )
    else:
        # error or unknown status → fail-closed
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gate error: {result.message}",
        )
