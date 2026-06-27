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
    # FastAPI wraps HTTPException detail in {"detail": ...} — status is nested.
    assert resp.json()["detail"]["status"] == "multitenant_disabled"


def test_state_flag_off_returns_409(monkeypatch, owner_csrf_client):
    """Flag OFF → GET state returns 409 with multitenant_disabled status."""
    monkeypatch.delenv("AUTOFOLIO_MULTI_TENANT_ENABLED", raising=False)
    resp = owner_csrf_client.get("/api/engine/users/user_a/state")
    assert resp.status_code == 409
    # FastAPI wraps HTTPException detail in {"detail": ...} — status is nested.
    assert resp.json()["detail"]["status"] == "multitenant_disabled"


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
# A-tests: anon (no session) → 401
# ---------------------------------------------------------------------------

@pytest.fixture()
def anon_client(_app):
    """Plain TestClient with no session cookie set."""
    from fastapi.testclient import TestClient
    return TestClient(_app, raise_server_exceptions=True)


def test_anon_reenable_returns_401(anon_client):
    """Unauthenticated POST /engine/users/{id}/reenable must return 401."""
    resp = anon_client.post(
        "/api/engine/users/user_a/reenable",
        headers=_csrf_headers(),
    )
    assert resp.status_code == 401


def test_anon_state_returns_401(anon_client):
    """Unauthenticated GET /engine/users/{id}/state must return 401."""
    resp = anon_client.get("/api/engine/users/user_a/state")
    assert resp.status_code == 401


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
    """_user_run_locks evicts oldest idle (fully released) entries when _USER_LOCKS_MAX is exceeded."""
    import app.api.routers.engine as engine_mod

    with engine_mod._user_run_locks_lock:
        engine_mod._user_run_locks.clear()
        engine_mod._user_run_lock_checkouts.clear()

    try:
        for i in range(engine_mod._USER_LOCKS_MAX + 1):
            # Simulate the full caller lifecycle: get lock, then immediately release
            # the checkout so the entry becomes evictable by subsequent insertions.
            engine_mod._run_lock_for(f"evict_user_{i}")
            engine_mod._release_run_lock(f"evict_user_{i}")

        with engine_mod._user_run_locks_lock:
            assert len(engine_mod._user_run_locks) <= engine_mod._USER_LOCKS_MAX
    finally:
        with engine_mod._user_run_locks_lock:
            engine_mod._user_run_locks.clear()
            engine_mod._user_run_lock_checkouts.clear()


def test_held_lock_not_evicted():
    """A currently-held lock must never be evicted from the pool."""
    import app.api.routers.engine as engine_mod

    with engine_mod._user_run_locks_lock:
        engine_mod._user_run_locks.clear()
        engine_mod._user_run_lock_checkouts.clear()
        old_max = engine_mod._USER_LOCKS_MAX
        engine_mod._USER_LOCKS_MAX = 2

    try:
        lock_a = engine_mod._run_lock_for("held_user_a")
        # Acquire lock_a to simulate a running job (checkout still open — matches
        # real caller behaviour where _release_run_lock is called after lock.release()).
        assert lock_a.acquire(blocking=False), "Should acquire idle lock"
        try:
            engine_mod._run_lock_for("held_user_b")
            # Release b's checkout so it becomes idle/evictable.
            engine_mod._release_run_lock("held_user_b")
            # Now pool = {held_user_a (held, checkout=1), held_user_b (idle, checkout=0)},
            # size == max == 2.
            engine_mod._run_lock_for("held_user_c")  # triggers eviction → b evicted
            engine_mod._release_run_lock("held_user_c")
            # held_user_a must NOT have been evicted (held + checkout > 0)
            with engine_mod._user_run_locks_lock:
                assert "held_user_a" in engine_mod._user_run_locks, (
                    "Held lock must not be evicted"
                )
        finally:
            lock_a.release()
            engine_mod._release_run_lock("held_user_a")
    finally:
        with engine_mod._user_run_locks_lock:
            engine_mod._USER_LOCKS_MAX = old_max
            engine_mod._user_run_locks.clear()
            engine_mod._user_run_lock_checkouts.clear()


