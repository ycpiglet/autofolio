"""Investor profile survey API tests."""
from __future__ import annotations

from dataclasses import replace

from fastapi.testclient import TestClient

from app.api.main import create_app
from app.api.security import encode_session
from app.database.sqlite_db import initialize_database

CSRF = "csrf-profile-test"
CONFIRMATION_TEXT = "위 항목을 모두 이해했습니다."
SIGNATURE_DATA_URL = "data:image/png;base64," + ("a" * 160)


def _owner_session(username: str = "alice") -> str:
    return encode_session(
        {
            "role": "owner",
            "username": username,
            "data_source": "backend",
            "csrf_token": CSRF,
        }
    )


def _member_session(username: str = "member-alice") -> str:
    return encode_session(
        {
            "role": "member",
            "username": username,
            "data_source": "backend",
            "csrf_token": CSRF,
        }
    )


def _guest_session() -> str:
    return encode_session(
        {"role": "guest", "data_source": "demo", "csrf_token": CSRF}
    )


def _client(db_path, monkeypatch, *, owner: bool | None = True, role: str | None = None) -> TestClient:
    import app.config.settings as settings_mod
    import app.database.sqlite_db as sqlite_mod

    test_settings = replace(settings_mod.settings, db_path=db_path)
    monkeypatch.setattr(settings_mod, "settings", test_settings)
    monkeypatch.setattr(sqlite_mod, "settings", test_settings)
    initialize_database(db_path)
    c = TestClient(create_app(), raise_server_exceptions=True)
    if role == "member":
        c.cookies.set("af_session", _member_session())
    elif owner is True:
        c.cookies.set("af_session", _owner_session())
    elif owner is False:
        c.cookies.set("af_session", _guest_session())
    return c


def _headers() -> dict[str, str]:
    return {"X-CSRF-Token": CSRF}


def _answers() -> dict:
    return {
        "investment_goal": "growth",
        "time_horizon": "five_plus",
        "capital_need": "separate_savings",
        "loss_response": "hold_20",
        "volatility_preference": "balanced",
        "experience": ["fund_etf", "domestic_stock"],
        "knowledge_diversification": "reduces_single_risk",
        "knowledge_drawdown": "largest_drop",
        "knowledge_order_type": "limit_controls_price",
        "automation_preference": "suggestions",
        "approval_preference": "every_time",
        "product_preference": ["etf", "large_cap"],
        "discomfort": ["weak_explanation", "too_many_alerts"],
        "satisfaction_focus": ["plan_adherence", "explainability"],
        "ack_loss_risk": True,
        "ack_not_advice": True,
        "ack_automation_scope": True,
        "ack_no_liability": True,
        "ack_data_use": True,
        "legal_signature": {
            "name": "홍길동",
            "confirmation_text": CONFIRMATION_TEXT,
            "signature_data_url": SIGNATURE_DATA_URL,
            "signed_at": "2026-06-18T23:30:00+09:00",
        },
    }


def test_get_profile_incomplete_shape(tmp_path, monkeypatch):
    c = _client(tmp_path / "profile.db", monkeypatch)
    resp = c.get("/api/profile/investor")
    assert resp.status_code == 200
    body = resp.json()
    assert body["completed"] is False
    assert body["risk_type"] == "미완료"
    assert body["recommended_autonomy_level"] == "L0"
    assert "scores" in body


def test_guest_cannot_get_profile(tmp_path, monkeypatch):
    c = _client(tmp_path / "profile.db", monkeypatch, owner=False)
    resp = c.get("/api/profile/investor")
    assert resp.status_code == 403


def test_get_survey_definition(tmp_path, monkeypatch):
    c = _client(tmp_path / "profile.db", monkeypatch)
    resp = c.get("/api/profile/survey")
    assert resp.status_code == 200
    body = resp.json()
    assert body["version"] == "investor-profile-v2"
    assert len(body["questions"]) >= 12
    assert body["questions"][0]["id"] == "investment_goal"
    assert "categories" in body
    assert len(body["categories"]) >= 5
    assert all("category" in question for question in body["questions"])


def test_get_survey_definition_without_session(tmp_path, monkeypatch):
    c = _client(tmp_path / "profile.db", monkeypatch, owner=None)
    resp = c.get("/api/profile/survey")
    assert resp.status_code == 200
    assert resp.json()["version"] == "investor-profile-v2"


