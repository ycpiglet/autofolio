"""Unit tests: investor_profile._ensure_tables() is a no-op on the PG backend.

These tests use monkeypatching / mocking only — no live Postgres connection is
required.  The SQLite path is tested implicitly by the full pytest suite (the
existing API tests exercise _ensure_tables() on every in-memory SQLite DB).
"""
from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_settings(database_url: str = ""):
    """Return a minimal settings-like object with the given database_url."""
    class FakeSettings:
        pass
    s = FakeSettings()
    s.database_url = database_url
    return s


# ---------------------------------------------------------------------------
# PG backend: _ensure_tables() must NOT touch get_connection
# ---------------------------------------------------------------------------

class TestEnsureTablesPgSkip:
    """When DATABASE_URL is a Postgres URL, _ensure_tables must be a no-op."""

    @pytest.mark.parametrize("pg_url", [
        "postgres://user:pw@host/db",
        "postgresql://user:pw@host/db",
        "POSTGRES://HOST/DB",
        "PostgreSQL://Host/DB",
    ])
    def test_pg_url_skips_get_connection(self, pg_url):
        """_ensure_tables() must not call get_connection when backend is Postgres."""
        import app.services.investor_profile as svc

        fake_settings = _make_settings(pg_url)
        with patch.object(svc, "settings", fake_settings), \
             patch.object(svc, "get_connection") as mock_conn:
            svc._ensure_tables()

        mock_conn.assert_not_called()

    @pytest.mark.parametrize("pg_url", [
        "postgres://user:pw@host/db",
        "postgresql://user:pw@host/db",
    ])
    def test_pg_url_skips_executescript(self, pg_url):
        """executescript (SQLite DDL) must never be called on the PG backend."""
        import app.services.investor_profile as svc

        fake_settings = _make_settings(pg_url)
        mock_conn_ctx = MagicMock()
        mock_conn_instance = MagicMock()
        mock_conn_ctx.__enter__ = MagicMock(return_value=mock_conn_instance)
        mock_conn_ctx.__exit__ = MagicMock(return_value=False)

        with patch.object(svc, "settings", fake_settings), \
             patch.object(svc, "get_connection", return_value=mock_conn_ctx):
            svc._ensure_tables()

        mock_conn_instance.executescript.assert_not_called()


# ---------------------------------------------------------------------------
# SQLite backend (DATABASE_URL unset / empty): _ensure_tables() runs normally
# ---------------------------------------------------------------------------

class TestEnsureTablesSqliteRuns:
    """When DATABASE_URL is unset/empty, _ensure_tables runs executescript."""

    @pytest.mark.parametrize("db_url", ["", None])
    def test_sqlite_path_calls_executescript(self, db_url):
        """_ensure_tables() must call executescript on the SQLite backend."""
        import app.services.investor_profile as svc

        fake_settings = _make_settings(db_url or "")
        mock_conn_ctx = MagicMock()
        mock_conn_instance = MagicMock()
        mock_conn_ctx.__enter__ = MagicMock(return_value=mock_conn_instance)
        mock_conn_ctx.__exit__ = MagicMock(return_value=False)

        with patch.object(svc, "settings", fake_settings), \
             patch.object(svc, "get_connection", return_value=mock_conn_ctx):
            svc._ensure_tables()

        mock_conn_instance.executescript.assert_called_once_with(svc._TABLE_SQL)


# ---------------------------------------------------------------------------
# is_postgres_url defaults — backend default is SQLite when DATABASE_URL unset
# ---------------------------------------------------------------------------

class TestBackendDefault:
    """Confirm the backend detection defaults to SQLite when DATABASE_URL is absent."""

    def test_empty_database_url_is_not_postgres(self):
        from app.database.pg_db import is_postgres_url
        assert is_postgres_url("") is False

    def test_none_database_url_is_not_postgres(self):
        from app.database.pg_db import is_postgres_url
        assert is_postgres_url(None) is False

    def test_sqlite_path_is_not_postgres(self):
        from app.database.pg_db import is_postgres_url
        assert is_postgres_url("trading_bot.db") is False

    def test_postgres_urls_detected(self):
        from app.database.pg_db import is_postgres_url
        assert is_postgres_url("postgres://host/db") is True
        assert is_postgres_url("postgresql://host/db") is True
