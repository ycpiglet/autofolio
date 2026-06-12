"""에이전트 런타임 shim — app.services.agents 의 re-export (Phase 0 마이그레이션).

구현은 app/services/agents.py 에 있다.
"""
from __future__ import annotations
from app.services.agents import (  # noqa: F401
    MODEL, EFFORT,
    ask, available, list_agents,
)

__all__ = ["MODEL", "EFFORT", "ask", "available", "list_agents"]
