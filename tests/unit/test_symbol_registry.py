"""Tests for expanded symbol registry and resolve_symbol_name()."""
from __future__ import annotations

import pytest


# ── Registry expansion ───────────────────────────────────────────────────────

class TestSeedRegistry:
    def test_seed_has_30_entries(self):
        from app.services.backend import _SEED
        assert len(_SEED) == 30, f"Expected 30 seed entries, got {len(_SEED)}"

    def test_seed_no_duplicates(self):
        from app.services.backend import _SEED
        codes = [s[0] for s in _SEED]
        assert len(codes) == len(set(codes)), "Duplicate codes in _SEED"

    def test_seed_contains_required_symbols(self):
        from app.services.backend import _SEED
        codes = {s[0] for s in _SEED}
        required = {
            "005930",  # 삼성전자
            "000660",  # SK하이닉스
            "005380",  # 현대차
            "005490",  # POSCO홀딩스
            "035420",  # NAVER
            "035720",  # 카카오
            "051910",  # LG화학
            "006400",  # 삼성SDI
            "068270",  # 셀트리온
            "000270",  # 기아
            "105560",  # KB금융
            "055550",  # 신한지주
            "086790",  # 하나금융지주
            "012330",  # 현대모비스
            "028260",  # 삼성물산
            "066570",  # LG전자
            "096770",  # SK이노베이션
            "034730",  # SK
            "015760",  # 한국전력
            "017670",  # SK텔레콤
            "009150",  # 삼성전기
            "010130",  # 고려아연
            "207940",  # 삼성바이오로직스
            "373220",  # LG에너지솔루션
            "000810",  # 삼성화재
            "069500",  # KODEX 200
            "102110",  # TIGER 200
            "360750",  # TIGER 미국S&P500
            "114260",  # KODEX 국고채3년
            "133690",  # TIGER 미국나스닥100
        }
        missing = required - codes
        assert not missing, f"Missing from _SEED: {missing}"

    def test_seed_has_names(self):
        from app.services.backend import _SEED
        for sym, name, role in _SEED:
            assert name, f"Empty name for symbol {sym}"
            assert sym, "Empty symbol code"

    def test_default_meta_covers_seed(self):
        from app.services.backend import _SEED, _DEFAULT_SYMBOL_META
        seed_codes = {s[0] for s in _SEED}
        for code in seed_codes:
            assert code in _DEFAULT_SYMBOL_META, f"{code} missing from _DEFAULT_SYMBOL_META"
            meta = _DEFAULT_SYMBOL_META[code]
            assert "name" in meta and meta["name"], f"Empty name in meta for {code}"
            assert "asset_class" in meta, f"Missing asset_class for {code}"
            assert "sector" in meta, f"Missing sector for {code}"


# ── resolve_symbol_name ──────────────────────────────────────────────────────

