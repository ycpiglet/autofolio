"""Multitenant readiness tests — Task A (endpoints) + Task B (eviction).

A-tests: owner-only re-enable + state endpoints, flag-gated.
B-tests: LRU eviction for _user_ctx (backend) and _user_run_locks (engine router).
"""
from __future__ import annotations

import pytest

from app.database.repositories import Repository
from app.database.sqlite_db import initialize_database

# ---------------------------------------------------------------------------
# CSRF / client helpers
# ---------------------------------------------------------------------------

CSRF = "test-csrf-readiness"


@pytest.fixture()
def _app():
    from app.api.main import create_app
    return create_app()


@pytest.fixture()
def owner_csrf_client(_app):
    from fastapi.testclient import TestClient
    from app.api.security import encode_session
    c = TestClient(_app, raise_server_exceptions=True)
    c.cookies.set("af_session", encode_session({
        "role": "owner",
        "username": "testuser",
        "data_source": "backend",
        "csrf_token": CSRF,
    }))
    return c


@pytest.fixture()
def owner_no_csrf_client(_app):
    """Owner session without CSRF token in the cookie."""
    from fastapi.testclient import TestClient
    from app.api.security import encode_session
    c = TestClient(_app, raise_server_exceptions=True)
    c.cookies.set("af_session", encode_session({
        "role": "owner",
        "username": "testuser",
        "data_source": "backend",
    }))
    return c


@pytest.fixture()
def member_csrf_client(_app):
    from fastapi.testclient import TestClient
    from app.api.security import encode_session
    c = TestClient(_app, raise_server_exceptions=True)
    c.cookies.set("af_session", encode_session({
        "role": "member",
        "username": "member1",
        "data_source": "backend",
        "csrf_token": CSRF,
    }))
    return c


def _csrf_headers():
    return {"X-CSRF-Token": CSRF}


# ---------------------------------------------------------------------------
# A-tests: endpoint flag-gate (flag OFF)
# ---------------------------------------------------------------------------

def test_reenable_flag_off_returns_409(monkeypatch, owner_csrf_client):
    """Flag OFF → POST reenable returns 409 with multitenant_disabled status."""
    monkeypatch.delenv("AUTOFOLIO_MULTI_TENANT_ENABLED", raising=False)
    resp = owner_csrf_client.post(
        "/api/engine/users/user_a/reenable",
        headers=_csrf_headers(),
    )
    assert resp.status_code == 409
    body = resp.json()
    # FastAPI wraps detail in {"detail": ...}
    detail = body.get("detail", body)
    if isinstance(detail, dict):
        assert detail.get("status") == "multitenant_disabled"
    else:
        # detail is the dict itself at top level
        assert body.get("status") == "multitenant_disabled" or body.get("detail", {}).get("status") == "multitenant_disabled"


def test_state_flag_off_returns_409(monkeypatch, owner_csrf_client):
    """Flag OFF → GET state returns 409."""
    monkeypatch.delenv("AUTOFOLIO_MULTI_TENANT_ENABLED", raising=False)
    resp = owner_csrf_client.get("/api/engine/users/user_a/state")
    assert resp.status_code == 409


def test_reenable_member_forbidden(monkeypatch, member_csrf_client):
    """Member (not owner) → POST reenable → 403."""
    monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
    resp = member_csrf_client.post(
        "/api/engine/users/user_a/reenable",
        headers=_csrf_headers(),
    )
    assert resp.status_code == 403


def test_reenable_missing_csrf_forbidden(monkeypatch, owner_no_csrf_client):
    """Owner without CSRF header → POST reenable → 403."""
    monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
    # No CSRF header sent, and the cookie has no csrf_token either
    resp = owner_no_csrf_client.post("/api/engine/users/user_a/reenable")
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# A-test: flag ON — reenable restores per-user state (repo-level unit test)
# ---------------------------------------------------------------------------

def test_reenable_flag_on_restores_user_state(tmp_path, monkeypatch):
    """Flag ON: simulate CB trip then reenable → per-user state restored.

    Global state is untouched. This is the key invariant test.
    """
    monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")
    db = tmp_path / "reenable.db"
    initialize_database(db)
    repo = Repository(db)

    user_id = "user_a"

    # Setup global state = enabled
    repo.set_system_state("auto_trading_enabled", "true")

    # Simulate CB trip: per-user auto_trading=false, failures=3
    repo.set_engine_state("auto_trading_enabled", "false", user_id=user_id)
    for _ in range(3):
        repo.increment_consecutive_failures(user_id=user_id)

    assert repo.get_engine_state("auto_trading_enabled", "false", user_id=user_id) == "false"
    assert repo.get_consecutive_failures(user_id=user_id) == 3

    # Global untouched before reenable
    assert repo.get_system_state("auto_trading_enabled") == "true"

    # Reenable
    repo.set_engine_state("auto_trading_enabled", "true", user_id=user_id)
    repo.reset_consecutive_failures(user_id=user_id)

    # Per-user state restored
    assert repo.get_engine_state("auto_trading_enabled", "false", user_id=user_id) == "true"
    assert repo.get_consecutive_failures(user_id=user_id) == 0

    # Global state still untouched
    assert repo.get_system_state("auto_trading_enabled") == "true"
    # Other user unaffected
    assert repo.get_consecutive_failures(user_id="user_b") == 0


