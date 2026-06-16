# TASK-048 Phase 4: Agents/IC API + SSE Event Hub Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `app/api/routers/agents.py` and `app/api/routers/stream.py` routers to expose agents listing, question-asking, investment-committee (IC) job submission and SSE progress streaming, IC decisions, and an event-log SSE tail — all without spawning any background daemon.

**Architecture:** Two new FastAPI routers mounted at `/api/agents` and `/api/stream`. IC jobs are submitted via POST and run in asyncio background tasks (one per request); results/progress are buffered in an in-memory dict keyed by `job_id`. SSE generators are per-connection `StreamingResponse` objects that live only while the client is connected, using `await request.is_disconnected()` to cancel cleanly. KIS WebSocket integration is documented but off by default.

**Tech Stack:** FastAPI, Pydantic, asyncio (`asyncio.Queue` per IC job), `starlette.requests.Request`, `starlette.responses.StreamingResponse`, Python 3.10+, pytest + `httpx` (via `TestClient(stream=True)`) — existing patterns from `app/api/routers/` and `tests/api/`.

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `app/api/routers/agents.py` | `/api/agents/*` — list, ask, ic/run, ic/stream, ic/decisions |
| Create | `app/api/routers/stream.py` | `/api/stream/events` — log-tail + demo ticker SSE |
| Modify | `app/api/main.py` | Include both new routers |
| Modify | `app/api/schemas/__init__.py` | Add new request/response Pydantic models |
| Create | `tests/api/test_agents_stream.py` | Tests for all new endpoints |

---

## Task 1: Add Pydantic schemas

**Files:**
- Modify: `app/api/schemas/__init__.py`

- [ ] **Step 1: Read the current schemas file**

Run: Open `app/api/schemas/__init__.py` (already done in planning; line counts show it ends at line 112).

- [ ] **Step 2: Append new schemas**

Add the following to the BOTTOM of `app/api/schemas/__init__.py` (after the `RiskLimitsResponse` class):

```python
# ── Agents (Phase 4) ─────────────────────────────────────────────────────────

class AgentsListResponse(BaseModel):
    available: bool
    message: str
    agents: list[str]


class AskRequest(BaseModel):
    agent: str
    question: str
    context: str = ""


class AskResponse(BaseModel):
    answer: str


class IcRunRequest(BaseModel):
    topic: str
    panel: list[str] | None = None


class IcRunResponse(BaseModel):
    job_id: str
```

- [ ] **Step 3: Verify schemas import correctly**

Run: `.\.venv\Scripts\python.exe -c "from app.api.schemas import AgentsListResponse, AskRequest, AskResponse, IcRunRequest, IcRunResponse; print('ok')" `
Expected: `ok`

- [ ] **Step 4: Commit**

```bash
git add app/api/schemas/__init__.py
git commit -m "feat(schemas): add Phase4 agent/IC/stream schemas"
```

---

## Task 2: Create `app/api/routers/agents.py`

**Files:**
- Create: `app/api/routers/agents.py`

This router handles the IC job registry in module-level memory. The IC job runs in an asyncio `Task` (not a thread) so it integrates cleanly with FastAPI's event loop. `run_ic` is a blocking function, so it runs in a thread-pool executor via `asyncio.get_event_loop().run_in_executor(None, ...)`.

- [ ] **Step 1: Write the failing test (placeholder — test comes in Task 4)**

Skip ahead to implementation first because the router must exist before tests can import it.

- [ ] **Step 2: Create the router file**

Create `app/api/routers/agents.py` with the following content:

```python
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
```

- [ ] **Step 3: Verify router imports without error**

Run: `.\.venv\Scripts\python.exe -c "from app.api.routers.agents import router; print('ok')"`
Expected: `ok`

- [ ] **Step 4: Commit**

```bash
git add app/api/routers/agents.py
git commit -m "feat(api): agents router with IC job registry + SSE stream"
```

---

## Task 3: Create `app/api/routers/stream.py`