def test_held_lock_eviction_worst_case_keeps_new_lock():
    """Worst case: ALL older locks held → new lock must not self-evict."""
    import app.api.routers.engine as engine_mod

    with engine_mod._user_run_locks_lock:
        engine_mod._user_run_locks.clear()
        engine_mod._user_run_lock_checkouts.clear()
    old_max = engine_mod._USER_LOCKS_MAX
    try:
        with engine_mod._user_run_locks_lock:
            engine_mod._USER_LOCKS_MAX = 2
        a = engine_mod._run_lock_for("worst_a")
        b = engine_mod._run_lock_for("worst_b")
        assert a.acquire(blocking=False)
        assert b.acquire(blocking=False)
        try:
            # pool is full ({a held+co=1, b held+co=1}); inserting c triggers eviction,
            # but every older lock is held/checked-out → nothing evictable.
            # c must NOT self-evict.
            c = engine_mod._run_lock_for("worst_c")
            with engine_mod._user_run_locks_lock:
                assert "worst_a" in engine_mod._user_run_locks
                assert "worst_b" in engine_mod._user_run_locks
                assert "worst_c" in engine_mod._user_run_locks, "new lock must not self-evict"
            c2 = engine_mod._run_lock_for("worst_c")
            assert c2 is c, "new lock must remain pooled (single-flight intact)"
            engine_mod._release_run_lock("worst_c")  # for the second _run_lock_for call
        finally:
            a.release()
            engine_mod._release_run_lock("worst_a")
            b.release()
            engine_mod._release_run_lock("worst_b")
            engine_mod._release_run_lock("worst_c")  # for the first _run_lock_for call
    finally:
        with engine_mod._user_run_locks_lock:
            engine_mod._USER_LOCKS_MAX = old_max
            engine_mod._user_run_locks.clear()
            engine_mod._user_run_lock_checkouts.clear()


def test_checkout_protects_from_preacquire_eviction():
    """Checkout refcount prevents eviction of a handed-out lock not yet acquired.

    Models the TOCTOU window: _run_lock_for has returned a lock (checkout=1)
    but the caller has not yet called acquire().  The lock is idle so the old
    acquire-probe would have incorrectly flagged it as evictable; the checkout
    count must shield it even in that window.
    """
    import app.api.routers.engine as engine_mod

    with engine_mod._user_run_locks_lock:
        engine_mod._user_run_locks.clear()
        engine_mod._user_run_lock_checkouts.clear()
        old_max = engine_mod._USER_LOCKS_MAX
        engine_mod._USER_LOCKS_MAX = 2

    try:
        # Step 1: hand out lock for user_a — checkout incremented to 1.
        # Do NOT call acquire() — this is exactly the TOCTOU window.
        lock_a = engine_mod._run_lock_for("toctou_user_a")

        # Step 2: hand out lock for user_b (pool now full at 2), then release
        # its checkout immediately so it is genuinely idle and evictable.
        engine_mod._run_lock_for("toctou_user_b")
        engine_mod._release_run_lock("toctou_user_b")
        # Pool: {toctou_user_a (idle, checkout=1), toctou_user_b (idle, checkout=0)}

        # Step 3: request user_c → triggers eviction.
        # toctou_user_a: checkout=1 → MUST be skipped (even though its lock is idle).
        # toctou_user_b: checkout=0 + idle → should be evicted.
        engine_mod._run_lock_for("toctou_user_c")
        engine_mod._release_run_lock("toctou_user_c")

        with engine_mod._user_run_locks_lock:
            assert "toctou_user_a" in engine_mod._user_run_locks, (
                "Checked-out lock must not be evicted even while idle (pre-acquire window)"
            )
            assert engine_mod._user_run_locks["toctou_user_a"] is lock_a, (
                "Must return the original lock object — not a silently replaced fresh one"
            )
    finally:
        # Simulate caller finally block: _release_run_lock is called even on 409 path.
        engine_mod._release_run_lock("toctou_user_a")
        with engine_mod._user_run_locks_lock:
            engine_mod._USER_LOCKS_MAX = old_max
            engine_mod._user_run_locks.clear()
            engine_mod._user_run_lock_checkouts.clear()
