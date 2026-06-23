"""Stream router — /api/stream/*

Endpoints:
  GET /stream/events (require_app_user) → SSE: new events.jsonl lines + demo ticker

SSE event types:
  engine  — new lines from logs/events.jsonl
  price   — periodic mock price (demo ticker, every 5 s)

Daemon-safety: StreamingResponse generator lives ONLY while the HTTP connection is
open. Disconnect detected via `await request.is_disconnected()`. No background
thread or daemon is started.

KIS WebSocket: OFF by default. To enable, set opt_in_kis_ws=true as a query
parameter AND ensure AUTOFOLIO_KIS_WS_ENABLE=1 in the environment. Even then,
the WS connection is per-request and torn down on disconnect. This stub is not
wired to real KIS WS in Phase 4 — it is a documented extension point only.
"""
from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Annotated, Any, AsyncGenerator

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse

from app.api.deps import require_app_user

router = APIRouter(prefix="/stream", tags=["stream"])

_EVENTS_JSONL = Path(__file__).resolve().parents[3] / "logs" / "events.jsonl"
_DEMO_TICKER_INTERVAL = 5.0  # seconds between demo price events
_TAIL_POLL_INTERVAL = 0.5    # seconds between log file polls
_MAX_EVENTS: int | None = None  # None = infinite (production); set to N in tests to auto-terminate


@router.get("/events")
async def stream_events(
    request: Request,
    _session: Annotated[dict[str, Any], Depends(require_app_user)],
    opt_in_kis_ws: bool = Query(default=False),
) -> StreamingResponse:
    """SSE stream: new events.jsonl entries + periodic demo ticker.

    opt_in_kis_ws: reserved for future KIS WebSocket integration (not active in Phase 4).
    """
    # Record the file size at connect time so we only tail NEW content.
    try:
        start_offset = _EVENTS_JSONL.stat().st_size if _EVENTS_JSONL.exists() else 0
    except OSError:
        start_offset = 0

    async def _generate() -> AsyncGenerator[str, None]:
        last_tick = time.monotonic()
        offset = start_offset
        events_emitted = 0
        try:
            while True:
                if await request.is_disconnected():
                    break

                # --- Tail events.jsonl for new lines ---
                if _EVENTS_JSONL.exists():
                    try:
                        current_size = _EVENTS_JSONL.stat().st_size
                    except OSError:
                        current_size = offset

                    if current_size > offset:
                        try:
                            with _EVENTS_JSONL.open("r", encoding="utf-8") as fh:
                                fh.seek(offset)
                                new_content = fh.read(current_size - offset)
                            offset = current_size
                            for raw_line in new_content.splitlines():
                                raw_line = raw_line.strip()
                                if not raw_line:
                                    continue
                                try:
                                    payload = json.loads(raw_line)
                                except json.JSONDecodeError:
                                    payload = {"raw": raw_line}
                                yield f"event: engine\ndata: {json.dumps(payload)}\n\n"
                                events_emitted += 1
                                if _MAX_EVENTS is not None and events_emitted >= _MAX_EVENTS:
                                    return
                        except OSError:
                            pass

                # --- Demo ticker: mock price event every _DEMO_TICKER_INTERVAL s ---
                now = time.monotonic()
                if now - last_tick >= _DEMO_TICKER_INTERVAL:
                    last_tick = now
                    mock_price = {
                        "event": "price",
                        "symbol": "005930",
                        "price": 75000,
                        "source": "demo",
                    }
                    yield f"event: price\ndata: {json.dumps(mock_price)}\n\n"
                    events_emitted += 1
                    if _MAX_EVENTS is not None and events_emitted >= _MAX_EVENTS:
                        return

                await asyncio.sleep(_TAIL_POLL_INTERVAL)
        finally:
            pass  # No daemon/WS to clean up

    return StreamingResponse(
        _generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
