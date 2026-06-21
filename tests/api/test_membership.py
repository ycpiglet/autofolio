"""Membership approval API tests."""
from __future__ import annotations

import importlib

from fastapi.testclient import TestClient

from app.api.main import create_app
from app.api.security import encode_session

CSRF = "csrf-membership-test"


def _client(
    tmp_path,
    monkeypatch,
    *,
    role: str | None = None,
    clear_bank_env: bool = True,
) -> TestClient:
    monkeypatch.setenv("AUTOFOLIO_HOME", str(tmp_path))
    if clear_bank_env:
        monkeypatch.delenv("AUTOFOLIO_MEMBERSHIP_BANK_NAME", raising=False)
        monkeypatch.delenv("AUTOFOLIO_MEMBERSHIP_ACCOUNT_HOLDER", raising=False)
        monkeypatch.delenv("AUTOFOLIO_MEMBERSHIP_BANK_ACCOUNT", raising=False)

    from app.ui import vault as vault_mod
    from app.services import auth_service as auth_mod
    from app.services import membership as membership_mod

    importlib.reload(vault_mod)
    importlib.reload(auth_mod)
    importlib.reload(membership_mod)

    c = TestClient(create_app(), raise_server_exceptions=True)
    if role == "owner":
        c.cookies.set(
            "af_session",
            encode_session(
                {
                    "role": "owner",
                    "username": "owner",
                    "data_source": "backend",
                    "csrf_token": CSRF,
                }
            ),
        )
    elif role == "guest":
        c.cookies.set(
            "af_session",
            encode_session({"role": "guest", "data_source": "demo", "csrf_token": CSRF}),
        )
    elif role == "member":
        c.cookies.set(
            "af_session",
            encode_session(
                {
                    "role": "member",
                    "username": "approved@example.com",
                    "data_source": "backend",
                    "csrf_token": CSRF,
                }
            ),
        )
    return c


def _payload() -> dict[str, str]:
    return {
        "display_name": "홍길동",
        "contact": "tester@example.com",
        "plan": "pilot_monthly",
        "referral_source": "owner_referral",
        "note": "테스트 신청",
    }


def _headers() -> dict[str, str]:
    return {"X-CSRF-Token": CSRF}


def test_public_signup_request_does_not_require_session(tmp_path, monkeypatch):
    c = _client(tmp_path, monkeypatch)
    resp = c.post("/api/membership/requests", json=_payload())
    assert resp.status_code == 201

    body = resp.json()
    assert body["request_id"].startswith("mrq_")
    assert body["status"] == "requested"
    assert body["price_krw"] == 20000
    assert body["deposit_instruction"] is None
    assert "af_session" not in resp.cookies


def test_duplicate_open_contact_returns_existing_request(tmp_path, monkeypatch):
    c = _client(tmp_path, monkeypatch)
    first = c.post("/api/membership/requests", json=_payload()).json()
    second = c.post("/api/membership/requests", json=_payload()).json()
    assert second["request_id"] == first["request_id"]
    assert second["message"] == "이미 접수된 가입 승인 신청입니다."


def test_owner_can_list_and_move_to_deposit_pending(tmp_path, monkeypatch):
    public = _client(tmp_path, monkeypatch, clear_bank_env=False)
    created = public.post("/api/membership/requests", json=_payload()).json()

    owner = _client(tmp_path, monkeypatch, role="owner", clear_bank_env=False)
    list_resp = owner.get("/api/membership/requests")
    assert list_resp.status_code == 200
    assert list_resp.json()["requests"][0]["request_id"] == created["request_id"]

    transition = owner.post(
        f"/api/membership/requests/{created['request_id']}/transition",
        json={
            "status": "deposit_pending",
            "evidence_type": "owner_verified_person",
            "note": "지인 확인 완료",
        },
        headers=_headers(),
    )
    assert transition.status_code == 200

    body = transition.json()
    assert body["status"] == "deposit_pending"
    assert body["deposit_instruction"]["deposit_code"].startswith("AF-")
    assert body["deposit_instruction"]["price_krw"] == 20000
    assert body["deposit_instruction"]["account_configured"] is False
    assert body["events"][-1]["previous_status"] == "requested"
    assert body["events"][-1]["next_status"] == "deposit_pending"