def test_submit_survey_persists_profile(tmp_path, monkeypatch):
    c = _client(tmp_path / "profile.db", monkeypatch)
    resp = c.post(
        "/api/profile/survey",
        json={"answers": _answers()},
        headers=_headers(),
    )
    assert resp.status_code == 200
    profile = resp.json()["profile"]
    assert profile["completed"] is True
    assert profile["risk_type"] in {"안정형", "안정추구형", "위험중립형", "적극투자형", "공격투자형"}
    assert profile["knowledge_level"] in {"입문", "기초", "경험자", "전문가"}
    assert profile["recommended_max_equity_pct"] > 0

    current = c.get("/api/profile/investor").json()
    assert current["completed"] is True
    assert current["risk_type"] == profile["risk_type"]


def test_member_can_submit_own_survey(tmp_path, monkeypatch):
    c = _client(tmp_path / "profile.db", monkeypatch, role="member")
    resp = c.post(
        "/api/profile/survey",
        json={"answers": _answers()},
        headers=_headers(),
    )
    assert resp.status_code == 200
    assert resp.json()["profile"]["completed"] is True


def test_submit_requires_acknowledgements(tmp_path, monkeypatch):
    c = _client(tmp_path / "profile.db", monkeypatch)
    answers = _answers()
    answers["ack_loss_risk"] = False
    resp = c.post(
        "/api/profile/survey",
        json={"answers": answers},
        headers=_headers(),
    )
    assert resp.status_code == 422


def test_submit_requires_signature(tmp_path, monkeypatch):
    c = _client(tmp_path / "profile.db", monkeypatch)
    answers = _answers()
    answers["legal_signature"] = {
        "name": "홍길동",
        "confirmation_text": CONFIRMATION_TEXT,
        "signature_data_url": "",
        "signed_at": "2026-06-18T23:30:00+09:00",
    }
    resp = c.post(
        "/api/profile/survey",
        json={"answers": answers},
        headers=_headers(),
    )
    assert resp.status_code == 422


def test_submit_requires_exact_confirmation_text(tmp_path, monkeypatch):
    c = _client(tmp_path / "profile.db", monkeypatch)
    answers = _answers()
    answers["legal_signature"] = {
        "name": "홍길동",
        "confirmation_text": "동의합니다",
        "signature_data_url": SIGNATURE_DATA_URL,
        "signed_at": "2026-06-18T23:30:00+09:00",
    }
    resp = c.post(
        "/api/profile/survey",
        json={"answers": answers},
        headers=_headers(),
    )
    assert resp.status_code == 422


def test_guest_cannot_submit_survey(tmp_path, monkeypatch):
    c = _client(tmp_path / "profile.db", monkeypatch, owner=False)
    resp = c.post(
        "/api/profile/survey",
        json={"answers": _answers()},
        headers=_headers(),
    )
    assert resp.status_code == 403


def test_condition_save_requires_completed_profile(tmp_path, monkeypatch):
    c = _client(tmp_path / "profile.db", monkeypatch)
    resp = c.post(
        "/api/trade/conditions",
        json={"symbol": "005930", "side": "BUY", "target_price": 70000, "quantity": 1},
        headers=_headers(),
    )
    assert resp.status_code == 428
    assert resp.json()["detail"]["status"] == "profile_required"


def test_run_once_requires_completed_profile(tmp_path, monkeypatch):
    c = _client(tmp_path / "profile.db", monkeypatch)
    resp = c.post("/api/engine/run-once", headers=_headers())
    assert resp.status_code == 428


def test_checkin_after_survey(tmp_path, monkeypatch):
    c = _client(tmp_path / "profile.db", monkeypatch)
    c.post("/api/profile/survey", json={"answers": _answers()}, headers=_headers())
    resp = c.post(
        "/api/profile/checkin",
        json={
            "trigger_type": "monthly",
            "satisfaction_score": 4,
            "confidence_score": 3,
            "stress_score": 2,
            "automation_adjustment": "same",
            "notes": "설명은 충분하고 알림은 적당함",
        },
        headers=_headers(),
    )
    assert resp.status_code == 200
    profile = resp.json()["profile"]
    assert profile["satisfaction_score"] == 4
    assert profile["confidence_score"] == 3
    assert profile["stress_score"] == 2


def test_override_ack_records(tmp_path, monkeypatch):
    c = _client(tmp_path / "profile.db", monkeypatch)
    resp = c.post(
        "/api/profile/override-ack",
        json={
            "symbol": "005930",
            "action": "condition_save",
            "reason": "profile_mismatch",
            "acknowledgement_text": "위험 불일치를 확인하고 진행합니다.",
        },
        headers=_headers(),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "recorded"
    assert resp.json()["id"] >= 1