class TestResolveSymbolName:
    def test_known_code_from_meta(self, monkeypatch):
        from app.services import backend
        # Bypass _ctx() so no DB is needed
        monkeypatch.setattr(backend, "_ctx", lambda: _ctx_stub())
        # Clear cache
        with backend._name_cache_lock:
            backend._name_cache.clear()
        name = backend.resolve_symbol_name("005930")
        assert name == "삼성전자"

    def test_unknown_code_returns_code(self, monkeypatch):
        from app.services import backend
        monkeypatch.setattr(backend, "_ctx", lambda: _ctx_stub())
        with backend._name_cache_lock:
            backend._name_cache.clear()
        name = backend.resolve_symbol_name("999999")
        assert name == "999999"

    def test_empty_string_returns_empty(self, monkeypatch):
        from app.services import backend
        monkeypatch.setattr(backend, "_ctx", lambda: _ctx_stub())
        with backend._name_cache_lock:
            backend._name_cache.clear()
        assert backend.resolve_symbol_name("") == ""

    def test_whitelist_db_takes_priority(self, monkeypatch):
        from app.services import backend

        class Repo:
            def list_whitelist_symbols(self, **kw):
                return [{"symbol": "005930", "name": "삼성전자(커스텀)"}]

        monkeypatch.setattr(backend, "_ctx", lambda: (Repo(), None, None, None))
        with backend._name_cache_lock:
            backend._name_cache.clear()
        name = backend.resolve_symbol_name("005930")
        assert name == "삼성전자(커스텀)"

    def test_cache_populated_after_first_call(self, monkeypatch):
        from app.services import backend
        monkeypatch.setattr(backend, "_ctx", lambda: _ctx_stub())
        with backend._name_cache_lock:
            backend._name_cache.clear()
        backend.resolve_symbol_name("000660")
        with backend._name_cache_lock:
            assert "000660" in backend._name_cache

    def test_resolve_map_returns_dict(self, monkeypatch):
        from app.services import backend
        monkeypatch.setattr(backend, "_ctx", lambda: _ctx_stub())
        with backend._name_cache_lock:
            backend._name_cache.clear()
        result = backend.resolve_symbol_name_map(["005930", "000660", "999999"])
        assert result["005930"] == "삼성전자"
        assert result["000660"] == "SK하이닉스"
        assert result["999999"] == "999999"

    def test_all_seed_codes_resolve_to_name(self, monkeypatch):
        from app.services import backend
        monkeypatch.setattr(backend, "_ctx", lambda: _ctx_stub())
        with backend._name_cache_lock:
            backend._name_cache.clear()
        for code, expected_name, _ in backend._SEED:
            name = backend.resolve_symbol_name(code)
            assert name != code, f"Code {code} resolved to itself (not to '{expected_name}')"
            assert name, f"Empty name for {code}"


# ── recent_fills name resolution ─────────────────────────────────────────────

class TestRecentFillsNameResolution:
    def test_fills_symbol_column_shows_name(self, monkeypatch):
        import pandas as pd
        from app.services import backend

        sample_logs = pd.DataFrame([{
            "order_status": "FILLED",
            "symbol": "005930",
            "side": "BUY",
            "quantity": 10,
            "filled_quantity": 10,
            "filled_price": 72000,
            "filled_at": "2026-06-25 09:05:00",
            "created_at": "2026-06-25 09:05:00",
            "order_price": 72000,
        }])

        monkeypatch.setattr(backend, "list_order_logs", lambda **kw: sample_logs)
        monkeypatch.setattr(backend, "_ctx", lambda: _ctx_stub())
        with backend._name_cache_lock:
            backend._name_cache.clear()

        df = backend.recent_fills(limit=5)
        assert not df.empty
        assert "종목" in df.columns
        # Should show name, not code
        assert df["종목"].iloc[0] == "삼성전자"


# ── list_conditions name resolution ─────────────────────────────────────────

class TestConditionsNameResolution:
    def test_conditions_symbol_column_shows_name(self, monkeypatch):
        from app.services import backend

        class Repo:
            def list_whitelist_symbols(self, **kw):
                return []

            def list_conditions(self):
                return [{
                    "symbol": "000660",
                    "side": "BUY",
                    "target_price": 130000,
                    "quantity": 5,
                    "order_type": "LIMIT",
                    "status": "ACTIVE",
                    "created_at": "2026-06-25 10:00:00",
                }]

        monkeypatch.setattr(backend, "_ctx", lambda: (Repo(), None, None, None))
        with backend._name_cache_lock:
            backend._name_cache.clear()

        df = backend.list_conditions()
        assert not df.empty
        assert "종목" in df.columns
        # Should show name, not code
        assert df["종목"].iloc[0] == "SK하이닉스"


# ── Helpers ──────────────────────────────────────────────────────────────────

def _ctx_stub():
    """Stub _ctx() returning a Repo that returns empty whitelist (forces meta fallback)."""
    class Repo:
        def list_whitelist_symbols(self, **kw):
            return []
    return Repo(), None, None, None
