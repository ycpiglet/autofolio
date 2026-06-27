"""FastAPI application factory — Autofolio API (Phase 1+3).

Usage:
  uvicorn app.api.main:create_app --factory --host 127.0.0.1 --port 8000 --reload
  (or via scripts/run_api.py)

SAFETY invariants enforced here:
  1. No POST /trade/orders or any direct-order endpoint.
  2. State-changing app-control paths require require_owner_csrf (owner role + CSRF token).
     Approved member self-service paths use require_app_user_csrf and must derive
     their target from the session.
     Public membership request intake is the only local prototype exception and
     cannot create a session or active account.
  3. KIS keys and user-owned integration tokens are never serialized in any response.
  4. Server binds 127.0.0.1 only (see run script).
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

_logger = logging.getLogger(__name__)

from app.api.routers import (
    account,
    agents,
    analysis,
    acknowledgements,
    auth,
    engine,
    finance_roadmap,
    integrations,
    market,
    manuals,
    membership,
    portfolio,
    profile,
    settings,
    stream,
    trade,
)
from app.api.schemas import HealthResponse


@asynccontextmanager
async def _lifespan(app: FastAPI):  # noqa: ARG001
    try:
        from app.services.backend import _ctx
        _ctx()
        _logger.info("backend _ctx warmed up at startup")
    except Exception:
        _logger.warning("backend _ctx warm-up failed; lazy init will retry on first request", exc_info=True)
    yield


def create_app() -> FastAPI:
    """Application factory consumed by uvicorn --factory."""
    # SECURITY: install the root-logger redaction filter as early as possible so
    # any credential-shaped value is scrubbed from logs (defence-in-depth).
    from app.observability.redaction import install_redaction_filter

    install_redaction_filter()

    app = FastAPI(
        title="Autofolio API",
        version="1.0.0",
        description="FastAPI backend for Autofolio Next.js UI (Phase 1 — read-only + auth).",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=_lifespan,
    )

    # Health — no auth required
    @app.get("/api/health", response_model=HealthResponse, tags=["health"])
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    # Routers — all under /api prefix
    app.include_router(auth.router, prefix="/api")
    app.include_router(account.router, prefix="/api")
    app.include_router(manuals.router, prefix="/api")
    app.include_router(acknowledgements.router, prefix="/api")
    app.include_router(membership.router, prefix="/api")
    app.include_router(integrations.router, prefix="/api")
    app.include_router(engine.router, prefix="/api")
    app.include_router(portfolio.router, prefix="/api")
    app.include_router(profile.router, prefix="/api")
    app.include_router(market.router, prefix="/api")
    app.include_router(trade.router, prefix="/api")
    app.include_router(settings.router, prefix="/api")
    app.include_router(analysis.router, prefix="/api")
    app.include_router(finance_roadmap.router, prefix="/api")
    app.include_router(agents.router, prefix="/api")
    app.include_router(stream.router, prefix="/api")

    return app