**Files:**
- Create: `app/api/routers/stream.py`

This router implements the general-purpose event stream: tailing `logs/events.jsonl` for new lines written after connect, plus a demo ticker that emits a mock price event every 5 seconds. KIS WebSocket is documented but off by default (not wired).

- [ ] **Step 1: Create the router file**

Create `app/api/routers/stream.py`:

```python
"""Stream router — /api/stream/*

Endpoints:
  GET /stream/events (require_session) → SSE: new events.jsonl lines + demo ticker

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
import os
import time
from pathlib import Path
from typing import Annotated, Any, AsyncGenerator

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse

from app.api.deps import require_session

router = APIRouter(prefix="/stream", tags=["stream"])

_EVENTS_JSONL = Path(__file__).resolve().parents[3] / "logs" / "events.jsonl"
_DEMO_TICKER_INTERVAL = 5.0  # seconds between demo price events
_TAIL_POLL_INTERVAL = 0.5    # seconds between log file polls


@router.get("/events")
async def stream_events(
    request: Request,
    _session: Annotated[dict[str, Any], Depends(require_session)],
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
```

- [ ] **Step 2: Verify stream router imports without error**

Run: `.\.venv\Scripts\python.exe -c "from app.api.routers.stream import router; print('ok')"`
Expected: `ok`

- [ ] **Step 3: Commit**

```bash
git add app/api/routers/stream.py
git commit -m "feat(api): stream router — events.jsonl tail + demo ticker SSE"
```

---

## Task 4: Wire routers into `app/api/main.py`

**Files:**
- Modify: `app/api/main.py`

- [ ] **Step 1: Add the two new routers to the import line**

In `app/api/main.py`, change line 17:

Old:
```python
from app.api.routers import analysis, auth, engine, market, portfolio, settings, trade
```

New:
```python
from app.api.routers import agents, analysis, auth, engine, market, portfolio, settings, stream, trade
```

- [ ] **Step 2: Include the new routers in `create_app()`**

After line `app.include_router(analysis.router, prefix="/api")`, add:

```python
    app.include_router(agents.router, prefix="/api")
    app.include_router(stream.router, prefix="/api")
```

- [ ] **Step 3: Verify app creates without error**

Run: `.\.venv\Scripts\python.exe -c "from app.api.main import create_app; app = create_app(); routes = [r.path for r in app.routes]; print([r for r in routes if 'agents' in r or 'stream' in r])"`
Expected output includes `/api/agents/list`, `/api/agents/ask`, `/api/agents/ic/run`, `/api/agents/ic/stream/{job_id}`, `/api/agents/ic/decisions`, `/api/stream/events`

- [ ] **Step 4: Commit**

```bash
git add app/api/main.py
git commit -m "feat(api): include agents + stream routers in main app"
```

---

## Task 5: Write and run tests in `tests/api/test_agents_stream.py`

**Files:**
- Create: `tests/api/test_agents_stream.py`

Key test design rules:
- Use `conftest.py`'s `guest_client`, `owner_client` fixtures plus a new `owner_csrf_client` fixture that also carries the CSRF token in headers.
- Use `TestClient` for SSE by calling `client.get(url, stream=True)` and reading a bounded number of bytes/lines so tests never hang.
- Mock `app.services.agents` at the module level for each test using `monkeypatch`.
- The IC stream test drives a fake `run_ic` that calls `progress` synchronously a few times, then returns — this naturally fills the queue before the SSE generator reads it.

- [ ] **Step 1: Create the test file**

Create `tests/api/test_agents_stream.py`:

