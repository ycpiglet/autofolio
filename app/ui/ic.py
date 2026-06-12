"""투자위원회(IC) 워크플로 shim — app.services.agents 의 re-export (Phase 0 마이그레이션).

구현은 app/services/agents.py 에 있다.
"""
from __future__ import annotations
from app.services.agents import (  # noqa: F401
    DEFAULT_PANEL, extract_condition_from_ic, list_decisions, run_ic,
)

__all__ = ["DEFAULT_PANEL", "extract_condition_from_ic", "list_decisions", "run_ic"]
