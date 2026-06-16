"""FastAPI application factory — Autofolio API (Phase 1+3).

Usage:
  uvicorn app.api.main:create_app --factory --host 127.0.0.1 --port 8000 --reload
  (or via scripts/run_api.py)

SAFETY invariants enforced here:
  1. No POST /trade/orders or any direct-order endpoint.
  2. All state-changing paths require require_owner_csrf (owner role + CSRF token).
  3. KIS keys are never serialized in any response.
  4. Server binds 127.0.0.1 only (see run script).
"""
from __future__ import annotations

from fastapi import FastAPI

from app.api.routers import (
    account,
    agents,
    analysis,
    auth,
    engine,
    market,
    portfolio,
    profile,
    settings,
    stream,
    trade,
)
from app.api.schemas import HealthResponse


def create_app() -> FastAPI:
    """Application factory consumed by uvicorn --factory."""
    app = FastAPI(
        title="Autofolio API",
        version="1.0.0",
        description="FastAPI backend for Autofolio Next.js UI (Phase 1 — read-only + auth).",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # Health — no auth required
    @app.get("/api/health", response_model=HealthResponse, tags=["health"])
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    # Routers — all under /api prefix
    app.include_router(auth.router, prefix="/api")
    app.include_router(account.router, prefix="/api")
    app.include_router(engine.router, prefix="/api")
    app.include_router(portfolio.router, prefix="/api")
    app.include_router(profile.router, prefix="/api")
    app.include_router(market.router, prefix="/api")
    app.include_router(trade.router, prefix="/api")
    app.include_router(settings.router, prefix="/api")
    app.include_router(analysis.router, prefix="/api")
    app.include_router(agents.router, prefix="/api")
    app.include_router(stream.router, prefix="/api")

    return app
