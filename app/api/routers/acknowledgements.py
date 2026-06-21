"""Risk acknowledgement API."""
from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import require_app_user, require_app_user_csrf
from app.api.schemas import (
    AcknowledgementRequest,
    AcknowledgementResponse,
    AcknowledgementStatusResponse,
)
from app.services.investor_profile import username_from_session

router = APIRouter(prefix="/acknowledgements", tags=["acknowledgements"])


@router.get("/status", response_model=AcknowledgementStatusResponse)
def status_view(
    session: Annotated[dict[str, Any], Depends(require_app_user)],
) -> AcknowledgementStatusResponse:
    from app.services.acknowledgements import acknowledgement_status

    return AcknowledgementStatusResponse(**acknowledgement_status(username_from_session(session)))


@router.post("", response_model=AcknowledgementResponse)
def create_acknowledgement(
    body: AcknowledgementRequest,
    session: Annotated[dict[str, Any], Depends(require_app_user_csrf)],
) -> AcknowledgementResponse:
    from app.services.acknowledgements import record_acknowledgement
    from app.services.auth_service import verify_password

    username = username_from_session(session)
    method = "session_ack"
    metadata: dict[str, Any] = {"totp_recommended": True, "totp_enabled": False}

    if body.current_password:
        ok, message = verify_password(username, body.current_password)
        if not ok:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message)
        method = "password_reauth"
        metadata["reauthenticated"] = True
    else:
        metadata["reauthenticated"] = False

    try:
        ack = record_acknowledgement(
            username=username,
            kind=body.kind,
            document_slug=body.document_slug,
            document_version=body.document_version,
            acknowledgement_text=body.acknowledgement_text,
            method=method,
            metadata=metadata,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    return AcknowledgementResponse(
        id=ack["id"],
        status="recorded",
        method=ack["method"],
        created_at=ack["created_at"],
    )