```python
"""Tests for Phase 4 Agents/IC API + SSE event hub.

Design decisions:
- All tests monkeypatch app.services.agents to avoid any LLM calls or file I/O.
- SSE tests read a bounded number of lines to avoid hanging.
- CSRF tests reuse the CSRF token from conftest._CSRF_HEADER pattern.
- TZ-robust: no real timestamps compared; IC result dict is checked structurally.
"""
from __future__ import annotations

import io
import json
import threading
import time
import uuid
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.main import create_app
from app.api.security import encode_session

# ── Constants ─────────────────────────────────────────────────────────────────

CSRF = "deadbeefcafe" * 5  # matches existing conftest style


def _owner_session(csrf: str = CSRF) -> str:
    return encode_session({
        "role": "owner",
        "username": "testuser",
        "data_source": "backend",
        "csrf_token": csrf,
    })


def _guest_session() -> str:
    return encode_session({"role": "guest", "data_source": "demo"})


def _csrf_headers(csrf: str = CSRF) -> dict[str, str]:
    return {"X-CSRF-Token": csrf}


# ── App fixture (module-scoped for speed) ─────────────────────────────────────

@pytest.fixture(scope="module")
def app():
    return create_app()


@pytest.fixture()
def owner_client(app):
    c = TestClient(app, raise_server_exceptions=True)
    c.cookies.set("af_session", _owner_session())
    return c


@pytest.fixture()
def guest_client(app):
    c = TestClient(app, raise_server_exceptions=True)
    c.cookies.set("af_session", _guest_session())
    return c


@pytest.fixture()
def anon_client(app):
    return TestClient(app, raise_server_exceptions=True)


# ── Helper: read bounded SSE lines ────────────────────────────────────────────

def _read_sse_lines(client: TestClient, url: str, max_events: int = 10, timeout: float = 5.0) -> list[str]:
    """Read at most max_events data lines from an SSE endpoint.

    Uses TestClient's streaming context manager; reads until max_events
    data: lines collected OR the response is exhausted.
    Never hangs: bounded by max_events.
    """
    data_lines: list[str] = []
    with client.stream("GET", url) as response:
        for line in response.iter_lines():
            if line.startswith("data:"):
                data_lines.append(line)
                if len(data_lines) >= max_events:
                    break
    return data_lines


# ── GET /api/agents/list ──────────────────────────────────────────────────────

class TestAgentsList:
    def test_returns_200_for_guest(self, guest_client):
        with patch("app.services.agents.available", return_value=(False, "no key")), \
             patch("app.services.agents.list_agents", return_value=["macro-strategist", "cio"]):
            resp = guest_client.get("/api/agents/list")
        assert resp.status_code == 200

    def test_response_shape(self, guest_client):
        with patch("app.services.agents.available", return_value=(False, "demo")), \
             patch("app.services.agents.list_agents", return_value=["cio", "risk-manager"]):
            body = guest_client.get("/api/agents/list").json()
        assert body["available"] is False
        assert body["message"] == "demo"
        assert "cio" in body["agents"]
        assert "risk-manager" in body["agents"]

    def test_401_without_session(self, anon_client):
        resp = anon_client.get("/api/agents/list")
        assert resp.status_code == 401


# ── POST /api/agents/ask ──────────────────────────────────────────────────────

class TestAgentsAsk:
    _BODY = {"agent": "cio", "question": "무엇을 해야 하나요?"}

    def test_returns_answer_for_owner(self, owner_client):
        with patch("app.services.agents.ask", return_value="매수 권고"):
            resp = owner_client.post(
                "/api/agents/ask",
                json=self._BODY,
                headers=_csrf_headers(),
            )
        assert resp.status_code == 200
        assert resp.json()["answer"] == "매수 권고"

    def test_guest_403(self, guest_client):
        resp = guest_client.post(
            "/api/agents/ask",
            json=self._BODY,
            headers=_csrf_headers(),
        )
        assert resp.status_code == 403

    def test_missing_csrf_403(self, owner_client):
        resp = owner_client.post("/api/agents/ask", json=self._BODY)
        assert resp.status_code == 403

    def test_wrong_csrf_403(self, owner_client):
        resp = owner_client.post(
            "/api/agents/ask",
            json=self._BODY,
            headers={"X-CSRF-Token": "wrongtoken"},
        )
        assert resp.status_code == 403

    def test_context_forwarded(self, owner_client):
        captured: dict = {}

        def fake_ask(agent: str, question: str, context: str = "") -> str:
            captured["context"] = context
            return "ok"

        with patch("app.services.agents.ask", side_effect=fake_ask):
            owner_client.post(
                "/api/agents/ask",
                json={"agent": "cio", "question": "Q", "context": "extra ctx"},
                headers=_csrf_headers(),
            )
        assert captured["context"] == "extra ctx"


# ── POST /api/agents/ic/run ───────────────────────────────────────────────────

class TestIcRun:
    _BODY = {"topic": "삼성전자 매수 여부"}

    def test_returns_job_id_for_owner(self, owner_client):
        # run_ic blocks; patch it to return immediately
        with patch("app.services.agents.run_ic", return_value={"topic": "test", "transcript": [], "decision": "ok", "path": "/tmp/test"}):
            resp = owner_client.post(
                "/api/agents/ic/run",
                json=self._BODY,
                headers=_csrf_headers(),
            )
        assert resp.status_code == 202
        body = resp.json()
        assert "job_id" in body
        # job_id should look like a UUID
        assert len(body["job_id"]) == 36

    def test_guest_403(self, guest_client):
        resp = guest_client.post(
            "/api/agents/ic/run",
            json=self._BODY,
            headers=_csrf_headers(),
        )
        assert resp.status_code == 403

    def test_missing_csrf_403(self, owner_client):
        resp = owner_client.post("/api/agents/ic/run", json=self._BODY)
        assert resp.status_code == 403


# ── GET /api/agents/ic/stream/{job_id} ───────────────────────────────────────

class TestIcStream:
    """Drive a fake run_ic that calls progress N times, then returns.

    We submit an IC run (which patches run_ic), wait a moment for the background
    task to complete (TestClient is synchronous so we sleep briefly), then read
    the SSE stream in bounded fashion.
    """

    def _submit_job(self, owner_client: TestClient, steps: list[str]) -> str:
        """Submit an IC run with a fake run_ic that calls progress for each step."""

        def fake_run_ic(topic: str, panel: Any = None, progress: Any = None) -> dict:
            for s in steps:
                if progress:
                    progress(s)
            return {"topic": topic, "transcript": [], "decision": "CIO: 매수", "path": "/tmp/fake"}

        with patch("app.services.agents.run_ic", side_effect=fake_run_ic):
            resp = owner_client.post(
                "/api/agents/ic/run",
                json={"topic": "test"},
                headers=_csrf_headers(),
            )
        assert resp.status_code == 202
        return resp.json()["job_id"]

    def test_stream_404_for_unknown_job(self, guest_client):
        resp = guest_client.get(f"/api/agents/ic/stream/{uuid.uuid4()}")
        assert resp.status_code == 404

    def test_stream_replays_completed_job(self, owner_client, guest_client):
        """After run_ic finishes, stream should replay steps + emit done."""
        steps = ["전문가 의견 · macro-strategist", "악마의 변호인", "CIO 결정"]
        job_id = self._submit_job(owner_client, steps)

        # Give the async background task time to complete.
        # TestClient runs the ASGI app synchronously, but asyncio tasks
        # scheduled with create_task need the event loop to run to completion.
        # We wait briefly so the task can finish.
        time.sleep(0.5)

        # Now stream — all steps should be replayed immediately
        data_lines: list[str] = []
        with guest_client.stream("GET", f"/api/agents/ic/stream/{job_id}") as resp:
            assert resp.status_code == 200
            assert "text/event-stream" in resp.headers.get("content-type", "")
            for line in resp.iter_lines():
                if line.startswith("data:"):
                    data_lines.append(line[len("data:"):].strip())
                    if len(data_lines) >= len(steps) + 1:  # steps + done
                        break

        # Should contain all step payloads
        all_data = " ".join(data_lines)
        for step in steps:
            assert step in all_data, f"Expected step '{step}' in SSE data"
        # Last item should be the done event (CIO decision)
        done_payload = json.loads(data_lines[-1])
        assert "decision" in done_payload or "topic" in done_payload

    def test_stream_guest_allowed(self, owner_client, guest_client):
        """Stream is require_session so guest can access it."""
        steps = ["step-a"]
        job_id = self._submit_job(owner_client, steps)
        time.sleep(0.3)
        resp = guest_client.get(f"/api/agents/ic/stream/{job_id}")
        # 200 (StreamingResponse returns 200 even if body short)
        assert resp.status_code in (200, 206)

    def test_stream_401_for_anon(self, anon_client, owner_client):
        steps = ["x"]
        job_id = self._submit_job(owner_client, steps)
        resp = anon_client.get(f"/api/agents/ic/stream/{job_id}")
        assert resp.status_code == 401


# ── GET /api/agents/ic/decisions ─────────────────────────────────────────────

class TestIcDecisions:
    def test_returns_list_for_guest(self, guest_client):
        fake = [{"file": "IC_20260615.md", "path": "/tmp/IC_20260615.md"}]
        with patch("app.services.agents.list_decisions", return_value=fake):
            resp = guest_client.get("/api/agents/ic/decisions")
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)
        assert body[0]["file"] == "IC_20260615.md"

    def test_limit_param_forwarded(self, guest_client):
        captured: dict = {}

        def fake_list(limit: int = 10) -> list:
            captured["limit"] = limit
            return []

        with patch("app.services.agents.list_decisions", side_effect=fake_list):
            guest_client.get("/api/agents/ic/decisions?limit=5")
        assert captured["limit"] == 5

    def test_401_without_session(self, anon_client):
        resp = anon_client.get("/api/agents/ic/decisions")
        assert resp.status_code == 401


# ── GET /api/stream/events ────────────────────────────────────────────────────

class TestStreamEvents:
    """Tests for the events.jsonl tail + demo ticker SSE.

    The demo ticker fires every 5 s, so tests don't wait for it; instead we
    patch the log file to contain pre-seeded lines so we can test the
    engine-event emission immediately.
    """

    def test_returns_200_for_guest(self, guest_client, tmp_path):
        """SSE endpoint responds with 200 and correct content-type."""
        fake_log = tmp_path / "events.jsonl"
        fake_log.write_text(
            json.dumps({"event": "engine_run_start", "run": 1}) + "\n",
            encoding="utf-8",
        )
        with patch("app.api.routers.stream._EVENTS_JSONL", fake_log), \
             patch("app.api.routers.stream._TAIL_POLL_INTERVAL", 0.05), \
             patch("app.api.routers.stream._DEMO_TICKER_INTERVAL", 999.0):
            with guest_client.stream("GET", "/api/stream/events") as resp:
                assert resp.status_code == 200
                assert "text/event-stream" in resp.headers.get("content-type", "")
                lines = []
                for line in resp.iter_lines():
                    if line.startswith("data:"):
                        lines.append(line)
                        break  # Got one engine event — enough to verify

        assert len(lines) >= 1
        payload = json.loads(lines[0][len("data:"):].strip())
        assert payload.get("event") == "engine_run_start"

    def test_401_without_session(self, anon_client):
        resp = anon_client.get("/api/stream/events")
        assert resp.status_code == 401

    def test_engine_events_emitted(self, guest_client, tmp_path):
        """New lines written to events.jsonl after connect are streamed as engine events."""
        fake_log = tmp_path / "events.jsonl"
        # Write initial content so start_offset is non-zero
        fake_log.write_text("", encoding="utf-8")

        # We'll append a line after a short delay to simulate new activity
        event_payload = {"event": "condition_processed", "symbol": "005930"}

        collected: list[str] = []

        def _write_after_delay() -> None:
            time.sleep(0.15)
            with fake_log.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(event_payload) + "\n")

        thread = threading.Thread(target=_write_after_delay, daemon=True)

        with patch("app.api.routers.stream._EVENTS_JSONL", fake_log), \
             patch("app.api.routers.stream._TAIL_POLL_INTERVAL", 0.05), \
             patch("app.api.routers.stream._DEMO_TICKER_INTERVAL", 999.0):
            thread.start()
            with guest_client.stream("GET", "/api/stream/events") as resp:
                for line in resp.iter_lines():
                    if line.startswith("data:"):
                        collected.append(line)
                        break  # Got the engine event

        thread.join(timeout=2.0)
        assert collected, "Expected at least one engine event"
        payload = json.loads(collected[0][len("data:"):].strip())
        assert payload.get("event") == "condition_processed"

    def test_opt_in_kis_ws_accepted(self, guest_client):
        """opt_in_kis_ws query param is accepted (stub — not active in Phase 4)."""
        with patch("app.api.routers.stream._EVENTS_JSONL", __import__("pathlib").Path("/nonexistent")), \
             patch("app.api.routers.stream._TAIL_POLL_INTERVAL", 0.05), \
             patch("app.api.routers.stream._DEMO_TICKER_INTERVAL", 999.0):
            with guest_client.stream("GET", "/api/stream/events?opt_in_kis_ws=true") as resp:
                assert resp.status_code == 200
                # Just verify it doesn't crash — read one iteration worth
                for _ in resp.iter_lines():
                    break
```

