"""Membership approval API — local prototype for verified signup."""
from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import require_admin, require_admin_csrf
from app.api.schemas import (
    MembershipRequestCreate,
    MembershipRequestListResponse,
    MembershipRequestResponse,
    MembershipTransitionRequest,
    MembershipDepositRecognitionRequest,
    MembershipDepositRecognitionResponse,
    MembershipReadinessResponse,
    MembershipRequestStatusLookup,
)

router = APIRouter(prefix="/membership", tags=["membership"])


@router.get("/readiness", response_model=MembershipReadinessResponse)
def membership_readiness(
    _session: Annotated[dict[str, Any], Depends(require_admin)],
) -> MembershipReadinessResponse:
    """Owner-visible production-readiness checklist for membership launch."""
    from app.services.membership_readiness import readiness

    return MembershipReadinessResponse(**readiness())


@router.post(
    "/requests",
    response_model=MembershipRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_membership_request(body: MembershipRequestCreate) -> MembershipRequestResponse:
    """Create a signup approval request without creating an active account."""
    from app.services.membership import create_request

    try:
        created = create_request(
            display_name=body.display_name,
            contact=body.contact,
            plan=body.plan,
            referral_source=body.referral_source,
            note=body.note,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return MembershipRequestResponse(**created)


@router.post("/requests/status", response_model=MembershipRequestResponse)
def lookup_membership_request_status(
    body: MembershipRequestStatusLookup,
) -> MembershipRequestResponse:
    """Applicant-safe status lookup; requires request id and contact."""
    from app.services.membership import lookup_request_status

    try:
        request = lookup_request_status(body.request_id, body.contact)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="membership request not found")
    return MembershipRequestResponse(**request)


@router.get("/requests", response_model=MembershipRequestListResponse)
def membership_requests(
    _session: Annotated[dict[str, Any], Depends(require_admin)],
    request_status: Annotated[str | None, Query(alias="status")] = None,
) -> MembershipRequestListResponse:
    """List approval requests for Owner review."""
    from app.services.membership import list_requests

    try:
        requests = list_requests(status=request_status)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return MembershipRequestListResponse(requests=[MembershipRequestResponse(**item) for item in requests])


@router.get("/requests/{request_id}", response_model=MembershipRequestResponse)
def membership_request_detail(
    request_id: str,
    _session: Annotated[dict[str, Any], Depends(require_admin)],
) -> MembershipRequestResponse:
    """Read one approval request for Owner review."""
    from app.services.membership import get_request

    request = get_request(request_id)
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="membership request not found")
    return MembershipRequestResponse(**request)


@router.post("/deposits/recognize", response_model=MembershipDepositRecognitionResponse)
def recognize_membership_deposits(
    body: MembershipDepositRecognitionRequest,
    _session: Annotated[dict[str, Any], Depends(require_admin_csrf)],
) -> MembershipDepositRecognitionResponse:
    """Match pasted bank statement text/CSV against deposit-pending requests."""
    from app.services.membership import recognize_deposits

    result = recognize_deposits(
        body.source_text,
        min_confidence=body.min_confidence,
    )
    return MembershipDepositRecognitionResponse(**result)


@router.post("/requests/{request_id}/transition", response_model=MembershipRequestResponse)
def transition_membership_request(
    request_id: str,
    body: MembershipTransitionRequest,
    session: Annotated[dict[str, Any], Depends(require_admin_csrf)],
) -> MembershipRequestResponse:
    """Move a request through verification/deposit/activation states."""
    from app.services.membership import transition_request

    actor = str(session.get("username") or "owner")
    try:
        updated = transition_request(
            request_id,
            next_status=body.status,
            actor=actor,
            evidence_type=body.evidence_type,
            note=body.note,
            grant_days=body.grant_days,
            login_username=body.login_username,
            initial_password=body.initial_password,
        )
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="membership request not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return MembershipRequestResponse(**updated)
