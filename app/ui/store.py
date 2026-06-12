"""연동 보관함 — app.services.connections 의 shim (Phase 0 마이그레이션).

이 파일은 기존 뷰 코드가 app.ui.store 로 임포트할 수 있도록 남겨둔 shim이다.
구현은 app/services/connections.py 에 있다.
"""
from __future__ import annotations
from app.services.connections import *  # noqa: F401,F403
from app.services.connections import __all__