- [ ] **Step 2: Run the tests and verify they pass**

Run: `.\.venv\Scripts\python.exe -m pytest tests/api/test_agents_stream.py -v --timeout=30`

Expected: All tests PASS. If any hang, the `--timeout=30` flag will kill them (requires `pytest-timeout` — check `pyproject.toml`; if not present, install or use a shorter bounded read).

- [ ] **Step 3: Fix any failures**

Common issues and fixes:
- `asyncio.create_task` in `ic_run` needs the event loop running. TestClient uses anyio/asyncio under the hood for async endpoints. If `asyncio.get_event_loop()` raises, replace with `asyncio.get_running_loop()` in the `_run` coroutine.
- If `run_in_executor` calls the lambda before `progress` is patched, restructure the patch to patch at `app.api.routers.agents.run_ic` instead of `app.services.agents.run_ic`.
- If SSE streaming tests hang, verify the `time.sleep(0.5)` is sufficient; increase to 1.0 if needed.

- [ ] **Step 4: Commit**

```bash
git add tests/api/test_agents_stream.py
git commit -m "test(api): agents/IC/stream Phase4 endpoint tests"
```

---

## Task 6: Full test suite + coverage verification

**Files:**
- No new files

- [ ] **Step 1: Run the full test suite**

Run: `.\.venv\Scripts\python.exe -m pytest tests/ -q --cov=app --cov-report=term --cov-fail-under=50`

