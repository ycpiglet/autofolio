"""Tests for app/quant/data_loader.py — SQLite price cache, load_prices, cache_prices."""
import pytest
import tempfile
from datetime import date
from pathlib import Path
from unittest.mock import patch, MagicMock


def _tmp_db_path(tmp_path):
    return tmp_path / "trading_bot.db"


@pytest.fixture
def patch_db(tmp_path):
    """Redirect all price_cache.db operations to a temp directory."""
    db_path = str(tmp_path / "trading_bot.db")
    with patch("app.config.settings.settings") as mock_settings:
        mock_settings.db_path = db_path
        yield tmp_path


def test_cache_prices_returns_row_count(patch_db):
    from app.quant.data_loader import cache_prices, _price_cache_db
    tmp_path = patch_db
    cache_path = tmp_path / "price_cache.db"
    with patch("app.quant.data_loader._price_cache_db", return_value=cache_path):
        rows = [
            {"date": "2026-06-09", "open": 300000.0, "high": 305000.0,
             "low": 299000.0, "close": 302000.0, "volume": 12000000},
            {"date": "2026-06-08", "open": 295000.0, "high": 300000.0,
             "low": 294000.0, "close": 298000.0, "volume": 9000000},
        ]
        count = cache_prices("005930", rows)
        assert count == 2


def test_load_prices_returns_cached_rows(patch_db):
    from app.quant.data_loader import cache_prices, load_prices, _price_cache_db
    tmp_path = patch_db
    cache_path = tmp_path / "price_cache.db"
    with patch("app.quant.data_loader._price_cache_db", return_value=cache_path):
        rows = [
            {"date": "2026-06-09", "open": 300000.0, "high": 305000.0,
             "low": 299000.0, "close": 302000.0, "volume": 12000000},
        ]
        cache_prices("005930", rows)
        result = load_prices("005930", date(2026, 6, 1), date(2026, 6, 30))
        assert len(result) == 1
        assert result[0]["close"] == 302000.0


def test_load_prices_returns_empty_when_no_data(patch_db):
    from app.quant.data_loader import load_prices, _price_cache_db
    tmp_path = patch_db
    cache_path = tmp_path / "price_cache.db"
    with patch("app.quant.data_loader._price_cache_db", return_value=cache_path):
        result = load_prices("999999", date(2026, 6, 1), date(2026, 6, 30))
        assert result == []


def test_load_prices_respects_as_of_cutoff(patch_db):
    from app.quant.data_loader import cache_prices, load_prices, _price_cache_db
    tmp_path = patch_db
    cache_path = tmp_path / "price_cache.db"
    with patch("app.quant.data_loader._price_cache_db", return_value=cache_path):
        rows = [
            {"date": "2026-06-05", "open": 290000.0, "high": 295000.0,
             "low": 289000.0, "close": 292000.0, "volume": 8000000},
            {"date": "2026-06-09", "open": 300000.0, "high": 305000.0,
             "low": 299000.0, "close": 302000.0, "volume": 12000000},
        ]
        cache_prices("005930", rows)
        # Cut off at June 7 — should not see June 9
        result = load_prices("005930", date(2026, 6, 1), date(2026, 6, 30),
                              as_of=date(2026, 6, 7))
        assert len(result) == 1
        assert result[0]["date"] == "2026-06-05"


def test_cache_prices_upsert_overwrites(patch_db):
    from app.quant.data_loader import cache_prices, load_prices, _price_cache_db
    tmp_path = patch_db
    cache_path = tmp_path / "price_cache.db"
    with patch("app.quant.data_loader._price_cache_db", return_value=cache_path):
        # Insert first
        cache_prices("005930", [{"date": "2026-06-09", "open": 300000.0, "high": 305000.0,
                                   "low": 299000.0, "close": 302000.0, "volume": 12000000}])
        # Upsert with different close
        cache_prices("005930", [{"date": "2026-06-09", "open": 300000.0, "high": 305000.0,
                                   "low": 299000.0, "close": 310000.0, "volume": 12000000}])
        result = load_prices("005930", date(2026, 6, 1), date(2026, 6, 30))
        assert len(result) == 1
        assert result[0]["close"] == 310000.0


def test_fetch_and_cache_returns_zero_on_exception(patch_db):
    """fetch_and_cache should return 0 when KIS API raises exception."""
    from app.quant.data_loader import fetch_and_cache
    # Patch requests.get to raise so the except clause runs and returns 0
    with patch("requests.get", side_effect=Exception("network error")):
        result = fetch_and_cache("005930", date(2026, 6, 1), date(2026, 6, 9))
    assert result == 0


def test_fetch_and_cache_returns_zero_on_api_error(patch_db):
    """fetch_and_cache returns 0 when rt_cd != 0."""
    from app.quant.data_loader import fetch_and_cache
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"rt_cd": "1", "msg1": "error"}
    with patch("requests.get", return_value=mock_resp):
        with patch("app.brokers.kis.kis_auth.KisAuth.get_access_token", return_value="fake-token"):
            result = fetch_and_cache("005930", date(2026, 6, 1), date(2026, 6, 9))
    assert result == 0


def test_fetch_and_cache_success_caches_rows(patch_db):
    """fetch_and_cache returns count when API returns data."""
    from app.quant.data_loader import fetch_and_cache, load_prices, _price_cache_db
    tmp_path = patch_db

    fake_rows = [
        {"stck_bsop_date": "20260609", "stck_oprc": "300000", "stck_hgpr": "305000",
         "stck_lwpr": "299000", "stck_clpr": "302000", "acml_vol": "12000000"},
        {"stck_bsop_date": "20260608", "stck_oprc": "295000", "stck_hgpr": "300000",
         "stck_lwpr": "294000", "stck_clpr": "298000", "acml_vol": "9000000"},
        {"stck_bsop_date": "", "stck_oprc": "0"},  # row without date → skipped
    ]
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"rt_cd": "0", "output2": fake_rows}

    cache_path = tmp_path / "price_cache.db"
    with patch("requests.get", return_value=mock_resp):
        with patch("app.brokers.kis.kis_auth.KisAuth.get_access_token", return_value="fake-token"):
            with patch("app.quant.data_loader._price_cache_db", return_value=cache_path):
                result = fetch_and_cache("005930", date(2026, 6, 1), date(2026, 6, 9))
    assert result == 2  # 2 rows cached (1 skipped because empty date)


def test_price_cache_db_uses_settings_path(tmp_path):
    """_price_cache_db returns a path based on settings.db_path."""
    from app.quant.data_loader import _price_cache_db
    db_path = str(tmp_path / "trading_bot.db")
    with patch("app.quant.data_loader.settings") as mock_settings:
        mock_settings.db_path = db_path
        result = _price_cache_db()
        assert result.name == "price_cache.db"
        assert result.parent == tmp_path
