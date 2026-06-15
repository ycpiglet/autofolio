"""Agents router — /api/agents/*

Endpoints:
  GET  /agents/list            (require_session) → available flag + agent names
  POST /agents/ask             (require_owner_csrf) → single-agent Q&A
  POST /agents/ic/run          (require_owner_csrf) → start IC job, return job_id (202)
  GET  /agents/ic/stream/{job_id} (require_session) → SSE progress + done event
  GET  /agents/ic/decisions    (require_session) → list of past decision files

SSE format: "data: <json>\\n\\n" per event.
IC reconnect-replay: on connect, any already-recorded steps are replayed before live streaming.
Daemon-safety: NO global background thread/daemon. Each IC job is an asyncio Task that lives
only as long as the job itself. SSE stream lives only while the HTTP connection is open.
KIS WebSocket: NOT started here — off by default (see stream.py opt-in stub).
"""
from __future__ import annotations

import asyncio
import json
import uuid
from typing import Annotated, Any, AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse

from app.api.deps import require_owner_csrf, require_session
from app.api.schemas import (
    AgentsListResponse,
    AskRequest,
    AskResponse,
    IcRunRequest,
    IcRunResponse,
)

router = APIRouter(prefix="/agents", tags=["agents"])

# ---------------------------------------------------------------------------
# In-memory IC job registry
# Keys: job_id (str UUID)
# Values: {
#   "steps": list[str],       — all progress strings recorded so far
#   "done": bool,             — True once run_ic has returned
#   "result": dict | None,    — the run_ic return value (set when done)
#   "queue": asyncio.Queue,   — live feed for in-progress subscribers
# }
# This dict is intentionally NOT cleaned up automatically — it is small and
# short-lived per session. A production system would add TTL eviction.
# ---------------------------------------------------------------------------
_jobs: dict[str, dict[str, Any]] = {}


# ---------------------------------------------------------------------------
# GET /agents/list
# ---------------------------------------------------------------------------

@router.get("/list", response_model=AgentsListResponse)
def agents_list(
    _session: Annotated[dict[str, Any], Depends(require_session)],
) -> AgentsListResponse:
    """Return available flag, message, and list of agent short names."""
    from app.services.agents import available, list_agents

    ok, msg = available()
    return AgentsListResponse(available=ok, message=msg, agents=list_agents())


# ---------------------------------------------------------------------------
# POST /agents/ask
# ---------------------------------------------------------------------------

@router.post("/ask", response_model=AskResponse)
def agents_ask(
    body: AskRequest,
    _session: Annotated[dict[str, Any], Depends(require_owner_csrf)],
) -> AskResponse:
    """Ask a single agent a question. Owner + CSRF required (blocks cost for guests)."""
    from app.services.agents import ask

    answer = ask(body.agent, body.question, body.context)
    return AskResponse(answer=answer)


# ---------------------------------------------------------------------------
# POST /agents/ic/run
# ---------------------------------------------------------------------------

@router.post("/ic/run", response_model=IcRunResponse, status_code=status.HTTP_202_ACCEPTED)
async def ic_run(
    body: IcRunRequest,
    _session: Annotated[dict[str, Any], Depends(require_owner_csrf)],
) -> IcRunResponse:
    """Start an IC run in the background and return a job_id for SSE tracking.

    The job records each progress step into _jobs[job_id]["steps"] AND pushes
    it into the per-job asyncio.Queue for live SSE subscribers.
    run_ic is a blocking function — run it in a thread-pool executor so the
    event loop is not blocked.
    """
    job_id = str(uuid.uuid4())
    q: asyncio.Queue[str | None] = asyncio.Queue()

    _jobs[job_id] = {
        "steps": [],
        "done": False,
        "result": None,
        "queue": q,
    }

    def _progress(step_info: str) -> None:
        """Called from the run_ic thread. Thread-safe queue put."""
        _jobs[job_id]["steps"].append(step_info)
        # asyncio.Queue.put_nowait is safe to call from any thread.
        q.put_nowait(step_info)

    async def _run() -> None:
        from app.services.agents import run_ic

        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                None,
                lambda: run_ic(body.topic, body.panel, _progress),
            )
            _jobs[job_id]["result"] = result
        except Exception as exc:  # noqa: BLE001
            _jobs[job_id]["result"] = {"error": str(exc)}
        finally:
            _jobs[job_id]["done"] = True
            q.put_nowait(None)  # sentinel: tell SSE stream that job is finished

    asyncio.create_task(_run())
    return IcRunResponse(job_id=job_id)


# ---------------------------------------------------------------------------
# GET /agents/ic/stream/{job_id}
# ---------------------------------------------------------------------------

@router.get("/ic/stream/{job_id}")
async def ic_stream(
    job_id: str,
    request: Request,
    _session: Annotated[dict[str, Any], Depends(require_session)],
) -> StreamingResponse:
    """SSE stream for an IC job.

    Reconnect-replay: replays all steps already recorded before streaming new ones.
    Stops when the job is done OR the client disconnects.
    SSE format: event line + data line per event.
    """
    if job_id not in _jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found",
        )

    async def _generate() -> AsyncGenerator[str, None]:
        job = _jobs[job_id]

        # --- Replay already-recorded steps (reconnect support) ---
        for step in list(job["steps"]):
            yield f"event: step\ndata: {json.dumps({'step': step})}\n\n"

        # --- If already done, emit final event and return ---
        if job["done"]:
            result = job.get("result") or {}
            yield f"event: done\ndata: {json.dumps(result)}\n\n"
            return

        # --- Stream live steps from the queue ---
        q: asyncio.Queue[str | None] = job["queue"]
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    item = await asyncio.wait_for(q.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    # Heartbeat to keep the connection alive and check disconnect
                    yield ": heartbeat\n\n"
                    continue
                if item is None:
                    # Sentinel: job is done
                    result = job.get("result") or {}
                    yield f"event: done\ndata: {json.dumps(result)}\n\n"
                    break
                yield f"event: step\ndata: {json.dumps({'step': item})}\n\n"
        finally:
            pass  # Connection cleanup — no daemon to stop

    return StreamingResponse(
        _generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# GET /agents/ic/decisions
# ---------------------------------------------------------------------------

@router.get("/ic/decisions")
def ic_decisions(
    _session: Annotated[dict[str, Any], Depends(require_session)],
    limit: int = Query(default=10, ge=1, le=100),
) -> list[dict[str, Any]]:
    """Return list of past IC decision files (most recent first)."""
    from app.services.agents import list_decisions

    return list_decisions(limit)