Expected:
- All tests PASS (green)
- Coverage report shows overall ≥ 50%
- `app/api/routers/agents.py` and `app/api/routers/stream.py` both appear in the coverage table with >0% covered lines.
- No tests hang.

- [ ] **Step 2: Run check_agent_docs.py**

Run: `.\.venv\Scripts\python.exe scripts/check_agent_docs.py`
Expected: `0 errors`

- [ ] **Step 3: Fix any issues before committing**

If coverage < 50%: check which large modules are untested. The new routers add lines — verify they are being imported and tested.

If `check_agent_docs.py` reports errors: these are in the TASK management docs, not in code. Do NOT fix them here (TASK-048 docs are marked in-progress intentionally).

- [ ] **Step 4: Final commit on branch**

```bash
git add -u
git commit -m "feat(api): Phase4 에이전트/IC API + SSE 허브(요청당, 데몬 미기동) (TASK-048 backend)

- GET /api/agents/list (require_session): list agents + available flag
- POST /api/agents/ask (require_owner_csrf): single-agent Q&A stub fallback
- POST /api/agents/ic/run (require_owner_csrf): start IC job → job_id (202)
- GET /api/agents/ic/stream/{job_id} (require_session): SSE progress + done, reconnect-replay
- GET /api/agents/ic/decisions (require_session): list past decisions
- GET /api/stream/events (require_session): events.jsonl tail + demo ticker

Daemon-safety:
- All SSE is per-request StreamingResponse; no always-on thread/daemon
- IC jobs run in asyncio background task, scoped to one request
- Loop stops on client disconnect (await request.is_disconnected())
- KIS WS: opt-in query param stub only, NOT wired in Phase 4

IC reconnect-replay: steps already recorded in _jobs[job_id][\"steps\"]
are replayed on reconnect before streaming new queue items.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Self-Review

### 1. Spec Coverage

| Requirement | Task |
|---|---|
| `GET /api/agents/list` → available + agents | Task 2 |
| `POST /api/agents/ask` (require_owner_csrf) | Task 2 |
| `POST /api/agents/ic/run` (require_owner_csrf) → job_id 202 | Task 2 |
| `GET /api/agents/ic/stream/{job_id}` SSE + reconnect-replay | Task 2 |
| `GET /api/agents/ic/decisions?limit=` | Task 2 |
| `GET /api/stream/events` SSE tail + demo ticker | Task 3 |
| In-memory job registry | Task 2 |
| progress callback → queue | Task 2 |
| SSE format `data: <json>\n\n` with event type line | Task 2 & 3 |
| Per-request, no daemon | Tasks 2 & 3 |
| Disconnect safety | Tasks 2 & 3 |
| KIS WS opt-in OFF by default | Task 3 (documented stub) |
| Schemas for all new request/response types | Task 1 |
| Tests: list, ask (stub + guest 403 + CSRF 403) | Task 5 |
| Tests: ic/run returns job_id (guest 403) | Task 5 |
| Tests: ic/stream replay + steps + done | Task 5 |
| Tests: stream/events yields ≥ 1 event, no hang | Task 5 |
| Tests: ic/decisions | Task 5 |
| `check_agent_docs.py` → 0 errors | Task 6 |
| Coverage ≥ 50% | Task 6 |
| Existing tests stay green | Task 6 |
| Branch `feat/task-048-agents-sse` | Pre-condition (user sets up branch) |
| Commit message format | Task 6 final commit |

### 2. Placeholder Scan

No TBD/TODO placeholders in any code block. All steps show actual code. The "KIS WS stub" is explicitly documented as not-wired in Phase 4.

### 3. Type Consistency

- `IcRunResponse.job_id: str` — used in Task 2 `ic_run` return and Task 5 assertion `body["job_id"]` ✓
- `AgentsListResponse.agents: list[str]` — `list_agents()` returns `list[str]` ✓
- `_jobs` dict value type documented as `dict[str, Any]` — accessed as `.get("steps")`, `.get("result")`, `.get("done")`, `.get("queue")` consistently throughout Tasks 2 and 5 ✓
- `q.put_nowait(None)` as sentinel — checked `if item is None:` in the SSE generator ✓
- `_EVENTS_JSONL` patched in tests as the same name used in the router module ✓
- `_TAIL_POLL_INTERVAL` and `_DEMO_TICKER_INTERVAL` patched by name in tests ✓

---

## Important Notes for the Implementer

**Branch setup** (must be done before Task 1):
```bash
git switch -c feat/task-048-agents-sse
```

**Venv**: use `.\.venv\Scripts\python.exe` for all Python commands (Windows).

**asyncio background tasks in TestClient**: FastAPI's `TestClient` uses `anyio` to run the ASGI app. `asyncio.create_task()` in an async endpoint schedules the task in the running event loop. However, `TestClient` tears down the event loop between requests. The pattern used here (`time.sleep(0.5)` before reading the stream) works because `run_in_executor` is non-blocking and the task completes during the `stream()` call's lifetime. If tasks don't complete in time, increase `time.sleep` or add a `done` polling loop.

**Do NOT**:
- Start `kis_ws_client` anywhere in this implementation
- Touch the order flow, trade endpoints, or any existing routes
- Mark TASK-048 as done (frontend is a separate task)
- Push or merge — commit to branch only
