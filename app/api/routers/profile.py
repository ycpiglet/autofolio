"""Investor profile router — /api/profile/*."""
from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import require_owner_csrf, require_session
from app.api.schemas import (
    InvestorProfileResponse,
    OverrideAckRequest,
    OverrideAckResponse,
    ProfileCheckinRequest,
    ProfileCheckinResponse,
    SurveyDefinitionResponse,
    SurveySubmitRequest,
    SurveySubmitResponse,
)
from app.services import investor_profile as profiles

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/investor", response_model=InvestorProfileResponse)
def investor_profile(
    session: Annotated[dict[str, Any], Depends(require_session)],
) -> InvestorProfileResponse:
    """Return the current user's personalization profile."""
    username = profiles.username_from_session(session)
    return InvestorProfileResponse(**profiles.get_profile(username))


@router.get("/survey", response_model=SurveyDefinitionResponse)
def survey_definition(
    _session: Annotated[dict[str, Any], Depends(require_session)],
) -> SurveyDefinitionResponse:
    """Return the current onboarding survey definition."""
    return SurveyDefinitionResponse(**profiles.survey_definition())


@router.post("/survey", response_model=SurveySubmitResponse)
def submit_survey(
    body: SurveySubmitRequest,
    session: Annotated[dict[str, Any], Depends(require_owner_csrf)],
) -> SurveySubmitResponse:
    """Store survey answers and update the user's active investor profile."""
    username = profiles.username_from_session(session)
    try:
        profile = profiles.submit_survey(username, body.answers)
    except profiles.SurveyValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return SurveySubmitResponse(status="saved", profile=InvestorProfileResponse(**profile))


@router.post("/override-ack", response_model=OverrideAckResponse)
def override_acknowledgement(
    body: OverrideAckRequest,
    session: Annotated[dict[str, Any], Depends(require_owner_csrf)],
) -> OverrideAckResponse:
    """Record an explicit user acknowledgement for a profile/risk mismatch."""
    username = profiles.username_from_session(session)
    result = profiles.record_override_acknowledgement(
        username,
        action=body.action,
        reason=body.reason,
        acknowledgement_text=body.acknowledgement_text,
        symbol=body.symbol,
    )
    return OverrideAckResponse(**result)


@router.post("/checkin", response_model=ProfileCheckinResponse)
def profile_checkin(
    body: ProfileCheckinRequest,
    session: Annotated[dict[str, Any], Depends(require_owner_csrf)],
) -> ProfileCheckinResponse:
    """Store a monthly/event satisfaction check-in."""
    username = profiles.username_from_session(session)
    try:
        result = profiles.record_checkin(
            username,
            trigger_type=body.trigger_type,
            satisfaction_score=body.satisfaction_score,
            confidence_score=body.confidence_score,
            stress_score=body.stress_score,
            automation_adjustment=body.automation_adjustment,
            notes=body.notes,
        )
    except profiles.SurveyValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail={"status": "profile_required", "message": str(exc)},
        ) from exc
    return ProfileCheckinResponse(**result)
