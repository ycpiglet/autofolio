"""Approved-user integration settings API tests."""
from __future__ import annotations

import importlib

from fastapi.testclient import TestClient

from app.api.main import create_app
from app.api.security import encode_session

CSRF = "csrf-integrations-test"
SECRET = "sk-test-secret-value"


def _client(tmp_path, monkeypatch, *, role: str | None = None, username: str | None = None) -> TestClient:
    monkeypatch.setenv("AUTOFOLIO_HOME", str(tmp_path))

    from app.ui import vault as vault_mod
    from app.services import integrations as integrations_mod

    importlib.reload(vault_mod)
    importlib.reload(integrations_mod)

    c = TestClient(create_app(), raise_server_exceptions=True)
    if role:
        c.cookies.set(
            "af_session",
            encode_session(
                {
                    "role": role,
                    "username": username,
                    "data_source": "backend" if role != "guest" else "demo",
                    "csrf_token": CSRF,
                }
            ),
        )
    return c


def _headers() -> dict[str, str]:
    return {"X-CSRF-Token": CSRF}


def test_integrations_require_approved_app_user(tmp_path, monkeypatch):
    anon = _client(tmp_path, monkeypatch)
    assert anon.get("/api/integrations").status_code == 401

    guest = _client(tmp_path, monkeypatch, role="guest", username=None)
    assert guest.get("/api/integrations").status_code == 403


def test_member_can_store_redacted_llm_token_status(tmp_path, monkeypatch):
    member = _client(tmp_path, monkeypatch, role="member", username="member@example.com")

    saved = member.put(
        "/api/integrations/openai",
        json={
            "secret_value": SECRET,
            "account_label": "member project",
            "scopes": ["analysis", "agent-chat", "analysis"],
            "enabled": True,
        },
        headers=_headers(),
    )
    assert saved.status_code == 200
    body = saved.json()
    assert body["provider_id"] == "openai"
    assert body["configured"] is True
    assert body["secret_set"] is True
    assert body["secret_hint"] == "****alue"
    assert body["scopes"] == ["analysis", "agent-chat"]
    assert SECRET not in saved.text

    listed = member.get("/api/integrations")
    assert listed.status_code == 200
    assert SECRET not in listed.text
    openai = [item for item in listed.json()["integrations"] if item["provider_id"] == "openai"][0]
    assert openai["configured"] is True
    assert openai["account_label"] == "member project"

    from app.ui import vault as vault_mod

    encrypted_bytes = (tmp_path / "vault.enc").read_bytes()
    assert SECRET.encode("utf-8") not in encrypted_bytes
    assert vault_mod.load()["user_integrations"]["member@example.com"]["openai"]["secret_value"] == SECRET


def test_integration_records_are_isolated_by_username(tmp_path, monkeypatch):
    owner = _client(tmp_path, monkeypatch, role="owner", username="owner@example.com")
    owner.put(
        "/api/integrations/telegram",
        json={"secret_value": "owner-token", "account_label": "owner-chat"},
        headers=_headers(),
    )

    member = _client(tmp_path, monkeypatch, role="member", username="member@example.com")
    listed = member.get("/api/integrations")
    telegram = [item for item in listed.json()["integrations"] if item["provider_id"] == "telegram"][0]
    assert telegram["configured"] is False
    assert "owner-token" not in listed.text
    assert "owner-chat" not in listed.text


def test_integration_upsert_requires_csrf_and_known_provider(tmp_path, monkeypatch):
    member = _client(tmp_path, monkeypatch, role="member", username="member@example.com")

    no_csrf = member.put("/api/integrations/openai", json={"secret_value": SECRET})
    assert no_csrf.status_code == 403

    unknown = member.put(
        "/api/integrations/not-a-provider",
        json={"secret_value": SECRET},
        headers=_headers(),
    )
    assert unknown.status_code == 422


def test_member_can_delete_own_integration(tmp_path, monkeypatch):
    member = _client(tmp_path, monkeypatch, role="member", username="member@example.com")
    member.put(
        "/api/integrations/anthropic",
        json={"secret_value": SECRET, "account_label": "member workspace"},
        headers=_headers(),
    )

    deleted = member.delete("/api/integrations/anthropic", headers=_headers())
    assert deleted.status_code == 200
    assert deleted.json()["status"] == "deleted"
    assert deleted.json()["integration"]["configured"] is False
    assert SECRET not in deleted.text

    listed = member.get("/api/integrations")
    anthropic = [item for item in listed.json()["integrations"] if item["provider_id"] == "anthropic"][0]
    assert anthropic["configured"] is False
