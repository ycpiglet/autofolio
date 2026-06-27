"""Contract tests for GET /api/agents/research — per-symbol expert briefing.

Design:
- READ-ONLY endpoint: it must NOT persist a trade condition (propose() only
  suggests). We assert backend.add_condition is never invoked.
- All backend functions are monkeypatched (no network, no DB, no KIS keys).
- Approved member gets 200; guest → 403; no session → 401; a backend exception
  must surface as a non-200 (fail-loud, no silent empty).
"""
from __future__ import annotations

import pytest

from app.agents.research_agent import ConditionProposal


SAMPLE_GATE = {"symbol": "005930", "blocked": False, "reason": ""}

SAMPLE_PROPOSAL = ConditionProposal(
    symbol="005930",
    side="BUY",
    target_price=74_250.0,
    quantity=1,
    order_type="LIMIT",
    allow_market_fallback=False,
    rationale="현재가보다 1% 낮은 보수적 매수 대기 조건 예시. 재무 지표: PER 12.5, PBR 1.3.",
    risk_note="가격이 목표가에 도달해도 추가 하락 가능성이 있으므로 자동주문은 기본 OFF로 저장해야 함.",
)


@pytest.fixture()
def research_backend(mock_backend, monkeypatch):
    """Extend the shared mock_backend with research-specific fns."""
    monkeypatch.setattr(mock_backend, "disclosure_gate_state", lambda symbol: SAMPLE_GATE)
    monkeypatch.setattr(mock_backend, "propose", lambda symbol, side="BUY": SAMPLE_PROPOSAL)
    return mock_backend


class TestResearchHappyPath:
    def test_member_200(self, member_client, research_backend):
        resp = member_client.get("/api/agents/research?symbol=005930")
        assert resp.status_code == 200

    def test_guest_403(self, guest_client, research_backend):
        resp = guest_client.get("/api/agents/research?symbol=005930")
        assert resp.status_code == 403

    def test_response_shape(self, member_client, research_backend):
        body = member_client.get("/api/agents/research?symbol=005930").json()
        # Top-level keys
        for key in ("symbol", "name", "price", "fundamental", "disclosures",
                    "disclosure_gate", "proposal"):
            assert key in body, f"missing key {key}"
        assert body["symbol"] == "005930"
        assert body["name"] == "삼성전자"  # resolved from whitelist
        assert body["price"] == 75_000.0
        assert body["fundamental"] == {"per": 12.5, "pbr": 1.3}
        # disclosures is a TableResponse
        assert "columns" in body["disclosures"] and "rows" in body["disclosures"]
        # disclosure gate
        assert body["disclosure_gate"]["blocked"] is False
        # proposal fields
        prop = body["proposal"]
        assert prop["side"] == "BUY"
        assert prop["target_price"] == 74_250.0
        assert prop["order_type"] == "LIMIT"
        assert prop["allow_market_fallback"] is False
        assert "rationale" in prop and "risk_note" in prop

    def test_owner_200(self, owner_client, research_backend):
        resp = owner_client.get("/api/agents/research?symbol=005930")
        assert resp.status_code == 200

    def test_days_param_forwarded(self, member_client, research_backend, monkeypatch):
        import pandas as pd

        captured: dict = {}

        def fake_disclosures(symbol, days=1):
            captured["symbol"] = symbol
            captured["days"] = days
            return pd.DataFrame(columns=["date", "title"])

        monkeypatch.setattr(research_backend, "disclosures_df", fake_disclosures)
        member_client.get("/api/agents/research?symbol=005930&days=14")
        assert captured["days"] == 14
        assert captured["symbol"] == "005930"


class TestReadOnly:
    def test_propose_does_not_save_condition(self, member_client, research_backend, monkeypatch):
        """propose() suggests only; the endpoint must NOT persist a condition."""
        called = {"add": 0}

        def fail_add(*args, **kwargs):
            called["add"] += 1
            raise AssertionError("add_condition must NOT be called by research endpoint")

        monkeypatch.setattr(research_backend, "add_condition", fail_add)
        resp = member_client.get("/api/agents/research?symbol=005930")
        assert resp.status_code == 200
        assert called["add"] == 0


class TestAuthAndValidation:
    def test_401_without_session(self, client, research_backend):
        client.cookies.clear()
        resp = client.get("/api/agents/research?symbol=005930")
        assert resp.status_code == 401

    def test_invalid_symbol_422(self, member_client, research_backend):
        resp = member_client.get("/api/agents/research?symbol=" + "X" * 50)
        assert resp.status_code == 422

    def test_missing_symbol_422(self, member_client, research_backend):
        resp = member_client.get("/api/agents/research")
        assert resp.status_code == 422


class TestFailLoud:
    def test_backend_exception_is_non_200(self, error_member_client, mock_backend, monkeypatch):
        """A backend error must surface as a non-200 — no silent empty briefing."""
        def boom(symbol):
            raise RuntimeError("price feed down")

        monkeypatch.setattr(mock_backend, "price", boom)
        resp = error_member_client.get("/api/agents/research?symbol=005930")
        assert resp.status_code != 200
        assert resp.status_code >= 500


# ── TASK-087 A2: recommendation lock ─────────────────────────────────────────

class TestRecommendationLock:
    """Deployment flag OFF → research endpoint returns 403 recommendation_locked."""

    def test_research_blocked_when_flag_off(self, member_client, research_backend, monkeypatch):
        """AUTOFOLIO_RECOMMENDATION_ENABLED not set → 403 recommendation_locked."""
        monkeypatch.delenv("AUTOFOLIO_RECOMMENDATION_ENABLED", raising=False)
        resp = member_client.get("/api/agents/research?symbol=005930")
        assert resp.status_code == 403
        assert resp.json()["detail"]["status"] == "recommendation_locked"

    def test_research_allowed_when_flag_on(self, member_client, research_backend, monkeypatch):
        """AUTOFOLIO_RECOMMENDATION_ENABLED=1 → 200 (normal operation)."""
        monkeypatch.setenv("AUTOFOLIO_RECOMMENDATION_ENABLED", "1")
        resp = member_client.get("/api/agents/research?symbol=005930")
        assert resp.status_code == 200
