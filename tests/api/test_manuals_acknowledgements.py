"""Manual and acknowledgement API tests."""
from __future__ import annotations

from dataclasses import replace

from fastapi.testclient import TestClient

from app.api.main import create_app
from app.api.security import encode_session
from app.database.sqlite_db import initialize_database

CSRF = "csrf-manuals-test"


def _client(db_path, monkeypatch, *, role: str = "owner") -> TestClient:
    import app.config.settings as settings_mod
    import app.database.sqlite_db as sqlite_mod
    import app.services.acknowledgements as ack_mod
    import app.services.investor_profile as profile_mod

    test_settings = replace(settings_mod.settings, db_path=db_path)
    monkeypatch.setattr(settings_mod, "settings", test_settings)
    monkeypatch.setattr(sqlite_mod, "settings", test_settings)
    monkeypatch.setattr(ack_mod, "get_connection", sqlite_mod.get_connection)
    monkeypatch.setattr(profile_mod, "get_connection", sqlite_mod.get_connection)
    initialize_database(db_path)

    c = TestClient(create_app(), raise_server_exceptions=True)
    payload = {"role": role, "username": "testuser", "data_source": "backend", "csrf_token": CSRF}
    if role == "guest":
        payload = {"role": "guest", "data_source": "demo", "csrf_token": CSRF}
    c.cookies.set("af_session", encode_session(payload))
    return c


def _headers() -> dict[str, str]:
    return {"X-CSRF-Token": CSRF}


def test_owner_sees_private_manuals(tmp_path, monkeypatch):
    c = _client(tmp_path / "manuals.db", monkeypatch, role="owner")
    resp = c.get("/api/manuals")
    assert resp.status_code == 200
    slugs = {item["slug"] for item in resp.json()["manuals"]}
    assert "KIS-CONNECTION-MANUAL" in slugs
    assert "SAFETY-AND-RISK" in slugs


def test_member_only_sees_public_manuals(tmp_path, monkeypatch):
    c = _client(tmp_path / "manuals.db", monkeypatch, role="member")
    resp = c.get("/api/manuals")
    assert resp.status_code == 200
    manuals = resp.json()["manuals"]
    assert all(item["visibility"] == "public" for item in manuals)
    assert "KIS-CONNECTION-MANUAL" not in {item["slug"] for item in manuals}


def test_guest_cannot_list_manuals(tmp_path, monkeypatch):
    c = _client(tmp_path / "manuals.db", monkeypatch, role="guest")
    resp = c.get("/api/manuals")
    assert resp.status_code == 403


def test_private_manual_detail_forbidden_to_member(tmp_path, monkeypatch):
    c = _client(tmp_path / "manuals.db", monkeypatch, role="member")
    resp = c.get("/api/manuals/KIS-CONNECTION-MANUAL")
    assert resp.status_code == 403


def test_acknowledgement_status_and_record(tmp_path, monkeypatch):
    c = _client(tmp_path / "manuals.db", monkeypatch, role="owner")
    before = c.get("/api/acknowledgements/status").json()
    assert before["live_trading_acknowledged"] is False
    assert before["totp_recommended"] is True

    resp = c.post(
        "/api/acknowledgements",
        json={
            "kind": "live_trading_risk_v1",
            "document_slug": "SAFETY-AND-RISK",
            "document_version": "live-trading-risk-v1",
            "acknowledgement_text": "실전 거래 손실 가능성과 자동화 오류를 이해하며 책임은 계좌 소유자에게 있음을 확인합니다.",
        },
        headers=_headers(),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "recorded"

    after = c.get("/api/acknowledgements/status").json()
    assert after["live_trading_acknowledged"] is True
    assert after["latest_live_trading_ack_id"] == resp.json()["id"]


def test_member_can_record_own_acknowledgement(tmp_path, monkeypatch):
    c = _client(tmp_path / "manuals.db", monkeypatch, role="member")
    resp = c.post(
        "/api/acknowledgements",
        json={
            "kind": "live_trading_risk_v1",
            "document_slug": "SAFETY-AND-RISK",
            "document_version": "live-trading-risk-v1",
            "acknowledgement_text": "실전 거래 손실 가능성과 자동화 오류를 이해하며 책임은 계좌 소유자에게 있음을 확인합니다.",
        },
        headers=_headers(),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "recorded"


def test_short_live_ack_rejected(tmp_path, monkeypatch):
    c = _client(tmp_path / "manuals.db", monkeypatch, role="owner")
    resp = c.post(
        "/api/acknowledgements",
        json={
            "kind": "live_trading_risk_v1",
            "document_slug": "SAFETY-AND-RISK",
            "document_version": "live-trading-risk-v1",
            "acknowledgement_text": "확인",
        },
        headers=_headers(),
    )
    assert resp.status_code == 422
