"""Tests for Phase 4 Agents/IC API + SSE event hub.

Design decisions:
- All tests monkeypatch app.services.agents to avoid any LLM calls or file I/O.
- SSE tests read a bounded number of lines to avoid hanging.
- CSRF tests reuse the CSRF token from conftest._CSRF_HEADER pattern.
- TZ-robust: no real timestamps compared; IC result dict is checked structurally.
"""
from __future__ import annotations

import json
import threading
import time
import uuid
from typing import Any
from unittest.mock import patch

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


def _member_session() -> str:
    return encode_session({"role": "member", "username": "member1", "data_source": "backend"})


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
def member_client(app):
    c = TestClient(app, raise_server_exceptions=True)
    c.cookies.set("af_session", _member_session())
    return c


@pytest.fixture()
def anon_client(app):
    return TestClient(app, raise_server_exceptions=True)


# ── GET /api/agents/list ──────────────────────────────────────────────────────

class TestAgentsList:
    def test_returns_200_for_member(self, member_client):
        with patch("app.services.agents.available", return_value=(False, "no key")), \
             patch("app.services.agents.list_agent_infos", return_value=[
                 {"name": "macro-strategist", "role": "매크로 전략", "category": "투자 리더십", "expert": True},
                 {"name": "cio", "role": "CIO", "category": "투자 리더십", "expert": True},
             ]):
            resp = member_client.get("/api/agents/list")
        assert resp.status_code == 200

    def test_guest_403(self, guest_client):
        resp = guest_client.get("/api/agents/list")
        assert resp.status_code == 403

    def test_response_shape(self, member_client):
        with patch("app.services.agents.available", return_value=(False, "demo")), \
             patch("app.services.agents.list_agent_infos", return_value=[
                 {"name": "cio", "role": "CIO", "category": "투자 리더십", "expert": True},
                 {"name": "risk-manager", "role": "리스크 매니저", "category": "투자 리더십", "expert": True},
             ]):
            body = member_client.get("/api/agents/list").json()
        assert body["available"] is False
        assert body["message"] == "demo"
        assert body["agents"][0]["name"] == "cio"
        assert body["agents"][0]["expert"] is True
        assert body["agents"][1]["name"] == "risk-manager"

    def test_experts_only_forwarded(self, member_client):
        captured: dict[str, bool] = {}

        def fake_infos(*, experts_only: bool = False) -> list[dict]:
            captured["experts_only"] = experts_only
            return []

        with patch("app.services.agents.available", return_value=(False, "demo")), \
             patch("app.services.agents.list_agent_infos", side_effect=fake_infos):
            resp = member_client.get("/api/agents/list?experts_only=true")
        assert resp.status_code == 200
        assert captured["experts_only"] is True

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
        with patch("app.services.agents.run_ic", return_value={"topic": "test", "transcript": [], "decision": "ok", "path": "/tmp/test"}):
            resp = owner_client.post(
                "/api/agents/ic/run",
                json=self._BODY,
                headers=_csrf_headers(),
            )
        assert resp.status_code == 202
        body = resp.json()
        assert "job_id" in body
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
    """Drive a fake run_ic that calls progress N times, then returns."""

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

    def test_stream_404_for_unknown_job(self, member_client):
        resp = member_client.get(f"/api/agents/ic/stream/{uuid.uuid4()}")
        assert resp.status_code == 404

    def test_stream_replays_completed_job(self, owner_client, member_client):
        """After run_ic finishes, stream should replay steps + emit done."""
        steps = ["전문가 의견 · macro-strategist", "악마의 변호인", "CIO 결정"]
        job_id = self._submit_job(owner_client, steps)

        # Allow background asyncio task to complete
        time.sleep(1.0)

        # Stream — all steps should be replayed immediately since job is done
        data_lines: list[str] = []
        with member_client.stream("GET", f"/api/agents/ic/stream/{job_id}") as resp:
            assert resp.status_code == 200
            assert "text/event-stream" in resp.headers.get("content-type", "")
            for line in resp.iter_lines():
                if line.startswith("data:"):
                    data_lines.append(line[len("data:"):].strip())
                    if len(data_lines) >= len(steps) + 1:  # steps + done
                        break

        # Should contain all step payloads (decode JSON to compare properly)
        parsed = [json.loads(d) for d in data_lines]
        step_texts = [p.get("step", "") for p in parsed if "step" in p]
        for step in steps:
            assert step in step_texts, f"Expected step '{step}' in SSE step events"
        # Last item should be the done event
        done_payload = parsed[-1]
        assert "decision" in done_payload or "topic" in done_payload

    def test_stream_member_allowed(self, owner_client, member_client):
        """Stream requires an approved app user."""
        steps = ["step-a"]
        job_id = self._submit_job(owner_client, steps)
        time.sleep(0.5)
        with member_client.stream("GET", f"/api/agents/ic/stream/{job_id}") as resp:
            assert resp.status_code == 200
            for _ in resp.iter_lines():
                break  # Just confirm it opens OK

    def test_stream_guest_403(self, owner_client, guest_client):
        steps = ["step-a"]
        job_id = self._submit_job(owner_client, steps)
        time.sleep(0.5)
        resp = guest_client.get(f"/api/agents/ic/stream/{job_id}")
        assert resp.status_code == 403

    def test_stream_401_for_anon(self, anon_client, owner_client):
        steps = ["x"]
        job_id = self._submit_job(owner_client, steps)
        resp = anon_client.get(f"/api/agents/ic/stream/{job_id}")
        assert resp.status_code == 401