def test_applicant_can_lookup_deposit_instruction_after_owner_verification(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFOLIO_MEMBERSHIP_BANK_NAME", "테스트은행")
    monkeypatch.setenv("AUTOFOLIO_MEMBERSHIP_ACCOUNT_HOLDER", "Autofolio")
    monkeypatch.setenv("AUTOFOLIO_MEMBERSHIP_BANK_ACCOUNT", "000-0000-0000")
    public = _client(tmp_path, monkeypatch, clear_bank_env=False)
    created = public.post("/api/membership/requests", json=_payload()).json()

    owner = _client(tmp_path, monkeypatch, role="owner", clear_bank_env=False)
    owner.post(
        f"/api/membership/requests/{created['request_id']}/transition",
        json={
            "status": "deposit_pending",
            "evidence_type": "owner_verified_person",
            "note": "internal owner note must not leak",
        },
        headers=_headers(),
    )

    lookup = public.post(
        "/api/membership/requests/status",
        json={"request_id": created["request_id"], "contact": _payload()["contact"]},
    )
    assert lookup.status_code == 200
    body = lookup.json()
    assert body["status"] == "deposit_pending"
    assert body["deposit_instruction"]["price_krw"] == 20000
    assert body["deposit_instruction"]["deposit_code"].startswith("AF-")
    assert body["deposit_instruction"]["bank_name"] == "테스트은행"
    assert body["deposit_instruction"]["account_holder"] == "Autofolio"
    assert body["deposit_instruction"]["account_number"] == "000-0000-0000"
    assert body["events"] == []
    assert body["account_grant"] is None
    assert body["subscription_grant"] is None
    assert "internal owner note" not in lookup.text
    assert "af_session" not in lookup.cookies


def test_applicant_status_lookup_requires_request_id_and_contact_match(tmp_path, monkeypatch):
    public = _client(tmp_path, monkeypatch)
    created = public.post("/api/membership/requests", json=_payload()).json()

    wrong_contact = public.post(
        "/api/membership/requests/status",
        json={"request_id": created["request_id"], "contact": "other@example.com"},
    )
    assert wrong_contact.status_code == 404

    missing = public.post(
        "/api/membership/requests/status",
        json={"request_id": "mrq_missing", "contact": _payload()["contact"]},
    )
    assert missing.status_code == 404


def test_runtime_bank_instruction_fields_are_env_only(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFOLIO_MEMBERSHIP_BANK_NAME", "테스트은행")
    monkeypatch.setenv("AUTOFOLIO_MEMBERSHIP_ACCOUNT_HOLDER", "Autofolio")
    monkeypatch.setenv("AUTOFOLIO_MEMBERSHIP_BANK_ACCOUNT", "000-0000-0000")
    public = _client(tmp_path, monkeypatch, clear_bank_env=False)
    created = public.post("/api/membership/requests", json=_payload()).json()

    monkeypatch.setenv("AUTOFOLIO_MEMBERSHIP_BANK_NAME", "테스트은행")
    monkeypatch.setenv("AUTOFOLIO_MEMBERSHIP_ACCOUNT_HOLDER", "Autofolio")
    monkeypatch.setenv("AUTOFOLIO_MEMBERSHIP_BANK_ACCOUNT", "000-0000-0000")
    owner = _client(tmp_path, monkeypatch, role="owner", clear_bank_env=False)
    transition = owner.post(
        f"/api/membership/requests/{created['request_id']}/transition",
        json={"status": "deposit_pending"},
        headers=_headers(),
    )
    instruction = transition.json()["deposit_instruction"]
    assert instruction["account_configured"] is True
    assert instruction["bank_name"] == "테스트은행"
    assert instruction["account_holder"] == "Autofolio"
    assert instruction["account_number"] == "000-0000-0000"


def test_guest_and_anonymous_cannot_review_requests(tmp_path, monkeypatch):
    c = _client(tmp_path, monkeypatch)
    assert c.get("/api/membership/requests").status_code == 401

    guest = _client(tmp_path, monkeypatch, role="guest")
    assert guest.get("/api/membership/requests").status_code == 403

    member = _client(tmp_path, monkeypatch, role="member")
    assert member.get("/api/membership/requests").status_code == 403


def test_owner_can_read_membership_production_readiness(tmp_path, monkeypatch):
    owner = _client(tmp_path, monkeypatch, role="owner")
    resp = owner.get("/api/membership/readiness")
    assert resp.status_code == 200

    body = resp.json()
    assert body["can_launch"] is False
    assert body["mode"] == "local_prototype"
    assert any(item["id"] == "local_membership_flow" and item["state"] == "pass" for item in body["items"])
    assert any(item["id"] == "production_contract" and item["state"] == "pass" for item in body["items"])
    assert any(item["id"] == "payment_evidence_policy" and item["state"] == "pass" for item in body["items"])
    assert any(item["id"] == "tenant_isolation_matrix" and item["state"] == "pass" for item in body["items"])
    assert any(item["id"] == "production_secret_policy" and item["state"] == "pass" for item in body["items"])
    assert any(item["id"] == "per_user_engine_safety_contract" and item["state"] == "pass" for item in body["items"])
    pass_ids = {item["id"] for item in body["items"] if item["state"] == "pass"}
    assert {
        "supabase_staging_field_map",
        "payment_recognition_decision",
        "production_secret_store_plan",
        "staging_deploy_preflight",
        "staging_env_inventory",
        "railway_backend_readiness",
        "staging_persistent_storage_decision",
        "supabase_migration_review_packet",
        "supabase_apply_evidence_checklist",
        "kis_terms_review_packet",
    }.issubset(pass_ids)
    assert any(item["id"] == "supabase_schema" and item["state"] == "block" for item in body["items"])
    block_ids = {item["id"] for item in body["items"] if item["state"] == "block"}
    assert {
        "supabase_schema",
        "rls_user_isolation",
        "production_secret_storage",
        "payment_recognition",
        "per_user_engine_safety",
        "external_deploy",
    }.issubset(block_ids)
    assert "SUPABASE" not in str(body)
    assert set(body["environment_flags"]) == {
        "supabase_url_present",
        "membership_bank_runtime_config_present",
        "guest_demo_enabled",
        "local_auto_register_enabled",
    }


def test_membership_readiness_is_owner_only(tmp_path, monkeypatch):
    anon = _client(tmp_path, monkeypatch)
    assert anon.get("/api/membership/readiness").status_code == 401

    guest = _client(tmp_path, monkeypatch, role="guest")
    assert guest.get("/api/membership/readiness").status_code == 403

    member = _client(tmp_path, monkeypatch, role="member")
    assert member.get("/api/membership/readiness").status_code == 403


def test_transition_requires_owner_csrf(tmp_path, monkeypatch):
    public = _client(tmp_path, monkeypatch)
    created = public.post("/api/membership/requests", json=_payload()).json()
    owner = _client(tmp_path, monkeypatch, role="owner")

    no_csrf = owner.post(
        f"/api/membership/requests/{created['request_id']}/transition",
        json={"status": "deposit_pending"},
    )
    assert no_csrf.status_code == 403

    guest = _client(tmp_path, monkeypatch, role="guest")
    guest_resp = guest.post(
        f"/api/membership/requests/{created['request_id']}/transition",
        json={"status": "deposit_pending"},
        headers=_headers(),
    )
    assert guest_resp.status_code == 403


def test_owner_can_activate_after_deposit_pending(tmp_path, monkeypatch):
    public = _client(tmp_path, monkeypatch)
    created = public.post("/api/membership/requests", json=_payload()).json()
    owner = _client(tmp_path, monkeypatch, role="owner")

    owner.post(
        f"/api/membership/requests/{created['request_id']}/transition",
        json={"status": "deposit_pending"},
        headers=_headers(),
    )
    active = owner.post(
        f"/api/membership/requests/{created['request_id']}/transition",
        json={
            "status": "active",
            "evidence_type": "manual_bank_app_check",
            "note": "입금 확인",
            "grant_days": 30,
        },
        headers=_headers(),
    )
    assert active.status_code == 200
    body = active.json()
    assert body["status"] == "active"
    assert body["activated_at"]
    assert body["grant_expires_at"]
    assert body["subscription_grant"]["plan"] == "pilot_monthly"
    assert body["account_grant"] is None
    assert body["events"][-1]["evidence_type"] == "manual_bank_app_check"


def test_owner_can_activate_and_create_local_login_account(tmp_path, monkeypatch):
    public = _client(tmp_path, monkeypatch)
    created = public.post("/api/membership/requests", json=_payload()).json()
    owner = _client(tmp_path, monkeypatch, role="owner")

    owner.post(
        f"/api/membership/requests/{created['request_id']}/transition",
        json={"status": "deposit_pending"},
        headers=_headers(),
    )
    active = owner.post(
        f"/api/membership/requests/{created['request_id']}/transition",
        json={
            "status": "active",
            "evidence_type": "manual_bank_app_check",
            "note": "입금 확인",
            "grant_days": 30,
            "login_username": "approved@example.com",
            "initial_password": "TempPass123!",
        },
        headers=_headers(),
    )
    assert active.status_code == 200
    body = active.json()
    assert body["status"] == "active"
    assert body["account_grant"] == {
        "username": "approved@example.com",
        "role": "member",
        "created_at": body["activated_at"],
        "password_set": True,
    }
    assert body["subscription_grant"]["ends_at"] == body["grant_expires_at"]
    assert "TempPass123!" not in active.text

    login_client = _client(tmp_path, monkeypatch)
    login = login_client.post(
        "/api/auth/login",
        json={"username": "approved@example.com", "password": "TempPass123!"},
    )
    assert login.status_code == 200
    assert login.json()["username"] == "approved@example.com"
    assert login.json()["role"] == "member"

    from app.ui import vault as vault_mod

    stored = vault_mod.load()["users"]["approved@example.com"]
    assert stored["source"] == "membership_approval"
    assert stored["membership_request_id"] == created["request_id"]
    assert stored["hash"]
    assert stored["salt"]
    assert "TempPass123!" not in str(stored)


def test_owner_can_recognize_deposit_code_from_pasted_statement(tmp_path, monkeypatch):
    public = _client(tmp_path, monkeypatch)
    created = public.post("/api/membership/requests", json=_payload()).json()
    owner = _client(tmp_path, monkeypatch, role="owner")

    pending = owner.post(
        f"/api/membership/requests/{created['request_id']}/transition",
        json={"status": "deposit_pending"},
        headers=_headers(),
    ).json()
    code = pending["deposit_instruction"]["deposit_code"]

    statement = f"2026-06-19 홍길동 {code} 입금 20,000원 123456789012"
    recognized = owner.post(
        "/api/membership/deposits/recognize",
        json={"source_text": statement, "min_confidence": 80},
        headers=_headers(),
    )
    assert recognized.status_code == 200
    body = recognized.json()
    assert body["scanned_lines"] == 1
    assert body["candidate_requests"] == 1
    assert body["matches"][0]["request_id"] == created["request_id"]
    assert body["matches"][0]["confidence"] == 100
    assert body["matches"][0]["reasons"] == ["deposit_code", "amount", "display_name"]
    assert body["matches"][0]["suggested_evidence_type"] == "code_assisted_deposit_match"
    assert "123456789012" not in body["matches"][0]["matched_text_excerpt"]

    from app.ui import vault as vault_mod

    persisted = str(vault_mod.load())
    assert statement not in persisted


def test_deposit_recognition_ignores_non_pending_requests(tmp_path, monkeypatch):
    public = _client(tmp_path, monkeypatch)
    created = public.post("/api/membership/requests", json=_payload()).json()
    owner = _client(tmp_path, monkeypatch, role="owner")
    request = owner.get(f"/api/membership/requests/{created['request_id']}").json()
    code = request["deposit_instruction"]
    assert code is None

    recognized = owner.post(
        "/api/membership/deposits/recognize",
        json={"source_text": "홍길동 AF-000000 20,000원", "min_confidence": 1},
        headers=_headers(),
    )
    assert recognized.status_code == 200
    assert recognized.json()["candidate_requests"] == 0
    assert recognized.json()["matches"] == []


def test_deposit_recognition_requires_owner_csrf(tmp_path, monkeypatch):
    public = _client(tmp_path, monkeypatch)
    public.post("/api/membership/requests", json=_payload()).json()

    owner = _client(tmp_path, monkeypatch, role="owner")
    no_csrf = owner.post(
        "/api/membership/deposits/recognize",
        json={"source_text": "AF-000000 20,000원"},
    )
    assert no_csrf.status_code == 403

    member = _client(tmp_path, monkeypatch, role="member")
    member_resp = member.post(
        "/api/membership/deposits/recognize",
        json={"source_text": "AF-000000 20,000원"},
        headers=_headers(),
    )
    assert member_resp.status_code == 403


def test_invalid_transition_rejected(tmp_path, monkeypatch):
    public = _client(tmp_path, monkeypatch)
    created = public.post("/api/membership/requests", json=_payload()).json()
    owner = _client(tmp_path, monkeypatch, role="owner")

    active = owner.post(
        f"/api/membership/requests/{created['request_id']}/transition",
        json={"status": "active"},
        headers=_headers(),
    )
    assert active.status_code == 200

    backwards = owner.post(
        f"/api/membership/requests/{created['request_id']}/transition",
        json={"status": "deposit_pending"},
        headers=_headers(),
    )
    assert backwards.status_code == 422
