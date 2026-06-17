"""app/services/context — _ctx() 싱글턴 + 초기화 락.

app/services/backend 의 _ctx 와 _ctx_lock 을 재-익스포트한다.
테스트에서 backend._ctx 를 직접 패치하는 방식을 사용한다(cache_clear() 경로는
backend._ctx.cache_clear() 로 계속 동작).
재-익스포트 특성 주의: runtime에 app.services.backend.X 를 패치해도 이미 바인딩된
app.services.context.X 이름에는 영향을 주지 않는다. 미래 테스트가 services 경로를
직접 대상으로 할 경우 서비스 모듈 자체를 패치해야 한다.
"""
from __future__ import annotations

from app.services.backend import _ctx, _ctx_lock  # noqa: F401

__all__ = ["_ctx", "_ctx_lock"]
