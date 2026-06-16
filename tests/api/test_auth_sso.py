"""SSO/SNS auth contract tests.

Network exchange is mocked. These tests assert state-cookie handling, redirect
shape, and owner session issuance without real provider credentials.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, patch
from urllib.parse import parse_qs, urlparse

from app.api.security import COOKIE_NAME, decode_session
from app.services.sso import SsoProfile


def _configure_google(monkeypatch) -> None:
    monkeypatch.setenv("AUTOFOLIO_PUBLIC_BASE_URL", "http://testserver")
    monkeypatch.setenv("AUTOFOLIO_GOOGLE_CLIENT_ID", "google-client-id")
    monkeypatch.setenv("AUTOFOLIO_GOOGLE_CLIENT_SECRET", "google-client-secret")


def _enable_mock_sso(
    monkeypatch,
    *,
    email: str = "owner@example.com",
    name: str = "Owner",
) -> None:
    monkeypatch.setenv("AUTOFOLIO_PUBLIC_BASE_URL", "http://testserver")
    monkeypatch.setenv("AUTOFOLIO_SSO_MOCK_ENABLED", "1")
    monkeypatch.setenv("AUTOFOLIO_SSO_MOCK_EMAIL", email)
    monkeypatch.setenv("AUTOFOLIO_SSO_MOCK_NAME", name)


class TestSsoProviders:
    def test_provider_list_exposes_enabled_without_secrets(self, client, monkeypatch):
        _configure_google(monkeypatch)
        body = client.get("/api/auth/sso/providers").json()
        google = next(p for p in body["providers"] if p["id"] == "google")
        assert google == {
            "id": "google",
            "label": "Google",
            "kind": "oidc",
            "enabled": True,
        }
        assert "secret" not in str(body).lower()

    def test_provider_disabled_when_credentials_missing(self, client, monkeypatch):
        monkeypatch.delenv("AUTOFOLIO_GOOGLE_CLIENT_ID", raising=False)
        monkeypatch.delenv("AUTOFOLIO_GOOGLE_CLIENT_SECRET", raising=False)
        body = client.get("/api/auth/sso/providers").json()
        google = next(p for p in body["providers"] if p["id"] == "google")
        assert google["enabled"] is False

    def test_mock_provider_is_disabled_by_default(self, client, monkeypatch):
        monkeypatch.delenv("AUTOFOLIO_SSO_MOCK_ENABLED", raising=False)
        body = client.get("/api/auth/sso/providers").json()
        mock = next(p for p in body["providers"] if p["id"] == "mock")
        assert mock == {
            "id": "mock",
            "label": "Mock SSO",
            "kind": "mock",
            "enabled": False,
        }

    def test_mock_provider_can_be_enabled_without_secrets(self, client, monkeypatch):
        _enable_mock_sso(monkeypatch)
        body = client.get("/api/auth/sso/providers").json()
        mock = next(p for p in body["providers"] if p["id"] == "mock")
        assert mock == {
            "id": "mock",
            "label": "Mock SSO",
            "kind": "mock",
            "enabled": True,
        }
        assert "secret" not in str(body).lower()


class TestSsoLogin:
    def test_login_redirect_sets_state_cookie(self, client, monkeypatch):
        _configure_google(monkeypatch)
        resp = client.get("/api/auth/sso/google/login", follow_redirects=False)
        assert resp.status_code == 307
        assert "af_oauth_state" in resp.cookies

        location = resp.headers["location"]
        parsed = urlparse(location)
        query = parse_qs(parsed.query)
        assert parsed.netloc == "accounts.google.com"
        assert query["client_id"] == ["google-client-id"]
        assert query["redirect_uri"] == ["http://testserver/api/auth/sso/google/callback"]
        assert query["state"]

    def test_unknown_provider_404(self, client):
        resp = client.get("/api/auth/sso/unknown/login", follow_redirects=False)
        assert resp.status_code == 404

    def test_unconfigured_provider_503(self, client, monkeypatch):
        monkeypatch.delenv("AUTOFOLIO_NAVER_CLIENT_ID", raising=False)
        monkeypatch.delenv("AUTOFOLIO_NAVER_CLIENT_SECRET", raising=False)
        resp = client.get("/api/auth/sso/naver/login", follow_redirects=False)
        assert resp.status_code == 503

    def test_mock_login_redirects_to_internal_callback(self, client, monkeypatch):
        _enable_mock_sso(monkeypatch)
        resp = client.get("/api/auth/sso/mock/login", follow_redirects=False)
        assert resp.status_code == 307
        assert "af_oauth_state" in resp.cookies

        parsed = urlparse(resp.headers["location"])
        query = parse_qs(parsed.query)
        assert parsed.netloc == "testserver"
        assert parsed.path == "/api/auth/sso/mock/callback"
        assert query["code"] == ["mock"]
        assert query["state"]


class TestSsoCallback:
    def test_callback_issues_owner_session(self, client, monkeypatch):
        _configure_google(monkeypatch)
        login = client.get("/api/auth/sso/google/login", follow_redirects=False)
        state = parse_qs(urlparse(login.headers["location"]).query)["state"][0]

        profile = SsoProfile(
            provider="google",
            subject="sub-123",
            email="owner@example.com",
            name="Owner",
        )
        with patch("app.services.sso.exchange_code_for_profile", new=AsyncMock(return_value=profile)):
            resp = client.get(
                f"/api/auth/sso/google/callback?code=abc&state={state}",
                follow_redirects=False,
            )

        assert resp.status_code == 303
        assert resp.headers["location"] == "http://testserver/home"
        cookie = resp.cookies[COOKIE_NAME]
        session = decode_session(cookie)
        assert session is not None
        assert session["role"] == "owner"
        assert session["username"] == "owner@example.com"
        assert session["data_source"] == "sso:google"
        assert session["csrf_token"]

    def test_callback_rejects_bad_state(self, client, monkeypatch):
        _configure_google(monkeypatch)
        client.get("/api/auth/sso/google/login", follow_redirects=False)
        resp = client.get(
            "/api/auth/sso/google/callback?code=abc&state=wrong",
            follow_redirects=False,
        )
        assert resp.status_code == 400

    def test_callback_respects_allowed_email_gate(self, client, monkeypatch):
        _configure_google(monkeypatch)
        monkeypatch.setenv("AUTOFOLIO_SSO_ALLOWED_EMAILS", "allowed@example.com")
        login = client.get("/api/auth/sso/google/login", follow_redirects=False)
        state = parse_qs(urlparse(login.headers["location"]).query)["state"][0]
        profile = SsoProfile(
            provider="google",
            subject="sub-123",
            email="blocked@example.com",
            name="Blocked",
        )
        with patch("app.services.sso.exchange_code_for_profile", new=AsyncMock(return_value=profile)):
            resp = client.get(
                f"/api/auth/sso/google/callback?code=abc&state={state}",
                follow_redirects=False,
            )
        assert resp.status_code == 403

    def test_mock_callback_issues_owner_session_without_external_exchange(self, client, monkeypatch):
        _enable_mock_sso(monkeypatch, email="owner@example.com", name="Owner")
        login = client.get("/api/auth/sso/mock/login", follow_redirects=False)
        parsed = urlparse(login.headers["location"])

        resp = client.get(f"{parsed.path}?{parsed.query}", follow_redirects=False)

        assert resp.status_code == 303
        assert resp.headers["location"] == "http://testserver/home"
        cookie = resp.cookies[COOKIE_NAME]
        session = decode_session(cookie)
        assert session is not None
        assert session["role"] == "owner"
        assert session["username"] == "owner@example.com"
        assert session["data_source"] == "sso:mock"
        assert session["provider"] == "mock"
        assert session["csrf_token"]

    def test_mock_callback_respects_allowed_email_gate(self, client, monkeypatch):
        _enable_mock_sso(monkeypatch, email="blocked@example.com")
        monkeypatch.setenv("AUTOFOLIO_SSO_ALLOWED_EMAILS", "allowed@example.com")
        login = client.get("/api/auth/sso/mock/login", follow_redirects=False)
        parsed = urlparse(login.headers["location"])

        resp = client.get(f"{parsed.path}?{parsed.query}", follow_redirects=False)

        assert resp.status_code == 403

    def test_mock_callback_rejects_invalid_code(self, client, monkeypatch):
        _enable_mock_sso(monkeypatch)
        login = client.get("/api/auth/sso/mock/login", follow_redirects=False)
        state = parse_qs(urlparse(login.headers["location"]).query)["state"][0]

        resp = client.get(
            f"/api/auth/sso/mock/callback?code=not-mock&state={state}",
            follow_redirects=False,
        )

        assert resp.status_code == 502