# ── GET /api/agents/ic/decisions ─────────────────────────────────────────────

class TestIcDecisions:
    def test_returns_list_for_member(self, member_client):
        fake = [{"file": "IC_20260615.md", "path": "/tmp/IC_20260615.md"}]
        with patch("app.services.agents.list_decisions", return_value=fake):
            resp = member_client.get("/api/agents/ic/decisions")
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)
        assert body[0]["file"] == "IC_20260615.md"

    def test_limit_param_forwarded(self, member_client):
        captured: dict = {}

        def fake_list(limit: int = 10) -> list:
            captured["limit"] = limit
            return []

        with patch("app.services.agents.list_decisions", side_effect=fake_list):
            member_client.get("/api/agents/ic/decisions?limit=5")
        assert captured["limit"] == 5

    def test_401_without_session(self, anon_client):
        resp = anon_client.get("/api/agents/ic/decisions")
        assert resp.status_code == 401


# ── GET /api/stream/events ────────────────────────────────────────────────────

class TestStreamEvents:
    """Tests for the events.jsonl tail + demo ticker SSE."""

    def test_returns_200_for_member(self, member_client, tmp_path):
        """SSE endpoint responds with 200 and correct content-type."""
        fake_log = tmp_path / "events.jsonl"
        fake_log.write_text("", encoding="utf-8")

        event_data = {"event": "engine_run_start", "run": 1}
        lines: list[str] = []

        # Append the event repeatedly until the stream picks it up. A single
        # delayed write can land BEFORE the server captures the tail start-offset
        # (race under CI load) → the event is never tailed → the generator never
        # emits → iter_lines hangs until CI timeout. Continuous appends guarantee
        # a post-offset line lands within one poll interval, making this
        # deterministic regardless of scheduling.
        stop = threading.Event()

        def _writer() -> None:
            while not stop.is_set():
                with fake_log.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(event_data) + "\n")
                stop.wait(0.05)

        thread = threading.Thread(target=_writer, daemon=True)

        with patch("app.api.routers.stream._EVENTS_JSONL", fake_log), \
             patch("app.api.routers.stream._TAIL_POLL_INTERVAL", 0.05), \
             patch("app.api.routers.stream._DEMO_TICKER_INTERVAL", 999.0), \
             patch("app.api.routers.stream._MAX_EVENTS", 1):
            thread.start()
            with member_client.stream("GET", "/api/stream/events") as resp:
                assert resp.status_code == 200
                assert "text/event-stream" in resp.headers.get("content-type", "")
                for line in resp.iter_lines():
                    if line.startswith("data:"):
                        lines.append(line)
                        break

        stop.set()
        thread.join(timeout=2.0)
        assert len(lines) >= 1
        payload = json.loads(lines[0][len("data:"):].strip())
        assert payload.get("event") == "engine_run_start"

    def test_401_without_session(self, anon_client):
        resp = anon_client.get("/api/stream/events")
        assert resp.status_code == 401

    def test_guest_403(self, guest_client):
        resp = guest_client.get("/api/stream/events")
        assert resp.status_code == 403

    def test_engine_events_emitted(self, member_client, tmp_path):
        """New lines written to events.jsonl after connect are streamed."""
        fake_log = tmp_path / "events.jsonl"
        fake_log.write_text("", encoding="utf-8")

        event_payload = {"event": "condition_processed", "symbol": "005930"}
        collected: list[str] = []

        # Continuous appends (see test_returns_200_for_member) to avoid the
        # connect-vs-write race that flakes/hangs under CI load.
        stop = threading.Event()

        def _writer() -> None:
            while not stop.is_set():
                with fake_log.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(event_payload) + "\n")
                stop.wait(0.05)

        thread = threading.Thread(target=_writer, daemon=True)

        with patch("app.api.routers.stream._EVENTS_JSONL", fake_log), \
             patch("app.api.routers.stream._TAIL_POLL_INTERVAL", 0.05), \
             patch("app.api.routers.stream._DEMO_TICKER_INTERVAL", 999.0), \
             patch("app.api.routers.stream._MAX_EVENTS", 1):
            thread.start()
            with member_client.stream("GET", "/api/stream/events") as resp:
                for line in resp.iter_lines():
                    if line.startswith("data:"):
                        collected.append(line)
                        break

        stop.set()
        thread.join(timeout=2.0)
        assert collected, "Expected at least one engine event"
        payload = json.loads(collected[0][len("data:"):].strip())
        assert payload.get("event") == "condition_processed"

    def test_opt_in_kis_ws_accepted(self, member_client, tmp_path):
        """opt_in_kis_ws query param is accepted without crashing."""
        import pathlib
        # Use demo ticker (interval=0 → fires immediately) to produce 1 event and terminate.
        with patch("app.api.routers.stream._EVENTS_JSONL", pathlib.Path(tmp_path / "noop.jsonl")), \
             patch("app.api.routers.stream._TAIL_POLL_INTERVAL", 0.05), \
             patch("app.api.routers.stream._DEMO_TICKER_INTERVAL", 0.0), \
             patch("app.api.routers.stream._MAX_EVENTS", 1):
            with member_client.stream("GET", "/api/stream/events?opt_in_kis_ws=true") as resp:
                assert resp.status_code == 200
                for _ in resp.iter_lines():
                    break
