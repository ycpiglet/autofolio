"""Manual asset API — in-app product help and safety content."""
from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import require_app_user
from app.api.schemas import ManualDetail, ManualsListResponse

router = APIRouter(prefix="/manuals", tags=["manuals"])


def _include_private(session: dict[str, Any]) -> bool:
    return session.get("role") == "owner"


@router.get("", response_model=ManualsListResponse)
def manuals(
    session: Annotated[dict[str, Any], Depends(require_app_user)],
) -> ManualsListResponse:
    from app.services.manuals import list_manuals

    return ManualsListResponse(manuals=list_manuals(include_private=_include_private(session)))


@router.get("/{slug}", response_model=ManualDetail)
def manual_detail(
    slug: str,
    session: Annotated[dict[str, Any], Depends(require_app_user)],
) -> ManualDetail:
    from app.services.manuals import get_manual

    try:
        manual = get_manual(slug, include_private=_include_private(session))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="manual not found") from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="manual is owner-only") from exc
    return ManualDetail(**manual)