# ---------------------------------------------------------------------------
# A-test: flag ON — API endpoint reenable (with mocked backend._ctx)
# ---------------------------------------------------------------------------

def test_reenable_flag_on_api_endpoint(tmp_path, monkeypatch, owner_csrf_client):
    """Flag ON: POST /api/engine/users/user_a/reenable returns 200 + reenabled status."""
    monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")

    db = tmp_path / "api_reenable.db"
    initialize_database(db)
    repo = Repository(db)
    repo.set_system_state("auto_trading_enabled", "true")
    # Simulate CB trip for user_a
    repo.set_engine_state("auto_trading_enabled", "false", user_id="user_a")
    for _ in range(3):
        repo.increment_consecutive_failures(user_id="user_a")

    import app.services.backend as backend_mod
    monkeypatch.setattr(backend_mod, "_ctx", lambda: (repo, None, None, None))

    resp = owner_csrf_client.post(
        "/api/engine/users/user_a/reenable",
        headers=_csrf_headers(),
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["status"] == "reenabled"
    assert body["auto_trading_enabled"] is True
    assert body["consecutive_failures"] == 0
    assert body["user_id"] == "user_a"


def test_state_flag_on_api_endpoint(tmp_path, monkeypatch, owner_csrf_client):
    """Flag ON: GET /api/engine/users/user_a/state returns 200 + correct state."""
    monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")

    db = tmp_path / "api_state.db"
    initialize_database(db)
    repo = Repository(db)
    repo.set_system_state("auto_trading_enabled", "true")
    repo.set_engine_state("auto_trading_enabled", "false", user_id="user_a")
    repo.increment_consecutive_failures(user_id="user_a")
    repo.increment_consecutive_failures(user_id="user_a")

    import app.services.backend as backend_mod
    monkeypatch.setattr(backend_mod, "_ctx", lambda: (repo, None, None, None))

    resp = owner_csrf_client.get("/api/engine/users/user_a/state")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["user_id"] == "user_a"
    assert body["auto_trading_enabled"] is False
    assert body["consecutive_failures"] == 2


# ---------------------------------------------------------------------------
# B-tests: eviction
# ---------------------------------------------------------------------------

def test_user_ctx_lru_eviction(tmp_path, monkeypatch):
    """_user_ctx evicts oldest entries when _USER_CTX_MAX is exceeded."""
    monkeypatch.setenv("AUTOFOLIO_MULTI_TENANT_ENABLED", "1")

    from app.brokers.mock.mock_client import MockBrokerClient
    from app.engine.live_trading_engine import LiveTradingEngine

    db = tmp_path / "lru_ctx.db"
    initialize_database(db)
    repo = Repository(db)
    broker = MockBrokerClient(prices={"005930": 70_000.0})
    base_engine = LiveTradingEngine(broker=broker, repo=repo)
    agent = object()

    import app.services.backend as backend
    monkeypatch.setattr(backend, "_ctx", lambda: (repo, broker, base_engine, agent))

    with backend._user_ctx_lock:
        backend._user_ctx.clear()

    try:
        # Insert _USER_CTX_MAX + 5 distinct users
        for i in range(backend._USER_CTX_MAX + 5):
            backend._ctx_for_user(f"user_{i}")

        with backend._user_ctx_lock:
            assert len(backend._user_ctx) <= backend._USER_CTX_MAX
    finally:
        with backend._user_ctx_lock:
            backend._user_ctx.clear()


def test_user_run_locks_lru_eviction():
    """_user_run_locks evicts oldest idle entries when _USER_LOCKS_MAX is exceeded."""
    import app.api.routers.engine as engine_mod

    with engine_mod._user_run_locks_lock:
        engine_mod._user_run_locks.clear()

    try:
        for i in range(engine_mod._USER_LOCKS_MAX + 1):
            engine_mod._run_lock_for(f"evict_user_{i}")

        with engine_mod._user_run_locks_lock:
            assert len(engine_mod._user_run_locks) <= engine_mod._USER_LOCKS_MAX
    finally:
        with engine_mod._user_run_locks_lock:
            engine_mod._user_run_locks.clear()


def test_held_lock_not_evicted():
    """A currently-held lock must never be evicted from the pool."""
    import app.api.routers.engine as engine_mod

    with engine_mod._user_run_locks_lock:
        engine_mod._user_run_locks.clear()
        old_max = engine_mod._USER_LOCKS_MAX
        engine_mod._USER_LOCKS_MAX = 2

    try:
        lock_a = engine_mod._run_lock_for("held_user_a")
        # Acquire lock_a to simulate a running job
        assert lock_a.acquire(blocking=False), "Should acquire idle lock"
        try:
            engine_mod._run_lock_for("held_user_b")
            # Now pool = {held_user_a (held), held_user_b (idle)}, size == max == 2
            engine_mod._run_lock_for("held_user_c")  # triggers eviction
            # held_user_a must NOT have been evicted (it's held)
            with engine_mod._user_run_locks_lock:
                assert "held_user_a" in engine_mod._user_run_locks, (
                    "Held lock must not be evicted"
                )
        finally:
            lock_a.release()
    finally:
        with engine_mod._user_run_locks_lock:
            engine_mod._USER_LOCKS_MAX = old_max
            engine_mod._user_run_locks.clear()
