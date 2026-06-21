"""Approved-user integration settings API."""
from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import require_app_user, require_app_user_csrf
from app.api.schemas import (
    IntegrationCredentialResponse,
    IntegrationCredentialUpsertRequest,
    IntegrationDeleteResponse,
    IntegrationSettingsResponse,
)

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("", response_model=IntegrationSettingsResponse)
def integration_settings(
    session: Annotated[dict[str, Any], Depends(require_app_user)],
) -> IntegrationSettingsResponse:
    """Return the current user's integration catalog and redacted status."""
    from app.services.integrations import list_user_integrations

    try:
        result = list_user_integrations(str(session.get("username") or ""))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    return IntegrationSettingsResponse(**result)


@router.put("/{provider_id}", response_model=IntegrationCredentialResponse)
def upsert_integration(
    provider_id: str,
    body: IntegrationCredentialUpsertRequest,
    session: Annotated[dict[str, Any], Depends(require_app_user_csrf)],
) -> IntegrationCredentialResponse:
    """Create or update one integration for the current user.

    Secret values are accepted only in the request body and are never echoed in
    the response.
    """
    from app.services.integrations import upsert_user_integration

    try:
        result = upsert_user_integration(
            str(session.get("username") or ""),
            provider_id,
            secret_value=body.secret_value,
            account_label=body.account_label,
            scopes=body.scopes,
            enabled=body.enabled,
            note=body.note,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return IntegrationCredentialResponse(**result)


@router.delete("/{provider_id}", response_model=IntegrationDeleteResponse)
def delete_integration(
    provider_id: str,
    session: Annotated[dict[str, Any], Depends(require_app_user_csrf)],
) -> IntegrationDeleteResponse:
    """Delete one integration for the current user."""
    from app.services.integrations import delete_user_integration

    try:
        result = delete_user_integration(str(session.get("username") or ""), provider_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return IntegrationDeleteResponse(
        status="deleted",
        integration=IntegrationCredentialResponse(**result),
    )
