"""app/services/context — _ctx() 싱글턴 + 초기화 락.

app/ui/backend 의 _ctx 와 _ctx_lock 을 재-익스포트한다.
테스트에서 cache_clear() 로 ctx 를 재설정하는 경로는 backend._ctx.cache_clear() 를
통해 계속 동작한다.
"""
from __future__ import annotations

from app.ui.backend import _ctx, _ctx_lock  # noqa: F401
