"""Agents router — /api/agents/*

Endpoints:
  GET  /agents/list            (require_app_user) → available flag + agent metadata
  POST /agents/ask             (require_owner_csrf) → single-agent Q&A
  POST /agents/ic/run          (require_owner_csrf) → start IC job, return job_id (202)
  GET  /agents/ic/stream/{job_id} (require_app_user) → SSE progress + done event
  GET  /agents/ic/decisions    (require_app_user) → list of past decision files

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

from app.api.deps import require_app_user, require_owner_csrf
from app.api.schemas import (
    AgentResearchResponse,
    AgentsListResponse,
    AskRequest,
    AskResponse,
    DisclosureGateInfo,
    IcRunRequest,
    IcRunResponse,
    ResearchProposal,
    PremarketSummaryResponse,
)
from app.api.serializers import df_records

router = APIRouter(prefix="/agents", tags=["agents"])

_SYMBOL_MAX_LEN = 20


def _validate_symbol(symbol: str) -> str:
    """Validate a whitelist-style symbol code (mirrors market router)."""
    s = symbol.strip()
    if not s or len(s) > _SYMBOL_MAX_LEN or not s.replace(".", "").isalnum():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid symbol: {symbol!r}",
        )
    return s

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
    _session: Annotated[dict[str, Any], Depends(require_app_user)],
    experts_only: bool = Query(default=False),
) -> AgentsListResponse:
    """Return available flag, message, and public agent metadata."""
    from app.services.agents import available, list_agent_infos

    ok, msg = available()
    return AgentsListResponse(
        available=ok,
        message=msg,
        agents=list_agent_infos(experts_only=experts_only),
    )


# ---------------------------------------------------------------------------
# GET /agents/premarket/summary
# ---------------------------------------------------------------------------

@router.get("/premarket/summary", response_model=PremarketSummaryResponse)
def premarket_summary(
    _session: Annotated[dict[str, Any], Depends(require_app_user)],
    date: str | None = Query(default=None, description="YYYY-MM-DD. Omit for latest saved summary."),
) -> PremarketSummaryResponse:
    """Load a CLI-generated pre-market summary markdown file.

    This endpoint is read-only and never generates summaries itself. Generation
    stays explicit via scripts/run_premarket_summary.py.
    """
    from app.services.premarket_summary import load_summary

    summary = load_summary(date)
    if summary is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No premarket summary file found",
        )
    return PremarketSummaryResponse(**summary)


# ---------------------------------------------------------------------------
# GET /agents/research
# ---------------------------------------------------------------------------

@router.get("/research", response_model=AgentResearchResponse)
def agents_research(
    _session: Annotated[dict[str, Any], Depends(require_app_user)],
    symbol: str = Query(..., description="종목 코드 (화이트리스트)"),
    days: int = Query(default=7, ge=1, le=30, description="공시 조회 기간(일)"),
) -> AgentResearchResponse:
    """Per-symbol expert briefing — READ-ONLY.

    Assembles a briefing from real backend functions: current price, fundamental
    metrics, recent disclosures (+ disclosure gate), and a rule-based proposal.

    READ-ONLY guarantee: backend.propose() only *suggests* a price condition; it
    does NOT create or persist a trade condition. No LLM is called here (cost +
    guest access). Fails loud — any backend error propagates as a non-200.

    Honest gaps: there is NO live-news API (briefing is disclosure-based) and NO
    auto-trigger (this runs only on a manual request).
    """
    from app.services import backend

    sym = _validate_symbol(symbol)

    # Resolve display name from the whitelist (symbol_options is "code · name").
    name = ""
    df = backend.list_whitelist()
    if not df.empty:
        match = df[df["symbol"].astype(str) == sym]
        if not match.empty:
            name = str(match.iloc[0]["name"])

    price = backend.price(sym)
    fundamental = backend.fundamental(sym) or {}
    disclosures = backend.disclosures_df(sym, days)
    gate = backend.disclosure_gate_state(sym)
    # propose() SUGGESTS only — it must NOT save a condition.
    proposal = backend.propose(sym, side="BUY")

    return AgentResearchResponse(
        symbol=sym,
        name=name,
        price=float(price),
        fundamental=fundamental,
        disclosures=df_records(disclosures),
        disclosure_gate=DisclosureGateInfo(
            symbol=str(gate.get("symbol", sym)),
            blocked=bool(gate.get("blocked", False)),
            reason=str(gate.get("reason", "")),
        ),
        proposal=ResearchProposal(
            symbol=proposal.symbol,
            side=proposal.side,
            target_price=float(proposal.target_price),
            quantity=int(proposal.quantity),
            order_type=proposal.order_type,
            allow_market_fallback=bool(proposal.allow_market_fallback),
            rationale=proposal.rationale,
            risk_note=proposal.risk_note,
        ),
    )


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

        loop = asyncio.get_running_loop()
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
    _session: Annotated[dict[str, Any], Depends(require_app_user)],
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
    _session: Annotated[dict[str, Any], Depends(require_app_user)],
    limit: int = Query(default=10, ge=1, le=100),
) -> list[dict[str, Any]]:
    """Return list of past IC decision files (most recent first)."""
    from app.services.agents import list_decisions

    return list_decisions(limit)
